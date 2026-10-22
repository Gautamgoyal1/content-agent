"""Brief and user input data models."""

from typing import Literal
from pydantic import BaseModel, Field


class ContentBrief(BaseModel):
    """Validated and normalized content brief."""

    topic: str = Field(..., min_length=3, max_length=300, description="Topic or content subject")
    content_type: Literal["blog", "press_release", "white_paper"] = "blog"
    target_audience: str = Field(default="General professionals and practitioners", max_length=200)
    target_word_count: int = Field(default=500, ge=100, le=5000)
    tone: str = "informative, authoritative, and evidence-grounded"
