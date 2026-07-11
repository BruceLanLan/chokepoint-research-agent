"""Tests for providers, filings tools, jobs, analytics."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_provider_registry():
    from src.providers.base import get_registry

    reg = get_registry()
    names = reg.list_providers()
    assert "sec_edgar" in names["filings"]
    assert "yahoo" in names["market"]


def test_sec_search_offline_shape():
    """Do not require network success; ensure tool returns string JSON-ish."""
    from src.tools.filings import sec_search_company, validate_citations

    # May succeed online or return error JSON offline
    out = sec_search_company.invoke({"query": "AAPL"})
    assert isinstance(out, str)
    assert len(out) > 2

    cite = validate_citations.invoke(
        {
            "markdown_report": "## 研究结论\n中性 chokepoint\n## 风险\nKill criteria: x\n## 来源\nhttps://sec.gov/a\n"
            + "正文" * 50
        }
    )
    data = json.loads(cite)
    assert data["unique_urls"] >= 1
    assert data["has_kill_criteria"] is True


def test_jobs_lifecycle(tmp_path, monkeypatch):
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path / "reports"))
    from src.config import clear_settings_cache
    from src.ops.jobs import get_job, list_jobs, submit_research_job
    import time

    clear_settings_cache()

    def run_fn(q, mode):
        return {"report_preview": "ok " + q, "quality": {"score": 1}, "saved_path": None}

    job = submit_research_job(question="test q", mode="chokepoint_fast", run_fn=run_fn)
    assert job["status"] == "queued"
    # wait for worker
    for _ in range(50):
        cur = get_job(job["id"])
        if cur and cur.get("status") in {"completed", "failed"}:
            break
        time.sleep(0.05)
    cur = get_job(job["id"])
    assert cur is not None
    assert cur["status"] == "completed"
    assert list_jobs(limit=5)


def test_analytics(tmp_path, monkeypatch):
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path / "reports"))
    from src.config import clear_settings_cache
    from src.ops.analytics import workspace_analytics
    from src.ops.watchlist import add_item

    clear_settings_cache()
    add_item(symbol="AAA", name="A", priority="high")
    a = workspace_analytics()
    assert a["watchlist_count"] >= 1
    assert "reports_count" in a


def test_tools_include_sec():
    from src.tools.research_tools import all_tools, researcher_tools

    names = {t.name for t in all_tools()}
    assert "sec_search_company" in names
    assert "sec_recent_filings" in names
    assert "validate_citations" in names
    assert "sec_search_company" in {t.name for t in researcher_tools()}
