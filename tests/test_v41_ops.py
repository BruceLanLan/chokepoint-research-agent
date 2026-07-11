"""v4.1 tests: citation network, lineage, plan, provider health, coverage svg."""

from __future__ import annotations

from pathlib import Path

import pytest

MD = """# Memo

## 研究结论
Node A is a chokepoint.

## 风险
kill criteria: copper wins

## 来源
- https://www.sec.gov/cgi-bin/browse-edgar
- https://www.reuters.com/example
- https://www.sec.gov/Archives/edgar/data/1
"""


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    reports = tmp_path / "reports"
    reports.mkdir()
    (tmp_path / "data").mkdir()
    monkeypatch.setenv("REPORTS_DIR", str(reports))
    from src.config import clear_settings_cache

    clear_settings_cache()
    yield tmp_path
    clear_settings_cache()


def test_citation_network(ws):
    from src.config import get_settings
    from src.ops.citation_network import build_citation_network, citation_mermaid

    p = Path(get_settings().reports_dir) / "c1.md"
    p.write_text(MD, encoding="utf-8")
    p2 = Path(get_settings().reports_dir) / "c2.md"
    p2.write_text(MD + "\nhttps://www.reuters.com/other\n", encoding="utf-8")
    g = build_citation_network()
    assert g["stats"]["reports_scanned"] >= 2
    assert g["stats"]["unique_domains"] >= 1
    mm = citation_mermaid()
    assert "flowchart" in mm


def test_lineage(ws):
    from src.ops.lineage import create_chain, lineage_for, link_reports, list_lineage

    link_reports("a.md", "b.md", note="follow-up")
    chain = create_chain("CPO series", ["a.md", "b.md", "c.md"])
    assert chain["id"]
    data = list_lineage()
    assert len(data["links"]) >= 1
    assert lineage_for("b.md")["parents"]


def test_research_plan(ws):
    from src.ops.research_plan import build_research_plan

    plan = build_research_plan("AI CPO racks", skill="semiconductor")
    assert plan["topic"]
    assert len(plan["steps"]) >= 5
    assert plan["seed_question"]
    assert "disclaimer" in plan


def test_provider_health_offline(ws):
    from src.ops.provider_health import probe_providers

    h = probe_providers(live=False)
    assert "filings" in h["providers"] or h["checks"]
    assert h["live_probed"] is False


def test_coverage_svg(ws):
    from src.charts.coverage import coverage_heat_svg
    from src.ops.watchlist import add_item

    add_item(symbol="NVDA", name="NVIDIA", priority="high")
    svg = coverage_heat_svg()
    assert svg.startswith("<svg")
    assert "Coverage heat" in svg
