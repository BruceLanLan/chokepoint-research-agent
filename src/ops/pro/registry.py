"""Registry for pro maturity-train modules (YAML + ProEngine)."""

from __future__ import annotations

from typing import Any

from src.ops.pro import PRO_MODULE_IDS
from src.ops.pro.engine import ProEngine, list_spec_ids, load_spec


def list_modules() -> list[dict[str, Any]]:
    items = []
    for mid in PRO_MODULE_IDS:
        spec = load_spec(mid)
        items.append(
            {
                "id": mid,
                "title": spec.get("title") or mid,
                "version_theme": spec.get("version_theme") or "",
                "description": spec.get("description") or "",
                "has_yaml": mid in list_spec_ids(),
                "disclaimer": "research_only_not_investment_advice",
            }
        )
    return items


def invoke_module(module_id: str, **kwargs: Any) -> dict[str, Any]:
    if module_id not in PRO_MODULE_IDS:
        return {"error": f"unknown module: {module_id}", "known": list(PRO_MODULE_IDS)}
    out = ProEngine(module_id).run(**kwargs)
    if isinstance(out, dict):
        out.setdefault("module", module_id)
        out.setdefault("disclaimer", "research_only_not_investment_advice")
    return out
