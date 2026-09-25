from __future__ import annotations

from collections import Counter
from typing import Iterable


def _judge_status(row: dict) -> str:
    judge = row.get("judge") or {}
    if not isinstance(judge, dict):
        return "error"
    status = str(judge.get("correctness") or "error").strip().lower()
    return status if status in {"correct", "partial", "incorrect", "error"} else "error"


def build_report(rows: Iterable[dict], name: str = "run") -> str:
    rows = list(rows)
    if not rows:
        return f"# Evaluation report: {name}\n\nNo rows were evaluated."

    category_counts = Counter(str(r.get("category") or "unknown") for r in rows)
    correctness = Counter(_judge_status(r) for r in rows if not r.get("refused"))
    judged = sum(1 for r in rows if not r.get("refused") and r.get("judge") is not None)
    refused = sum(1 for r in rows if r.get("refused"))

    lines = [
        f"# Evaluation report: {name}",
        "",
        f"- Total rows: {len(rows)}",
        f"- Refused: {refused}",
        f"- Judged: {judged}",
        "",
        "## By category",
    ]

    for category in sorted(category_counts):
        lines.append(f"- {category}: {category_counts[category]}")

    lines += [
        "",
        "## Judgement summary",
        f"- correct: {correctness.get('correct', 0)}",
        f"- partial: {correctness.get('partial', 0)}",
        f"- incorrect: {correctness.get('incorrect', 0)}",
        f"- error: {correctness.get('error', 0)}",
    ]

    if rows:
        avg_cost = sum(float(r.get("cost_usd") or 0.0) for r in rows) / len(rows)
        avg_latency = sum(float(r.get("latency_s") or 0.0) for r in rows) / len(rows)
        lines += [
            "",
            "## Cost and latency",
            f"- Average cost per question: ${avg_cost:.6f}",
            f"- Average latency per question: {avg_latency:.2f}s",
        ]

    return "\n".join(lines)
