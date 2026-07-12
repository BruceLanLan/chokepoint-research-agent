#!/usr/bin/env python3
"""Workstation UI smoke — default offline (TestClient); optional Playwright.

Usage:
  python scripts/ui_smoke.py                 # FastAPI TestClient only (CI-safe)
  CHOKEPOINT_UI_BROWSER=1 python scripts/ui_smoke.py   # + Playwright if installed
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def smoke_testclient() -> None:
    from fastapi.testclient import TestClient

    from src.api import app

    c = TestClient(app)
    r = c.get("/")
    assert r.status_code == 200, r.status_code
    assert b"app.js" in r.content or b"Desk" in r.content or b"desk" in r.content.lower()

    for path in (
        "/static/js/app.js",
        "/static/js/i18n.js",
        "/static/css/app.css",
        "/health",
        "/desk",
        "/pro/verticals",
        "/about",
    ):
        rr = c.get(path)
        assert rr.status_code == 200, f"{path} -> {rr.status_code}"

    js = c.get("/static/js/app.js").text
    assert "loadDesk" in js or "/desk" in js
    assert "mock" in js

    health = c.get("/health").json()
    assert "config" in health and "ops" in health
    assert "gates" in health

    # Offline research path
    res = c.post(
        "/research",
        json={
            "question": "vertical",
            "vertical": "cpo_optics",
            "mock": True,
            "save_report": False,
            "export": False,
        },
    )
    assert res.status_code == 200, res.text[:300]
    assert res.json().get("report")

    demo = c.post("/demo-journey", json={"vertical": "cpo_optics", "save": False})
    assert demo.status_code == 200
    print("ui_smoke TestClient: OK")


def smoke_playwright() -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        print("SKIP Playwright (pip install -e '.[ui]' && playwright install chromium):", exc)
        return

    import threading
    import time

    import uvicorn

    from src.api import app

    host, port = "127.0.0.1", 8765
    config = uvicorn.Config(app, host=host, port=port, log_level="warning")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    # wait for bind
    for _ in range(50):
        try:
            import httpx

            if httpx.get(f"http://{host}:{port}/health", timeout=0.3).status_code == 200:
                break
        except Exception:  # noqa: BLE001
            time.sleep(0.1)
    else:
        raise RuntimeError("server did not start for Playwright smoke")

    base = f"http://{host}:{port}"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(base + "/", wait_until="domcontentloaded", timeout=15000)
        # language toggle + desk
        page.locator("#lang-en").click()
        page.wait_for_timeout(200)
        assert page.locator("#tab-desk").count() >= 0 or page.locator("[data-tab=desk]").count()
        page.locator("[data-tab=research]").click()
        page.wait_for_timeout(200)
        # mock should be present
        assert page.locator("#mock").count() == 1
        page.locator("#vertical").select_option("cpo_optics")
        page.locator("#vert-scaffold").click()
        page.wait_for_timeout(400)
        q = page.locator("#q").input_value()
        assert len(q) > 20
        page.locator("#run").click()
        page.wait_for_timeout(1500)
        out = page.locator("#out").inner_text()
        assert len(out) > 50 or "Mock" in out or "mock" in out.lower() or "CPO" in out
        browser.close()
    server.should_exit = True
    print("ui_smoke Playwright: OK")


def main() -> int:
    smoke_testclient()
    if (os.environ.get("CHOKEPOINT_UI_BROWSER") or "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }:
        smoke_playwright()
    else:
        print("ui_smoke browser: skipped (set CHOKEPOINT_UI_BROWSER=1 for Playwright)")
    print("ui_smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
