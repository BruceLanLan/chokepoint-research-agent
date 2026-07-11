"""Refresh quote cache for the entire watchlist (research monitoring)."""

from __future__ import annotations

from typing import Any

from src.ops.quote_cache import refresh_symbols
from src.ops.watchlist import list_items


def refresh_watchlist_quotes(*, limit: int = 50) -> dict[str, Any]:
    items = list_items()
    order = {"high": 0, "medium": 1, "low": 2}
    items = sorted(items, key=lambda x: order.get(x.get("priority") or "medium", 1))
    symbols = []
    for it in items[: max(1, min(limit, 100))]:
        s = str(it.get("symbol") or "").strip().upper()
        if s:
            symbols.append(s)
    if not symbols:
        return {
            "refreshed": 0,
            "symbols": [],
            "note": "watchlist empty",
            "disclaimer": "research_only_not_investment_advice",
        }
    out = refresh_symbols(symbols)
    out["symbols"] = symbols
    out["disclaimer"] = "research_only_not_investment_advice"
    out["note"] = "Best-effort snapshots for research coverage — not investment advice."
    return out
