"""Claim and claim-to-source traceability data models."""

from typing import Literal
from pydantic import BaseModel, Field


class Claim(BaseModel):
    """An individual assertion or factual statement in content."""

    id: int
    text: str = Field(..., description="Factual claim or assertion text")
    section: str = Field(default="General", description="Document section containing the claim")
    supporting_source_ids: list[int] = Field(default_factory=list, description="IDs of backing sources")
    verification_status: Literal["verified", "unverified", "disputed", "extrapolated"] = "unverified"
    verification_notes: str = ""


class ClaimEvidenceLink(BaseModel):
    """Explicit mapping linking a claim to source evidence excerpt."""

    claim_id: int
    source_id: int
    source_url: str
    excerpt: str
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
