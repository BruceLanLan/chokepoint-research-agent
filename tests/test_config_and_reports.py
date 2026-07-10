from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_settings_validate_and_cache(tmp_path, monkeypatch):
    from src.config import Settings, clear_settings_cache, get_settings

    clear_settings_cache()
    s = Settings(
        model_provider="openai_compatible",
        model_name="x",
        openai_api_key="sk-test",
        openai_base_url="https://example.com/v1",
        tavily_api_key="tvly-test",
        reports_dir=tmp_path / "reports",
    )
    assert s.validate_runtime() == []

    s2 = Settings(model_provider="anthropic")
    probs = s2.validate_runtime(require_tavily=True)
    assert any("ANTHROPIC" in p for p in probs)


def test_save_and_list_reports(tmp_path, monkeypatch):
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path))
    from src.config import clear_settings_cache
    from src.tools.reports import list_reports, read_report, save_report_file

    clear_settings_cache()
    path = save_report_file(
        title="测试报告 CPO",
        markdown_body="## 研究结论\n中性\n## 风险\n有\n## 来源\nhttps://example.com",
        mode="chokepoint_fast",
        quality={"score": 70},
    )
    assert Path(path).is_file()
    items = list_reports(limit=5)
    assert items
    body = read_report(items[0]["name"])
    assert body and "研究结论" in body
    assert read_report("../etc/passwd") is None


def test_normalize_symbol():
    from src.tools.research_tools import normalize_symbol

    assert normalize_symbol("600519") == "600519.SS"
    assert normalize_symbol("000001") == "000001.SZ"


def test_web_search_signature_has_topic():
    from src.tools.research_tools import web_search

    # Ensure model-visible params exist (not InjectedToolArg-only)
    schema = web_search.args_schema.model_json_schema()
    props = schema.get("properties") or {}
    assert "topic" in props
    assert "max_results" in props


def test_specialists_for_mode():
    from src.agents.fallback_orchestrator import specialists_for_mode

    assert len(specialists_for_mode("full")) == 4
    assert len(specialists_for_mode("chokepoint_fast")) == 1
    assert specialists_for_mode("risk_only") == []
    assert len(specialists_for_mode("compare")) == 2
