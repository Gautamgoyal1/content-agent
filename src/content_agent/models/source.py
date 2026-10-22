"""Source and evidence data models."""

from pydantic import BaseModel, Field


class SourceEvidence(BaseModel):
    """Authoritative research evidence source."""

    id: int
    title: str
    url: str
    snippet: str
    key_facts: list[str] = Field(default_factory=list)
    is_mock: bool = False
    source_type: str = "web_article"
