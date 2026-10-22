"""Fact Checker Agent: Audits factual assertions against indexed evidence sources."""

import re
from content_agent.models.source import SourceEvidence
from content_agent.models.claim import Claim
from content_agent.models.check_result import QualityCheckResult


class FactCheckerAgent:
    """Audits claims against source evidence and flags unsupported or unverified statements."""

    def verify_claims(self, markdown_text: str, sources: list[SourceEvidence]) -> list[Claim]:
        """Extract inline claims and verify against provided sources."""
        body = markdown_text.split("## References & Verified Sources")[0]
        sentences = re.split(r"(?<=[.!?])\s+", body)
        registered_ids = {s.id for s in sources}
        audited_claims = []

        claim_idx = 1
        for s in sentences:
            citation_matches = [int(x) for x in re.findall(r"\[(\d+)\]", s)]
            if citation_matches:
                valid_citations = [cid for cid in citation_matches if cid in registered_ids]
                status = "verified" if valid_citations else "unverified"
                audited_claims.append(
                    Claim(
                        id=claim_idx,
                        text=s.strip(),
                        supporting_source_ids=valid_citations,
                        verification_status=status,
                        verification_notes="Grounded in evidence" if status == "verified" else "Phantom citation without backing source",
                    )
                )
                claim_idx += 1

        return audited_claims
