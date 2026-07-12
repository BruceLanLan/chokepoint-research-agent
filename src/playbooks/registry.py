"""Playbook registry."""
from __future__ import annotations
import importlib
from pathlib import Path
from typing import Any

def list_playbooks() -> list[str]:
    d = Path(__file__).parent
    return sorted(p.stem for p in d.glob("*.py") if p.stem not in {"__init__", "registry"})

def get_playbook(pid: str) -> dict[str, Any]:
    mod = importlib.import_module(f"src.playbooks.{pid}")
    return mod.run()
