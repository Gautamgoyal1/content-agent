"""Unit tests for quality validators."""

import pytest
from content_agent.models.source import SourceEvidence
from content_agent.validators.word_count import validate_word_count
from content_agent.validators.headings import validate_headings
from content_agent.validators.url_check import validate_citations
from content_agent.validators.duplicate_claims import validate_duplicate_claims
from content_agent.validators.keyword_placement import validate_keyword_placement
from content_agent.validators.ai_detector import validate_ai_content
from content_agent.validators.editorial_quality import audit_editorial_quality
from content_agent.models.brief import ContentBrief


def test_validate_word_count():
    text = "word " * 500
    res = validate_word_count(text, target_words=500)
    assert res.passed is True
    assert "500 words" in res.score_or_metric

    short_text = "word " * 100
    res_short = validate_word_count(short_text, target_words=500)
    assert res_short.passed is False


def test_validate_headings():
    good_markdown = """# Top Title
Introduction text.
## Section One
Content one.
## Section Two
Content two.
"""
    res = validate_headings(good_markdown)
    assert res.passed is True

    no_h1 = """## Section One
Content.
## Section Two
Content.
"""
    res_no_h1 = validate_headings(no_h1)
    assert res_no_h1.passed is False
    assert res_no_h1.severity == "error"

    multi_h1 = """# Title One
# Title Two
## Section One
"""
    res_multi = validate_headings(multi_h1)
    assert res_multi.passed is False


def test_validate_citations():
    sources = [
        SourceEvidence(id=1, title="S1", url="http://example.com/1", snippet="snip 1"),
        SourceEvidence(id=2, title="S2", url="http://example.com/2", snippet="snip 2"),
    ]

    valid_text = "Assertion with evidence [1] and another citation [2]."
    res = validate_citations(valid_text, sources)
    assert res.passed is True
    assert "2 distinct evidence references" in res.score_or_metric

    phantom_text = "Assertion with unbacked citation [99]."
    res_phantom = validate_citations(phantom_text, sources)
    assert res_phantom.passed is False
    assert res_phantom.severity == "error"

    no_citations = "Assertion with no citations at all."
    res_none = validate_citations(no_citations, sources)
    assert res_none.passed is False


def test_validate_duplicate_claims():
    diverse_text = """This is the first paragraph focusing on initial architecture and system constraints.

This is the second distinct paragraph discussing telemetry collection, latency metrics, and performance testing."""
    res = validate_duplicate_claims(diverse_text)
    assert res.passed is True


def test_validate_keyword_placement():
    good_text = "# Cloud Observability in Modern Systems\nUnderstanding cloud observability requires telemetry data."
    res = validate_keyword_placement(good_text, topic="Cloud Observability", audience="DevOps")
    assert res.passed is True


def test_validate_ai_content():
    human_text = (
        "We built this distributed system to handle high throughput during flash sales. "
        "It was messy at first. We spent three weeks debugging a race condition in Redis before "
        "eventually switching to PostgreSQL for atomic transactions. Don't make the same mistake we made."
    )
    res = validate_ai_content(human_text, content_id="test-human")
    assert "Human" in res.score_or_metric

    formulaic_ai_text = (
        "In the ever-evolving landscape of modern technology, it is crucial to delve into the tapestry "
        "of autonomous systems. Furthermore, this serves as a testament to innovation, unlocking the potential "
        "of digital transformation. In conclusion, navigating the landscape plays a pivotal role."
    )
    res_ai = validate_ai_content(formulaic_ai_text, content_id="test-ai")
    assert "AI" in res_ai.score_or_metric
    assert res_ai.passed is False


def test_audit_editorial_quality():
    sources = [SourceEvidence(id=1, title="S1", url="http://example.com/1", snippet="snip 1")]
    brief = ContentBrief(topic="Kubernetes Reliability", content_type="blog", target_word_count=400)

    good_text = (
        "# Kubernetes Reliability\n\n"
        "## Practical Reality\n"
        "Managing distributed pods incurs distinct architectural friction and operational tradeoffs [1].\n\n"
        "## Benchmark Evidence\n"
        "Controlled trials show that mitigating failure modes and network latency overhead requires strict limits [1].\n"
    )

    results = audit_editorial_quality(good_text, brief, sources)
    assert len(results) == 3
    assert any("Depth of Analysis" in r.name and r.passed for r in results)
    assert any("Section Evidence Grounding" in r.name and r.passed for r in results)


