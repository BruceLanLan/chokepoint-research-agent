"""Aggregate dashboard across all 50 pro research-ops modules."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.ops.pro import PRO_MODULE_IDS
from src.ops.pro.registry import invoke_module


def pro_dashboard(*, limit_per_module: int = 20) -> dict[str, Any]:
    """Summarize entry counts / density / flags across pro modules."""
    rows = []
    total_entries = 0
    flag_totals: dict[str, int] = {}
    dens_all: list[float] = []
    for mid in PRO_MODULE_IDS:
        s = invoke_module(mid, action="summarize", limit=limit_per_module)
        n = int(s.get("count") or 0)
        total_entries += n
        avg = s.get("avg_density")
        if isinstance(avg, (int, float)):
            dens_all.append(float(avg))
        for f, c in (s.get("flag_counts") or {}).items():
            flag_totals[f] = flag_totals.get(f, 0) + int(c)
        rows.append(
            {
                "module": mid,
                "version_theme": s.get("version_theme"),
                "count": n,
                "avg_density": avg,
                "symbols": len(s.get("symbols") or {}),
                "flags": s.get("flag_counts") or {},
            }
        )
    rows.sort(key=lambda r: -r["count"])
    active = [r for r in rows if r["count"] > 0]
    return {
        "modules": len(rows),
        "active_modules": len(active),
        "total_entries": total_entries,
        "avg_density_global": round(sum(dens_all) / len(dens_all), 1) if dens_all else None,
        "flag_totals": flag_totals,
        "top_modules": rows[:15],
        "empty_modules": [r["module"] for r in rows if r["count"] == 0][:20],
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "disclaimer": "research_only_not_investment_advice",
        "note": "Ops activity dashboard — not portfolio performance.",
    }
