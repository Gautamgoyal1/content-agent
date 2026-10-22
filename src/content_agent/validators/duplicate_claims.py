"""Duplicate claims and repetition detection gate."""

import re
from content_agent.models.check_result import QualityCheckResult
from content_agent.tools.embeddings import TextSimilarity


def validate_duplicate_claims(markdown_text: str, similarity_threshold: float = 0.85) -> QualityCheckResult:
    """Identify repetitive or redundant claims across document paragraphs."""
    paragraphs = [p.strip() for p in markdown_text.split("\n\n") if p.strip() and not p.startswith("#")]

    if len(paragraphs) < 2:
        return QualityCheckResult(
            name="Claim Redundancy",
            passed=True,
            score_or_metric="0 duplicates",
            details="Document has concise structure with no redundant paragraphs.",
            severity="info",
        )

    duplicate_pairs = []
    for i in range(len(paragraphs)):
        for j in range(i + 1, len(paragraphs)):
            sim = TextSimilarity.cosine_similarity(paragraphs[i], paragraphs[j])
            if sim >= similarity_threshold:
                duplicate_pairs.append((i + 1, j + 1, sim))

    if duplicate_pairs:
        return QualityCheckResult(
            name="Claim Redundancy",
            passed=False,
            score_or_metric=f"{len(duplicate_pairs)} duplicate claim pair(s)",
            details=f"High semantic overlap detected between paragraphs {duplicate_pairs[0][0]} and {duplicate_pairs[0][1]}.",
            severity="warning",
        )

    return QualityCheckResult(
        name="Claim Redundancy",
        passed=True,
        score_or_metric="No duplicates detected",
        details="Paragraphs display diverse arguments and distinct factual claims.",
        severity="info",
    )
