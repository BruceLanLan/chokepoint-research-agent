"""Guards and estimates before live LLM queue / research burns."""

from __future__ import annotations

import os
from typing import Any

from src.ops.research_queue import list_queue, next_queued

# Rough heuristic tokens — not a billing system
_CHARS_PER_TOKEN = 3.5
_OUTPUT_TOKENS_ASSUMED = 2500
_INPUT_OVERHEAD = 4000  # tools/system rough


def estimate_queue_live_cost(n: int = 1) -> dict[str, Any]:
    """Heuristic cost banner for next N queued items (no API call)."""
    n = max(1, min(int(n or 1), 20))
    queued = list_queue(status="queued")[:n]
    items = []
    total_in = 0
    total_out = 0
    for it in queued:
        q = it.get("question") or ""
        est_in = int(len(q) / _CHARS_PER_TOKEN) + _INPUT_OVERHEAD
        est_out = _OUTPUT_TOKENS_ASSUMED
        total_in += est_in
        total_out += est_out
        items.append(
            {
                "id": it.get("id"),
                "mode": it.get("mode"),
                "question_preview": q[:80],
                "est_input_tokens": est_in,
                "est_output_tokens": est_out,
            }
        )
    # if queue empty, still show generic unit estimate
    if not items:
        nxt = next_queued()
        if not nxt:
            items = []
            total_in = (_INPUT_OVERHEAD + 200) * n
            total_out = _OUTPUT_TOKENS_ASSUMED * n
    return {
        "n_requested": n,
        "n_queued_matched": len(queued),
        "items": items,
        "est_total_input_tokens": total_in,
        "est_total_output_tokens": total_out,
        "est_total_tokens": total_in + total_out,
        "note": (
            "Heuristic only — not a bill. Live runs call your model + search providers. "
            "Research only — not investment advice."
        ),
        "require": {
            "cli": "queue --run N --live --i-accept-live-costs",
            "env": "CHOKEPOINT_I_ACCEPT_LIVE_COSTS=1 (API live=true)",
            "disclaimer": "research_only_not_investment_advice",
        },
    }


def live_costs_accepted(
    *,
    flag: bool = False,
    env_var: str = "CHOKEPOINT_I_ACCEPT_LIVE_COSTS",
) -> bool:
    """True if user explicitly accepted live LLM cost risk."""
    if flag:
        return True
    val = (os.environ.get(env_var) or "").strip().lower()
    return val in {"1", "true", "yes", "on"}


def assert_live_allowed(*, flag: bool = False) -> dict[str, Any]:
    """Return ok dict or raise ValueError with guidance."""
    estimate = estimate_queue_live_cost(n=1)
    if live_costs_accepted(flag=flag):
        return {"ok": True, "estimate": estimate}
    raise ValueError(
        "Live LLM queue blocked. Heuristic estimate: "
        f"~{estimate.get('est_total_tokens')} tokens/item. "
        "Re-run with --i-accept-live-costs or set CHOKEPOINT_I_ACCEPT_LIVE_COSTS=1. "
        "Prefer: python main.py queue --run N  (mock, free)."
    )


def live_tests_enabled(
    *,
    env_var: str = "CHOKEPOINT_RUN_LIVE_TESTS",
) -> bool:
    """True only when operator explicitly opted into live integration tests."""
    val = (os.environ.get(env_var) or "").strip().lower()
    return val in {"1", "true", "yes", "on"}


def browser_tests_enabled(
    *,
    env_var: str = "CHOKEPOINT_UI_BROWSER",
) -> bool:
    """True when optional Playwright UI browser smoke is requested."""
    val = (os.environ.get(env_var) or "").strip().lower()
    return val in {"1", "true", "yes", "on"}


def live_gate_status() -> dict[str, Any]:
    """Snapshot of live / browser gates for doctor, health, and docs."""
    return {
        "live_costs_accepted": live_costs_accepted(flag=False),
        "live_tests_enabled": live_tests_enabled(),
        "browser_tests_enabled": browser_tests_enabled(),
        "env": {
            "CHOKEPOINT_I_ACCEPT_LIVE_COSTS": "set to 1 to allow live queue/research burns",
            "CHOKEPOINT_RUN_LIVE_TESTS": "set to 1 to run live integration tests (also needs cost accept + keys)",
            "CHOKEPOINT_UI_BROWSER": "set to 1 to run optional Playwright UI smoke",
        },
        "prefer_offline": [
            "python main.py research --mock -V cpo_optics",
            "python main.py demo-journey -V cpo_optics",
            "python main.py queue --run 1",
            "pytest -q",
        ],
        "disclaimer": "research_only_not_investment_advice",
    }


def assert_live_research_allowed(
    *,
    flag: bool = False,
    require_model_key: bool = True,
) -> dict[str, Any]:
    """Gate non-mock research / stream paths.

    Requires explicit cost acceptance (flag or env) and optionally a model API key.
    Does **not** require CHOKEPOINT_RUN_LIVE_TESTS (that is for pytest only).
    """
    estimate = {
        "note": (
            "Live research calls your model provider and may call web search. "
            "Heuristic only — not a bill. Research only — not investment advice."
        ),
        "prefer_mock": "POST /research {mock:true} or CLI research --mock",
    }
    if not live_costs_accepted(flag=flag):
        raise ValueError(
            "Live research blocked. Re-run with --i-accept-live-costs / "
            "body i_accept_live_costs=true / env CHOKEPOINT_I_ACCEPT_LIVE_COSTS=1, "
            "or use mock:true / --mock for offline memos."
        )
    model_ok = True
    model_detail = "ok"
    if require_model_key:
        try:
            from src.config import get_settings

            settings = get_settings()
            problems = settings.validate_runtime(require_tavily=False)
            model_problems = [p for p in problems if "API_KEY" in p and "TAVILY" not in p]
            if model_problems:
                model_ok = False
                model_detail = "; ".join(model_problems)
        except Exception as exc:  # noqa: BLE001
            model_ok = False
            model_detail = str(exc)
    if not model_ok:
        raise ValueError(
            f"Live research blocked — model key missing/invalid: {model_detail}. "
            "Configure .env or use research --mock."
        )
    return {
        "ok": True,
        "estimate": estimate,
        "model": model_detail,
        "disclaimer": "research_only_not_investment_advice",
    }
