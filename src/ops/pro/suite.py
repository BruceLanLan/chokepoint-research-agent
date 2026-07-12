"""Run offline analyze across all pro maturity-train modules."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.ops.pro import PRO_MODULE_IDS
from src.ops.pro.registry import invoke_module, list_modules


def run_full_suite(*, text: str = "", symbol: str = "", title: str = "suite") -> dict[str, Any]:
    """Analyze text through every pro module; aggregate gate stats."""
    results = []
    gates_ok = 0
    for mid in PRO_MODULE_IDS:
        out = invoke_module(
            mid,
            action="analyze",
            text=text,
            symbol=symbol,
            title=title,
        )
        ok = bool(out.get("gate_ok"))
        if ok:
            gates_ok += 1
        results.append(
            {
                "module": mid,
                "version_theme": out.get("version_theme"),
                "gate_ok": ok,
                "checklist_passed": out.get("checklist_passed"),
                "density": (out.get("score") or {}).get("density_score"),
                "flags": (out.get("score") or {}).get("flags"),
            }
        )
    n = len(results)
    return {
        "modules": n,
        "gates_ok": gates_ok,
        "gate_rate": round(gates_ok / n, 3) if n else None,
        "catalog_size": len(list_modules()),
        "results": results,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "disclaimer": "research_only_not_investment_advice",
        "note": "Offline process suite — not investment advice or a trading signal.",
    }


def suite_markdown(text: str = "", symbol: str = "") -> str:
    s = run_full_suite(text=text, symbol=symbol)
    lines = [
        "# Pro module suite report\n\n",
        f"modules: {s['modules']}  gates_ok: {s['gates_ok']}  rate: {s['gate_rate']}\n\n",
        "> Research only — not investment advice.\n\n",
    ]
    for r in s["results"]:
        mark = "OK" if r["gate_ok"] else "FAIL"
        lines.append(
            f"- [{mark}] `{r['module']}` {r.get('version_theme')} "
            f"checklist={r.get('checklist_passed')} dens={r.get('density')}\n"
        )
    return "".join(lines)
