"""White paper workflow specialization and configuration."""

WHITE_PAPER_WORKFLOW_CONFIG = {
    "content_type": "white_paper",
    "required_sections": [
        "Executive Summary",
        "Problem Statement & Architectural Vulnerabilities",
        "Empirical Findings & Quantitative Benchmarks",
        "Recommended Best Practices for Technical Leaders",
        "Conclusion & Traceability Framework",
    ],
    "default_target_word_count": 800,
    "min_sources_required": 3,
    "quality_gates": ["word_count", "headings", "citations", "exec_summary_check", "keyword_placement"],
}
