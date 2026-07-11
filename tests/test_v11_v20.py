"""Tests for v1.1–v1.20 feature train."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_diff_and_backup(tmp_path, monkeypatch):
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path / "reports"))
    from src.config import clear_settings_cache
    from src.ops.backup import create_backup, restore_backup
    from src.ops.report_diff import diff_reports
    from src.ops.watchlist import add_item
    from src.tools.reports import save_report_file

    clear_settings_cache()
    save_report_file(title="a", markdown_body="hello alpha\n## 风险\n", mode="full", quality={})
    save_report_file(title="b", markdown_body="hello beta\n## 风险\n", mode="full", quality={})
    from src.ops.catalog import build_catalog

    names = [r["name"] for r in build_catalog(limit=5)]
    assert len(names) >= 2
    d = diff_reports(names[0], names[1])
    assert "ratio" in d

    add_item(symbol="ZZZ", name="Z")
    bak = create_backup(tmp_path / "bak")
    assert Path(bak["path"]).is_file()
    # wipe and restore
    from src.ops.watchlist import list_items, _path

    _path().write_text('{"version":1,"items":[]}', encoding="utf-8")
    assert list_items() == []
    restore_backup(bak["path"])
    assert any(i["symbol"] == "ZZZ" for i in list_items())


def test_csv_and_thesis_export(tmp_path, monkeypatch):
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path / "reports"))
    from src.config import clear_settings_cache
    from src.ops.io_csv import export_watchlist_csv, import_watchlist_csv
    from src.ops.thesis_export import export_theses_markdown
    from src.ops.theses import add_thesis
    from src.ops.watchlist import add_item, list_items

    clear_settings_cache()
    add_item(symbol="ABC", name="Abc")
    csv_path = tmp_path / "w.csv"
    export_watchlist_csv(csv_path)
    assert csv_path.is_file()
    n_before = len(list_items())
    import_watchlist_csv(csv_path)
    assert len(list_items()) >= n_before

    add_thesis(title="T", statement="S", kill_criteria=["k"])
    md = export_theses_markdown(tmp_path / "t.md")
    assert Path(md).is_file()


def test_peer_review_and_prompt_version():
    from src.ops.peer_review import peer_review_question
    from src.prompts.version import PROMPT_PACK_VERSION

    q = peer_review_question("thesis text")
    assert "Kill criteria" in q or "kill criteria" in q.lower()
    assert PROMPT_PACK_VERSION


def test_cost_budget_and_providers():
    from src.providers.base import get_registry
    from src.tools.resilience import CostTracker

    t = CostTracker()
    t.add_llm(4000, 4000)
    assert t.over_budget(1000) is True
    assert t.over_budget(0) is False
    names = get_registry().list_providers()
    assert "cn_announcements" in names["filings"]


def test_checklist_template():
    from src.ops.templates import list_templates, render_template

    ids = {t["id"] for t in list_templates()}
    assert "checklist_gate" in ids
    r = render_template("checklist_gate", {"draft": "demo draft"})
    assert "demo draft" in r["question"]
