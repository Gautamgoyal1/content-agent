"""Blog workflow specialization and configuration."""

BLOG_WORKFLOW_CONFIG = {
    "content_type": "blog",
    "required_sections": [
        "Introduction: The State of the Field",
        "Why This Breakthrough Matters Now",
        "Key Insights from Recent Empirical Research",
        "Actionable Recommendations for Practitioners",
        "Summary & Strategic Takeaways",
    ],
    "default_target_word_count": 500,
    "min_sources_required": 2,
    "quality_gates": ["word_count", "headings", "citations", "duplicate_claims", "keyword_placement"],
}
