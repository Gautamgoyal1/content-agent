"""Repeatable evaluation script evaluating writing quality, factual grounding, and cadence metrics."""

import json
import os
import sys
import time
from pathlib import Path

# Add src to pythonpath
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
load_dotenv()

from content_agent.api.schemas import RunCreateRequest
from content_agent.pipeline import execute_content_pipeline
from content_agent.tools.ai_detector import AIDetectorClient


TEST_BRIEFS = [
    RunCreateRequest(
        topic="Kubernetes Multi-Cluster Networking & Service Mesh",
        content_type="blog",
        target_audience="DevOps & Platform Engineering Leaders",
        target_word_count=450,
    ),
    RunCreateRequest(
        topic="Autonomous Observability & Telemetry Verification",
        content_type="press_release",
        target_audience="Enterprise IT Executives & CISOs",
        target_word_count=350,
    ),
    RunCreateRequest(
        topic="Zero Trust Architecture in Cloud Native Infrastructure",
        content_type="white_paper",
        target_audience="Security Architects and Staff Engineers",
        target_word_count=500,
    ),
]


def evaluate_pipeline():
    detector = AIDetectorClient()
    results = []

    print("==================================================================")
    print("      CONTENT AGENT - EDITORIAL QUALITY & CADENCE BENCHMARK       ")
    print("==================================================================")

    for idx, brief in enumerate(TEST_BRIEFS, 1):
        print(f"\n[{idx}/3] Executing Pipeline for '{brief.topic}' ({brief.content_type})...")
        start_time = time.time()

        record = execute_content_pipeline(brief)
        elapsed = round(time.time() - start_time, 2)

        detection = detector.detect(record.markdown_content, content_id=record.id)

        # Calculate metrics
        passed_checks = sum(1 for c in record.quality_checks if c.passed)
        total_checks = len(record.quality_checks)
        sections = [s for s in record.markdown_content.split("## ") if s.strip()]
        has_citations = sum(1 for s in sections if "[" in s and "]" in s)
        citation_coverage = round(has_citations / max(1, len(sections)) * 100, 1)

        metric = {
            "topic": brief.topic,
            "content_type": brief.content_type,
            "target_words": brief.target_word_count,
            "actual_words": record.actual_word_count,
            "word_count_compliance_pct": round(
                (1 - abs(record.actual_word_count - brief.target_word_count) / brief.target_word_count) * 100, 1
            ),
            "citations_found": record.markdown_content.count("[") - 1,  # exclude ref list header if any
            "section_citation_coverage_pct": citation_coverage,
            "sentence_burstiness": detection.burstiness_score,
            "lexical_richness": detection.vocabulary_richness,
            "flagged_cliches": detection.flagged_phrases,
            "ai_heuristic_score_pct": int(detection.ai_score * 100),
            "human_authenticity_pct": int(detection.human_score * 100),
            "quality_gates_passed": f"{passed_checks}/{total_checks}",
            "quality_iterations": record.quality_iteration_count,
            "latency_seconds": elapsed,
            "status": record.workflow_status,
        }

        results.append(metric)

        print(f" -> Result: {metric['actual_words']} words in {elapsed}s | Gates: {metric['quality_gates_passed']}")
        print(f" -> Burstiness: {metric['sentence_burstiness']} | Heuristic AI: {metric['ai_heuristic_score_pct']}% | Clichés: {len(metric['flagged_cliches'])}")

    # Store benchmark results
    out_path = Path("evals/evaluation_results.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n==================================================================")
    print("                      BENCHMARK SUMMARY                          ")
    print("==================================================================")
    for r in results:
        print(f"* {r['content_type'].upper():14} | {r['actual_words']:4}w | Burstiness: {r['sentence_burstiness']:4.1f} | AI: {r['ai_heuristic_score_pct']:2}% | Citations: {r['section_citation_coverage_pct']}% | Status: {r['status']}")
    print(f"\nSaved full diagnostic run to: {out_path.resolve()}")


if __name__ == "__main__":
    evaluate_pipeline()
