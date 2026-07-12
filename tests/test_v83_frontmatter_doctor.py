"""v8.3 — vertical_id frontmatter + doctor config/ops scores + UI smoke."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.api import app
from src.ops.doctor import run_doctor
from src.tools.reports import parse_frontmatter, save_report_file


def test_save_report_writes_vertical_id(tmp_path, monkeypatch):
    from src.config import get_settings, clear_settings_cache

    clear_settings_cache()
    s = get_settings()
    monkeypatch.setattr(s, "reports_dir", tmp_path)
    path = save_report_file(
        "cpo demo",
        "## memo\nkill criteria https://example.com\n",
        mode="chokepoint_fast",
        skill="semiconductor",
        vertical="cpo_optics",
        quality={"score": 70},
    )
    text = Path(path).read_text(encoding="utf-8")
    meta = parse_frontmatter(text)
    assert meta.get("vertical_id") == "cpo_optics"
    assert meta.get("skill") == "semiconductor"
    assert "disclaimer" in meta


def test_mock_research_saves_vertical_frontmatter(tmp_path, monkeypatch):
    from src.config import clear_settings_cache, get_settings

    clear_settings_cache()
    s = get_settings()
    monkeypatch.setattr(s, "reports_dir", tmp_path)
    c = TestClient(app)
    r = c.post(
        "/research",
        json={
            "question": "vertical",
            "vertical": "hbm_packaging",
            "mock": True,
            "save_report": True,
            "export": False,
        },
    )
    assert r.status_code == 200
    path = r.json().get("saved_path")
    assert path
    meta = parse_frontmatter(Path(path).read_text(encoding="utf-8"))
    assert meta.get("vertical_id") == "hbm_packaging"


def test_doctor_config_and_ops_scores():
    d = run_doctor()
    assert "config" in d and "ops" in d
    assert "score" in d["config"] and "grade" in d["config"]
    assert "score" in d["ops"] and "grade" in d["ops"]
    assert "live_ready" in d
    assert "ops_ok" in d
    # tavily missing should be warn not error
    tavily = next(c for c in d["checks"] if c["name"] == "tavily_api_key")
    if not tavily["ok"]:
        assert tavily["level"] == "warn"
    assert any(c.get("bucket") == "ops" for c in d["checks"])
    assert any(c.get("name") == "verticals" for c in d["checks"])


def test_catalog_exposes_vertical_id(tmp_path, monkeypatch):
    from src.config import clear_settings_cache, get_settings
    from src.ops.catalog import build_catalog

    clear_settings_cache()
    s = get_settings()
    monkeypatch.setattr(s, "reports_dir", tmp_path)
    save_report_file(
        "vert memo",
        "body",
        vertical="power_cooling",
        quality={"score": 50},
    )
    items = build_catalog(limit=10)
    assert items
    assert any(i.get("vertical_id") == "power_cooling" for i in items)


def test_static_ui_smoke_assets():
    root = Path(__file__).resolve().parents[1] / "src" / "static"
    html = (root / "index.html").read_text(encoding="utf-8")
    js = (root / "js" / "app.js").read_text(encoding="utf-8")
    assert 'id="mock"' in html
    assert 'id="desk-demo"' in html
    assert "mock" in js and "demo-journey" in js or "/demo-journey" in js
    assert "vertical_id" in js or "vertical" in js
    c = TestClient(app)
    assert c.get("/").status_code == 200
    assert c.get("/static/js/app.js").status_code == 200
    assert c.get("/static/css/app.css").status_code == 200
    d = c.get("/doctor").json()
    assert "config" in d and "ops" in d
