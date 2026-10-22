"""Database repositories for runs and content records."""

from content_agent.models.draft import ContentDraftRecord
from content_agent.pipeline import RUNS_STORE


class RunRepository:
    """Repository accessing stored pipeline runs."""

    def get_by_id(self, run_id: str) -> ContentDraftRecord | None:
        return RUNS_STORE.get(run_id)

    def list_all(self) -> list[ContentDraftRecord]:
        return list(RUNS_STORE.values())

    def save(self, record: ContentDraftRecord) -> None:
        RUNS_STORE[record.id] = record
