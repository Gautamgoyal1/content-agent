"""Press release workflow specialization and configuration."""

PRESS_RELEASE_WORKFLOW_CONFIG = {
    "content_type": "press_release",
    "required_sections": [
        "Executive Headline & Dateline",
        "Key Benchmark Findings & Efficiency Metrics",
        "Operational Governance & Industry Impact",
        "Media Contacts & Verification Repositories",
    ],
    "default_target_word_count": 400,
    "min_sources_required": 2,
    "quality_gates": ["word_count", "headings", "citations", "dateline_check", "keyword_placement"],
}
