"""v4.7 marketplace, live safety, quotes capabilities."""

from __future__ import annotations

import pytest


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "reports").mkdir()
    (tmp_path / "data").mkdir()
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path / "reports"))
    monkeypatch.delenv("CHOKEPOINT_I_ACCEPT_LIVE_COSTS", raising=False)
    from src.config import clear_settings_cache

    clear_settings_cache()
    yield tmp_path, monkeypatch
    clear_settings_cache()


def test_marketplace_index(ws):
    from src.ops.marketplace import marketplace_index, marketplace_search

    idx = marketplace_index()
    assert idx["status"] == "local_only"
    assert idx["counts"]["listings"] >= 5
    assert any(x["kind"] == "skill_pack" for x in idx["listings"])
    hits = marketplace_search("cpo")
    assert hits["count"] >= 1


def test_live_safety_blocks_without_accept(ws):
    tmp_path, monkeypatch = ws
    from src.ops.live_safety import (
        assert_live_allowed,
        estimate_queue_live_cost,
        live_costs_accepted,
    )
    from src.ops.research_queue import enqueue

    enqueue("test live estimate question about CPO")
    est = estimate_queue_live_cost(n=1)
    assert est["est_total_tokens"] > 0
    assert live_costs_accepted(flag=False) is False
    with pytest.raises(ValueError, match="Live LLM queue blocked"):
        assert_live_allowed(flag=False)
    assert assert_live_allowed(flag=True)["ok"] is True
    monkeypatch.setenv("CHOKEPOINT_I_ACCEPT_LIVE_COSTS", "1")
    assert live_costs_accepted(flag=False) is True


def test_quotes_capabilities():
    from src.ops.quotes_meta import quotes_capabilities

    c = quotes_capabilities()
    assert c["sse"]["path"] == "/quotes/stream"
    assert c["websocket"]["path"] == "/ws/quotes"
    assert c["limitations"]
