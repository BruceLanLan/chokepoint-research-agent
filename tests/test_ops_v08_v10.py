"""Tests for ops layer v0.8–v0.10."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_watchlist_crud(tmp_path, monkeypatch):
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path / "reports"))
    from src.config import clear_settings_cache
    from src.ops import watchlist as w

    clear_settings_cache()
    item = w.add_item(symbol="nvda", name="NVIDIA", thesis="AI GPU", priority="high", tags=["ai"])
    assert item["symbol"] == "NVDA"
    assert len(w.list_items()) == 1
    assert w.get_item(item["id"])["name"] == "NVIDIA"
    q = w.research_question_for(item)
    assert "NVDA" in q
    assert w.remove_item(item["id"]) is True
    assert w.list_items() == []


def test_thesis_registry(tmp_path, monkeypatch):
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path / "reports"))
    from src.config import clear_settings_cache
    from src.ops import theses as t

    clear_settings_cache()
    th = t.add_thesis(
        title="CPO path",
        statement="CPO is required for scale-up",
        kill_criteria=["copper wins"],
        related_symbols=["nvda"],
    )
    assert th["status"] == "active"
    t.set_status(th["id"], "watching", note="monitor")
    assert t.get_thesis(th["id"])["status"] == "watching"
    rq = t.research_question_for(th, mode="risk_only")
    assert "魔鬼代言人" in rq or "kill" in rq.lower()


def test_templates_render():
    from src.ops.templates import list_templates, render_template

    items = list_templates()
    assert any(i["id"] == "chokepoint_map" for i in items)
    r = render_template("chokepoint_map", {"system": "AI cluster", "context": "test"})
    assert "AI cluster" in r["question"]
    assert r["mode"] == "chokepoint_fast"


def test_catalog_search(tmp_path, monkeypatch):
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path))
    from src.config import clear_settings_cache
    from src.ops.catalog import search_catalog
    from src.tools.reports import save_report_file

    clear_settings_cache()
    save_report_file(
        title="CPO test memo",
        markdown_body="## 研究结论\nok\n## 风险\nr\n## 来源\nhttps://example.com\n" + "x" * 200,
        mode="full",
        quality={"score": 70},
    )
    hits = search_catalog("CPO", limit=10)
    assert hits


def test_doctor_structure():
    from src.ops.doctor import run_doctor

    d = run_doctor()
    assert "checks" in d
    assert "ok" in d
    names = {c["name"] for c in d["checks"]}
    assert "python_version" in names


def test_brief_dry(tmp_path, monkeypatch):
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path / "reports"))
    from src.config import clear_settings_cache
    from src.ops.brief import build_brief_questions, run_brief
    from src.ops.watchlist import add_item

    clear_settings_cache()
    add_item(symbol="TEST", name="TestCo", thesis="x", priority="high")
    jobs = build_brief_questions(limit=5)
    assert len(jobs) == 1

    def fake_invoke(q, mode):
        return "## 研究结论\n中性\n## 风险\n有\n## 来源\nhttps://example.com\n" + "分析" * 100

    out = run_brief(invoke_fn=fake_invoke, limit=1, save=True)
    assert out["count"] == 1
    assert out["saved_path"]
