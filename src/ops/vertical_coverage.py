"""Per-vertical coverage dashboard — memo counts, quality, freshness."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.ops.catalog import filter_catalog
from src.ops.pro.verticals import list_verticals
from src.ops.vertical_compare import compare_vertical_latest

DISCLAIMER = "research_only_not_investment_advice"


def vertical_coverage_row(vertical_id: str) -> dict[str, Any]:
    items = filter_catalog(vertical_id=vertical_id, limit=50)
    scores: list[float] = []
    for it in items:
        try:
            scores.append(float(it.get("quality_score") or 0))
        except (TypeError, ValueError):
            pass
    latest = items[0] if items else None
    compare_hint = None
    if len(items) >= 2:
        try:
            c = compare_vertical_latest(vertical_id, include_udiff=False)
            if not c.get("error"):
                compare_hint = {
                    "similarity_ratio": c.get("similarity_ratio"),
                    "quality_delta_b_minus_a": c.get("quality_delta_b_minus_a"),
                    "a": (c.get("a") or {}).get("name"),
                    "b": (c.get("b") or {}).get("name"),
                }
        except Exception:  # noqa: BLE001
            compare_hint = None
    return {
        "vertical_id": vertical_id,
        "memo_count": len(items),
        "avg_quality": round(sum(scores) / len(scores), 1) if scores else None,
        "latest": {
            "name": (latest or {}).get("name"),
            "modified": (latest or {}).get("modified"),
            "quality_score": (latest or {}).get("quality_score"),
        }
        if latest
        else None,
        "latest_compare": compare_hint,
        "stale": len(items) == 0,
        "needs_pair": 0 < len(items) < 2,
    }


def vertical_coverage_dashboard() -> dict[str, Any]:
    packs = list_verticals()
    rows = [vertical_coverage_row(p["id"]) for p in packs]
    covered = sum(1 for r in rows if r["memo_count"] > 0)
    paired = sum(1 for r in rows if r["memo_count"] >= 2)
    actions: list[str] = []
    for r in rows:
        if r["stale"]:
            actions.append(f"Seed memos: research --mock -V {r['vertical_id']}")
        elif r["needs_pair"]:
            actions.append(f"Second pass for compare: research --mock -V {r['vertical_id']}")
    if not actions:
        actions.append("Run compare-vertical on active packs; weekly-ops for hygiene")
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "packs": len(rows),
        "with_memos": covered,
        "with_pairs": paired,
        "rows": rows,
        "next_actions": actions[:8],
        "disclaimer": DISCLAIMER,
        "note": "Coverage process hygiene by vertical — not P&L or advice.",
    }
