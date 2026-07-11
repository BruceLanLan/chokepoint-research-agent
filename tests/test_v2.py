"""v2.0 tests: scheduler, PDF, CN multi-source."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_scheduler_config_and_cron(tmp_path, monkeypatch):
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path / "reports"))
    from src.config import clear_settings_cache
    from src.ops.scheduler import cron_line, load_schedule, save_schedule, schedule_status

    clear_settings_cache()
    cfg = load_schedule()
    cfg["limit"] = 2
    cfg["hour"] = 8
    cfg["minute"] = 30
    save_schedule(cfg)
    loaded = load_schedule()
    assert loaded["limit"] == 2
    line = cron_line(8, 30)
    assert "8" in line and "30" in line
    assert "run_scheduled_brief.py" in line
    st = schedule_status()
    assert st["runner_exists"] is True


def test_pdf_generation(tmp_path, monkeypatch):
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path / "reports"))
    from src.config import clear_settings_cache
    from src.tools.pdf_report import markdown_to_pdf

    clear_settings_cache()
    body = """# Title
## 研究结论
Neutral view for research only.
## 风险
Kill criteria: delay of CPO
## 来源
https://example.com/x
""" + ("detail paragraph. " * 40)
    out = markdown_to_pdf("Test Memo", body, out_path=tmp_path / "t.pdf")
    assert out.get("path")
    assert Path(out["path"]).is_file()
    assert Path(out["path"]).stat().st_size > 500


def test_cn_provider_multi_source_shape():
    from src.providers.cn_announcements import CnAnnouncementProvider
    from src.providers.base import get_registry

    reg = get_registry()
    assert "cn_announcements" in reg.list_providers()["filings"]
    p = CnAnnouncementProvider(timeout=8.0)
    # network optional — just ensure returns list
    hits = p.search_company("600519")
    assert isinstance(hits, list)
    assert len(hits) >= 1


def test_cn_tools_registered():
    from src.tools.research_tools import all_tools

    names = {t.name for t in all_tools()}
    assert "cn_search_announcements" in names
    assert "cn_company_suggest" in names


def test_export_bundle_includes_pdf_key(tmp_path, monkeypatch):
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path))
    from src.config import clear_settings_cache
    from src.tools.export import export_report_bundle

    clear_settings_cache()
    paths = export_report_bundle(
        title="pdf demo",
        markdown_body="## 研究结论\nok\n## 风险\nKill criteria: x\n## 来源\nhttps://a.com\n"
        + "body " * 80,
        mode="full",
    )
    assert "md" in paths and "html" in paths
    # pdf may succeed with system font
    assert "pdf" in paths or "pdf_error" in paths
