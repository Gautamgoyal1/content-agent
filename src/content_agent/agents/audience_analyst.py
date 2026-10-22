"""Audience Analyst Agent: Profiles reader intent, knowledge level, and tone constraints."""

from typing import Any
from content_agent.models.brief import ContentBrief


class AudienceAnalystAgent:
    """Derives stylistic guidelines and technical expectations for target audiences."""

    def profile_audience(self, brief: ContentBrief) -> dict[str, Any]:
        audience_lower = brief.target_audience.lower()

        if any(w in audience_lower for w in ["executive", "c-level", "chief", "officer", "ciso", "cto", "cio", "leader", "director", "manager"]):
            depth = "strategic"
            focus = "business impact, risk mitigation, and empirical ROI metrics"
        elif any(w in audience_lower for w in ["engineer", "developer", "architect", "sre", "technical", "practitioner", "devops"]):
            depth = "deep_technical"
            focus = "implementation architectures, benchmarks, and concrete mechanisms"
        else:
            depth = "accessible_professional"
            focus = "foundational principles, practical best practices, and actionable takeaways"

        return {
            "audience": brief.target_audience,
            "technical_depth": depth,
            "core_focus": focus,
            "recommended_tone": brief.tone,
        }
