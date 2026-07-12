"""Tests for 50-version pro maturity train (v5.2–v5.51) + suite."""

from __future__ import annotations

import pytest

from src.ops.pro import PRO_MODULE_IDS


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "reports").mkdir()
    (tmp_path / "data").mkdir()
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path / "reports"))
    from src.config import clear_settings_cache

    clear_settings_cache()
    yield tmp_path
    clear_settings_cache()


def test_fifty_modules_registered():
    assert len(PRO_MODULE_IDS) == 50
    from src.ops.pro.registry import list_modules

    items = list_modules()
    assert len(items) == 50
    ids = {m["id"] for m in items}
    assert ids == set(PRO_MODULE_IDS)


def test_each_module_analyze_and_summarize(ws):
    from src.ops.pro.registry import invoke_module

    sample = (
        "System boundary: AI CPO. Chokepoint node laser. "
        "Kill criteria: multi-source. Source https://example.com/a 2024 Q3 capacity."
    )
    # sample subset + full count via random picks to keep CI fast but cover all
    for mid in PRO_MODULE_IDS:
        a = invoke_module(mid, action="analyze", text=sample, symbol="TEST")
        assert a.get("module") == mid
        assert "checklist" in a
        assert a.get("disclaimer")
        s = invoke_module(mid, action="summarize")
        assert s.get("module") == mid
        add = invoke_module(
            mid,
            action="add",
            title="note",
            body=sample,
            symbol="TEST",
        )
        assert add.get("id")


def test_pro_suite(ws):
    from src.ops.pro.suite import run_full_suite, suite_markdown

    text = (
        "System chokepoint research with kill criteria and peer substitutes. "
        "Evidence https://sec.gov/x capacity 2024."
    )
    s = run_full_suite(text=text, symbol="NVDA")
    assert s["modules"] == 50
    assert s["gates_ok"] >= 1
    md = suite_markdown(text=text)
    assert "suite" in md.lower() or "module" in md.lower()


def test_unknown_module():
    from src.ops.pro.registry import invoke_module

    out = invoke_module("not_a_real_module_xyz")
    assert out.get("error")
