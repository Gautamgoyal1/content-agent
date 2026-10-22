"""Evidence Researcher Agent: Gathers source pages and extracts verifiable quotes."""

from content_agent.tools.page_fetcher import PageFetcher
from content_agent.models.source import SourceEvidence


class EvidenceResearcherAgent:
    """Fetches full page content and extracts verifiable quotes and citations."""

    def __init__(self, page_fetcher: PageFetcher | None = None):
        self.page_fetcher = page_fetcher or PageFetcher()

    def deep_crawl_source(self, source: SourceEvidence) -> SourceEvidence:
        """Fetch live page if available to enrich source evidence snippets."""
        if not source.is_mock and source.url.startswith("http"):
            result = self.page_fetcher.fetch_text(source.url)
            if result.get("success") and result.get("text"):
                source.snippet = result["text"][:350]
        return source
