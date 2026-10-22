"""In-memory evidence store for indexing research sources and claim verification."""

from content_agent.models.source import SourceEvidence
from content_agent.models.claim import Claim


class EvidenceStore:
    """Stores and retrieves research sources and claim mappings."""

    def __init__(self):
        self._sources: dict[int, SourceEvidence] = {}
        self._claims: dict[int, Claim] = {}

    def add_source(self, source: SourceEvidence) -> None:
        self._sources[source.id] = source

    def add_sources(self, sources: list[SourceEvidence]) -> None:
        for s in sources:
            self.add_source(s)

    def get_source(self, source_id: int) -> SourceEvidence | None:
        return self._sources.get(source_id)

    def all_sources(self) -> list[SourceEvidence]:
        return list(self._sources.values())

    def clear(self) -> None:
        self._sources.clear()
        self._claims.clear()
