"""v8.0 — professional UI static assets + package splits."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src import __version__
from src.api import app
from src.cli.common import build_app


def test_version_is_semver_major():
    # Product is past 8.x train; accept 8+ majors (current milestone 10.x)
    major = int((__version__ or "0").split(".")[0])
    assert major >= 8


def test_cli_app_builds():
    t = build_app()
    assert t is not None


def test_static_ui_assets_exist():
    root = Path(__file__).resolve().parents[1] / "src" / "static"
    assert (root / "index.html").is_file()
    assert (root / "css" / "app.css").is_file()
    assert (root / "js" / "app.js").is_file()
    assert (root / "js" / "i18n.js").is_file()
    html = (root / "index.html").read_text(encoding="utf-8")
    assert "data-tab=\"desk\"" in html
    assert "lang-zh" in html
    js = (root / "js" / "app.js").read_text(encoding="utf-8")
    assert "loadDesk" in js or "/desk" in js
    i18n = (root / "js" / "i18n.js").read_text(encoding="utf-8")
    assert "window.I18N" in i18n
    assert "applyI18n" in i18n


def test_api_serves_ui_and_verticals():
    c = TestClient(app)
    r = c.get("/")
    assert r.status_code == 200
    assert "Chokepoint" in r.text or "desk" in r.text.lower()
    r2 = c.get("/static/js/app.js")
    assert r2.status_code == 200
    assert len(r2.text) > 1000
    r3 = c.get("/static/css/app.css")
    assert r3.status_code == 200
    r4 = c.get("/pro/verticals")
    assert r4.status_code == 200
    items = r4.json().get("items") or []
    assert len(items) >= 5
    ids = {i.get("id") for i in items}
    assert "cpo_optics" in ids
    # deep content (not keyword-only stubs)
    cpo = next(i for i in items if i.get("id") == "cpo_optics")
    assert cpo.get("kill_criteria")
    assert cpo.get("physical_nodes")


def test_api_route_modules_importable():
    from src.api.routes import core, coverage, knowledge, ops, pro, reports, research

    for m in (core, research, coverage, reports, pro, knowledge, ops):
        assert hasattr(m, "register")
