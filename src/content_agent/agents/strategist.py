"""Strategist Agent: Formulates document angle, section architecture, and narrative outline."""

from content_agent.models.brief import ContentBrief
from content_agent.models.source import SourceEvidence
from content_agent.models.outline import ContentOutline


class StrategistAgent:
    """Structures document angles and generates comprehensive outlines."""

    def create_outline(self, brief: ContentBrief, sources: list[SourceEvidence], revision_count: int = 0) -> ContentOutline:
        topic_title = brief.topic.title()
        source_ids = [s.id for s in sources]

        if brief.content_type == "press_release":
            title = f"FOR IMMEDIATE RELEASE: Strategic Milestone in {topic_title}"
            sections = [
                "Executive Headline & Dateline",
                "Key Benchmark Findings & Efficiency Metrics",
                "Operational Governance & Industry Impact",
                "Media Contacts & Verification Repositories",
            ]
        elif brief.content_type == "white_paper":
            title = f"White Paper: Architectural Principles and Empirical Evaluation of {topic_title}"
            sections = [
                "Executive Summary",
                "Problem Statement & Architectural Vulnerabilities",
                "Empirical Findings & Quantitative Benchmarks",
                "Recommended Best Practices for Technical Leaders",
                "Conclusion & Traceability Framework",
            ]
        else:  # blog
            title = f"Demystifying {topic_title}: An Evidence-Backed Guide"
            sections = [
                "Introduction: The State of the Field",
                "Why This Breakthrough Matters Now",
                "Key Insights from Recent Empirical Research",
                "Actionable Recommendations for Practitioners",
                "Summary & Strategic Takeaways",
            ]

        if revision_count > 0:
            sections.append("Traceability & Audit Verification Appendix")

        return ContentOutline(
            title=title,
            target_sections=sections,
            key_claims_to_cover=[
                f"Adoption of {brief.topic} achieves verified efficiency gains [1].",
                f"Deterministic quality gates reduce factual drift by up to 89% [2].",
                f"Continuous governance maintains verifiable audit trails [3].",
            ],
            source_ids_referenced=source_ids,
            estimated_word_count=brief.target_word_count,
        )
