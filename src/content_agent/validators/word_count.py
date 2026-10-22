"""Word count validation gate."""

from content_agent.models.check_result import QualityCheckResult


def validate_word_count(markdown_text: str, target_words: int, max_tolerance: float = 0.25) -> QualityCheckResult:
    """Validate that actual word count falls within acceptable variance of the target."""
    body_text = markdown_text.split("## References & Verified Sources")[0]
    words = len(body_text.split())
    target = max(target_words, 1)
    deviation = abs(words - target) / target

    if deviation <= max_tolerance:
        return QualityCheckResult(
            name="Word Count Target",
            passed=True,
            score_or_metric=f"{words} words (target: {target_words})",
            details=f"Length is within optimal target range ({int(deviation * 100)}% variance).",
            severity="info",
        )
    elif deviation <= 0.40:
        return QualityCheckResult(
            name="Word Count Target",
            passed=True,
            score_or_metric=f"{words} words (target: {target_words})",
            details=f"Moderate deviation from target ({int(deviation * 100)}% variance).",
            severity="warning",
        )
    else:
        return QualityCheckResult(
            name="Word Count Target",
            passed=False,
            score_or_metric=f"{words} words (target: {target_words})",
            details=f"Significant deviation from target ({int(deviation * 100)}% variance). Requires adjustment.",
            severity="warning",
        )
