"""Markdown document exporter with YAML frontmatter and audit metadata."""

from content_agent.models.draft import ContentDraftRecord


class MarkdownExporter:
    """Exports content drafts as well-formed Markdown files with metadata."""

    @staticmethod
    def export(record: ContentDraftRecord) -> str:
        passed_checks = sum(1 for c in record.quality_checks if c.passed)
        total_checks = len(record.quality_checks)

        frontmatter = (
            f"---\n"
            f"title: \"{record.title}\"\n"
            f"topic: \"{record.brief.topic}\"\n"
            f"content_type: \"{record.brief.content_type}\"\n"
            f"target_audience: \"{record.brief.target_audience}\"\n"
            f"word_count: {record.actual_word_count}\n"
            f"quality_score: \"{passed_checks}/{total_checks} gates passed\"\n"
            f"workflow_status: \"{record.workflow_status}\"\n"
            f"outline_revisions: {record.outline_revision_count}\n"
            f"quality_iterations: {record.quality_iteration_count}\n"
            f"pipeline_mode: \"{record.mode_label}\"\n"
            f"---\n\n"
        )
        return frontmatter + record.markdown_content
