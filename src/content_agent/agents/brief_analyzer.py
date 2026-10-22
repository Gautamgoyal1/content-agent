"""Brief Analyzer Agent: Validates, cleans, and structures user content briefs."""

from content_agent.models.brief import ContentBrief


class BriefAnalyzerAgent:
    """Validates and normalizes briefs into structured specifications."""

    def analyze(self, raw_topic: str, content_type: str = "blog", target_audience: str = "", target_word_count: int = 500, tone: str = "") -> ContentBrief:
        topic = raw_topic.strip()
        audience = (target_audience or "Technical practitioners and industry decision makers").strip()
        tone_val = (tone or "authoritative, objective, and evidence-grounded").strip()

        # Sanitize word count
        count = max(100, min(5000, target_word_count))

        return ContentBrief(
            topic=topic,
            content_type=content_type,  # type: ignore
            target_audience=audience,
            target_word_count=count,
            tone=tone_val,
        )
