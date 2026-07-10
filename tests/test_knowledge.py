"""Knowledge map tools."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_list_and_load_maps():
    from src.tools.knowledge import list_knowledge_maps, load_knowledge_map, parse_map

    listing = list_knowledge_maps.invoke({})
    assert "cpo_ai_interconnect" in listing

    body = load_knowledge_map.invoke({"name": "cpo_ai_interconnect"})
    assert "CPO" in body or "cpo" in body.lower()
    assert "Educational" in body or "educational" in body.lower() or "sketch" in body.lower()

    data = parse_map("cpo_ai_interconnect")
    assert data is not None
    assert "layers" in data


def test_path_traversal_blocked():
    from src.tools.knowledge import load_knowledge_map

    out = load_knowledge_map.invoke({"name": "../../../etc/passwd"})
    assert "not found" in out.lower() or "Invalid" in out or "Available" in out
