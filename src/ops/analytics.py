"""Coverage / report analytics for the research workstation."""

from __future__ import annotations

from collections import Counter
from typing import Any

from src.ops.catalog import build_catalog
from src.ops.theses import list_theses
from src.ops.watchlist import list_items


def workspace_analytics() -> dict[str, Any]:
    reports = build_catalog(limit=200)
    modes = Counter((r.get("mode") or "unknown") for r in reports)
    qualities = []
    for r in reports:
        qs = r.get("quality_score")
        try:
            if qs not in (None, ""):
                qualities.append(float(qs))
        except (TypeError, ValueError):
            pass
    theses = list_theses()
    thesis_status = Counter((t.get("status") or "unknown") for t in theses)
    watch = list_items()
    pri = Counter((w.get("priority") or "medium") for w in watch)
    return {
        "reports_count": len(reports),
        "reports_by_mode": dict(modes),
        "quality_avg": round(sum(qualities) / len(qualities), 1) if qualities else None,
        "quality_n": len(qualities),
        "watchlist_count": len(watch),
        "watchlist_by_priority": dict(pri),
        "theses_count": len(theses),
        "theses_by_status": dict(thesis_status),
        "recent_reports": [
            {"name": r["name"], "mode": r.get("mode"), "quality_score": r.get("quality_score")}
            for r in reports[:8]
        ],
        "disclaimer": "research_only_not_investment_advice",
    }
