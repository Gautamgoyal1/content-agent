"""API routes for brief analysis and normalization."""

from fastapi import APIRouter
from content_agent.api.schemas import RunCreateRequest
from content_agent.models.brief import ContentBrief
from content_agent.agents.brief_analyzer import BriefAnalyzerAgent
from content_agent.agents.audience_analyst import AudienceAnalystAgent

router = APIRouter(prefix="/briefs", tags=["Briefs"])
analyzer = BriefAnalyzerAgent()
audience_analyst = AudienceAnalystAgent()


@router.post("/validate", response_model=ContentBrief)
def validate_brief(payload: RunCreateRequest):
    """Normalize and validate a content brief."""
    return analyzer.analyze(
        raw_topic=payload.topic,
        content_type=payload.content_type,
        target_audience=payload.target_audience,
        target_word_count=payload.target_word_count,
        tone=payload.tone,
    )


@router.post("/profile")
def profile_audience(payload: RunCreateRequest):
    """Extract audience depth and tone recommendations."""
    brief = analyzer.analyze(
        raw_topic=payload.topic,
        content_type=payload.content_type,
        target_audience=payload.target_audience,
        target_word_count=payload.target_word_count,
        tone=payload.tone,
    )
    return audience_analyst.profile_audience(brief)
