"""AI content detection and human authenticity quality gate."""

from content_agent.models.check_result import QualityCheckResult
from content_agent.tools.ai_detector import AIDetectorClient


def validate_ai_content(markdown_text: str, content_id: str = "run") -> QualityCheckResult:
    """Evaluate text for AI generated probability and human writing authenticity."""
    client = AIDetectorClient()
    result = client.detect(markdown_text, content_id=content_id)

    human_pct = int(result.human_score * 100)
    ai_pct = int(result.ai_score * 100)
    label_prefix = "Heuristic: " if result.is_heuristic else "API: "

    cliches_note = f" Flagged clichés: {', '.join(result.flagged_phrases)}." if result.flagged_phrases else " Zero flagged clichés."

    if result.is_human_like:
        return QualityCheckResult(
            name="AI Content & Human Likeness Heuristic",
            passed=True,
            score_or_metric=f"{human_pct}% Human / {ai_pct}% AI ({label_prefix}{result.tool})",
            details=f"Authentic natural cadence verified (burstiness: {result.burstiness_score} std dev, lexical diversity: {result.vocabulary_richness}).{cliches_note}",
            severity="info",
        )

    return QualityCheckResult(
        name="AI Content & Human Likeness Heuristic",
        passed=False,
        score_or_metric=f"{ai_pct}% AI Likelihood / {human_pct}% Human ({label_prefix}{result.tool})",
        details=f"Elevated AI cadence detected (threshold: <= {int(client.threshold * 100)}% AI). Burstiness: {result.burstiness_score}.{cliches_note} Recommend humanizing cadence.",
        severity="warning",
    )
