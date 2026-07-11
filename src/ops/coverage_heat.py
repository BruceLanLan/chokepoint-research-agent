"""Coverage heat map — watchlist × reports × theses density."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

from src.ops.catalog import build_catalog
from src.ops.theses import list_theses
from src.ops.watchlist import list_items


def coverage_heatmap() -> dict[str, Any]:
    watch = list_items()
    theses = list_theses()
    reports = build_catalog(limit=200)

    # symbol → stats
    rows: list[dict[str, Any]] = []
    for w in watch:
        sym = str(w.get("symbol") or "").upper()
        if not sym:
            continue
        thesis_hits = [
            t
            for t in theses
            if sym in [s.upper() for s in (t.get("related_symbols") or [])]
            or sym.lower() in (t.get("statement") or "").lower()
            or sym.lower() in (t.get("title") or "").lower()
        ]
        report_hits = []
        for r in reports:
            blob = f"{r.get('title')} {r.get('name')} {r.get('preview')}".upper()
            if sym in blob or re.search(rf"\b{re.escape(sym)}\b", blob):
                report_hits.append(r.get("name"))
        coverage_score = (
            (3 if thesis_hits else 0)
            + min(3, len(report_hits))
            + (1 if w.get("priority") == "high" else 0)
        )
        rows.append(
            {
                "symbol": sym,
                "name": w.get("name") or "",
                "priority": w.get("priority") or "medium",
                "thesis_count": len(thesis_hits),
                "report_count": len(report_hits),
                "recent_reports": report_hits[:5],
                "coverage_score": coverage_score,
                "heat": (
                    "hot"
                    if coverage_score >= 5
                    else "warm"
                    if coverage_score >= 2
                    else "cold"
                ),
            }
        )

    # orphan theses without symbols
    orphans = [
        {"id": t.get("id"), "title": t.get("title")}
        for t in theses
        if not (t.get("related_symbols") or [])
    ]

    modes = Counter((r.get("mode") or "unknown") for r in reports)
    heat_dist = Counter(r["heat"] for r in rows)

    return {
        "symbols": sorted(rows, key=lambda x: -x["coverage_score"]),
        "heat_distribution": dict(heat_dist),
        "reports_by_mode": dict(modes),
        "orphan_theses": orphans,
        "watchlist_count": len(watch),
        "disclaimer": "research_only_not_investment_advice",
    }
