"""Bulk watchlist helpers."""

from __future__ import annotations

from typing import Any

from src.ops.watchlist import add_item, list_items


def bulk_add_symbols(
    symbols: str | list[str],
    *,
    priority: str = "medium",
    tag: str = "bulk",
) -> dict[str, Any]:
    if isinstance(symbols, str):
        parts = [s.strip().upper() for s in symbols.replace(";", ",").split(",") if s.strip()]
    else:
        parts = [str(s).strip().upper() for s in symbols if str(s).strip()]
    existing = {str(i.get("symbol") or "").upper() for i in list_items()}
    added = []
    skipped = []
    for sym in parts:
        if sym in existing:
            skipped.append(sym)
            continue
        item = add_item(symbol=sym, name=sym, priority=priority, tags=[tag] if tag else None)
        added.append(item)
        existing.add(sym)
    return {
        "added": len(added),
        "skipped_existing": skipped,
        "items": added,
        "disclaimer": "research_only_not_investment_advice",
    }
