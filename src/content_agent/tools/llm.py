"""Unified LLM client supporting OpenAI, Groq, and deterministic synthesis."""

import os
from typing import Any
import httpx

from content_agent.models.source import SourceEvidence


class LLMClient:
    """Client for LLM invocations with automatic fallback to deterministic synthesis."""

    def __init__(self, api_key: str | None = None, provider: str | None = None):
        self.openai_key = api_key or os.getenv("OPENAI_API_KEY")
        self.groq_key = api_key or os.getenv("GROQ_API_KEY")
        self.provider = provider or os.getenv("LLM_PROVIDER") or ("openai" if self.openai_key else ("groq" if self.groq_key else None))

    @property
    def is_available(self) -> bool:
        return bool(self.openai_key or self.groq_key)

    def generate(self, prompt: str, system_prompt: str = "You are an expert technical writer and fact checker.") -> str | None:
        """Call external LLM API if configured."""
        if not self.is_available:
            return None

        url = "https://api.openai.com/v1/chat/completions" if (self.provider == "openai" or self.openai_key) else "https://api.groq.com/openai/v1/chat/completions"
        key = self.openai_key or self.groq_key
        model = "gpt-4o-mini" if (self.provider == "openai" or self.openai_key) else "llama-3.1-8b-instant"

        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.post(
                    url,
                    headers={"Authorization": f"Bearer {key}"},
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.3,
                    },
                )
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"]
        except Exception:
            pass
        return None
