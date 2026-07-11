"""v4.8–v5.0 professional workstation: health, runbook, batch review, quotes cache, weekly ops."""

from __future__ import annotations

from pathlib import Path

import pytest

MD = """# Pro memo

## 研究结论
Node is a chokepoint.

## 风险与证伪 / Kill criteria
- Multi-source

## 来源
- https://www.sec.gov/x

| 节点 | 不可替代 | 集中度 | 杠杆 | 真空 | 拐点 | 备注 |
|------|---------|--------|------|------|------|------|
| N | 5 | 4 | 5 | 4 | 4 | k |

仅供研究学习，不构成投资建议。
"""


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    reports = tmp_path / "reports"
    reports.mkdir()
    (tmp_path / "data").mkdir()
    monkeypatch.setenv("REPORTS_DIR", str(reports))
    from src.config import clear_settings_cache

    clear_settings_cache()
    yield tmp_path
    clear_settings_cache()


def test_quote_cache(ws):
    from src.ops.quote_cache import history_summary, load_history, refresh_symbols

    out = refresh_symbols(
        ["TEST"],
        fetch_fn=lambda s: {"symbol": s, "price": 1.23, "stub": True},
    )
    assert out["refreshed"] == 1
    hist = load_history("TEST")
    assert hist and hist[-1]["snapshot"]["price"] == 1.23
    assert history_summary()["count"] >= 1


def test_workspace_health(ws):
    from src.ops.theses import add_thesis
    from src.ops.watchlist import add_item
    from src.ops.workspace_health import workspace_health_score
    from src.tools.reports import save_report_file

    add_item(symbol="NVDA", name="NVIDIA", priority="high")
    add_thesis(
        title="ok",
        statement="s",
        kill_criteria=["x"],
        chokepoints=["a"],
        related_symbols=["NVDA"],
    )
    save_report_file(title="m", markdown_body=MD, mode="full", quality={"score": 80})
    h = workspace_health_score()
    assert 0 <= h["score"] <= 100
    assert h["grade"] in set("ABCDF")
    assert h["actions"]


def test_runbook(ws):
    from src.ops.runbook import professional_runbook, runbook_markdown

    rb = professional_runbook(system="AI CPO")
    assert len(rb["steps"]) >= 5
    assert "chokepoint" in rb["cli_cheatsheet"][2] or "research" in rb["cli_cheatsheet"][2]
    md = runbook_markdown("AI CPO")
    assert "Runbook" in md or "runbook" in md.lower() or "Chokepoint" in md


def test_batch_review_and_weekly(ws):
    from src.config import get_settings
    from src.ops.batch_review import batch_structure_review
    from src.ops.weekly_ops import run_weekly_ops

    p = Path(get_settings().reports_dir) / "good.md"
    p.write_text(MD, encoding="utf-8")
    rev = batch_structure_review(limit=10)
    assert rev["reviewed"] >= 1
    pack = run_weekly_ops(save=True, enqueue_watchlist=0)
    assert "Workspace health" in pack["markdown"] or "health" in pack["markdown"].lower()
    assert pack.get("saved_path")


def test_grade_memo_and_watchlist_refresh(ws):
    from src.config import get_settings
    from src.ops.coverage_refresh import refresh_watchlist_quotes
    from src.ops.memo_grade import grade_memo
    from src.ops.quote_cache import refresh_symbols
    from src.ops.watchlist import add_item

    p = Path(get_settings().reports_dir) / "g.md"
    p.write_text(MD, encoding="utf-8")
    g = grade_memo("g.md")
    assert g["grade"] in set("ABCDF")
    assert g["score"] >= 50
    add_item(symbol="AAA", name="A")
    # inject via refresh_symbols path used by coverage_refresh
    out = refresh_symbols(["AAA"], fetch_fn=lambda s: {"symbol": s, "price": 9})
    assert out["refreshed"] == 1
    # watchlist refresh uses network/stub — must not crash
    wr = refresh_watchlist_quotes(limit=5)
    assert "refreshed" in wr
