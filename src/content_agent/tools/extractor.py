"""Extraction utilities for markdown headings, claims, citations, and stats."""

import re
from typing import Any


class Extractor:
    """Extracts structural and semantic elements from text and markdown."""

    @staticmethod
    def extract_headings(markdown_text: str) -> list[dict[str, Any]]:
        """Extract all markdown headings with their level and line number."""
        headings = []
        for line_no, line in enumerate(markdown_text.splitlines(), start=1):
            match = re.match(r"^(#{1,6})\s+(.+)$", line.strip())
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                headings.append({"level": level, "title": title, "line": line_no})
        return headings

    @staticmethod
    def extract_citations(text: str) -> list[int]:
        """Extract all numerical citation markers like [1], [2], [1][2]."""
        raw_matches = re.findall(r"\[(\d+)\]", text)
        return sorted(list({int(m) for m in raw_matches}))

    @staticmethod
    def extract_claims(text: str) -> list[str]:
        """Extract sentences that contain factual assertions or numerical claims."""
        sentences = re.split(r"(?<=[.!?])\s+", text)
        factual_sentences = []
        for s in sentences:
            clean = s.strip()
            # Sentences containing percentages, statistics, or citation markers are prioritized
            if re.search(r"\b\d+%\b|\b\d+\b|\[\d+\]|demonstrates|reveals|found that|benchmarks|increases|reduces", clean, re.IGNORECASE):
                if len(clean) > 20:
                    factual_sentences.append(clean)
        return factual_sentences

    @staticmethod
    def extract_links(markdown_text: str) -> list[dict[str, str]]:
        """Extract markdown links [text](url)."""
        pattern = r"\[([^\]]+)\]\((https?://[^\)]+)\)"
        matches = re.findall(pattern, markdown_text)
        return [{"anchor": m[0], "url": m[1]} for m in matches]
