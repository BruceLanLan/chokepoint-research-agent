"""Audit Quality — thin shim over ProEngine (YAML-backed).

Version theme: v5.41.0
Research process helper only — not investment advice.
"""
from __future__ import annotations
from typing import Any
from src.ops.pro.engine import ProEngine

_ENGINE = ProEngine("audit_quality")
TITLE = _ENGINE.title
VERSION_THEME = _ENGINE.version_theme
DESCRIPTION = _ENGINE.description

def run(**kwargs: Any) -> dict[str, Any]:
    return _ENGINE.run(**kwargs)

def analyze(**kwargs: Any) -> dict[str, Any]:
    return _ENGINE.analyze(**kwargs)

def add_entry(**kwargs: Any) -> dict[str, Any]:
    return _ENGINE.add_entry(**kwargs)

def list_entries(**kwargs: Any) -> list:
    return _ENGINE.list_entries(**kwargs)

def summarize(**kwargs: Any) -> dict[str, Any]:
    return _ENGINE.summarize(**kwargs)
