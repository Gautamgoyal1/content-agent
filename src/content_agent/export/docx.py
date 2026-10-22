"""Clean structured text export formatted for Word/document import."""

from content_agent.models.draft import ContentDraftRecord


class PlainDocxExporter:
    """Exports content drafts as clean, structured text ready for word processors."""

    @staticmethod
    def export(record: ContentDraftRecord) -> str:
        header = (
            f"TITLE: {record.title}\n"
            f"TOPIC: {record.brief.topic}\n"
            f"CONTENT TYPE: {record.brief.content_type.upper()}\n"
            f"TARGET AUDIENCE: {record.brief.target_audience}\n"
            f"WORD COUNT: {record.actual_word_count}\n"
            f"STATUS: {record.workflow_status.upper()}\n"
            f"{'=' * 60}\n\n"
        )
        return header + record.markdown_content
