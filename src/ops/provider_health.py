"""Provider health probes — best-effort offline-friendly checks."""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any

from src.providers.base import get_registry


def probe_providers(*, live: bool = False) -> dict[str, Any]:
    """Check provider registration; optional light live probes (network)."""
    reg = get_registry()
    listing = reg.list_providers()
    checks: list[dict[str, Any]] = []

    for kind, names in listing.items():
        for name in names:
            row: dict[str, Any] = {
                "kind": kind,
                "name": name,
                "registered": True,
                "live": None,
            }
            if live:
                t0 = time.time()
                try:
                    if kind == "filings":
                        prov = reg.filings(name)
                        if prov and hasattr(prov, "search_company"):
                            hits = prov.search_company("AAPL" if "sec" in name else "600519")
                            row["live"] = {
                                "ok": True,
                                "latency_ms": int((time.time() - t0) * 1000),
                                "sample_n": len(hits) if isinstance(hits, list) else 1,
                            }
                        else:
                            row["live"] = {"ok": False, "error": "no search_company"}
                    elif kind == "market":
                        prov = reg.market(name)
                        if prov and hasattr(prov, "quote"):
                            q = prov.quote("AAPL")
                            row["live"] = {
                                "ok": bool(q),
                                "latency_ms": int((time.time() - t0) * 1000),
                                "keys": list(q.keys())[:8] if isinstance(q, dict) else [],
                            }
                        else:
                            row["live"] = {"ok": False, "error": "no quote"}
                except Exception as exc:  # noqa: BLE001
                    row["live"] = {
                        "ok": False,
                        "error": str(exc)[:200],
                        "latency_ms": int((time.time() - t0) * 1000),
                    }
            checks.append(row)

    return {
        "at": datetime.now().isoformat(timespec="seconds"),
        "providers": listing,
        "checks": checks,
        "live_probed": live,
        "disclaimer": "research_only_not_investment_advice",
    }
