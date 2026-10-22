"""Markdown heading hierarchy and structural gate."""

import re
from content_agent.models.check_result import QualityCheckResult


def validate_headings(markdown_text: str) -> QualityCheckResult:
    """Verify document heading structure contains exactly one H1 and multiple H2 sections."""
    h1_matches = re.findall(r"^#\s+(.+)$", markdown_text, re.MULTILINE)
    h2_matches = re.findall(r"^##\s+(.+)$", markdown_text, re.MULTILINE)

    if len(h1_matches) == 1 and len(h2_matches) >= 2:
        return QualityCheckResult(
            name="Heading Structure",
            passed=True,
            score_or_metric=f"1 H1 title, {len(h2_matches)} H2 sections",
            details="Valid markdown document hierarchy with clear sections.",
            severity="info",
        )
    elif len(h1_matches) == 0:
        return QualityCheckResult(
            name="Heading Structure",
            passed=False,
            score_or_metric="Missing H1 title",
            details="Document lacks a primary top-level # title heading.",
            severity="error",
        )
    elif len(h1_matches) > 1:
        return QualityCheckResult(
            name="Heading Structure",
            passed=False,
            score_or_metric=f"{len(h1_matches)} H1 titles detected",
            details="Document contains multiple top-level H1 headings. Subsections should use ##.",
            severity="warning",
        )
    else:
        return QualityCheckResult(
            name="Heading Structure",
            passed=False,
            score_or_metric=f"{len(h2_matches)} H2 sections",
            details="Document lacks sufficient H2 section headings (minimum 2 required).",
            severity="warning",
        )
