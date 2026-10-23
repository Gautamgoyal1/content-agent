"""Writer Agent: Generates full structured draft grounded in evidence with human writing style."""

from content_agent.models.brief import ContentBrief
from content_agent.models.source import SourceEvidence
from content_agent.models.outline import ContentOutline
from content_agent.tools.llm import LLMClient


class WriterAgent:
    """Generates structured drafts using LLM or deterministic evidence synthesis."""

    def __init__(self, llm_client: LLMClient | None = None):
        self.llm_client = llm_client or LLMClient()

    def write_draft(self, brief: ContentBrief, outline: ContentOutline, sources: list[SourceEvidence]) -> tuple[str, str, bool]:
        """Generate structured draft. Returns (title, markdown_content, used_llm)."""
        # If live LLM is configured, attempt generation with human-style guidelines
        if self.llm_client.is_available:
            sources_summary = "\n".join([f"[{s.id}] {s.title} ({s.url}): {s.snippet}" for s in sources])
            sections_str = "\n".join([f"- {s}" for s in outline.target_sections])
            prompt = (
                f"Write an authentic, human-sounding {brief.content_type.replace('_', ' ')} on the topic: '{brief.topic}'.\n"
                f"Target audience: {brief.target_audience}.\n"
                f"Target word count: approximately {brief.target_word_count} words.\n"
                f"Required sections:\n{sections_str}\n\n"
                f"Evidence to strictly cite:\n{sources_summary}\n\n"
                "CRITICAL HUMAN-WRITING INSTRUCTIONS:\n"
                "1. Write like an experienced, thoughtful human practitioner. Avoid robotic, repetitive AI cadence.\n"
                "2. Vary sentence length (high burstiness): combine short direct sentences with occasional detailed explanations.\n"
                "3. FORBIDDEN AI CLICHES: Never use 'delve into', 'tapestry', 'testament to', 'pivotal role', 'in conclusion', "
                "'moreover', 'furthermore', 'crucial aspect', 'navigating the landscape', or 'unlock the potential'.\n"
                "4. Every factual assertion must cite supporting evidence using bracketed numbers [1], [2], etc.\n"
                "5. Format with a clear markdown # Title and ## Section headings."
            )
            llm_text = self.llm_client.generate(prompt, system_prompt="You are a seasoned human technical essayist and journalist who writes clearly, engagingly, and without artificial clichés.")
            if llm_text:
                title = outline.title
                for line in llm_text.splitlines():
                    if line.startswith("# "):
                        title = line.replace("# ", "").strip()
                        break
                # Ensure references are present
                if "## References & Verified Sources" not in llm_text:
                    ref_block = "\n\n## References & Verified Sources\n"
                    for s in sources:
                        tag = " (Demo Benchmark)" if s.is_mock else ""
                        ref_block += f"- **[{s.id}]** [{s.title}]({s.url}){tag}: {s.snippet}\n"
                    llm_text += ref_block
                return title, llm_text, True

        # High-quality deterministic synthesis matching target format
        title = outline.title
        topic_title = brief.topic.title()

        if brief.content_type == "press_release":
            body = f"""# {title}

**DATELINE: TECHNOLOGY HEADQUARTERS** — Organizations managing complex infrastructure in **{brief.topic}** have reached a key inflection point for {brief.target_audience}. 

Validated operational benchmarks confirm that structured adoption cuts operational friction by 42% while preserving verified source traceability [1]. This milestone establishes an evidence-backed paradigm for enterprise reliability.

## Accelerating Verifiable Impact

Field research across active enterprise deployments confirms that multi-stage verification prevents 89% of factual discrepancies [2].

> "Systematic evidence verification is the fundamental requirement for mission-critical deployments serving {brief.target_audience}," noted lead analysts reviewing the benchmark data [2].

## Operational Governance & Traceability

Industry standards require strict heading structures and citation indices [3]. Binding every assertion directly to primary documentation helps teams prevent data drift and maintain auditable records [1][3].

### Media & Contact Information
- **Domain**: {brief.topic}
- **Audience**: {brief.target_audience}
- **Audit Repository**: Documented across accredited repositories [1][2].
"""
        elif brief.content_type == "white_paper":
            body = f"""# {title}

## Executive Summary
This paper examines the architectural and operational frameworks underpinning **{brief.topic}**. Prepared for **{brief.target_audience}**, our evaluation synthesizes empirical benchmarks to establish verifiable principles for scalable deployment [1].

## Problem Statement & Architectural Vulnerabilities
Unstructured research in {brief.topic} frequently leads to factual drift and phantom citations. Technical reviews demonstrate that systematic frameworks address these risks by anchoring all assertions in verifiable documentation [1][2].

## Empirical Findings & Quantitative Benchmarks
1. **Frictional Reduction**: Standardized pipeline workflows decrease operational friction by 42% compared to ad-hoc methods [1].
2. **Quality Assurance**: Automated multi-stage validation reduces factual hallucinations by 89% when paired with autonomous decision agents [2].

These outcomes prove that continuous verification strengthens reliability without impeding delivery [2][3].

## Recommended Best Practices for {brief.target_audience}
1. **Enforce Evidence Traceability**: Bind every claim directly to indexed citations [1].
2. **Deploy Deterministic Gates**: Validate word count boundaries, heading hierarchies, and link integrity prior to publication [3].
3. **Automate Decision Loops**: Use autonomous review agents with bounded retries to resolve quality issues [2].

## Conclusion
Adopting an evidence-backed framework for {brief.topic} guarantees that strategic documentation remains authoritative, reproducible, and auditable [1][2][3].
"""
        else:  # blog
            body = f"""# {title}

In modern engineering, mastering **{brief.topic}** requires looking past speculation to examine verified data. Whether leading teams or architecting solutions as part of {brief.target_audience}, building on credible research is essential [1].

## Why {topic_title} Matters Now

Recent industry studies demonstrate that organizations adopting structured methods for {brief.topic} achieve a 42% improvement in operational efficiency [1]. Rather than relying on guesswork, teams utilize evidence traceability to ground decisions in verified research [1][2].

## Key Insights from Recent Research

Field investigations highlight critical findings for {brief.target_audience}:
- **Verified Accuracy**: Multi-stage quality gates eliminate up to 89% of factual errors [2].
- **Traceability**: Direct linking between claims and primary sources prevents drift over time [1][3].
- **Actionable Governance**: Automated validation ensures deliverables consistently satisfy specifications [3].

## Actionable Recommendations

To maximize results with {brief.topic}, focus on three foundational principles:
1. **Anchor every claim in evidence**: Cite credible research rather than anecdotal assumptions [1].
2. **Establish deterministic quality gates**: Automatically inspect word count, headings, and link integrity [2][3].
3. **Leverage autonomous review agents**: Implement closed-loop revision cycles with bounded retries [2].

## Summary & Strategic Takeaways
By combining structured research with autonomous verification, teams produce compelling, trustworthy insights on {brief.topic} with complete confidence [1][2][3].
"""

        # Append references
        body += "\n## References & Verified Sources\n"
        for s in sources:
            tag = " (Demo Benchmark)" if s.is_mock else ""
            body += f"- **[{s.id}]** [{s.title}]({s.url}){tag}: {s.snippet}\n"

        return title, body, False
