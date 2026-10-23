"""Unit tests for specialized agent logic."""

from content_agent.models.brief import ContentBrief
from content_agent.models.source import SourceEvidence
from content_agent.agents.strategist import StrategistAgent
from content_agent.agents.writer import WriterAgent
from content_agent.agents.fact_checker import FactCheckerAgent
from content_agent.agents.editor import EditorAgent
from content_agent.agents.knowledge_curator import KnowledgeCuratorAgent


def test_strategist_agent():
    brief = ContentBrief(topic="Zero-Trust Architecture", content_type="blog", target_word_count=500)
    sources = [SourceEvidence(id=1, title="S1", url="http://s1.org", snippet="Sample snippet 1")]

    strategist = StrategistAgent()
    outline = strategist.create_outline(brief, sources)

    assert "Zero-Trust Architecture" in outline.title
    assert len(outline.target_sections) >= 4
    assert 1 in outline.source_ids_referenced


def test_writer_agent():
    brief = ContentBrief(topic="Edge Computing", content_type="blog", target_word_count=400)
    sources = [SourceEvidence(id=1, title="S1", url="http://s1.org", snippet="Sample snippet 1")]
    strategist = StrategistAgent()
    outline = strategist.create_outline(brief, sources)

    writer = WriterAgent()
    title, body, used_llm = writer.write_draft(brief, outline, sources)

    assert "Edge Computing" in title
    assert "[1]" in body
    assert "## References & Verified Sources" in body


def test_fact_checker_agent():
    sources = [SourceEvidence(id=1, title="S1", url="http://s1.org", snippet="Sample snippet 1")]
    checker = FactCheckerAgent()

    text = "Deploying edge computing reduces latency by 42% [1]. Unknown statement with fake source [99]."
    claims = checker.verify_claims(text, sources)

    assert len(claims) == 2
    assert claims[0].verification_status == "verified"
    assert claims[1].verification_status == "unverified"


def test_editor_agent():
    brief = ContentBrief(topic="Microservices", content_type="blog", target_word_count=500)
    editor = EditorAgent()

    short_draft = "# Title\nShort draft text [1].\n## References & Verified Sources\n- [1] S1"
    polished = editor.polish_draft(short_draft, brief)
    assert len(polished.split()) > len(short_draft.split())
