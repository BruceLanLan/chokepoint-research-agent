"""Quality leaderboard over recent memos (structure scores)."""

from __future__ import annotations

from typing import Any

from src.ops.catalog import build_catalog
from src.ops.tags import get_tags
from src.schemas.scorecard import validate_report_structure
from src.tools.reports import read_report


def quality_leaderboard(limit: int = 30) -> dict[str, Any]:
    items = build_catalog(limit=max(limit, 50))
    rows = []
    for it in items[: max(1, min(limit, 100))]:
        name = it.get("name") or ""
        body = read_report(name) or ""
        q = validate_report_structure(body) if body else {"score": 0, "pass": False}
        # prefer catalog score if present
        cat_q = it.get("quality_score")
        try:
            cat_score = float(cat_q) if cat_q not in (None, "") else None
        except (TypeError, ValueError):
            cat_score = None
        score = cat_score if cat_score is not None else q.get("score")
        tags = (get_tags(name) or {}).get("tags") or []
        rows.append(
            {
                "name": name,
                "mode": it.get("mode"),
                "score": score,
                "pass": q.get("pass"),
                "url_count": q.get("url_count"),
                "tags": tags,
                "modified": it.get("modified"),
            }
        )
    rows.sort(key=lambda r: (-(r["score"] or 0), r.get("name") or ""))
    scores = [r["score"] for r in rows if isinstance(r.get("score"), (int, float))]
    return {
        "count": len(rows),
        "avg_score": round(sum(scores) / len(scores), 1) if scores else None,
        "top": rows[:10],
        "bottom": list(reversed(rows[-5:])) if len(rows) >= 5 else list(reversed(rows)),
        "all": rows,
        "disclaimer": "research_only_not_investment_advice",
        "note": "Structure/heuristic quality only — not factual accuracy or investment merit.",
    }
