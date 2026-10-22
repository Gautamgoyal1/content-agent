"""Integration tests for autonomous LangGraph pipeline."""

from content_agent.api.schemas import RunCreateRequest
from content_agent.pipeline import execute_content_pipeline


def test_autonomous_blog_pipeline_execution():
    req = RunCreateRequest(
        topic="Autonomous AI Orchestration",
        content_type="blog",
        target_audience="Engineering Leaders",
        target_word_count=450,
    )

    record = execute_content_pipeline(req)

    # 1. Pipeline metadata
    assert record.id.startswith("run-")
    assert record.brief.topic == "Autonomous AI Orchestration"
    assert record.actual_word_count > 0

    # 2. Outline Review Agent
    assert record.outline is not None
    assert record.outline_decision is not None
    assert record.outline_decision.decision in ("approve", "revise", "research_more")
    assert record.outline_revision_count <= 2

    # 3. Quality Decision Agent & Gates
    assert len(record.quality_checks) >= 5
    assert record.quality_decision is not None
    assert record.quality_decision.action in ("export", "invoke_editor", "repair_formatting", "terminate_failure")
    assert record.quality_iteration_count <= 2

    # 4. Auto-export status
    assert record.export_ready is True
    assert record.workflow_status == "completed"

    # 5. Execution trace log
    assert len(record.execution_log) >= 5
    assert any("[Brief Analyzer]" in entry for entry in record.execution_log)
    assert any("[Outline Review Agent]" in entry for entry in record.execution_log)
    assert any("[Quality Decision Agent]" in entry for entry in record.execution_log)
    assert any("[Export Node]" in entry for entry in record.execution_log)


def test_press_release_pipeline_execution():
    req = RunCreateRequest(
        topic="Next-Gen Security Benchmark",
        content_type="press_release",
        target_audience="CISO and Security Officers",
        target_word_count=400,
    )
    record = execute_content_pipeline(req)

    assert "FOR IMMEDIATE RELEASE" in record.markdown_content or "DATELINE" in record.markdown_content
    assert record.export_ready is True
    assert record.workflow_status == "completed"


def test_white_paper_pipeline_execution():
    req = RunCreateRequest(
        topic="Zero Trust Empirical Architecture",
        content_type="white_paper",
        target_audience="Enterprise Architects",
        target_word_count=500,
    )
    record = execute_content_pipeline(req)

    assert "Executive Summary" in record.markdown_content
    assert record.export_ready is True
    assert record.workflow_status == "completed"
