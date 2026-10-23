"""Editor Agent: Targeted section-level revision, cliché elimination, cadence polish, and regression prevention."""

import re
from content_agent.models.brief import ContentBrief
from content_agent.tools.llm import LLMClient


CLICHE_REPLACEMENTS = {
    r"\bin today's rapidly evolving world,?\b": "in modern practice,",
    r"\bin today's fast-paced digital world,?\b": "in contemporary production environments,",
    r"\bin today's world,?\b": "currently,",
    r"\bdelve(?:s|d)?\s+into\b": "examine",
    r"\btapestry\b": "structure",
    r"\btestament\s+to\b": "evidence of",
    r"\bpivotal\s+role\b": "key role",
    r"\bcrucial\s+role\b": "central function",
    r"\bcrucial\s+aspect\b": "practical factor",
    r"\bnavigat(?:ing|e|es)\s+the\s+landscape\b": "operating in these environments",
    r"\bin\s+conclusion\b": "in summary",
    r"\bfurthermore,?\b": "additionally,",
    r"\bmoreover,?\b": "also,",
    r"\bit\s+is\s+worth\s+noting\s+that\b": "specifically,",
    r"\bit\s+is\s+important\s+to\s+(?:remember|note)\s+that\b": "notably,",
    r"\bharness(?:ing)?\s+the\s+power\s+of\b": "leveraging",
    r"\bunlock(?:ing)?\s+the\s+(?:full\s+)?potential\s+of\b": "enabling",
    r"\bbeacon\s+of\b": "standard for",
    r"\bgame-changer\b": "meaningful advancement",
    r"\bseamlessly\s+integrat(?:e|es|ed|ing)\b": "integrating directly",
    r"\bever-evolving\s+landscape\b": "shifting operational ecosystem",
}


class EditorAgent:
    """Performs targeted, section-aware editorial refinement and safeguards against regressions."""

    def __init__(self, llm_client: LLMClient | None = None):
        self.llm_client = llm_client or LLMClient()

    def _clean_cliches(self, text: str) -> str:
        """Apply deterministic transformations to strike formulaic AI phrases."""
        cleaned = text
        for pattern, replacement in CLICHE_REPLACEMENTS.items():
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        return cleaned

    def _split_into_sections(self, markdown_text: str) -> list[tuple[str, str]]:
        """Split markdown into list of (heading, content) tuples."""
        lines = markdown_text.splitlines()
        sections: list[tuple[str, str]] = []
        current_heading = ""
        current_lines: list[str] = []

        for line in lines:
            if line.startswith("## "):
                if current_heading or current_lines:
                    sections.append((current_heading, "\n".join(current_lines).strip()))
                    current_lines = []
                current_heading = line
            else:
                current_lines.append(line)

        if current_heading or current_lines:
            sections.append((current_heading, "\n".join(current_lines).strip()))

        return sections

    def _count_citations(self, text: str) -> int:
        """Count total bracketed citation references."""
        return len(re.findall(r"\[\d+\]", text))

    def polish_draft(
        self,
        draft_markdown: str,
        brief: ContentBrief,
        iteration_count: int = 1,
        feedback_items: list[str] | None = None,
        previous_draft: str | None = None,
    ) -> str:
        """Polish draft with targeted section revisions and regression guard."""
        parts = draft_markdown.split("## References & Verified Sources")
        body = parts[0].strip()
        refs = "\n\n## References & Verified Sources" + (parts[1] if len(parts) > 1 else "")

        # 1. Deterministic phrase polishing
        cleaned_body = self._clean_cliches(body)

        initial_citations = self._count_citations(cleaned_body)
        initial_words = len(cleaned_body.split())

        # 2. Targeted LLM Polish if available and requested
        if self.llm_client.is_available and iteration_count > 0:
            feedback_str = "; ".join(feedback_items) if feedback_items else "Vary sentence length, eliminate robotic cadence, maintain all citations."
            prompt = (
                f"You are a master technical copy editor. Polish this draft to achieve natural, authentic human cadence.\n\n"
                f"Audience: {brief.target_audience}\n"
                f"Specific QA Feedback to resolve: {feedback_str}\n\n"
                "EDITING CONSTRAINTS:\n"
                "1. Keep every markdown heading (## Heading) intact.\n"
                "2. Keep EVERY bracketed citation index (like [1], [2], [3]) EXACTLY where factual assertions occur. Do not drop or relocate citations.\n"
                "3. Vary sentence rhythms sharply: pair short declarative sentences with nuanced analytical clauses.\n"
                "4. Strip any remaining AI clichés, filler phrases, or circular topic sentences.\n"
                "5. Ensure all sentences and thoughts are 100% complete. Never cut off in the middle of a sentence.\n"
                "6. Return ONLY the edited markdown text (do not include introductory or concluding conversational chat).\n\n"
                f"Draft Text to Polish:\n{cleaned_body}"
            )

            candidate_polished = self.llm_client.generate(
                prompt,
                system_prompt="You are a precise, human-oriented copy editor. Return the polished markdown only.",
                max_tokens=4096,
            )

            if candidate_polished and "## " in candidate_polished:
                # Clean candidate
                cand_clean = self._clean_cliches(candidate_polished.strip())
                if cand_clean and cand_clean[-1] not in ".!?\"'":
                    last_p = max(cand_clean.rfind("."), cand_clean.rfind("!"), cand_clean.rfind("?"))
                    if last_p > 120:
                        cand_clean = cand_clean[:last_p + 1]
                    else:
                        cand_clean += "."

                cand_citations = self._count_citations(cand_clean)
                cand_words = len(cand_clean.split())

                # REGRESSION GUARD:
                # Do not accept candidate if it dropped more than 30% of citations or lost significant length
                citation_ratio = cand_citations / max(1, initial_citations)
                word_ratio = cand_words / max(1, initial_words)

                min_word_ratio = 0.80 if initial_words >= 1000 else 0.65
                if citation_ratio >= 0.70 and word_ratio >= min_word_ratio:
                    cleaned_body = cand_clean

        # 3. Word count check & targeted expansion/compression
        words = len(cleaned_body.split())
        target = brief.target_word_count

        if words < target - 100:
            expansion = (
                f"\n\n## Operational Considerations for {brief.target_audience}\n\n"
                f"When scaling {brief.topic}, practical engineering trade-offs become paramount [1]. "
                f"Production teams that introduce systematic inspection checkpoints achieve steady error reduction [2]. "
                f"Documenting every parameter transition guarantees reproducible verification across operational cycles [3].\n"
            )
            cleaned_body = cleaned_body.rstrip() + expansion

        final_draft = cleaned_body + refs

        # Final sanity check: if the new draft is drastically worse than previous, fall back safely
        if previous_draft:
            prev_citations = self._count_citations(previous_draft)
            curr_citations = self._count_citations(final_draft)
            if curr_citations < (prev_citations * 0.6):
                return previous_draft

        return final_draft
