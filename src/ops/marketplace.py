"""Local plugin / skill / template marketplace index (filesystem only, no remote install)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.ops.knowledge_maps import list_maps
from src.ops.plugin_catalog import plugin_catalog
from src.ops.templates import list_templates
from src.plugins.loader import list_plugin_files, plugins_dir
from src.skills.loader import list_skill_packs

ROOT = Path(__file__).resolve().parents[2]


def marketplace_index() -> dict[str, Any]:
    """Unified local discovery surface for extensions."""
    cat = plugin_catalog()
    listings: list[dict[str, Any]] = []

    for p in list_plugin_files():
        listings.append(
            {
                "kind": "plugin",
                "id": p["name"],
                "name": p["name"],
                "path": p["path"],
                "install": f"Drop/keep under ./plugins/{p['name']}.py; python main.py plugins --load {p['name']}",
                "status": "local",
            }
        )
    for s in list_skill_packs():
        listings.append(
            {
                "kind": "skill_pack",
                "id": s.get("id"),
                "name": s.get("name"),
                "description": s.get("description"),
                "install": f"skills/packs/{s.get('id')}.yaml — use --skill {s.get('id')}",
                "status": "bundled",
            }
        )
    for t in list_templates():
        listings.append(
            {
                "kind": "template",
                "id": t.get("id"),
                "name": t.get("name"),
                "description": t.get("description"),
                "install": f"templates/research/{t.get('id')}.yaml",
                "status": "bundled",
            }
        )
    for m in list_maps():
        listings.append(
            {
                "kind": "knowledge_map",
                "id": m.get("id"),
                "name": m.get("system"),
                "install": f"knowledge/maps/{m.get('id')}.yaml — python main.py maps {m.get('id')} --seed",
                "status": "bundled",
            }
        )

    readme = ROOT / "docs" / "PLUGIN_SDK.md"
    return {
        "title": "Local extension marketplace",
        "status": "local_only",
        "note": (
            "No remote package install. Browse bundled + ./plugins/ items. "
            "Third-party: copy .py into plugins/ or YAML into skills/packs/."
        ),
        "counts": {
            "plugins": len(list_plugin_files()),
            "skill_packs": len(list_skill_packs()),
            "templates": len(list_templates()),
            "knowledge_maps": len(list_maps()),
            "listings": len(listings),
        },
        "plugins_dir": str(plugins_dir()),
        "sdk_docs": str(readme) if readme.is_file() else None,
        "listings": listings,
        "catalog": cat,
        "disclaimer": "research_only_not_investment_advice",
    }


def marketplace_search(query: str) -> dict[str, Any]:
    q = (query or "").strip().lower()
    idx = marketplace_index()
    if not q:
        return idx
    hits = []
    for item in idx.get("listings") or []:
        blob = " ".join(
            str(item.get(k) or "") for k in ("kind", "id", "name", "description", "install")
        ).lower()
        if q in blob:
            hits.append(item)
    return {
        "query": query,
        "hits": hits,
        "count": len(hits),
        "disclaimer": "research_only_not_investment_advice",
    }
