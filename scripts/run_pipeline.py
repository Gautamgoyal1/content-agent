"""CLI runner for content-agent pipeline."""

import argparse
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from content_agent.api.schemas import RunCreateRequest
from content_agent.pipeline import execute_content_pipeline
from content_agent.export.markdown import MarkdownExporter


def main():
    parser = argparse.ArgumentParser(description="Run autonomous content-agent pipeline from CLI.")
    parser.add_argument("--topic", type=str, required=True, help="Topic or brief title")
    parser.add_argument("--type", type=str, default="blog", choices=["blog", "press_release", "white_paper"])
    parser.add_argument("--audience", type=str, default="Engineering Leaders and Practitioners")
    parser.add_argument("--words", type=int, default=500)
    parser.add_argument("--output", type=str, default=None, help="Optional output markdown file path")

    args = parser.parse_args()

    print(f"[*] Launching autonomous content agent for topic: '{args.topic}' ({args.type})...")
    req = RunCreateRequest(
        topic=args.topic,
        content_type=args.type,
        target_audience=args.audience,
        target_word_count=args.words,
    )

    record = execute_content_pipeline(req)

    print("\n" + "=" * 60)
    print(f"TITLE: {record.title}")
    print(f"STATUS: {record.workflow_status.upper()} (Export Ready: {record.export_ready})")
    print(f"WORDS: {record.actual_word_count} (Target: {args.words})")
    print(f"OUTLINE REVISIONS: {record.outline_revision_count}")
    print(f"QUALITY ITERATIONS: {record.quality_iteration_count}")
    print(f"SOURCES COUNT: {len(record.sources)}")
    print("=" * 60 + "\n")

    print("QUALITY GATES:")
    for gate in record.quality_checks:
        status_symbol = "[PASS]" if gate.passed else ("[WARN]" if gate.severity == "warning" else "[FAIL]")
        print(f"  {status_symbol} {gate.name}: {gate.score_or_metric}")

    md_content = MarkdownExporter.export(record)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"\n[+] Successfully saved output to {args.output}")
    else:
        print("\n" + "-" * 40 + " DRAFT PREVIEW " + "-" * 40)
        print(record.markdown_content[:600] + "\n...\n")


if __name__ == "__main__":
    main()
