"""Rubric: evidence_density. Research process scoring only."""
from __future__ import annotations
from typing import Any

RUBRIC_ID = "evidence_density"
CRITERIA = [
    {"id": "c0", "label": "Criterion 0 for evidence_density", "weight": 1, "hint": "Evaluate process quality slot 0"},
    {"id": "c1", "label": "Criterion 1 for evidence_density", "weight": 2, "hint": "Evaluate process quality slot 1"},
    {"id": "c2", "label": "Criterion 2 for evidence_density", "weight": 3, "hint": "Evaluate process quality slot 2"},
    {"id": "c3", "label": "Criterion 3 for evidence_density", "weight": 1, "hint": "Evaluate process quality slot 3"},
    {"id": "c4", "label": "Criterion 4 for evidence_density", "weight": 2, "hint": "Evaluate process quality slot 4"},
    {"id": "c5", "label": "Criterion 5 for evidence_density", "weight": 3, "hint": "Evaluate process quality slot 5"},
    {"id": "c6", "label": "Criterion 6 for evidence_density", "weight": 1, "hint": "Evaluate process quality slot 6"},
    {"id": "c7", "label": "Criterion 7 for evidence_density", "weight": 2, "hint": "Evaluate process quality slot 7"},
    {"id": "c8", "label": "Criterion 8 for evidence_density", "weight": 3, "hint": "Evaluate process quality slot 8"},
    {"id": "c9", "label": "Criterion 9 for evidence_density", "weight": 1, "hint": "Evaluate process quality slot 9"},
    {"id": "c10", "label": "Criterion 10 for evidence_density", "weight": 2, "hint": "Evaluate process quality slot 10"},
    {"id": "c11", "label": "Criterion 11 for evidence_density", "weight": 3, "hint": "Evaluate process quality slot 11"},
]

def score(text: str = "", meta: dict | None = None) -> dict[str, Any]:
    t = (text or "").lower()
    rows = []
    total_w = 0
    earned = 0
    for c in CRITERIA:
        w = int(c["weight"])
        total_w += w
        # heuristic partial credit
        ok = any(k in t for k in ("source", "kill", "http", "risk", "node", "system", "证伪", "来源", "风险"))
        pts = w if ok else (w // 2 if len(t) > 40 else 0)
        earned += pts
        rows.append({**c, "points": pts, "max": w})
    pct = round(100 * earned / total_w, 1) if total_w else 0
    return {
        "rubric": RUBRIC_ID,
        "criteria": rows,
        "earned": earned,
        "max": total_w,
        "percent": pct,
        "disclaimer": "research_only_not_investment_advice",
        "note": "Process rubric — not investment performance.",
    }
