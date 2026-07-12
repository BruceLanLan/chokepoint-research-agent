"""v6.1–v6.2: desk, pro dashboard, memo bridge, glossary, quote chart."""

from __future__ import annotations

from pathlib import Path

import pytest

MD = """# Memo

## 研究结论
System chokepoint laser node.

## 风险
Kill criteria: multi-source

## 来源
https://example.com/a

仅供研究学习，不构成投资建议。
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


def test_pro_dashboard_and_export(ws):
    from src.ops.pro.registry import invoke_module
    from src.ops.pro_dashboard import pro_dashboard
    from src.ops.pro_pack_export import export_pro_pack

    invoke_module(
        "risk_matrix",
        action="add",
        title="t",
        body="chokepoint kill https://x.com",
        symbol="T",
    )
    d = pro_dashboard()
    assert d["modules"] == 50
    assert d["total_entries"] >= 1
    pack = export_pro_pack()
    assert Path(pack["path"]).is_file()


def test_memo_pro_bridge(ws):
    from src.config import get_settings
    from src.ops.memo_pro_bridge import analyze_memo_with_pro

    p = Path(get_settings().reports_dir) / "m.md"
    p.write_text(MD, encoding="utf-8")
    out = analyze_memo_with_pro("m.md", modules=["risk_matrix", "moat_score"])
    assert out["modules"] == 2
    assert "results" in out


def test_glossary_and_desk(ws):
    from src.ops.glossary_search import list_glossary_terms, search_glossary
    from src.ops.research_desk import research_desk_status

    terms = list_glossary_terms()
    assert len(terms) > 50
    hits = search_glossary("chokepoint")
    assert hits["count"] >= 1
    desk = research_desk_status()
    assert desk["version"]
    assert desk["catalog"]["playbooks"] >= 10
    assert desk["pro_ops"]["modules"] == 50


def test_quote_history_svg(ws):
    from src.charts.quote_history import quote_history_svg
    from src.ops.quote_cache import refresh_symbols

    refresh_symbols(["ZZZ"], fetch_fn=lambda s: {"symbol": s, "price": 10.0})
    refresh_symbols(["ZZZ"], fetch_fn=lambda s: {"symbol": s, "price": 11.5})
    svg = quote_history_svg("ZZZ")
    assert svg.startswith("<svg")
    assert "polyline" in svg or "Need" in svg


def test_multi_quotes(ws):
    from src.ops.multi_quotes import multi_quote_snapshot
    from src.ops.quote_cache import refresh_symbols

    # prime with stub fetch via multi path using real refresh (may stub)
    out = multi_quote_snapshot(["AAA", "BBB"])
    assert out["count"] == 2
    assert len(out["table"]) == 2
