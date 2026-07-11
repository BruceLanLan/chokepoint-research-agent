"""v4.5: digest, map compare, hypotheses, frontmatter enrich."""

from __future__ import annotations

from pathlib import Path

import pytest

MD = """# Test

## 研究结论
CPO node test

## 风险
Kill criteria: x

## 来源
https://www.sec.gov/x
"""


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "reports").mkdir()
    (tmp_path / "data").mkdir()
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path / "reports"))
    from src.config import clear_settings_cache

    clear_settings_cache()
    yield tmp_path
    clear_settings_cache()


def test_digest(ws):
    from src.ops.digest import build_workspace_digest
    from src.ops.theses import add_thesis
    from src.ops.watchlist import add_item

    add_item(symbol="NVDA", name="NVIDIA", priority="high")
    add_thesis(title="t", statement="s", status="active")
    out = build_workspace_digest(save=True)
    assert "Workspace Research Digest" in out["markdown"]
    assert out["saved_path"]


def test_compare_maps():
    from src.ops.map_compare import compare_maps

    r = compare_maps("cpo_ai_interconnect", "optical_pluggables")
    assert "jaccard" in r
    assert r["a"]["id"] == "cpo_ai_interconnect"


def test_hypotheses(ws):
    from src.ops.hypotheses import add_hypothesis, list_hypotheses, promote_to_thesis
    from src.ops.theses import list_theses

    h = add_hypothesis("ELS remains sole-source for 2 years", system="CPO")
    assert h["id"]
    assert list_hypotheses()
    out = promote_to_thesis(h["id"])
    assert out["thesis"]["id"]
    assert list_theses()


def test_enrich_frontmatter(ws):
    from src.config import get_settings
    from src.ops.report_frontmatter import enrich_report_frontmatter

    p = Path(get_settings().reports_dir) / "e.md"
    p.write_text(MD, encoding="utf-8")
    out = enrich_report_frontmatter("e.md")
    assert out["written"]
    body = p.read_text(encoding="utf-8")
    assert "tags:" in body
    assert "quality_score:" in body
