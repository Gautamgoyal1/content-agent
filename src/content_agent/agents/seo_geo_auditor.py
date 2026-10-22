"""SEO & Geographic/Regional intent auditor agent."""

import re
from content_agent.models.brief import ContentBrief
from content_agent.models.check_result import QualityCheckResult


class SeoGeoAuditorAgent:
    """Audits content for clear search intent, heading hierarchy, and discoverability."""

    def audit(self, markdown_text: str, brief: ContentBrief) -> list[QualityCheckResult]:
        checks = []
        # Heading hierarchy
        h1s = re.findall(r"^#\s+(.+)$", markdown_text, re.MULTILINE)
        h2s = re.findall(r"^##\s+(.+)$", markdown_text, re.MULTILINE)

        checks.append(
            QualityCheckResult(
                name="SEO Heading Hierarchy",
                passed=len(h1s) == 1 and len(h2s) >= 2,
                score_or_metric=f"{len(h1s)} H1, {len(h2s)} H2",
                details="Clear single title and structured section headings optimize indexability.",
                severity="info" if (len(h1s) == 1 and len(h2s) >= 2) else "warning",
            )
        )
        return checks
