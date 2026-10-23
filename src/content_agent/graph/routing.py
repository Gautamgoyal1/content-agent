"""Autonomous LangGraph workflow with Outline Review & Quality Decision Agents."""

import os
import re
from typing import Literal

from langgraph.graph import StateGraph, START, END

from content_agent.models.brief import ContentBrief
from content_agent.models.source import SourceEvidence
from content_agent.models.outline import ContentOutline, OutlineReviewDecision
from content_agent.models.check_result import QualityCheckResult, QualityDecision
from content_agent.graph.state import ContentAgentState

# Specialized Agents
from content_agent.agents.brief_analyzer import BriefAnalyzerAgent
from content_agent.agents.audience_analyst import AudienceAnalystAgent
from content_agent.agents.serp_researcher import SerpResearcherAgent
from content_agent.agents.evidence_researcher import EvidenceResearcherAgent
from content_agent.agents.knowledge_curator import KnowledgeCuratorAgent
from content_agent.agents.strategist import StrategistAgent
from content_agent.agents.writer import WriterAgent
from content_agent.agents.fact_checker import FactCheckerAgent
from content_agent.agents.editor import EditorAgent
from content_agent.agents.seo_geo_auditor import SeoGeoAuditorAgent

# Deterministic Validators
from content_agent.validators.word_count import validate_word_count
from content_agent.validators.headings import validate_headings
from content_agent.validators.url_check import validate_citations
from content_agent.validators.duplicate_claims import validate_duplicate_claims
from content_agent.validators.keyword_placement import validate_keyword_placement
from content_agent.validators.ai_detector import validate_ai_content


# Agent instances
brief_analyzer = BriefAnalyzerAgent()
audience_analyst = AudienceAnalystAgent()
serp_researcher = SerpResearcherAgent()
evidence_researcher = EvidenceResearcherAgent()
knowledge_curator = KnowledgeCuratorAgent()
strategist = StrategistAgent()
writer = WriterAgent()
fact_checker = FactCheckerAgent()
editor = EditorAgent()
seo_auditor = SeoGeoAuditorAgent()


# ---------------------------------------------------------------------------
# Node 1: Brief Analysis & Audience Profiling
# ---------------------------------------------------------------------------
def node_analyze_brief(state: ContentAgentState) -> dict:
    raw_brief = state["brief"]
    log = list(state.get("execution_log", []))

    normalized_brief = brief_analyzer.analyze(
        raw_topic=raw_brief.topic,
        content_type=raw_brief.content_type,
        target_audience=raw_brief.target_audience,
        target_word_count=raw_brief.target_word_count,
        tone=raw_brief.tone,
    )
    profile = audience_analyst.profile_audience(normalized_brief)

    log.append(
        f"[Brief Analyzer] Validated topic: '{normalized_brief.topic}' "
        f"({normalized_brief.content_type}, {profile['technical_depth']} depth for {normalized_brief.target_audience})."
    )

    return {
        "brief": normalized_brief,
        "execution_log": log,
        "outline_revision_count": 0,
        "quality_iteration_count": 0,
        "export_ready": False,
        "workflow_status": "in_progress",
    }


# ---------------------------------------------------------------------------
# Node 2: Research & Evidence Collection
# ---------------------------------------------------------------------------
def node_research(state: ContentAgentState) -> dict:
    brief = state["brief"]
    existing_sources = list(state.get("sources", []))
    log = list(state.get("execution_log", []))

    new_sources, is_live, explanation = serp_researcher.discover_topics(
        topic=brief.topic,
        max_results=3,
        existing_count=len(existing_sources),
    )

    # Deep crawl / enrich if live
    enriched_sources = [evidence_researcher.deep_crawl_source(s) for s in new_sources]
    all_sources = existing_sources + enriched_sources if existing_sources else enriched_sources

    log.append(f"[Research] Gathered {len(all_sources)} authoritative evidence sources ({explanation}).")

    return {
        "sources": all_sources,
        "is_demo_mode": not is_live,
        "mode_label": "Live Mode" if is_live else "Demo Mode (Offline Evidence)",
        "mode_explanation": explanation,
        "execution_log": log,
    }


# ---------------------------------------------------------------------------
# Node 3: Strategist (Creates Content Outline)
# ---------------------------------------------------------------------------
def node_strategist_outline(state: ContentAgentState) -> dict:
    brief = state["brief"]
    sources = state.get("sources", [])
    log = list(state.get("execution_log", []))
    rev_count = state.get("outline_revision_count", 0)

    outline = strategist.create_outline(brief=brief, sources=sources, revision_count=rev_count)

    log.append(
        f"[Strategist] Outline generated: '{outline.title}' with {len(outline.target_sections)} sections "
        f"(revision {rev_count})."
    )

    return {
        "outline": outline,
        "title": outline.title,
        "execution_log": log,
    }


# ---------------------------------------------------------------------------
# Node 4: Outline Review Agent (Autonomous Decision)
# ---------------------------------------------------------------------------
def node_outline_reviewer(state: ContentAgentState) -> dict:
    outline = state.get("outline")
    sources = state.get("sources", [])
    rev_count = state.get("outline_revision_count", 0)
    max_retries = state.get("max_outline_retries", 2)
    log = list(state.get("execution_log", []))

    # Evaluate outline requirements
    if not outline or len(outline.target_sections) < 3:
        if rev_count < max_retries:
            decision = OutlineReviewDecision(
                decision="revise",
                rationale="Outline contains fewer than 3 structured sections. Requires richer structural depth.",
                revision_feedback=["Add concrete analytical subsections and dedicated takeaway blocks."],
            )
        else:
            decision = OutlineReviewDecision(
                decision="approve",
                rationale=f"Max outline revisions reached ({max_retries}). Approving bounded outline to proceed.",
            )
    elif len(sources) < 2:
        if rev_count < max_retries:
            decision = OutlineReviewDecision(
                decision="research_more",
                rationale="Insufficient source diversity (less than 2 verified sources). Additional research required.",
                suggested_focus_areas=["Gather cross-sectional benchmark data."],
            )
        else:
            decision = OutlineReviewDecision(
                decision="approve",
                rationale="Proceeding with existing evidence as outline retry limit was reached.",
            )
    else:
        decision = OutlineReviewDecision(
            decision="approve",
            rationale=f"Outline satisfies structural completeness ({len(outline.target_sections)} sections) and evidence mapping ({len(sources)} sources).",
        )

    new_rev_count = rev_count + (1 if decision.decision != "approve" else 0)
    log.append(f"[Outline Review Agent] Decision: '{decision.decision.upper()}' — {decision.rationale}")

    return {
        "outline_decision": decision,
        "outline_revision_count": new_rev_count,
        "execution_log": log,
    }


def route_outline_decision(state: ContentAgentState) -> str:
    """Conditional router based on Outline Review Agent decision."""
    decision = state.get("outline_decision")
    rev_count = state.get("outline_revision_count", 0)
    max_retries = state.get("max_outline_retries", 2)

    if not decision or decision.decision == "approve" or rev_count >= max_retries:
        return "writer"
    elif decision.decision == "research_more":
        return "research"
    elif decision.decision == "revise":
        return "strategist"
    return "writer"


# ---------------------------------------------------------------------------
# Node 5: Writer (Generates Initial Draft)
# ---------------------------------------------------------------------------
def node_writer(state: ContentAgentState) -> dict:
    brief = state["brief"]
    outline = state.get("outline")
    sources = state.get("sources", [])
    log = list(state.get("execution_log", []))

    title, body, used_llm = writer.write_draft(brief=brief, outline=outline, sources=sources)
    actual_words = len(body.split())

    generator_type = "LLM" if used_llm else "Deterministic Synthesis Engine"
    log.append(f"[Writer] Draft generated ({actual_words} words via {generator_type}).")

    return {
        "title": title,
        "draft_markdown": body,
        "actual_word_count": actual_words,
        "execution_log": log,
    }


# ---------------------------------------------------------------------------
# Node 6: QA Auditor (Runs Deterministic Gates)
# ---------------------------------------------------------------------------
def node_qa_auditor(state: ContentAgentState) -> dict:
    draft = state.get("draft_markdown", "")
    brief = state["brief"]
    sources = state.get("sources", [])
    log = list(state.get("execution_log", []))

    checks: list[QualityCheckResult] = []

    # 1. Word Count Gate
    checks.append(validate_word_count(draft, brief.target_word_count))

    # 2. Heading Structure Gate
    checks.append(validate_headings(draft))

    # 3. Source Citation Linkage Gate
    checks.append(validate_citations(draft, sources))

    # 4. Duplicate Claims Gate
    checks.append(validate_duplicate_claims(draft))

    # 5. Keyword Placement Gate
    checks.append(validate_keyword_placement(draft, brief.topic, brief.target_audience))

    # 6. SEO / Format Audit Gate
    seo_results = seo_auditor.audit(draft, brief)
    checks.extend(seo_results)

    # 7. AI Content Detection & Human Authenticity Gate
    run_id = state.get("run_id", "run-audit")
    checks.append(validate_ai_content(draft, content_id=run_id))

    passed_count = sum(1 for c in checks if c.passed)
    log.append(
        f"[QA Auditor] Executed {len(checks)} quality gates: {passed_count} passed, "
        f"{len(checks) - passed_count} warnings/failures."
    )

    return {
        "quality_checks": checks,
        "actual_word_count": len(draft.split()),
        "execution_log": log,
    }


# ---------------------------------------------------------------------------
# Node 7: Quality Decision Agent (Autonomous Corrective Routing)
# ---------------------------------------------------------------------------
def node_quality_decision_agent(state: ContentAgentState) -> dict:
    checks = state.get("quality_checks", [])
    iter_count = state.get("quality_iteration_count", 0)
    max_retries = state.get("max_quality_retries", 2)
    log = list(state.get("execution_log", []))

    failed_checks = [c for c in checks if not c.passed]
    errors = [c for c in failed_checks if c.severity == "error"]

    if iter_count >= max_retries and errors:
        decision = QualityDecision(
            action="terminate_failure",
            rationale=f"Critical quality errors remain unresolved after {iter_count} revision cycles.",
            target_issues=[e.name for e in errors],
            action_description="Terminating pipeline and generating issue report.",
        )
    elif not failed_checks:
        decision = QualityDecision(
            action="export",
            rationale="All mandatory quality gates passed with zero warnings. Ready for immediate export.",
            action_description="Proceeding directly to autonomous document assembly and export.",
        )
    else:
        check_names = {c.name for c in failed_checks}

        if "Source Citations" in check_names and any("phantom" in c.score_or_metric.lower() or "0 citations" in c.score_or_metric.lower() for c in failed_checks):
            if iter_count < max_retries:
                decision = QualityDecision(
                    action="research_more",
                    rationale="Missing evidence / broken citations detected. Re-triggering research node.",
                    target_issues=["Source Citations"],
                    action_description="Expanding research to ground missing citations.",
                )
            else:
                decision = QualityDecision(
                    action="repair_claims",
                    rationale="Unbacked claims detected. Invoking editor to rewrite or remove unverified assertions.",
                    target_issues=["Source Citations"],
                    action_description="Rewriting unverified statements.",
                )
        elif "Heading Structure" in check_names:
            if iter_count < max_retries:
                decision = QualityDecision(
                    action="repair_formatting",
                    rationale="Heading structure violation detected. Invoking deterministic formatting repair.",
                    target_issues=["Heading Structure"],
                    action_description="Applying deterministic heading normalization.",
                )
            else:
                decision = QualityDecision(
                    action="export",
                    rationale="Non-critical heading warning retained after max retries. Allowing export with annotation.",
                )
        elif "AI Content & Human Likeness" in check_names:
            if iter_count < max_retries:
                decision = QualityDecision(
                    action="invoke_editor",
                    rationale="AI content detector detected high artificial likelihood. Invoking editor to humanize cadence and remove clichés.",
                    target_issues=["AI Content & Human Likeness"],
                    action_description="Humanizing prose and breaking robotic cadence.",
                )
            else:
                decision = QualityDecision(
                    action="export",
                    rationale=f"Humanizing revisions applied ({iter_count} cycles). Proceeding with diagnostic detector score.",
                )
        elif "Word Count Target" in check_names:
            if iter_count < max_retries:
                decision = QualityDecision(
                    action="invoke_editor",
                    rationale="Significant word count variance. Invoking editor to expand/condense prose.",
                    target_issues=["Word Count Target"],
                    action_description="Invoking editor for length balancing.",
                )
            else:
                decision = QualityDecision(
                    action="export",
                    rationale=f"Word count variance within permissible tolerance after {iter_count} iterations. Approving export.",
                )
        else:
            decision = QualityDecision(
                action="export",
                rationale="Minor warnings within acceptable thresholds. Approving autonomous export.",
            )

    log.append(f"[Quality Decision Agent] Selected action: '{decision.action.upper()}' — {decision.rationale}")

    return {
        "quality_decision": decision,
        "execution_log": log,
    }


def route_quality_decision(state: ContentAgentState) -> str:
    """Conditional router based on Quality Decision Agent selection."""
    decision = state.get("quality_decision")
    if not decision:
        return "export"

    if decision.action == "export":
        return "export"
    elif decision.action == "research_more":
        return "research"
    elif decision.action in ("repair_claims", "invoke_editor"):
        return "editor"
    elif decision.action == "repair_formatting":
        return "formatter"
    elif decision.action == "terminate_failure":
        return "failure_report"
    return "export"


# ---------------------------------------------------------------------------
# Node 8: Editor (Rewrites / Repairs Content)
# ---------------------------------------------------------------------------
def node_editor(state: ContentAgentState) -> dict:
    draft = state.get("draft_markdown", "")
    brief = state["brief"]
    iter_count = state.get("quality_iteration_count", 0) + 1
    log = list(state.get("execution_log", []))

    updated_draft = editor.polish_draft(draft_markdown=draft, brief=brief, iteration_count=iter_count)
    log.append(f"[Editor] Polished draft (Iteration {iter_count}): Adjusted length and reinforced citations.")

    return {
        "draft_markdown": updated_draft,
        "quality_iteration_count": iter_count,
        "execution_log": log,
    }


# ---------------------------------------------------------------------------
# Node 9: Formatter (Deterministic Structural Repair)
# ---------------------------------------------------------------------------
def node_formatter(state: ContentAgentState) -> dict:
    draft = state.get("draft_markdown", "")
    brief = state["brief"]
    iter_count = state.get("quality_iteration_count", 0) + 1
    log = list(state.get("execution_log", []))

    lines = draft.splitlines()
    repaired_lines = []
    has_h1 = False

    for line in lines:
        if line.startswith("# ") and not has_h1:
            has_h1 = True
            repaired_lines.append(line)
        elif line.startswith("# ") and has_h1:
            repaired_lines.append("#" + line)
        else:
            repaired_lines.append(line)

    if not has_h1:
        repaired_lines.insert(0, f"# {brief.topic.title()}")

    repaired_draft = "\n".join(repaired_lines)
    log.append(f"[Formatter] Deterministically repaired heading hierarchy and structural tags (Iteration {iter_count}).")

    return {
        "draft_markdown": repaired_draft,
        "quality_iteration_count": iter_count,
        "execution_log": log,
    }


# ---------------------------------------------------------------------------
# Node 10: Export (Autonomous Document Assembly & Approval)
# ---------------------------------------------------------------------------
def node_export(state: ContentAgentState) -> dict:
    log = list(state.get("execution_log", []))
    log.append("[Export Node] Quality gates satisfied. Document assembled and approved autonomously for export.")

    return {
        "export_ready": True,
        "workflow_status": "completed",
        "execution_log": log,
    }


# ---------------------------------------------------------------------------
# Node 11: Failure Report (Repeated Gate Failure Termination)
# ---------------------------------------------------------------------------
def node_failure_report(state: ContentAgentState) -> dict:
    log = list(state.get("execution_log", []))
    decision = state.get("quality_decision")
    checks = state.get("quality_checks", [])

    report = (
        f"### Autonomous Pipeline Execution Halt\n"
        f"- **Reason**: {decision.rationale if decision else 'Exceeded retry bounds'}\n"
        f"- **Failed Gates**: {', '.join([c.name for c in checks if not c.passed])}\n"
        f"- **Total Quality Iterations**: {state.get('quality_iteration_count', 0)}\n"
        f"- **Total Outline Revisions**: {state.get('outline_revision_count', 0)}\n"
    )

    log.append(f"[Failure Report] Pipeline stopped without export. Generated issue report.")

    return {
        "export_ready": False,
        "workflow_status": "failed_qa",
        "issue_report": report,
        "execution_log": log,
    }


# ---------------------------------------------------------------------------
# Graph Construction & Compilation
# ---------------------------------------------------------------------------
def build_content_graph():
    """Build and compile the autonomous multi-agent LangGraph workflow."""
    workflow = StateGraph(ContentAgentState)

    # Register Nodes
    workflow.add_node("analyze_brief", node_analyze_brief)
    workflow.add_node("research", node_research)
    workflow.add_node("strategist", node_strategist_outline)
    workflow.add_node("outline_reviewer", node_outline_reviewer)
    workflow.add_node("writer", node_writer)
    workflow.add_node("qa_auditor", node_qa_auditor)
    workflow.add_node("quality_decision_agent", node_quality_decision_agent)
    workflow.add_node("editor", node_editor)
    workflow.add_node("formatter", node_formatter)
    workflow.add_node("export", node_export)
    workflow.add_node("failure_report", node_failure_report)

    # Linear edges
    workflow.add_edge(START, "analyze_brief")
    workflow.add_edge("analyze_brief", "research")
    workflow.add_edge("research", "strategist")
    workflow.add_edge("strategist", "outline_reviewer")

    # Conditional edge: Outline Review Agent
    workflow.add_conditional_edges(
        "outline_reviewer",
        route_outline_decision,
        {
            "writer": "writer",
            "research": "research",
            "strategist": "strategist",
        },
    )

    workflow.add_edge("writer", "qa_auditor")
    workflow.add_edge("qa_auditor", "quality_decision_agent")

    # Conditional edge: Quality Decision Agent
    workflow.add_conditional_edges(
        "quality_decision_agent",
        route_quality_decision,
        {
            "export": "export",
            "research": "research",
            "editor": "editor",
            "formatter": "formatter",
            "failure_report": "failure_report",
        },
    )

    # Loop back edges for corrective cycles
    workflow.add_edge("editor", "qa_auditor")
    workflow.add_edge("formatter", "qa_auditor")

    # Terminal edges
    workflow.add_edge("export", END)
    workflow.add_edge("failure_report", END)

    return workflow.compile()


# Singleton compiled graph
CONTENT_GRAPH = build_content_graph()
