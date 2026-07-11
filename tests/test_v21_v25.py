"""Tests for v2.1–v2.5 roadmap completion."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_auth_open_and_api_key(monkeypatch):
    monkeypatch.delenv("API_ACCESS_KEY", raising=False)
    monkeypatch.delenv("API_BEARER_TOKEN", raising=False)
    monkeypatch.delenv("OIDC_ISSUER", raising=False)
    from src.auth.plugins import authenticate_request, build_auth_chain
    from src.config import clear_settings_cache

    clear_settings_cache()
    # force open by clearing settings api key
    monkeypatch.setenv("API_ACCESS_KEY", "")
    clear_settings_cache()
    names = [p.name for p in build_auth_chain()]
    assert "open" in names or "api_key" in names

    monkeypatch.setenv("API_ACCESS_KEY", "secret-test-key")
    clear_settings_cache()
    # rebuild chain picks up env via settings
    from src.config import get_settings

    get_settings.cache_clear()
    ctx = authenticate_request(None, "secret-test-key")
    assert ctx.method in {"api_key", "open"}


def test_auth_bearer(monkeypatch):
    monkeypatch.setenv("API_ACCESS_KEY", "")
    monkeypatch.setenv("API_BEARER_TOKEN", "tok123")
    monkeypatch.delenv("OIDC_ISSUER", raising=False)
    from src.auth.base import AuthError
    from src.auth.plugins import authenticate_request
    from src.config import clear_settings_cache

    clear_settings_cache()
    ctx = authenticate_request("Bearer tok123", None)
    assert ctx.method == "bearer"
    try:
        authenticate_request("Bearer wrong", None)
        assert False, "should deny"
    except AuthError:
        pass


def test_memo_search(tmp_path, monkeypatch):
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path))
    from src.config import clear_settings_cache
    from src.ops.memo_search import search_memos
    from src.tools.reports import save_report_file

    clear_settings_cache()
    save_report_file(
        title="cpo memo",
        markdown_body="CPO co-packaged optics chokepoint laser supply chain research",
        mode="full",
        quality={"score": 60},
    )
    hits = search_memos("CPO optics", limit=5)
    assert hits
    assert hits[0]["score"] > 0


def test_scorecard_svg():
    from src.charts.scorecard import charts_from_memo

    md = """
| 节点 | 不可替代 | 集中度 | 杠杆 | 真空 | 拐点 |
| --- | --- | --- | --- | --- | --- |
| ELS | 5 | 4 | 5 | 3 | 3 |
| SOI | 4 | 5 | 4 | 4 | 2 |
"""
    charts = charts_from_memo(md)
    assert charts["nodes"] == 2
    assert "<svg" in charts["scorecard_svg"]


def test_providers_include_hkex():
    from src.providers.base import get_registry

    # reset registry for clean test
    import src.providers.base as base

    base._REGISTRY = None
    names = get_registry().list_providers()
    assert "hkex_news" in names["filings"]
    assert "cn_announcements" in names["filings"]


def test_chart_tools_registered():
    from src.tools.research_tools import all_tools

    names = {t.name for t in all_tools()}
    assert "render_scorecard_chart" in names
    assert "render_price_chart" in names
