"""Load local knowledge maps for optional context injection."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from langchain.tools import tool

ROOT = Path(__file__).resolve().parents[2]
MAPS_DIR = ROOT / "knowledge" / "maps"


@tool(parse_docstring=True)
def list_knowledge_maps() -> str:
    """List available local supply-chain knowledge maps (YAML sketches).

    Returns:
        Newline-separated map filenames under knowledge/maps/.
    """
    if not MAPS_DIR.is_dir():
        return "No knowledge/maps directory found."
    files = sorted(p.name for p in MAPS_DIR.glob("*.yaml"))
    if not files:
        return "No YAML maps found."
    return "Available maps:\n" + "\n".join(f"- {f}" for f in files)


@tool(parse_docstring=True)
def load_knowledge_map(name: str) -> str:
    """Load a local educational supply-chain map by filename or stem.

    Args:
        name: e.g. "cpo_ai_interconnect" or "cpo_ai_interconnect.yaml"

    Returns:
        YAML/text content of the map, or an error string.
    """
    raw = name.strip()
    if not raw.endswith(".yaml"):
        raw = f"{raw}.yaml"
    # Prevent path traversal
    path = (MAPS_DIR / Path(raw).name).resolve()
    if not str(path).startswith(str(MAPS_DIR.resolve())):
        return "Invalid map name."
    if not path.is_file():
        available = ", ".join(p.stem for p in MAPS_DIR.glob("*.yaml")) or "(none)"
        return f"Map not found: {raw}. Available: {available}"
    text = path.read_text(encoding="utf-8")
    return (
        f"# Knowledge map: {path.name}\n"
        f"# Educational sketch only — verify with live sources.\n\n{text}"
    )


def parse_map(name: str) -> dict[str, Any] | None:
    """Programmatic YAML load for tests / future UI."""
    path = MAPS_DIR / (name if name.endswith(".yaml") else f"{name}.yaml")
    if not path.is_file():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8"))
