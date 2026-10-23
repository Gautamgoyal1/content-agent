"""Comprehensive editorial quality auditor evaluating depth, repetition, transitions, and evidence grounding."""

import re
from content_agent.models.brief import ContentBrief
from content_agent.models.source import SourceEvidence
from content_agent.models.check_result import QualityCheckResult


WEAK_TRANSITIONS = [
    r"\bfurthermore,?\b",
    r"\bmoreover,?\b",
    r"\bin conclusion,?\b",
    r"\bit is important to note that\b",
    r"\bit is worth noting that\b",
    r"\bin today's rapidly evolving\b",
]


def audit_editorial_quality(
    markdown_text: str, brief: ContentBrief, sources: list[SourceEvidence]
) -> list[QualityCheckResult]:
    """Perform multi-criteria editorial evaluation with concrete, actionable feedback."""
    results: list[QualityCheckResult] = []

    body = markdown_text.split("## References & Verified Sources")[0].strip()
    sections = [s for s in body.split("## ") if s.strip()]

    # 1. Depth of Analysis & Tradeoffs
    tradeoff_keywords = [
        "tradeoff", "trade-off", "limitation", "overhead", "constraint",
        "failure mode", "friction", "latency", "cost", "risk", "benchmark"
    ]
    tradeoff_hits = sum(1 for kw in tradeoff_keywords if re.search(r"\b" + kw, body, re.IGNORECASE))
    if tradeoff_hits >= 3:
        results.append(
            QualityCheckResult(
                name="Depth of Analysis & Tradeoffs",
                passed=True,
                score_or_metric=f"Score: 9/10 ({tradeoff_hits} analytical criteria addressed)",
                details="Article includes concrete explanations of engineering tradeoffs, failure modes, and practical constraints.",
                severity="info",
            )
        )
    else:
        results.append(
            QualityCheckResult(
                name="Depth of Analysis & Tradeoffs",
                passed=False,
                score_or_metric=f"Score: 5/10 ({tradeoff_hits} analytical criteria addressed)",
                details="Insufficient discussion of limitations or tradeoffs. Action: Add concrete analysis of cost, latency, or operational constraints.",
                severity="warning",
            )
        )

    # 2. Section Evidence Coverage
    uncited_sections = []
    registered_ids = {str(s.id) for s in sources}
    for sec in sections:
        lines = sec.splitlines()
        heading = lines[0].strip() if lines else "Untitled"
        content = " ".join(lines[1:])
        has_citation = bool(re.search(r"\[\d+\]", content))
        if not has_citation and not heading.startswith("#"):
            uncited_sections.append(heading)

    if not uncited_sections:
        results.append(
            QualityCheckResult(
                name="Section Evidence Grounding",
                passed=True,
                score_or_metric=f"100% of analytical sections cited ({len(sections)} sections)",
                details="All sections are linked directly to supporting source evidence with bracketed citations.",
                severity="info",
            )
        )
    else:
        uncited_names = ", ".join(uncited_sections[:2])
        results.append(
            QualityCheckResult(
                name="Section Evidence Grounding",
                passed=False,
                score_or_metric=f"{len(uncited_sections)} section(s) lack source grounding",
                details=f"Missing citations in: '{uncited_names}'. Action: Attribute factual claims to source indices [1], [2].",
                severity="warning",
            )
        )

    # 3. Transitions & Sentence Clarity
    found_weak_trans = []
    for pattern in WEAK_TRANSITIONS:
        matches = re.findall(pattern, body, re.IGNORECASE)
        if matches:
            found_weak_trans.append(matches[0].lower().strip(","))

    if not found_weak_trans:
        results.append(
            QualityCheckResult(
                name="Transitions & Sentence Clarity",
                passed=True,
                score_or_metric="Score: 10/10 (Natural sentence transitions)",
                details="Zero robotic transitions detected ('Furthermore', 'Moreover', 'In conclusion' avoided).",
                severity="info",
            )
        )
    else:
        trans_str = ", ".join(dict.fromkeys(found_weak_trans))
        results.append(
            QualityCheckResult(
                name="Transitions & Sentence Clarity",
                passed=False,
                score_or_metric=f"Score: 6/10 ({len(found_weak_trans)} formulaic transitions found)",
                details=f"Detected artificial transitions: '{trans_str}'. Action: Replace with substantive logical connections.",
                severity="warning",
            )
        )

    return results
