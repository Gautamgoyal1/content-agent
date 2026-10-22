"""Unit tests for BriefAnalyzerAgent and ContentBrief models."""

import pytest
from pydantic import ValidationError
from content_agent.models.brief import ContentBrief
from content_agent.agents.brief_analyzer import BriefAnalyzerAgent
from content_agent.agents.audience_analyst import AudienceAnalystAgent


def test_content_brief_validation():
    brief = ContentBrief(
        topic="Cloud-Native Observability",
        content_type="blog",
        target_audience="DevOps and SREs",
        target_word_count=600,
    )
    assert brief.topic == "Cloud-Native Observability"
    assert brief.target_word_count == 600
    assert brief.content_type == "blog"


def test_content_brief_bounds():
    with pytest.raises(ValidationError):
        ContentBrief(topic="ab")  # less than min 3 chars

    with pytest.raises(ValidationError):
        ContentBrief(topic="Valid Topic", target_word_count=50)  # below 100


def test_brief_analyzer_agent():
    agent = BriefAnalyzerAgent()
    brief = agent.analyze(
        raw_topic="  AI Reliability Engineering  ",
        content_type="white_paper",
        target_audience="VP of Engineering",
        target_word_count=750,
    )
    assert brief.topic == "AI Reliability Engineering"
    assert brief.content_type == "white_paper"
    assert brief.target_word_count == 750


def test_audience_analyst_agent():
    analyzer = BriefAnalyzerAgent()
    profiler = AudienceAnalystAgent()

    brief = analyzer.analyze("Zero-Trust Security", target_audience="Chief Information Security Officer")
    profile = profiler.profile_audience(brief)
    assert profile["technical_depth"] == "strategic"

    tech_brief = analyzer.analyze("Zero-Trust Security", target_audience="Software Engineer")
    tech_profile = profiler.profile_audience(tech_brief)
    assert tech_profile["technical_depth"] == "deep_technical"
