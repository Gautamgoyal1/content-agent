"""State definition for LangGraph workflow."""

from typing import TypedDict, Literal
from content_agent.models.brief import ContentBrief
from content_agent.models.source import SourceEvidence
from content_agent.models.outline import ContentOutline, OutlineReviewDecision
from content_agent.models.check_result import QualityCheckResult, QualityDecision


class ContentAgentState(TypedDict, total=False):
    """Execution state passed between LangGraph nodes."""

    run_id: str
    brief: ContentBrief
    sources: list[SourceEvidence]
    outline: ContentOutline | None
    outline_decision: OutlineReviewDecision | None
    outline_revision_count: int
    max_outline_retries: int
    draft_markdown: str
    title: str
    actual_word_count: int
    quality_checks: list[QualityCheckResult]
    quality_decision: QualityDecision | None
    quality_iteration_count: int
    max_quality_retries: int
    execution_log: list[str]
    export_ready: bool
    workflow_status: Literal["completed", "failed_qa", "in_progress"]
    issue_report: str | None
    is_demo_mode: bool
    mode_label: str
    mode_explanation: str
