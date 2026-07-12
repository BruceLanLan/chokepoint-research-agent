"""v8.2 — user journey / hardening tests from 20-round review loop."""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.api import app
from src.ops.research_plan import build_research_plan
from src.tools.research_tools import web_search


def test_template_render_accepts_vars_object():
    c = TestClient(app)
    r = c.post(
        "/templates/chokepoint_map/render",
        json={"vars": {"system": "AI rack CPO", "context": ""}},
    )
    assert r.status_code == 200
    assert "AI rack CPO" in r.json().get("question", "")
    r2 = c.post("/templates/chokepoint_map/render", json={"vars": {}})
    assert r2.status_code == 200


def test_web_search_soft_fail_without_tavily(monkeypatch):
    from src.config import get_settings

    s = get_settings()
    monkeypatch.setattr(s, "tavily_api_key", "")
    # clear settings cache if any
    from src.config import clear_settings_cache

    clear_settings_cache()
    monkeypatch.setenv("TAVILY_API_KEY", "")
    clear_settings_cache()
    out = web_search.invoke({"query": "CPO optics"})
    assert "TAVILY" in out or "unavailable" in out.lower()


def test_mock_research_offline():
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
    body = r.json()
    assert body.get("report")
    assert body.get("quality", {}).get("mock") is True or "mock" in str(body.get("cost"))


def test_mock_research_vertical_only():
    c = TestClient(app)
    r = c.post(
        "/research",
        json={
            "question": "",
            "vertical": "hbm_packaging",
            "mock": True,
            "save_report": False,
            "export": False,
        },
    )
    assert r.status_code == 200
    assert "HBM" in r.json().get("question", "") or "hbm" in r.json().get("report", "").lower()


def test_research_empty_without_scaffold_422():
    c = TestClient(app)
    r = c.post(
        "/research",
        json={"question": "", "mock": True, "save_report": False, "export": False},
    )
    assert r.status_code == 422


def test_plan_suggests_vertical():
    plan = build_research_plan("CPO ELS silicon photonics for AI GPU racks")
    assert plan.get("vertical") == "cpo_optics" or (
        plan.get("suggested_verticals")
        and plan["suggested_verticals"][0]["id"] == "cpo_optics"
    )
    assert plan.get("seed_question")


def test_thesis_process_warning_without_kills():
    c = TestClient(app)
    r = c.post(
        "/theses",
        json={"title": "journey thesis", "statement": "something happens by 2030"},
    )
    assert r.status_code == 200
    assert r.json().get("process_warning")


def test_mock_stream_research():
    c = TestClient(app)
    with c.stream(
        "POST",
        "/research/stream",
        json={
            "question": "mock stream",
            "mock": True,
            "save_report": False,
            "export": False,
        },
    ) as r:
        assert r.status_code == 200
        raw = r.read().decode()
    assert "final" in raw or "mock" in raw.lower()


def test_demo_journey_api():
    c = TestClient(app)
    r = c.post("/demo-journey", json={"vertical": "cpo_optics", "save": False})
    assert r.status_code == 200
    body = r.json()
    assert body.get("vertical") == "cpo_optics"
    assert len(body.get("steps") or []) >= 4
