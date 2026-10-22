"""Pipeline execution adapter connecting FastAPI to the LangGraph autonomous engine."""

import uuid
from content_agent.models.brief import ContentBrief
from content_agent.models.draft import ContentDraftRecord
from content_agent.api.schemas import RunCreateRequest
from content_agent.graph.routing import CONTENT_GRAPH
from content_agent.graph.state import ContentAgentState

# In-memory storage for runs
RUNS_STORE: dict[str, ContentDraftRecord] = {}


def execute_content_pipeline(req: RunCreateRequest) -> ContentDraftRecord:
    """Execute the multi-agent autonomous LangGraph content generation pipeline."""
    run_id = f"run-{uuid.uuid4().hex[:8]}"

    brief = ContentBrief(
        topic=req.topic.strip(),
        content_type=req.content_type,
        target_audience=(req.target_audience or "General technical audience").strip(),
        target_word_count=req.target_word_count,
        tone=req.tone,
    )

    initial_state: ContentAgentState = {
        "run_id": run_id,
        "brief": brief,
        "sources": [],
        "outline": None,
        "outline_decision": None,
        "outline_revision_count": 0,
        "max_outline_retries": 2,
        "draft_markdown": "",
        "title": brief.topic.title(),
        "actual_word_count": 0,
        "quality_checks": [],
        "quality_decision": None,
        "quality_iteration_count": 0,
        "max_quality_retries": 2,
        "execution_log": [f"[Workflow Init] Starting autonomous multi-agent pipeline for run {run_id}."],
        "export_ready": False,
        "workflow_status": "in_progress",
        "issue_report": None,
        "is_demo_mode": True,
        "mode_label": "Demo Mode",
        "mode_explanation": "",
    }

    # Invoke autonomous LangGraph
    final_state = CONTENT_GRAPH.invoke(initial_state)

    record = ContentDraftRecord(
        id=run_id,
        brief=final_state["brief"],
        title=final_state.get("title", brief.topic.title()),
        markdown_content=final_state.get("draft_markdown", ""),
        actual_word_count=final_state.get("actual_word_count", 0),
        sources=final_state.get("sources", []),
        outline=final_state.get("outline"),
        outline_decision=final_state.get("outline_decision"),
        outline_revision_count=final_state.get("outline_revision_count", 0),
        quality_checks=final_state.get("quality_checks", []),
        quality_decision=final_state.get("quality_decision"),
        quality_iteration_count=final_state.get("quality_iteration_count", 0),
        execution_log=final_state.get("execution_log", []),
        export_ready=final_state.get("export_ready", False),
        workflow_status=final_state.get("workflow_status", "completed"),
        issue_report=final_state.get("issue_report"),
        is_demo_mode=final_state.get("is_demo_mode", True),
        mode_label=final_state.get("mode_label", "Demo Mode"),
        mode_explanation=final_state.get("mode_explanation", ""),
    )

    RUNS_STORE[run_id] = record
    return record
