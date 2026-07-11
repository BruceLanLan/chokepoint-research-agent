"""Optional webhook notify when async jobs complete."""

from __future__ import annotations

from typing import Any

import httpx

from src.config import get_settings
from src.logging_utils import get_logger

log = get_logger("chokepoint.webhooks")


def notify_job_complete(job: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    url = getattr(settings, "webhook_url", None) or None
    # also read from env via settings if we add field
    url = url or _webhook_from_settings()
    if not url:
        return {"skipped": True, "reason": "no WEBHOOK_URL"}
    payload = {
        "event": "research_job_complete",
        "job_id": job.get("id"),
        "status": job.get("status"),
        "question": (job.get("question") or "")[:200],
        "mode": job.get("mode"),
        "disclaimer": "research_only_not_investment_advice",
    }
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.post(url, json=payload)
            return {"ok": r.is_success, "status_code": r.status_code}
    except Exception as exc:  # noqa: BLE001
        log.warning("webhook failed: %s", exc)
        return {"ok": False, "error": str(exc)}


def _webhook_from_settings() -> str | None:
    try:
        from src.config import get_settings

        return get_settings().webhook_url
    except Exception:  # noqa: BLE001
        return None
