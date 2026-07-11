"""Yahoo Finance market provider wrapper (best-effort)."""

from __future__ import annotations

import json
from typing import Any

from src.tools.research_tools import get_market_snapshot, normalize_symbol


class YahooMarketProvider:
    name = "yahoo"

    def quote(self, symbol: str) -> dict[str, Any]:
        raw = get_market_snapshot.invoke({"symbol": normalize_symbol(symbol)})
        try:
            return json.loads(raw) if isinstance(raw, str) and raw.strip().startswith("{") else {"raw": raw}
        except json.JSONDecodeError:
            return {"raw": raw, "symbol": symbol}
