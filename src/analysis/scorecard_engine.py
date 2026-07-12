"""Expanded scorecard analytics for research memos."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.schemas.scorecard import extract_scorecard_table, validate_report_structure


@dataclass
class ScorecardAnalytics:
    node_count: int = 0
    top_nodes: list[str] = field(default_factory=list)
    total_scores: list[int] = field(default_factory=list)
    mean_total: float | None = None
    structure: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_count": self.node_count,
            "top_nodes": self.top_nodes,
            "mean_total": self.mean_total,
            "structure": self.structure,
            "disclaimer": "research_only_not_investment_advice",
        }


def analyze_memo_scorecard(markdown: str) -> dict[str, Any]:
    card = extract_scorecard_table(markdown or "")
    structure = validate_report_structure(markdown or "")
    totals = []
    names = []
    for n in card.nodes:
        totals.append(n.total)
        names.append(n.node)
    order = sorted(zip(names, totals), key=lambda x: -x[1])
    mean = round(sum(totals) / len(totals), 2) if totals else None
    return ScorecardAnalytics(
        node_count=len(card.nodes),
        top_nodes=[n for n, _ in order[:5]],
        total_scores=totals,
        mean_total=mean,
        structure=structure,
    ).to_dict()


def compare_scorecards(md_a: str, md_b: str) -> dict[str, Any]:
    a = analyze_memo_scorecard(md_a)
    b = analyze_memo_scorecard(md_b)
    set_a, set_b = set(a["top_nodes"]), set(b["top_nodes"])
    return {
        "a": a,
        "b": b,
        "shared_top": sorted(set_a & set_b),
        "only_a": sorted(set_a - set_b),
        "only_b": sorted(set_b - set_a),
        "disclaimer": "research_only_not_investment_advice",
    }
