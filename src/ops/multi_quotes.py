"""Multi-symbol quote snapshot helper (batch research monitoring)."""

from __future__ import annotations

from typing import Any

from src.ops.quote_cache import refresh_symbols


def multi_quote_snapshot(symbols: list[str] | str) -> dict[str, Any]:
    if isinstance(symbols, str):
        symbols = [s.strip() for s in symbols.replace(";", ",").split(",") if s.strip()]
    out = refresh_symbols(list(symbols))
    # flatten for easy table view
    table = []
    for item in out.get("items") or []:
        snap = item.get("snapshot") or {}
        price = snap.get("price") or snap.get("regularMarketPrice") or snap.get("last")
        table.append(
            {
                "symbol": item.get("symbol"),
                "price": price,
                "stub": bool(snap.get("stub")),
                "error": snap.get("error"),
                "at": item.get("at"),
            }
        )
    return {
        "count": len(table),
        "table": table,
        "raw": out,
        "disclaimer": "research_only_not_investment_advice",
        "note": "Best-effort batch snapshot — not a market-data terminal.",
    }
