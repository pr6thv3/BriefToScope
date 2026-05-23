"""Deterministic BriefToScope AI output evaluator.

Usage:
  python evals/evaluate_outputs.py
  python evals/evaluate_outputs.py --outputs evals/generated_outputs.json

`generated_outputs.json` may be either a list or object keyed by sample id. Each
output can contain `content_json`, `content_markdown`, `risk_flags`, or plain
`text`. When no output file is supplied, the script evaluates the sample
transcript baseline so CI can still verify the eval harness without calling an
LLM.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.services.scope_risk_rules import detect_rule_based_risks  # noqa: E402


DIMENSIONS = [
    "clarity",
    "deliverable_specificity",
    "timeline_completeness",
    "payment_schedule_presence",
    "client_responsibilities",
    "revision_policy",
    "acceptance_criteria",
    "risk_detection",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", default="evals/sample_transcripts.json")
    parser.add_argument("--outputs", default="")
    parser.add_argument("--out-dir", default="evals/reports")
    args = parser.parse_args()

    samples = json.loads((ROOT / args.samples).read_text(encoding="utf-8"))
    outputs = load_outputs(ROOT / args.outputs) if args.outputs else {}
    mode = "generated_output" if outputs else "transcript_baseline"

    results = []
    for sample in samples:
        candidate = outputs.get(sample["id"]) or {"text": sample["transcript"]}
        text = output_to_text(candidate)
        detected_risks = {risk.id.replace("rule_", "") for risk in detect_rule_based_risks([text])}
        scores = score_candidate(text, detected_risks, set(sample.get("expected_risks", [])))
        results.append(
            {
                "sample_id": sample["id"],
                "industry": sample["industry"],
                "mode": mode,
                "scores": scores,
                "overall": round(sum(scores.values()) / len(scores), 1),
                "expected_risks": sample.get("expected_risks", []),
                "detected_risks": sorted(detected_risks),
            }
        )

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "sample_count": len(results),
        "dimension_averages": {
            dimension: round(sum(item["scores"][dimension] for item in results) / len(results), 1)
            for dimension in DIMENSIONS
        },
        "overall_average": round(sum(item["overall"] for item in results) / len(results), 1),
    }
    report = {"summary": summary, "results": results}

    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "latest.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (out_dir / "latest.md").write_text(markdown_report(report), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


def load_outputs(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return data
    return {item["id"]: item for item in data}


def output_to_text(output: Any) -> str:
    if isinstance(output, str):
        return output
    if not isinstance(output, dict):
        return ""
    parts: list[str] = []
    if output.get("content_markdown"):
        parts.append(str(output["content_markdown"]))
    if output.get("text"):
        parts.append(str(output["text"]))
    content_json = output.get("content_json")
    if isinstance(content_json, dict):
        if isinstance(content_json.get("sections"), list):
            parts.extend(str(section.get("content_markdown", "")) for section in content_json["sections"])
        else:
            parts.extend(flatten_value(value) for value in content_json.values())
    for risk in output.get("risk_flags", []) or []:
        if isinstance(risk, dict):
            parts.append(" ".join(str(risk.get(key, "")) for key in ("title", "description", "suggested_fix", "recommended_fix")))
    return "\n".join(part for part in parts if part)


def flatten_value(value: Any) -> str:
    if isinstance(value, list):
        return "\n".join(str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value)
    return str(value or "")


def score_candidate(text: str, detected_risks: set[str], expected_risks: set[str]) -> dict[str, int]:
    lower = text.lower()
    return {
        "clarity": keyword_score(lower, ["scope", "deliverable", "timeline", "payment", "approval"], 72),
        "deliverable_specificity": keyword_score(lower, ["page", "deliverable", "audit", "design", "report", "video", "api"], 68),
        "timeline_completeness": keyword_score(lower, ["timeline", "launch", "week", "milestone", "uat", "feedback"], 60),
        "payment_schedule_presence": keyword_score(lower, ["payment", "50", "25", "deposit", "retainer", "invoice"], 55),
        "client_responsibilities": keyword_score(lower, ["client will", "client handles", "provide", "access", "approval"], 55),
        "revision_policy": keyword_score(lower, ["revision", "round", "change order", "edits"], 55),
        "acceptance_criteria": keyword_score(lower, ["acceptance", "sign-off", "sign off", "approval criteria", "complete"], 55),
        "risk_detection": risk_score(detected_risks, expected_risks),
    }


def keyword_score(text: str, keywords: list[str], floor: int) -> int:
    hits = sum(1 for keyword in keywords if keyword in text)
    return min(100, floor + hits * 8)


def risk_score(detected: set[str], expected: set[str]) -> int:
    if not expected:
        return 100 if not detected else 85
    hits = len(detected & expected)
    missed = len(expected - detected)
    false_positives = len(detected - expected)
    return max(35, min(100, 55 + hits * 18 - missed * 10 - false_positives * 3))


def markdown_report(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# BriefToScope AI Eval Report",
        "",
        f"- Generated at: `{summary['generated_at']}`",
        f"- Mode: `{summary['mode']}`",
        f"- Samples: `{summary['sample_count']}`",
        f"- Overall average: `{summary['overall_average']}`",
        "",
        "## Dimension Averages",
        "",
    ]
    for dimension, value in summary["dimension_averages"].items():
        lines.append(f"- `{dimension}`: {value}")
    lines.extend(["", "## Samples", ""])
    for item in report["results"]:
        lines.append(
            f"- `{item['sample_id']}` ({item['industry']}): {item['overall']} "
            f"| expected risks={len(item['expected_risks'])} detected={len(item['detected_risks'])}"
        )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
