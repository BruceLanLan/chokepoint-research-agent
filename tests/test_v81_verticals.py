"""v8.1 — deep vertical packs wired into desk / suite / scaffold."""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.api import app
from src.ops.pro.suite import run_suite
from src.ops.pro.verticals import (
    list_verticals,
    load_vertical,
    scaffold_research_question,
    suggest_vertical,
    vertical_prompt_suffix,
)
from src.ops.research_desk import research_desk_status


def test_list_five_verticals():
    items = list_verticals()
    assert len(items) >= 5
    ids = {i["id"] for i in items}
    assert "cpo_optics" in ids
    assert "hbm_packaging" in ids


def test_load_cpo_has_depth():
    v = load_vertical("cpo_optics")
    assert v is not None
    assert v.get("physical_nodes")
    assert v.get("kill_criteria")
    assert v.get("modules")


def test_prompt_suffix_and_scaffold():
    s = vertical_prompt_suffix("cpo_optics")
    assert "CPO" in s or "cpo" in s.lower()
    assert "Kill" in s or "kill" in s.lower()
    sc = scaffold_research_question("cpo_optics")
    assert "question" in sc
    assert "CPO" in sc["question"] or "cpo" in sc["question"].lower()
    assert sc.get("suggested_skill")


def test_suggest_vertical_from_text():
    hits = suggest_vertical("CPO silicon photonics ELS laser for AI racks")
    assert hits
    assert hits[0]["id"] == "cpo_optics"


def test_vertical_suite_scoped():
    out = run_suite(
        text="System boundary CPO with kill criteria and https://example.com source nodes",
        vertical="cpo_optics",
    )
    assert out.get("vertical_id") == "cpo_optics"
    assert out.get("modules", 0) >= 3
    assert "results" in out
    assert out["modules"] < 50  # not full train


def test_desk_surfaces_verticals():
    desk = research_desk_status()
    assert desk.get("verticals", {}).get("count", 0) >= 5
    assert "cpo_optics" in (desk.get("verticals", {}).get("ids") or [])


def test_api_verticals_and_scaffold():
    c = TestClient(app)
    r = c.get("/pro/verticals")
    assert r.status_code == 200
    assert r.json().get("count", 0) >= 5 or len(r.json().get("items") or []) >= 5
    r2 = c.get("/pro/verticals/cpo_optics")
    assert r2.status_code == 200
    assert r2.json().get("scaffold", {}).get("question")
    r3 = c.post("/pro/verticals/cpo_optics/scaffold", json={"system": "AI optical I/O"})
    assert r3.status_code == 200
    assert "AI optical" in r3.json().get("question", "") or "optical" in r3.json().get(
        "question", ""
    ).lower()
    r4 = c.get("/pro/verticals", params={"q": "HBM CoWoS packaging"})
    assert r4.status_code == 200
    assert r4.json().get("suggestions")
    r5 = c.post(
        "/pro/suite",
        json={
            "text": "chokepoint capacity kill https://example.com",
            "vertical": "hbm_packaging",
        },
    )
    assert r5.status_code == 200
    assert r5.json().get("vertical_id") == "hbm_packaging"
