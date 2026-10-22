"""API routes for exporting generated content in multiple formats."""

from typing import Literal
from fastapi import APIRouter, HTTPException, Query, Response
from content_agent.pipeline import RUNS_STORE
from content_agent.export.markdown import MarkdownExporter
from content_agent.export.html import HTMLExporter
from content_agent.export.docx import PlainDocxExporter

router = APIRouter(prefix="/exports", tags=["Exports"])


@router.get("/{run_id}")
def export_draft(run_id: str, format: Literal["markdown", "html", "docx", "text"] = "markdown"):
    """Export draft in requested format (markdown, html, docx/text)."""
    record = RUNS_STORE.get(run_id)
    if not record:
        raise HTTPException(status_code=404, detail="Run not found")

    if not record.export_ready:
        raise HTTPException(
            status_code=400,
            detail=f"Draft cannot be exported: status is '{record.workflow_status}'. {record.issue_report or 'Failed mandatory quality gates.'}",
        )

    if format == "html":
        content = HTMLExporter.export(record)
        return Response(
            content=content,
            media_type="text/html",
            headers={"Content-Disposition": f'attachment; filename="{record.brief.content_type}-{record.id}.html"'},
        )
    elif format in ("docx", "text"):
        content = PlainDocxExporter.export(record)
        return Response(
            content=content,
            media_type="text/plain",
            headers={"Content-Disposition": f'attachment; filename="{record.brief.content_type}-{record.id}.txt"'},
        )
    else:  # markdown
        content = MarkdownExporter.export(record)
        return Response(
            content=content,
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{record.brief.content_type}-{record.id}.md"'},
        )
