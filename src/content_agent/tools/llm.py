"""Unified LLM client supporting OpenAI, Groq, and deterministic synthesis."""

import os
from typing import Any
from dotenv import load_dotenv
import httpx

load_dotenv()


class LLMClient:
    """Client for LLM invocations with automatic fallback to deterministic synthesis."""

    def __init__(self, api_key: str | None = None, provider: str | None = None, model: str | None = None):
        self._api_key = api_key
        self._provider = provider
        self._custom_model = model

    @property
    def openai_key(self) -> str | None:
        return self._api_key or os.getenv("OPENAI_API_KEY")

    @property
    def groq_key(self) -> str | None:
        return self._api_key or os.getenv("GROQ_API_KEY")

    @property
    def provider(self) -> str | None:
        if self._provider:
            return self._provider
        env_prov = os.getenv("LLM_PROVIDER")
        if env_prov:
            return env_prov.lower()
        if self.openai_key:
            return "openai"
        if self.groq_key:
            return "groq"
        return None

    @property
    def is_available(self) -> bool:
        return bool(self.openai_key or self.groq_key)

    def generate(
        self,
        prompt: str,
        system_prompt: str = "You are an expert technical writer and investigative journalist.",
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str | None:
        """Call external LLM API if configured."""
        if not self.is_available:
            return None

        is_openai = (self.provider == "openai" or (self.openai_key and not self.groq_key))
        url = "https://api.openai.com/v1/chat/completions" if is_openai else "https://api.groq.com/openai/v1/chat/completions"
        key = self.openai_key if is_openai else self.groq_key

        if self._custom_model or os.getenv("LLM_MODEL"):
            model = self._custom_model or os.getenv("LLM_MODEL")
        elif is_openai:
            model = "gpt-4o-mini"
        else:
            # Fast, high-capacity model on Groq that returns direct content
            model = "qwen/qwen3.8-27b"

        try:
            with httpx.Client(timeout=60.0) as client:
                res = client.post(
                    url,
                    headers={"Authorization": f"Bearer {key}"},
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                )
                if res.status_code == 200:
                    data = res.json()
                    msg = data.get("choices", [{}])[0].get("message", {})
                    content = msg.get("content")
                    if content and content.strip():
                        return content.strip()
                    # If reasoning model stored answer in reasoning field
                    reasoning = msg.get("reasoning")
                    if reasoning and reasoning.strip():
                        return reasoning.strip()

                # Fallback to secondary model if needed
                if not is_openai and res.status_code != 200:
                    fallback_models = ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]
                    for fb_model in fallback_models:
                        res2 = client.post(
                            url,
                            headers={"Authorization": f"Bearer {key}"},
                            json={
                                "model": fb_model,
                                "messages": [
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": prompt},
                                ],
                                "temperature": temperature,
                                "max_tokens": max_tokens,
                            },
                        )
                        if res2.status_code == 200:
                            data2 = res2.json()
                            msg2 = data2.get("choices", [{}])[0].get("message", {})
                            content2 = msg2.get("content")
                            if content2 and content2.strip():
                                return content2.strip()
                            reasoning2 = msg2.get("reasoning")
                            if reasoning2 and reasoning2.strip():
                                return reasoning2.strip()
        except Exception:
            pass
        return None
