"""Draft and autonomous workflow record models."""

from typing import Literal
from pydantic import BaseModel, Field
from content_agent.models.brief import ContentBrief
from content_agent.models.source import SourceEvidence
from content_agent.models.check_result import QualityCheckResult, QualityDecision
from content_agent.models.outline import ContentOutline, OutlineReviewDecision


class ContentDraftRecord(BaseModel):
    """Full workflow record with autonomous decisions and execution history."""

    id: str
    brief: ContentBrief
    title: str
    markdown_content: str
    actual_word_count: int
    sources: list[SourceEvidence] = Field(default_factory=list)
    outline: ContentOutline | None = None
    outline_decision: OutlineReviewDecision | None = None
    outline_revision_count: int = 0
    quality_checks: list[QualityCheckResult] = Field(default_factory=list)
    quality_decision: QualityDecision | None = None
    quality_iteration_count: int = 0
    execution_log: list[str] = Field(default_factory=list)
    export_ready: bool = False
    workflow_status: Literal["completed", "failed_qa", "in_progress"] = "in_progress"
    issue_report: str | None = None
    is_demo_mode: bool = True
    mode_label: str = "Demo Mode"
    mode_explanation: str = ""
