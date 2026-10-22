"""API request and response schemas."""

from typing import Literal
from pydantic import BaseModel, Field
from content_agent.models.brief import ContentBrief
from content_agent.models.draft import ContentDraftRecord


class RunCreateRequest(BaseModel):
    """Payload to initiate content pipeline."""

    topic: str = Field(..., min_length=3, max_length=300)
    content_type: Literal["blog", "press_release", "white_paper"] = "blog"
    target_audience: str = "General audience / Technical practitioners"
    target_word_count: int = Field(default=500, ge=100, le=5000)
    tone: str = "authoritative and evidence-backed"


class ApprovalUpdateRequest(BaseModel):
    """Payload to update draft approval status."""

    status: Literal["approved", "rejected", "pending_review"]
    notes: str = ""
