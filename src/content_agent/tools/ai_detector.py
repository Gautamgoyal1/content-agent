"""AI Content Detector client supporting GPTZero, Sapling, Winston, and Linguistic LLM Inspection."""

import os
import re
import math
import csv
from datetime import datetime, timezone
from typing import Any
import httpx
from pydantic import BaseModel, Field

from content_agent.tools.llm import LLMClient


class AIDetectionResult(BaseModel):
    """Detailed results from AI content detection."""

    ai_score: float = Field(..., description="Estimated AI-generated probability from 0.0 to 1.0")
    human_score: float = Field(..., description="Estimated human-written probability from 0.0 to 1.0")
    is_human_like: bool = Field(..., description="True if content passes human authenticity threshold")
    tool: str = Field(..., description="Detector engine or API provider used")
    flagged_phrases: list[str] = Field(default_factory=list, description="Common AI formulaic phrases detected")
    burstiness_score: float = Field(default=0.0, description="Sentence length standard deviation (higher = more human)")
    details: str = ""


# Common formulaic phrases heavily over-indexed in typical AI generation
AI_CLICHE_PATTERNS = [
    r"\bdelve(?:s|d)?\s+into\b",
    r"\btapestry\b",
    r"\btestament\s+to\b",
    r"\bpivotal\s+role\b",
    r"\bcrucial\s+role\b",
    r"\bnavigat(?:ing|e|es)\s+the\s+landscape\b",
    r"\bin\s+conclusion\b",
    r"\bfurthermore\b",
    r"\bmoreover\b",
    r"\bit\s+is\s+worth\s+noting\b",
    r"\bit\s+is\s+important\s+to\s+remember\b",
    r"\bever-evolving\s+landscape\b",
    r"\bharness(?:ing)?\s+the\s+power\s+of\b",
    r"\bunlock(?:ing)?\s+the\s+potential\b",
    r"\bbeacon\s+of\b",
    r"\bgame-changer\b",
]


class AIDetectorClient:
    """Evaluates content using dedicated AI detector APIs or an adversarial linguistic evaluator."""

    def __init__(self, api_key: str | None = None, provider: str | None = None):
        self.gptzero_key = api_key or os.getenv("GPTZERO_API_KEY") or os.getenv("AI_DETECTOR_API_KEY")
        self.sapling_key = api_key or os.getenv("SAPLING_API_KEY")
        self.winston_key = api_key or os.getenv("WINSTON_API_KEY")
        self.provider = (provider or os.getenv("AI_DETECTOR_PROVIDER", "")).lower()
        self.llm_client = LLMClient()
        self.csv_log_path = "evals/detector_scores.csv"

    def _calculate_burstiness(self, text: str) -> float:
        """Measure variance in sentence length. Humans write with varied sentence lengths (burstiness); AI is uniform."""
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if len(s.strip()) > 5]
        if len(sentences) < 2:
            return 0.0
        lengths = [len(s.split()) for s in sentences]
        mean_len = sum(lengths) / len(lengths)
        variance = sum((l - mean_len) ** 2 for l in lengths) / len(lengths)
        return round(math.sqrt(variance), 2)

    def _find_cliches(self, text: str) -> list[str]:
        """Scan text for common AI transition clichés."""
        found = []
        for pattern in AI_CLICHE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                found.append(matches[0].lower())
        return list(dict.fromkeys(found))

    def _log_score_to_csv(self, content_id: str, tool: str, score: float, notes: str) -> None:
        """Append detection metrics to evals/detector_scores.csv."""
        try:
            os.makedirs(os.path.dirname(self.csv_log_path), exist_ok=True)
            file_exists = os.path.exists(self.csv_log_path)
            with open(self.csv_log_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["date", "content_id", "tool", "score", "notes"])
                writer.writerow([
                    datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                    content_id,
                    tool,
                    f"{score:.2f}",
                    notes.replace(",", ";"),
                ])
        except Exception:
            pass

    def detect(self, text: str, content_id: str = "draft") -> AIDetectionResult:
        """Analyze text and return comprehensive AI vs human authenticity metrics."""
        # Strip references for clean textual evaluation
        body_text = text.split("## References & Verified Sources")[0].strip()
        if not body_text:
            return AIDetectionResult(
                ai_score=0.0,
                human_score=1.0,
                is_human_like=True,
                tool="none",
                details="Empty document body",
            )

        burstiness = self._calculate_burstiness(body_text)
        cliches = self._find_cliches(body_text)

        # 1. External API: GPTZero
        if (self.provider == "gptzero" or self.gptzero_key) and self.gptzero_key:
            try:
                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(
                        "https://api.gptzero.me/v2/predict/text",
                        headers={"x-api-key": self.gptzero_key, "Content-Type": "application/json"},
                        json={"document": body_text},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        prob = data.get("documents", [{}])[0].get("completely_generated_prob", 0.0)
                        ai_score = round(float(prob), 2)
                        human_score = round(1.0 - ai_score, 2)
                        result = AIDetectionResult(
                            ai_score=ai_score,
                            human_score=human_score,
                            is_human_like=ai_score <= 0.35,
                            tool="GPTZero API",
                            flagged_phrases=cliches,
                            burstiness_score=burstiness,
                            details=f"GPTZero verification score: {int(human_score * 100)}% Human.",
                        )
                        self._log_score_to_csv(content_id, "GPTZero API", ai_score, f"Burstiness: {burstiness}")
                        return result
            except Exception:
                pass

        # 2. External API: Sapling AI
        if self.sapling_key:
            try:
                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(
                        "https://api.sapling.ai/api/v1/aidetect",
                        headers={"Content-Type": "application/json"},
                        json={"key": self.sapling_key, "text": body_text[:4000]},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        score = round(float(data.get("score", 0.0)), 2)
                        result = AIDetectionResult(
                            ai_score=score,
                            human_score=round(1.0 - score, 2),
                            is_human_like=score <= 0.35,
                            tool="Sapling AI Detector API",
                            flagged_phrases=cliches,
                            burstiness_score=burstiness,
                            details=f"Sapling AI detection probability: {int((1.0 - score) * 100)}% Human.",
                        )
                        self._log_score_to_csv(content_id, "Sapling AI API", score, f"Burstiness: {burstiness}")
                        return result
            except Exception:
                pass

        # 3. LLM-Based Adversarial Inspection (Groq / OpenAI)
        if self.llm_client.is_available:
            try:
                eval_prompt = (
                    "You are a strict, forensic AI Content Detector analyzing an article draft.\n"
                    "Analyze the writing style for tell-tale artificial characteristics: predictable sentence cadence, "
                    "lack of burstiness, formulaic transitions, passive phrasing, or generic platitudes.\n\n"
                    f"Text excerpt:\n\"\"\"{body_text[:1500]}\"\"\"\n\n"
                    "Respond with ONLY a JSON object in this exact format:\n"
                    "{\"ai_percentage\": <integer between 0 and 100>, \"reason\": \"<one-sentence rationale>\"}"
                )
                raw_eval = self.llm_client.generate(eval_prompt, system_prompt="You are an unbiased forensic AI-content detector. Output valid JSON only.")
                if raw_eval:
                    match = re.search(r"\{\s*\"ai_percentage\"\s*:\s*(\d+)", raw_eval)
                    if match:
                        ai_pct = int(match.group(1))
                        ai_score = round(ai_pct / 100.0, 2)
                        human_score = round(1.0 - ai_score, 2)
                        tool_name = f"Linguistic AI Inspector ({self.llm_client.provider.title() if self.llm_client.provider else 'LLM'})"
                        result = AIDetectionResult(
                            ai_score=ai_score,
                            human_score=human_score,
                            is_human_like=ai_score <= 0.35,
                            tool=tool_name,
                            flagged_phrases=cliches,
                            burstiness_score=burstiness,
                            details=f"Evaluated by {tool_name}: {int(human_score * 100)}% Human Authenticity.",
                        )
                        self._log_score_to_csv(content_id, tool_name, ai_score, f"Burstiness: {burstiness}, Cliches: {len(cliches)}")
                        return result
            except Exception:
                pass

        # 4. Fallback: Deterministic Linguistic & Burstiness Heuristic Analyzer
        # Low burstiness (< 6.0) + presence of clichés elevates AI score
        base_ai = 0.20
        if burstiness < 5.0:
            base_ai += 0.25
        elif burstiness > 8.0:
            base_ai -= 0.10

        base_ai += min(0.35, len(cliches) * 0.10)
        ai_score = round(max(0.05, min(0.95, base_ai)), 2)
        human_score = round(1.0 - ai_score, 2)

        result = AIDetectionResult(
            ai_score=ai_score,
            human_score=human_score,
            is_human_like=ai_score <= 0.35,
            tool="Deterministic Linguistic & Burstiness Inspector",
            flagged_phrases=cliches,
            burstiness_score=burstiness,
            details=f"Linguistic Burstiness Score: {burstiness} (Sentence variance). {len(cliches)} generic AI clichés detected.",
        )
        self._log_score_to_csv(content_id, "Linguistic Burstiness Inspector", ai_score, f"Burstiness: {burstiness}")
        return result
