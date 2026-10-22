"""Knowledge Curator Agent: Indexes facts, links citations, and maintains ground truth."""

from content_agent.models.source import SourceEvidence
from content_agent.models.claim import Claim, ClaimEvidenceLink


class KnowledgeCuratorAgent:
    """Manages evidence indexing and links assertions to backing sources."""

    def build_claim_index(self, sources: list[SourceEvidence]) -> list[Claim]:
        """Index verifiable claims from collected sources."""
        claims = []
        claim_id = 1
        for s in sources:
            for fact in s.key_facts:
                claims.append(
                    Claim(
                        id=claim_id,
                        text=fact,
                        section="Core Empirical Evidence",
                        supporting_source_ids=[s.id],
                        verification_status="verified",
                        verification_notes=f"Extracted directly from [{s.id}] {s.title}",
                    )
                )
                claim_id += 1
        return claims

    def format_sources_section(self, sources: list[SourceEvidence]) -> str:
        """Render markdown references block."""
        section = "\n## References & Verified Sources\n"
        for s in sources:
            tag = " (Demo Benchmark)" if s.is_mock else ""
            section += f"- **[{s.id}]** [{s.title}]({s.url}){tag}: {s.snippet}\n"
        return section
