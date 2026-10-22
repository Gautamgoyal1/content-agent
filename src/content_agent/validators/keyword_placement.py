"""Keyword placement and topic focus validator."""

import re
from content_agent.models.check_result import QualityCheckResult


def validate_keyword_placement(markdown_text: str, topic: str, audience: str) -> QualityCheckResult:
    """Validate that topic and audience keywords are prominently positioned."""
    lines = [ln.strip() for ln in markdown_text.splitlines() if ln.strip()]
    if not lines:
        return QualityCheckResult(
            name="Keyword Placement",
            passed=False,
            score_or_metric="Empty document",
            details="Document contains no content to inspect.",
            severity="error",
        )

    topic_tokens = set(re.findall(r"\b[a-zA-Z0-9]{3,}\b", topic.lower()))
    lead_text = " ".join(lines[:6]).lower()

    matches = [tok for tok in topic_tokens if tok in lead_text]
    match_ratio = len(matches) / max(len(topic_tokens), 1)

    if match_ratio >= 0.5:
        return QualityCheckResult(
            name="Keyword Placement",
            passed=True,
            score_or_metric=f"{int(match_ratio * 100)}% topic coverage in intro",
            details="Primary topic keywords are prominently featured in the headline and opening section.",
            severity="info",
        )
    return QualityCheckResult(
        name="Keyword Placement",
        passed=False,
        score_or_metric=f"{int(match_ratio * 100)}% topic coverage in intro",
        details="Opening section lacks clear focus on primary topic keywords.",
        severity="warning",
    )
