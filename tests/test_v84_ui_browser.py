"""Optional Playwright browser smoke — skipped in default CI."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from src.ops.live_safety import browser_tests_enabled

_ROOT = Path(__file__).resolve().parents[1]
_UI_SMOKE = _ROOT / "scripts" / "ui_smoke.py"


def _load_ui_smoke():
    spec = importlib.util.spec_from_file_location("ui_smoke", _UI_SMOKE)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ui_smoke"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.browser
def test_playwright_ui_optional():
    if not browser_tests_enabled():
        pytest.skip("set CHOKEPOINT_UI_BROWSER=1 to enable Playwright smoke")
    try:
        import playwright  # noqa: F401
    except ImportError:
        pytest.skip(
            "playwright not installed — pip install -e '.[ui]' && playwright install chromium"
        )

    mod = _load_ui_smoke()
    mod.smoke_playwright()


def test_ui_smoke_script_testclient():
    mod = _load_ui_smoke()
    mod.smoke_testclient()
