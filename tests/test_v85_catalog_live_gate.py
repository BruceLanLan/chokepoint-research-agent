"""v8.5 — catalog filters + live research cost gate."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api import app
from src.ops.catalog import catalog_facets, filter_catalog
from src.ops.live_safety import assert_live_research_allowed
from src.tools.reports import save_report_file


def test_filter_catalog_by_vertical(tmp_path, monkeypatch):
    from src.config import clear_settings_cache, get_settings

    clear_settings_cache()
    s = get_settings()
    monkeypatch.setattr(s, "reports_dir", tmp_path)
    save_report_file("a", "body a", vertical="cpo_optics", skill="semiconductor", mode="chokepoint_fast")
    save_report_file("b", "body b", vertical="hbm_packaging", skill="semiconductor", mode="full")
    save_report_file("c", "body c", mode="risk_only")

    only_cpo = filter_catalog(vertical_id="cpo_optics", limit=20)
    assert len(only_cpo) == 1
    assert only_cpo[0]["vertical_id"] == "cpo_optics"

    semi = filter_catalog(skill="semiconductor", limit=20)
    assert len(semi) == 2

    facets = catalog_facets()
    ids = {v["id"] for v in facets["verticals"]}
    assert "cpo_optics" in ids
    assert "hbm_packaging" in ids


def test_reports_api_filters(tmp_path, monkeypatch):
    from src.config import clear_settings_cache, get_settings

    clear_settings_cache()
    monkeypatch.setattr(get_settings(), "reports_dir", tmp_path)
    save_report_file("x", "memo", vertical="power_cooling", skill="ai_infra")
    c = TestClient(app)
    r = c.get("/reports", params={"vertical_id": "power_cooling"})
    assert r.status_code == 200
    body = r.json()
    assert body["count"] >= 1
    assert all(i.get("vertical_id") == "power_cooling" for i in body["items"])
    assert "facets" in body
    r2 = c.get("/reports/facets")
    assert r2.status_code == 200
    assert "verticals" in r2.json()


def test_live_research_blocked_without_accept(monkeypatch):
    monkeypatch.delenv("CHOKEPOINT_I_ACCEPT_LIVE_COSTS", raising=False)
    with pytest.raises(ValueError, match="blocked|accept|mock"):
        assert_live_research_allowed(flag=False)
    # flag alone is enough for cost accept; model key may still fail
    try:
        assert_live_research_allowed(flag=True, require_model_key=False)
    except ValueError:
        pytest.fail("flag=True with require_model_key=False should pass")


def test_api_live_research_returns_402_without_accept(monkeypatch):
    monkeypatch.delenv("CHOKEPOINT_I_ACCEPT_LIVE_COSTS", raising=False)
    c = TestClient(app)
    r = c.post(
        "/research",
        json={
            "question": "Map CPO chokepoints briefly",
            "mock": False,
            "i_accept_live_costs": False,
            "save_report": False,
            "export": False,
        },
    )
    assert r.status_code == 402
    assert "mock" in str(r.json().get("detail", "")).lower() or "accept" in str(
        r.json().get("detail", "")
    ).lower()


def test_api_mock_research_still_works_without_accept(monkeypatch):
    monkeypatch.delenv("CHOKEPOINT_I_ACCEPT_LIVE_COSTS", raising=False)
    c = TestClient(app)
    r = c.post(
        "/research",
        json={
            "question": "vertical",
            "vertical": "cpo_optics",
            "mock": True,
            "save_report": False,
            "export": False,
        },
    )
    assert r.status_code == 200
    assert r.json().get("report")
