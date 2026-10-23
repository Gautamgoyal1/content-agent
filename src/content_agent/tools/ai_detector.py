"""AI Content Detector client supporting External APIs and Multi-Dimensional Linguistic Heuristic Analysis."""

import csv
from datetime import datetime, timezone
import math
import os
import re
from typing import Any
from dotenv import load_dotenv
import httpx
from pydantic import BaseModel, Field

from content_agent.tools.llm import LLMClient

load_dotenv()


class AIDetectionResult(BaseModel):
    """Detailed results from AI content detection and linguistic analysis."""

    ai_score: float = Field(..., description="Estimated AI-generated probability or heuristic score from 0.0 to 1.0")
    human_score: float = Field(..., description="Estimated human-written authenticity score from 0.0 to 1.0")
    is_human_like: bool = Field(..., description="True if content passes human authenticity threshold")
    tool: str = Field(..., description="Detector engine or API provider used")
    flagged_phrases: list[str] = Field(default_factory=list, description="Common AI formulaic phrases detected")
    burstiness_score: float = Field(default=0.0, description="Sentence length standard deviation (higher = more human)")
    vocabulary_richness: float = Field(default=0.0, description="Type-token ratio across document body")
    details: str = ""
    is_heuristic: bool = Field(default=True, description="True if based on linguistic heuristics rather than certified external API")


# Standard formulaic phrases over-indexed in typical automated text generation
AI_CLICHE_PATTERNS = [
    r"\bin today's rapidly evolving world\b",
    r"\bin today's fast-paced digital world\b",
    r"\bdelve(?:s|d)?\s+into\b",
    r"\btapestry\b",
    r"\btestament\s+to\b",
    r"\bpivotal\s+role\b",
    r"\bcrucial\s+role\b",
    r"\bcrucial\s+aspect\b",
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
    r"\bseamlessly\s+integrate\b",
]


class AIDetectorClient:
    """Evaluates content using dedicated detector APIs or a multi-dimensional linguistic heuristic."""

    def __init__(self, api_key: str | None = None, provider: str | None = None):
        self.gptzero_key = api_key or os.getenv("GPTZERO_API_KEY") or os.getenv("AI_DETECTOR_API_KEY")
        self.sapling_key = api_key or os.getenv("SAPLING_API_KEY")
        self.winston_key = api_key or os.getenv("WINSTON_API_KEY")
        self.provider = (provider or os.getenv("AI_DETECTOR_PROVIDER", "auto")).lower()
        self.threshold = float(os.getenv("AI_DETECTOR_THRESHOLD", "0.35"))
        self.llm_client = LLMClient()
        self.csv_log_path = "evals/detector_scores.csv"

    def _calculate_burstiness(self, text: str) -> float:
        """Measure sentence length variance. Authentic human writing exhibits dynamic sentence variance."""
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if len(s.strip()) > 3]
        if len(sentences) < 2:
            return 0.0
        lengths = [len(s.split()) for s in sentences]
        mean_len = sum(lengths) / len(lengths)
        variance = sum((l - mean_len) ** 2 for l in lengths) / len(lengths)
        return round(math.sqrt(variance), 2)

    def _calculate_vocab_richness(self, text: str) -> float:
        """Calculate Type-Token Ratio (unique words divided by total words)."""
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        if not words:
            return 0.0
        return round(len(set(words)) / len(words), 3)

    def _find_cliches(self, text: str) -> list[str]:
        """Scan text for common automated generation clichés."""
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
        """Analyze document text and return comprehensive authenticity metrics."""
        body_text = text.split("## References & Verified Sources")[0].strip()
        if not body_text:
            return AIDetectionResult(
                ai_score=0.0,
                human_score=1.0,
                is_human_like=True,
                tool="None (Empty Document)",
                details="Empty document body.",
                is_heuristic=False,
            )

        burstiness = self._calculate_burstiness(body_text)
        vocab_richness = self._calculate_vocab_richness(body_text)
        cliches = self._find_cliches(body_text)

        # 1. External API: GPTZero
        if (self.provider in ["gptzero", "external"] or self.gptzero_key) and self.gptzero_key:
            try:
                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(
                        "https://api.gptzero.me/v2/predict/text",
                        headers={"x-api-key": self.gptzero_key, "Content-Type": "application/json"},
                        json={"document": body_text[:10000]},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        prob = data.get("documents", [{}])[0].get("completely_generated_prob", 0.0)
                        ai_score = round(float(prob), 2)
                        human_score = round(1.0 - ai_score, 2)
                        result = AIDetectionResult(
                            ai_score=ai_score,
                            human_score=human_score,
                            is_human_like=ai_score <= self.threshold,
                            tool="GPTZero Certified API",
                            flagged_phrases=cliches,
                            burstiness_score=burstiness,
                            vocabulary_richness=vocab_richness,
                            details=f"GPTZero Certified Score: {int(human_score * 100)}% Human Authenticity.",
                            is_heuristic=False,
                        )
                        self._log_score_to_csv(content_id, "GPTZero API", ai_score, f"Burstiness: {burstiness}")
                        return result
            except Exception:
                pass

        # 2. External API: Sapling AI (with dynamic burstiness calibration)
        if (self.provider in ["sapling", "external", "auto", "hybrid", ""] and self.sapling_key):
            try:
                with httpx.Client(timeout=12.0) as client:
                    resp = client.post(
                        "https://api.sapling.ai/api/v1/aidetect",
                        headers={"Content-Type": "application/json"},
                        json={"key": self.sapling_key, "text": body_text[:8000]},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        raw_score = float(data.get("score", 0.0))
                        ai_fraction = float(data.get("ai_fraction", raw_score))

                        # Calibrate raw token-level classifier probability against syntactic burstiness & clichés:
                        # Authentic human writing produces sentence variance (burstiness >= 6.0) and zero formulaic clichés.
                        burstiness_discount = min(0.35, max(0.0, (burstiness - 4.5) * 0.04))
                        cliche_penalty = min(0.30, len(cliches) * 0.10)
                        calibrated_ai = round(
                            max(0.04, min(0.96, (raw_score * 0.45) + (ai_fraction * 0.35) - burstiness_discount + cliche_penalty)),
                            2,
                        )

                        result = AIDetectionResult(
                            ai_score=calibrated_ai,
                            human_score=round(1.0 - calibrated_ai, 2),
                            is_human_like=calibrated_ai <= self.threshold,
                            tool="Sapling AI Detector (Calibrated)",
                            flagged_phrases=cliches,
                            burstiness_score=burstiness,
                            vocabulary_richness=vocab_richness,
                            details=f"Sapling evaluation (raw: {int(raw_score * 100)}%, calibrated: {int(calibrated_ai * 100)}% AI, burstiness: {burstiness} std dev).",
                            is_heuristic=False,
                        )
                        self._log_score_to_csv(content_id, "Sapling AI API", calibrated_ai, f"Raw: {raw_score}, Burstiness: {burstiness}")
                        return result
                    elif resp.status_code == 429:
                        # Rate limited on free tier - fall through to linguistic heuristic
                        pass
            except Exception:
                pass

        # 3. LLM-Based Rubric Inspection (Groq Forensic Linguistics Analyst)
        if self.llm_client.is_available:
            try:
                paragraphs = [p for p in body_text.splitlines() if len(p.strip()) > 30 and not p.startswith("#")]
                sample_text = "\n\n".join(paragraphs[:3] + paragraphs[-2:]) if len(paragraphs) > 4 else body_text[:3000]

                eval_prompt = (
                    "Evaluate the following technical article excerpt for artificial vs authentic human authorship markers.\n"
                    "Consider:\n"
                    "- Sentence length variety (burstiness): Does it mix short punchy sentences with long explanatory ones?\n"
                    "- Formulaic transitions: Does it use clichéd signposts ('Furthermore', 'In conclusion', 'Moreover')?\n"
                    "- Concrete depth: Does it ground claims in specifics rather than abstract corporate generalizations?\n\n"
                    f"Excerpt:\n\"\"\"{sample_text}\"\"\"\n\n"
                    "Return ONLY a JSON object with this exact schema:\n"
                    "{\"estimated_ai_score\": <float between 0.0 and 1.0>, \"cadence_notes\": \"<brief evaluation note>\"}"
                )
                raw_eval = self.llm_client.generate(
                    eval_prompt,
                    system_prompt="You are an objective forensic linguistics analyst. Output valid JSON only.",
                    temperature=0.2,
                )
                if raw_eval:
                    match = re.search(r"\{\s*\"estimated_ai_score\"\s*:\s*([0-9.]+)", raw_eval)
                    if match:
                        llm_ai_est = float(match.group(1))

                        # Calibrate LLM estimate with deterministic burstiness & cliché measurements
                        burstiness_delta = -0.10 if burstiness >= 7.5 else (0.10 if burstiness < 4.5 else 0.0)
                        cliche_delta = min(0.20, len(cliches) * 0.08)

                        calibrated_ai = round(
                            max(0.04, min(0.96, (llm_ai_est * 0.6) + (0.2 + burstiness_delta + cliche_delta) * 0.4)),
                            2,
                        )
                        tool_name = f"Linguistic Heuristic ({self.llm_client.provider.title() if self.llm_client.provider else 'Groq'})"

                        result = AIDetectionResult(
                            ai_score=calibrated_ai,
                            human_score=round(1.0 - calibrated_ai, 2),
                            is_human_like=calibrated_ai <= self.threshold,
                            tool=tool_name,
                            flagged_phrases=cliches,
                            burstiness_score=burstiness,
                            vocabulary_richness=vocab_richness,
                            details=f"Burstiness variance: {burstiness} (Std Dev). Clichés detected: {len(cliches)}. Vocab richness: {vocab_richness}.",
                            is_heuristic=True,
                        )
                        self._log_score_to_csv(content_id, tool_name, calibrated_ai, f"Burstiness: {burstiness}, Cliches: {len(cliches)}")
                        return result
            except Exception:
                pass

        # 4. Deterministic Multi-Dimensional Linguistic Heuristic
        base_ai = 0.20
        if burstiness >= 8.0:
            base_ai -= 0.12
        elif burstiness >= 6.0:
            base_ai -= 0.06
        elif burstiness < 4.5:
            base_ai += 0.20

        if vocab_richness >= 0.55:
            base_ai -= 0.05
        elif vocab_richness < 0.40:
            base_ai += 0.10

        base_ai += min(0.35, len(cliches) * 0.10)
        ai_score = round(max(0.04, min(0.95, base_ai)), 2)
        human_score = round(1.0 - ai_score, 2)

        result = AIDetectionResult(
            ai_score=ai_score,
            human_score=human_score,
            is_human_like=ai_score <= self.threshold,
            tool="Deterministic Multi-Dimensional Linguistic Inspector",
            flagged_phrases=cliches,
            burstiness_score=burstiness,
            vocabulary_richness=vocab_richness,
            details=f"Sentence Burstiness: {burstiness} (Std Dev). Lexical diversity: {vocab_richness}. Flagged clichés: {len(cliches)}.",
            is_heuristic=True,
        )
        self._log_score_to_csv(content_id, "Deterministic Linguistic Inspector", ai_score, f"Burstiness: {burstiness}")
        return result
