"""v4.4: queue worker, export pack, auto-tag, thesis health, config, notion, bulk."""

from __future__ import annotations

from pathlib import Path

import pytest

MD = """# CPO research

## 研究结论
External laser is a chokepoint for CPO silicon photonics.

## 风险
Kill criteria: multi-source ELS.

## 来源
- https://www.sec.gov/Archives/edgar/data/1
- 港交所公告示例

| 节点 | 不可替代 | 集中度 | 杠杆 | 真空 | 拐点 | 备注 |
|------|---------|--------|------|------|------|------|
| ELS | 5 | 4 | 5 | 4 | 4 | key |
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


def test_queue_worker_mock(ws):
    from src.ops.queue_worker import process_batch, process_one
    from src.ops.research_queue import enqueue, queue_summary

    enqueue("Map CPO laser supply", mode="chokepoint_fast", skill="semiconductor")
    enqueue("Red-team HBM path", mode="risk_only")
    r = process_one(dry_run=True)
    assert r["ok"] and r["processed"]
    assert r["report"]
    batch = process_batch(n=2, dry_run=True)
    assert batch["count"] >= 1
    s = queue_summary()
    assert s["by_status"].get("done", 0) >= 1


def test_export_pack_and_auto_tag(ws):
    from src.config import get_settings
    from src.ops.auto_tag import auto_tag_report, suggest_tags
    from src.ops.export_pack import build_export_pack

    p = Path(get_settings().reports_dir) / "cpo_demo.md"
    p.write_text(MD, encoding="utf-8")
    tags = suggest_tags(MD)
    assert "cpo" in tags or "optics" in tags
    tagged = auto_tag_report("cpo_demo.md")
    assert tagged.get("tags")
    pack = build_export_pack("cpo_demo.md")
    assert Path(pack["path"]).is_file()
    assert pack["size_kb"] > 0


def test_thesis_health(ws):
    from src.ops.theses import add_thesis
    from src.ops.thesis_health import thesis_health_report

    add_thesis(title="Weak", statement="x", status="active")
    add_thesis(
        title="Strong",
        statement="Concentrated ELS supply",
        system="AI optical",
        chokepoints=["ELS", "coupling"],
        kill_criteria=["Multi-source"],
        related_symbols=["COHR"],
        status="active",
    )
    rep = thesis_health_report()
    assert rep["count"] == 2
    scores = {i["title"]: i["process_score"] for i in rep["items"]}
    assert scores["Strong"] > scores["Weak"]


def test_config_sanitized(ws):
    from src.ops.config_export import sanitized_config

    cfg = sanitized_config()
    assert cfg["version"]
    # never leak raw keys
    for k, v in cfg.items():
        if "key" in k.lower() or "token" in k.lower():
            assert v in ("set", "missing") or k == "version"


def test_notion_export(ws):
    from src.config import get_settings
    from src.ops.notion_export import export_report_for_notion, memo_to_notion_blocks

    blocks = memo_to_notion_blocks(MD, title="t")
    assert blocks["block_count"] >= 3
    p = Path(get_settings().reports_dir) / "n.md"
    p.write_text(MD, encoding="utf-8")
    out = export_report_for_notion("n.md")
    assert out["plain_text"]


def test_plugin_catalog():
    from src.ops.plugin_catalog import plugin_catalog

    cat = plugin_catalog()
    assert "plugins_dir" in cat
    assert "builtin_providers" in cat


def test_watch_bulk(ws):
    from src.ops.watchlist_bulk import bulk_add_symbols
    from src.ops.watchlist import list_items

    r = bulk_add_symbols("NVDA,AAPL,TEST")
    assert r["added"] == 3
    r2 = bulk_add_symbols("NVDA")
    assert r2["added"] == 0
    assert "NVDA" in r2["skipped_existing"]
    assert len(list_items()) >= 3


def test_quality_board_and_schedule_queue(ws):
    from src.config import get_settings
    from src.ops.quality_board import quality_leaderboard
    from src.ops.research_queue import enqueue
    from src.ops.schedule_queue import scheduled_queue_tick

    p = Path(get_settings().reports_dir) / "qb.md"
    p.write_text(MD, encoding="utf-8")
    board = quality_leaderboard(limit=10)
    assert board["count"] >= 1
    enqueue("scheduled mock item")
    tick = scheduled_queue_tick(n=1, live=False)
    assert tick["ok"] is True
    blocked = scheduled_queue_tick(n=1, live=True)
    assert blocked["ok"] is False
