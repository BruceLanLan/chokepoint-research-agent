"""Local quote snapshot cache for multi-symbol research monitoring (best-effort)."""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from src.config import get_settings


def _path() -> Path:
    base = Path(get_settings().reports_dir).parent / "data"
    base.mkdir(parents=True, exist_ok=True)
    return base / "quote_history.jsonl"


def append_quote(
    symbol: str,
    snapshot: dict[str, Any],
    *,
    source: str = "manual",
) -> dict[str, Any]:
    snap = dict(snapshot or {})
    # never present offline stubs as silent real prices
    if snap.get("stub") or snap.get("error"):
        snap.setdefault("display_warning", "STUB_OR_ERROR_NOT_LIVE_PRICE")
    row = {
        "at": datetime.now().isoformat(timespec="seconds"),
        "ts": time.time(),
        "symbol": str(symbol).upper().strip(),
        "source": source,
        "snapshot": snap,
        "is_stub": bool(snap.get("stub") or snap.get("error")),
    }
    with _path().open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def load_history(
    symbol: str | None = None,
    *,
    limit: int = 200,
) -> list[dict[str, Any]]:
    p = _path()
    if not p.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in p.read_text(encoding="utf-8").strip().splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if symbol and str(row.get("symbol") or "").upper() != symbol.upper():
            continue
        rows.append(row)
    return rows[-max(1, min(limit, 2000)) :]


def history_summary(symbol: str | None = None) -> dict[str, Any]:
    rows = load_history(symbol, limit=500)
    by_sym: dict[str, int] = {}
    for r in rows:
        s = r.get("symbol") or "?"
        by_sym[s] = by_sym.get(s, 0) + 1
    return {
        "count": len(rows),
        "by_symbol": by_sym,
        "latest": rows[-5:] if rows else [],
        "disclaimer": "research_only_not_investment_advice",
        "note": "Local cache of snapshots — not a market-data terminal.",
    }


def refresh_symbols(
    symbols: list[str],
    *,
    fetch_fn: Callable[[str], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Fetch and cache quotes. fetch_fn(symbol)->dict; default uses market snapshot tool offline-safe mock if fails."""
    results = []
    for raw in symbols:
        sym = str(raw).strip().upper()
        if not sym:
            continue
        snap: dict[str, Any]
        try:
            if fetch_fn:
                snap = fetch_fn(sym)
            else:
                snap = _default_fetch(sym)
        except Exception as exc:  # noqa: BLE001
            snap = {"error": str(exc)[:200], "symbol": sym}
        row = append_quote(sym, snap, source="refresh")
        results.append(row)
    return {
        "refreshed": len(results),
        "items": results,
        "disclaimer": "research_only_not_investment_advice",
    }


def _default_fetch(symbol: str) -> dict[str, Any]:
    try:
        from src.tools.research_tools import get_market_snapshot

        raw = get_market_snapshot.invoke({"symbol": symbol})
        if isinstance(raw, str):
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return {"raw": raw[:500], "symbol": symbol}
        return dict(raw) if isinstance(raw, dict) else {"value": raw, "symbol": symbol}
    except Exception as exc:  # noqa: BLE001
        # offline-friendly stub so workstation never hard-fails
        return {
            "symbol": symbol,
            "stub": True,
            "error": str(exc)[:160],
            "note": "provider unavailable — stub row for research cache",
        }
