"""HTML document exporter with standalone typography and CSS styling."""

import re
from content_agent.models.draft import ContentDraftRecord


class HTMLExporter:
    """Exports content drafts as standalone, styled HTML documents."""

    @staticmethod
    def _simple_markdown_to_html(md: str) -> str:
        html = md
        # Headings
        html = re.sub(r"^### (.*)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
        html = re.sub(r"^## (.*)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
        html = re.sub(r"^# (.*)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)
        # Bold and Italic
        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
        html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)
        # Blockquotes
        html = re.sub(r"^> (.*)$", r"<blockquote>\1</blockquote>", html, flags=re.MULTILINE)
        # Links
        html = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank">\1</a>', html)
        # Citations highlighting
        html = re.sub(r"\[(\d+)\]", r'<cite class="citation">[\1]</cite>', html)
        # Paragraphs
        paragraphs = html.split("\n\n")
        formatted = []
        for p in paragraphs:
            p_strip = p.strip()
            if p_strip.startswith("<h") or p_strip.startswith("<blockquote") or p_strip.startswith("<ul>"):
                formatted.append(p_strip)
            elif p_strip.startswith("- "):
                items = p_strip.split("\n")
                li_html = "".join([f"<li>{item[2:]}</li>" for item in items if item.startswith("- ")])
                formatted.append(f"<ul>{li_html}</ul>")
            else:
                formatted.append(f"<p>{p_strip.replace(chr(10), '<br>')}</p>")
        return "\n".join(formatted)

    @classmethod
    def export(cls, record: ContentDraftRecord) -> str:
        body_html = cls._simple_markdown_to_html(record.markdown_content)
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{record.title}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.7; color: #1e293b; max-width: 800px; margin: 40px auto; padding: 0 20px; }}
    h1 {{ color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 24px; }}
    h2 {{ color: #1e293b; margin-top: 32px; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px; }}
    h3 {{ color: #334155; margin-top: 24px; }}
    blockquote {{ border-left: 4px solid #3b82f6; padding-left: 16px; color: #64748b; font-style: italic; margin: 20px 0; }}
    .citation {{ color: #2563eb; font-weight: bold; font-style: normal; }}
    a {{ color: #2563eb; text-decoration: underline; }}
    .metadata {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px 18px; margin-bottom: 28px; font-size: 0.9rem; color: #475569; }}
  </style>
</head>
<body>
  <div class="metadata">
    <strong>Content Agent Verified Publication</strong><br>
    Topic: {record.brief.topic} | Audience: {record.brief.target_audience} | Format: {record.brief.content_type.title()} | Words: {record.actual_word_count}
  </div>
  {body_html}
</body>
</html>"""
