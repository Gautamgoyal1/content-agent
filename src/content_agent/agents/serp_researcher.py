"""SERP Researcher Agent: Identifies relevant search queries and competitor discussions."""

from content_agent.tools.search_client import SearchClient
from content_agent.models.source import SourceEvidence


class SerpResearcherAgent:
    """Discovers top search results and authority domains for requested topics."""

    def __init__(self, search_client: SearchClient | None = None):
        self.search_client = search_client or SearchClient()

    def discover_topics(self, topic: str, max_results: int = 3, existing_count: int = 0) -> tuple[list[SourceEvidence], bool, str]:
        query = f"{topic} architecture best practices benchmarks"
        return self.search_client.search(query=query, max_results=max_results, existing_count=existing_count)
