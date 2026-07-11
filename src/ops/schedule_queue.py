"""Helpers to run mock queue processing from scheduled jobs (no LLM by default)."""

from __future__ import annotations

from typing import Any

from src.ops.audit import log_event
from src.ops.queue_worker import process_batch
from src.ops.research_queue import queue_summary


def scheduled_queue_tick(*, n: int = 1, live: bool = False) -> dict[str, Any]:
    """
    Intended for launchd/cron: process up to n queue items.
    Default dry-run/mock to avoid surprise LLM bills.
    """
    if live:
        # Explicit live path left to CLI --run --live; keep scheduler safe.
        result = {
            "ok": False,
            "error": "scheduled live runs disabled; use CLI queue --run --live interactively",
            "summary_before": queue_summary(),
        }
        log_event("schedule_queue_blocked_live", detail=result)
        return result
    out = process_batch(n=n, dry_run=True)
    log_event("schedule_queue_tick", detail={"n": n, "count": out.get("count")})
    return {"ok": True, "result": out, "summary_after": queue_summary()}
