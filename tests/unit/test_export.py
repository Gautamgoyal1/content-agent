"""Unit tests for export modules (Markdown, HTML, PlainDocx)."""

from content_agent.models.brief import ContentBrief
from content_agent.models.draft import ContentDraftRecord
from content_agent.models.source import SourceEvidence
from content_agent.export.markdown import MarkdownExporter
from content_agent.export.html import HTMLExporter
from content_agent.export.docx import PlainDocxExporter


def create_sample_record():
    brief = ContentBrief(topic="Observability", content_type="blog", target_word_count=500)
    return ContentDraftRecord(
        id="run-test1234",
        brief=brief,
        title="Demystifying Observability",
        markdown_content="# Demystifying Observability\n\nInsight paragraph [1].\n\n## References & Verified Sources\n- **[1]** [Ref](http://ref.org): Snip",
        actual_word_count=350,
        sources=[SourceEvidence(id=1, title="Ref", url="http://ref.org", snippet="Snip")],
        export_ready=True,
        workflow_status="completed",
    )


def test_markdown_exporter():
    record = create_sample_record()
    exported = MarkdownExporter.export(record)
    assert "---" in exported
    assert 'title: "Demystifying Observability"' in exported
    assert 'workflow_status: "completed"' in exported


def test_html_exporter():
    record = create_sample_record()
    exported = HTMLExporter.export(record)
    assert "<!DOCTYPE html>" in exported
    assert "<h1>Demystifying Observability</h1>" in exported
    assert '<cite class="citation">[1]</cite>' in exported


def test_docx_exporter():
    record = create_sample_record()
    exported = PlainDocxExporter.export(record)
    assert "TITLE: Demystifying Observability" in exported
    assert "STATUS: COMPLETED" in exported
