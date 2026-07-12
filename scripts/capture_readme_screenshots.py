#!/usr/bin/env python3
"""Capture workstation UI screenshots into docs/images/ for README.

Requires: pip install playwright && playwright install chromium
"""

from __future__ import annotations

import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "docs" / "images"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> int:
    import httpx
    import uvicorn
    from playwright.sync_api import sync_playwright

    from src.api import app

    host, port = "127.0.0.1", 8768
    config = uvicorn.Config(app, host=host, port=port, log_level="warning")
    server = uvicorn.Server(config)
    t = threading.Thread(target=server.run, daemon=True)
    t.start()
    for _ in range(80):
        try:
            if httpx.get(f"http://{host}:{port}/health", timeout=0.4).status_code == 200:
                break
        except Exception:
            time.sleep(0.1)
    else:
        print("server failed to start")
        return 1

    base = f"http://{host}:{port}"
    shots = [
        ("desk", "01-desk.png", "desk"),
        ("research", "02-research.png", "research"),
        ("reports", "03-reports.png", "reports"),
        ("knowledge", "04-knowledge.png", "knowledge"),
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(base + "/", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(800)
        # Chinese UI
        if page.locator("#lang-zh").count():
            page.locator("#lang-zh").click()
            page.wait_for_timeout(300)

        for tab, filename, _ in shots:
            page.locator(f"[data-tab={tab}]").click()
            page.wait_for_timeout(900)
            # trigger data loads
            if tab == "desk":
                page.locator("#desk-refresh").click()
                page.wait_for_timeout(1200)
            if tab == "research":
                page.locator("#vertical").select_option("cpo_optics")
                page.locator("#vert-scaffold").click()
                page.wait_for_timeout(600)
            if tab == "reports":
                page.locator("#r-refresh").click()
                page.wait_for_timeout(1000)
            if tab == "knowledge":
                page.locator("#k-vert").click()
                page.wait_for_timeout(800)
            path = OUT / filename
            page.screenshot(path=str(path), full_page=False)
            print("wrote", path)

        # hero: full shell desk again
        page.locator("[data-tab=desk]").click()
        page.wait_for_timeout(500)
        page.screenshot(path=str(OUT / "00-hero.png"), full_page=False)
        print("wrote", OUT / "00-hero.png")
        browser.close()

    server.should_exit = True
    print("done", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
