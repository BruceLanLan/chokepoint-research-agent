"""v4.3 research queue + SQLite memo index."""

from __future__ import annotations

from pathlib import Path

import pytest


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


def test_memo_index(ws):
    from src.config import get_settings
    from src.ops.memo_index import rebuild_index, search_index

    p = Path(get_settings().reports_dir) / "cpo.md"
    p.write_text("# CPO study\n\nlaser chokepoint external source\n", encoding="utf-8")
    meta = rebuild_index()
    assert meta["indexed"] >= 1
    hits = search_index("laser")
    assert hits
    assert hits[0]["name"] == "cpo.md"


def test_research_queue(ws):
    from src.ops.research_queue import (
        enqueue,
        list_queue,
        next_queued,
        queue_summary,
        set_status,
    )
    from src.ops.watchlist import add_item
    from src.ops.research_queue import enqueue_from_watchlist

    a = enqueue("Map CPO nodes", mode="full", priority=10)
    assert a["status"] == "queued"
    assert next_queued()["id"] == a["id"]
    set_status(a["id"], "done", report="ok.md")
    assert queue_summary()["by_status"].get("done") == 1
    add_item(symbol="NVDA", name="NVIDIA", priority="high")
    items = enqueue_from_watchlist(limit=3)
    assert items
    assert list_queue()
