"""Compare two educational knowledge maps (node overlap / risks)."""

from __future__ import annotations

from typing import Any

from src.ops.knowledge_maps import load_map, map_to_graph


def _candidate_labels(data: dict[str, Any]) -> set[str]:
    labels: set[str] = set()
    for layer in data.get("layers") or []:
        for cand in layer.get("candidates") or []:
            if isinstance(cand, dict):
                labels.add(str(cand.get("node") or cand.get("name") or "").strip().lower())
            else:
                labels.add(str(cand).strip().lower())
        for ex in layer.get("examples") or []:
            labels.add(str(ex).strip().lower())
    return {x for x in labels if x}


def compare_maps(a: str, b: str) -> dict[str, Any]:
    da, db = load_map(a), load_map(b)
    if not da:
        return {"error": f"unknown map: {a}"}
    if not db:
        return {"error": f"unknown map: {b}"}
    la, lb = _candidate_labels(da), _candidate_labels(db)
    shared = sorted(la & lb)
    only_a = sorted(la - lb)
    only_b = sorted(lb - la)
    ga, gb = map_to_graph(a), map_to_graph(b)
    return {
        "a": {"id": a, "system": da.get("system"), "nodes": len(ga.get("nodes") or [])},
        "b": {"id": b, "system": db.get("system"), "nodes": len(gb.get("nodes") or [])},
        "shared_labels": shared,
        "only_a": only_a[:40],
        "only_b": only_b[:40],
        "jaccard": round(len(shared) / max(1, len(la | lb)), 3),
        "risks_a": (da.get("risks") or [])[:5],
        "risks_b": (db.get("risks") or [])[:5],
        "disclaimer": "research_only_not_investment_advice",
        "note": "Educational map overlap — not a portfolio comparison.",
    }
