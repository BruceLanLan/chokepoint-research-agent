"""v8.4 — live gates always offline-safe; real live path opt-in only.

Default CI: only offline gate tests run.
Live path requires ALL of:
  CHOKEPOINT_RUN_LIVE_TESTS=1
  CHOKEPOINT_I_ACCEPT_LIVE_COSTS=1
  model API key available

Never burns tokens without explicit env.
"""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from src.api import app
from src.ops.live_safety import (
    assert_live_allowed,
    browser_tests_enabled,
    estimate_queue_live_cost,
    live_costs_accepted,
    live_gate_status,
    live_tests_enabled,
)


def test_live_tests_disabled_by_default(monkeypatch):
    monkeypatch.delenv("CHOKEPOINT_RUN_LIVE_TESTS", raising=False)
    monkeypatch.delenv("CHOKEPOINT_I_ACCEPT_LIVE_COSTS", raising=False)
    monkeypatch.delenv("CHOKEPOINT_UI_BROWSER", raising=False)
    assert live_tests_enabled() is False
    assert live_costs_accepted(flag=False) is False
    assert browser_tests_enabled() is False


def test_live_gate_status_shape():
    st = live_gate_status()
    assert "prefer_offline" in st
    assert "env" in st
    assert st["disclaimer"].startswith("research_only")


def test_assert_live_blocked_without_accept(monkeypatch):
    monkeypatch.delenv("CHOKEPOINT_I_ACCEPT_LIVE_COSTS", raising=False)
    with pytest.raises(ValueError, match="blocked|accept"):
        assert_live_allowed(flag=False)
    ok = assert_live_allowed(flag=True)
    assert ok["ok"] is True
    assert "estimate" in ok


def test_estimate_queue_is_offline():
    est = estimate_queue_live_cost(n=1)
    assert "est_total_tokens" in est
    assert est["require"]["env"]


def test_health_exposes_gates_and_scores():
    c = TestClient(app)
    r = c.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert "config" in body and "ops" in body
    assert "gates" in body
    assert "live_ready" in body
    assert body["gates"]["prefer_offline"]


@pytest.mark.live
def test_live_integration_optional(monkeypatch):
    """Only runs when operator opts in — may touch network/providers."""
    if not live_tests_enabled():
        pytest.skip("set CHOKEPOINT_RUN_LIVE_TESTS=1 to enable")
    if not live_costs_accepted(flag=False):
        pytest.skip("set CHOKEPOINT_I_ACCEPT_LIVE_COSTS=1 to enable")

    from src.config import clear_settings_cache, get_settings

    clear_settings_cache()
    settings = get_settings()
    problems = settings.validate_runtime(require_tavily=False)
    if any("API_KEY" in p and "TAVILY" not in p for p in problems):
        pytest.skip(f"model key missing: {problems}")

    # Live-ish but bounded: provider health with live=False is free;
    # with live=True only if still gated (optional network).
    from src.ops.provider_health import probe_providers

    offline = probe_providers(live=False)
    assert "providers" in offline or "market" in str(offline).lower() or offline

    # Optional true live probe (no LLM research memo — still cost-aware)
    if os.environ.get("CHOKEPOINT_LIVE_PROVIDER_PROBE", "").strip() in {"1", "true", "yes"}:
        live = probe_providers(live=True)
        assert live is not None

    # Explicit cost accept still required for live queue path
    assert assert_live_allowed(flag=False)["ok"] is True
