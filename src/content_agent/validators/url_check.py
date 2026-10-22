"""Source citation and URL linkage verification gate."""

import re
from content_agent.models.source import SourceEvidence
from content_agent.models.check_result import QualityCheckResult


def validate_citations(markdown_text: str, sources: list[SourceEvidence]) -> QualityCheckResult:
    """Verify all inline citation markers [X] in markdown body map to a registered source."""
    body_text = markdown_text.split("## References & Verified Sources")[0]
    raw_citations = re.findall(r"\[(\d+)\]", body_text)
    citation_ids = {int(x) for x in raw_citations}
    registered_ids = {s.id for s in sources}

    if not citation_ids:
        return QualityCheckResult(
            name="Source Citations",
            passed=False,
            score_or_metric="0 citations found",
            details="No inline citations found in document body. Claims must be grounded in evidence.",
            severity="warning",
        )

    phantom_ids = citation_ids - registered_ids
    if phantom_ids:
        return QualityCheckResult(
            name="Source Citations",
            passed=False,
            score_or_metric=f"{len(phantom_ids)} phantom citation(s)",
            details=f"Citations {sorted(list(phantom_ids))} lack backing research sources.",
            severity="error",
        )

    return QualityCheckResult(
        name="Source Citations",
        passed=True,
        score_or_metric=f"{len(citation_ids)} distinct evidence references",
        details=f"All inline citations {sorted(list(citation_ids))} resolve to verified sources.",
        severity="info",
    )
