"""Local plugin catalog — discover plugins + document install surface."""

from __future__ import annotations

from typing import Any

from src.plugins.loader import list_plugin_files, load_plugin
from src.providers.base import get_registry
from src.skills.loader import list_skill_packs


def plugin_catalog() -> dict[str, Any]:
    files = list_plugin_files()
    loaded = []
    for f in files:
        meta = load_plugin(f["name"])
        loaded.append(
            {
                "name": f["name"],
                "path": f["path"],
                "attrs": meta.get("attrs") if "error" not in meta else [],
                "error": meta.get("error"),
            }
        )
    reg = get_registry().list_providers()
    return {
        "plugins_dir": loaded,
        "builtin_providers": reg,
        "skill_packs": list_skill_packs(),
        "install_notes": [
            "Drop a .py into ./plugins/ implementing search_company/recent_filings or quote.",
            "Register at runtime via get_registry().register_filings(...) / register_market(...).",
            "Skill packs: YAML under skills/packs/*.yaml",
            "Auth plugins: env API_ACCESS_KEY / API_BEARER_TOKEN / OIDC_*",
        ],
        "marketplace": {
            "status": "local_only",
            "note": "No remote marketplace yet — catalog is local filesystem discovery.",
        },
        "disclaimer": "research_only_not_investment_advice",
    }
