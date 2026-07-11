"""Auto-discover optional plugins under ./plugins/."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


def plugins_dir() -> Path:
    # project root / plugins
    return Path(__file__).resolve().parents[2] / "plugins"


def list_plugin_files() -> list[dict[str, str]]:
    d = plugins_dir()
    if not d.is_dir():
        return []
    items = []
    for p in sorted(d.glob("*.py")):
        if p.name.startswith("_"):
            continue
        items.append({"name": p.stem, "path": str(p.resolve())})
    return items


def load_plugin(name: str) -> dict[str, Any]:
    """Load a plugin module by stem name. Returns module summary."""
    d = plugins_dir()
    path = d / f"{name}.py"
    if not path.is_file():
        return {"error": f"plugin not found: {name}"}
    mod_name = f"chokepoint_plugin_{name}"
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if not spec or not spec.loader:
        return {"error": f"cannot load: {name}"}
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    meta = {
        "name": name,
        "path": str(path.resolve()),
        "attrs": [a for a in dir(mod) if not a.startswith("_")],
    }
    # common hooks
    for hook in ("PLUGIN_NAME", "PROVIDER_ID", "register", "get_provider"):
        if hasattr(mod, hook):
            val = getattr(mod, hook)
            meta[hook] = val if not callable(val) else f"<callable {hook}>"
    return meta


def load_all_plugins() -> list[dict[str, Any]]:
    results = []
    for item in list_plugin_files():
        results.append(load_plugin(item["name"]))
    return results
