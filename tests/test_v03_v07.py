"""Regression tests for v0.3–v0.7 features."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_cn_market_detect():
    from src.tools.market_cn import _detect_market

    assert _detect_market("600519")[0] == "sh"
    assert _detect_market("000001.SZ")[0] == "sz"
    assert _detect_market("0700.HK")[0] == "hk"


def test_cost_tracker_and_retry():
    from src.tools.resilience import get_cost_tracker, reset_cost_tracker, with_retry

    reset_cost_tracker()
    t = get_cost_tracker()
    t.add_llm(100, 40)
    t.add_tool("web_search")
    s = t.summary()
    assert s["llm_calls"] == 1
    assert s["tool_calls"] == 1

    n = {"i": 0}

    @with_retry(attempts=3, base_delay=0.01)
    def flaky():
        n["i"] += 1
        if n["i"] < 3:
            raise RuntimeError("boom")
        return "ok"

    assert flaky() == "ok"
    assert get_cost_tracker().retries >= 2


def test_export_bundle(tmp_path, monkeypatch):
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path))
    from src.config import clear_settings_cache
    from src.tools.export import export_report_bundle

    clear_settings_cache()
    paths = export_report_bundle(
        title="demo",
        markdown_body="## 研究结论\nok\n## 风险\nr\n## 来源\nhttps://example.com\n" + "x" * 400,
        mode="full",
    )
    assert Path(paths["md"]).is_file()
    assert Path(paths["json"]).is_file()
    assert Path(paths["html"]).is_file()


def test_session_memory(tmp_path, monkeypatch):
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path / "reports"))
    from src.config import clear_settings_cache
    from src.memory.sessions import append_turn, load_session, new_session_id, session_context_block

    clear_settings_cache()
    sid = new_session_id()
    append_turn(sid, question="Q1", report="R1 " * 100, mode="full")
    data = load_session(sid)
    assert len(data["turns"]) == 1
    ctx = session_context_block(sid)
    assert "Q1" in ctx


def test_eval_harness():
    from src.eval.harness import run_all

    result = run_all()
    assert result["total"] >= 2
    assert result["failed"] == 0


def test_tools_include_cn():
    from src.tools.research_tools import all_tools, researcher_tools

    names = {t.name for t in all_tools()}
    assert "get_cn_stock_quote" in names
    assert "search_cn_company_news" in names
    assert "get_cn_stock_quote" in {t.name for t in researcher_tools()}
