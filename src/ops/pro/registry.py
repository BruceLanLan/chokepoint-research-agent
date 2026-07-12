"""Registry for pro maturity-train modules."""

from __future__ import annotations

import importlib
from typing import Any

from src.ops.pro import PRO_MODULE_IDS


def list_modules() -> list[dict[str, Any]]:
    items = []
    for mid in PRO_MODULE_IDS:
        mod = importlib.import_module(f"src.ops.pro.{mid}")
        items.append(
            {
                "id": mid,
                "title": getattr(mod, "TITLE", mid),
                "version_theme": getattr(mod, "VERSION_THEME", ""),
                "description": getattr(mod, "DESCRIPTION", ""),
                "disclaimer": "research_only_not_investment_advice",
            }
        )
    return items


def invoke_module(module_id: str, **kwargs: Any) -> dict[str, Any]:
    if module_id not in PRO_MODULE_IDS:
        return {"error": f"unknown module: {module_id}", "known": list(PRO_MODULE_IDS)}
    mod = importlib.import_module(f"src.ops.pro.{module_id}")
    if hasattr(mod, "run"):
        out = mod.run(**kwargs)
    elif hasattr(mod, "analyze"):
        out = mod.analyze(**kwargs)
    else:
        out = {"error": "no run/analyze"}
    if isinstance(out, dict):
        out.setdefault("module", module_id)
        out.setdefault("disclaimer", "research_only_not_investment_advice")
    return out
