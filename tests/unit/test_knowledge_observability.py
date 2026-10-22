"""Unit tests for knowledge curation and observability modules."""

from content_agent.models.source import SourceEvidence
from content_agent.knowledge.evidence_store import EvidenceStore
from content_agent.knowledge.company_kb import CompanyKnowledgeBase
from content_agent.knowledge.vector_store import InMemoryVectorStore
from content_agent.observability.logging import get_logger
from content_agent.observability.cost_tracker import CostTracker
from content_agent.observability.tracing import WorkflowTracer


def test_evidence_store():
    store = EvidenceStore()
    source = SourceEvidence(id=1, title="Benchmark Test", url="https://example.com/bm", snippet="Snippet")
    store.add_source(source)

    assert store.get_source(1) == source
    assert len(store.all_sources()) == 1

    store.clear()
    assert len(store.all_sources()) == 0


def test_company_knowledge_base():
    kb = CompanyKnowledgeBase()
    voice = kb.get_brand_voice()
    assert len(voice) > 0


def test_in_memory_vector_store():
    store = InMemoryVectorStore()
    store.add_texts([
        "Kubernetes orchestration and container management",
        "PostgreSQL vector search and embedding databases",
        "Baking artisanal sourdough bread at home",
    ])

    results = store.similarity_search("container cluster deployment", top_k=1)
    assert len(results) == 1
    assert "Kubernetes" in results[0]["text"]


def test_observability_tracker_and_tracer():
    logger = get_logger("test_logger")
    assert logger is not None

    tracker = CostTracker()
    tracker.record_usage(prompt_tokens=1000, completion_tokens=500)
    summary = tracker.summary()
    assert summary["total_tokens"] == 1500
    assert summary["estimated_cost_usd"] > 0

    tracer = WorkflowTracer()
    span = tracer.start_span("agent_execution", node="strategist")
    tracer.end_span(span, status="success")
    spans = tracer.to_dict()
    assert len(spans) == 1
    assert spans[0]["name"] == "agent_execution"
    assert spans[0]["status"] == "success"
