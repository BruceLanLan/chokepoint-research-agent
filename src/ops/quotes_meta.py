"""Document quote stream capabilities and limits (research utility, not a terminal)."""

from __future__ import annotations

from typing import Any


def quotes_capabilities() -> dict[str, Any]:
    return {
        "sse": {
            "path": "/quotes/stream",
            "params": ["symbol", "interval"],
            "interval_seconds": {"min": 2, "max": 60, "default": 5},
            "max_events_per_connection": 30,
            "mechanism": "server polls provider on interval (not exchange push)",
        },
        "websocket": {
            "path": "/ws/quotes",
            "init_message": {"symbol": "AAPL", "interval": 5},
            "max_messages": 40,
            "mechanism": "client WebSocket; server still polls under the hood",
        },
        "limitations": [
            "Not a professional market-data terminal",
            "Best-effort public/Yahoo-style snapshots; delays and gaps expected",
            "No guaranteed uptime, tick completeness, or regulatory-grade feed",
            "Research utility only — not investment advice",
        ],
        "disclaimer": "research_only_not_investment_advice",
    }
