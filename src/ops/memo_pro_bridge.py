"""Bridge saved memos into pro-module analyze + optional persist."""

from __future__ import annotations

from typing import Any

from src.ops.pro.suite import run_full_suite
from src.ops.pro.registry import invoke_module
from src.tools.reports import read_report


def analyze_memo_with_pro(
    report_name: str,
    *,
    modules: list[str] | None = None,
    persist: bool = False,
    symbol: str = "",
) -> dict[str, Any]:
    """Run pro analyze on a saved memo (all modules or a subset)."""
    body = read_report(report_name)
    if body is None:
        return {"error": f"not found: {report_name}"}

    if modules:
        results = []
        ok = 0
        for mid in modules:
            out = invoke_module(
                mid,
                action="analyze",
                text=body,
                title=report_name,
                symbol=symbol,
            )
            if out.get("gate_ok"):
                ok += 1
            if persist and not out.get("error"):
                invoke_module(
                    mid,
                    action="add",
                    title=f"from:{report_name}",
                    body=body[:2000],
                    symbol=symbol,
                )
            results.append(
                {
                    "module": mid,
                    "gate_ok": out.get("gate_ok"),
                    "checklist_passed": out.get("checklist_passed"),
                    "density": (out.get("score") or {}).get("density_score"),
                    "flags": (out.get("score") or {}).get("flags"),
                }
            )
        return {
            "report": report_name,
            "mode": "subset",
            "modules": len(results),
            "gates_ok": ok,
            "results": results,
            "persisted": persist,
            "disclaimer": "research_only_not_investment_advice",
        }

    suite = run_full_suite(text=body, symbol=symbol, title=report_name)
    if persist:
        # persist only modules that passed gate to avoid noise
        for r in suite.get("results") or []:
            if r.get("gate_ok"):
                invoke_module(
                    r["module"],
                    action="add",
                    title=f"from:{report_name}",
                    body=body[:1500],
                    symbol=symbol,
                )
    return {
        "report": report_name,
        "mode": "full_suite",
        "suite": suite,
        "persisted": persist,
        "disclaimer": "research_only_not_investment_advice",
    }
