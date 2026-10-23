"""AI content detection and human authenticity quality gate."""

from content_agent.models.check_result import QualityCheckResult
from content_agent.tools.ai_detector import AIDetectorClient


def validate_ai_content(markdown_text: str, content_id: str = "run") -> QualityCheckResult:
    """Evaluate text for AI generated probability and human writing authenticity."""
    client = AIDetectorClient()
    result = client.detect(markdown_text, content_id=content_id)

    human_pct = int(result.human_score * 100)
    ai_pct = int(result.ai_score * 100)

    if result.is_human_like:
        return QualityCheckResult(
            name="AI Content & Human Likeness",
            passed=True,
            score_or_metric=f"{human_pct}% Human / {ai_pct}% AI ({result.tool})",
            details=f"Authentic natural phrasing verified. Burstiness score: {result.burstiness_score}.",
            severity="info",
        )

    cliche_notice = f" Flagged clichés: {', '.join(result.flagged_phrases)}." if result.flagged_phrases else ""
    return QualityCheckResult(
        name="AI Content & Human Likeness",
        passed=False,
        score_or_metric=f"{ai_pct}% AI Likelihood / {human_pct}% Human ({result.tool})",
        details=f"Elevated AI content detected (threshold: <= 35% AI).{cliche_notice} Recommend humanizing cadence.",
        severity="warning",
    )
