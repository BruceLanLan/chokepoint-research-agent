"""Aggregate cost / quality metrics for the research workstation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.config import get_settings
from src.ops.audit import audit_summary
from src.pipeline.postprocess import metrics_summary


def cost_quality_dashboard(limit: int = 200) -> dict[str, Any]:
    metrics = metrics_summary(limit=limit)
    audit = audit_summary()
    # optional jobs file
    jobs_path = Path(get_settings().reports_dir).parent / "data" / "jobs.json"
    jobs_n = 0
    if jobs_path.is_file():
        try:
            jobs_n = len((json.loads(jobs_path.read_text(encoding="utf-8")) or {}).get("items") or [])
        except Exception:  # noqa: BLE001
            jobs_n = 0

    return {
        "postprocess_metrics": metrics,
        "audit": {"count": audit.get("count"), "by_action": audit.get("by_action")},
        "jobs_recorded": jobs_n,
        "quality_avg": metrics.get("quality_avg"),
        "gate_pass_rate": metrics.get("gate_pass_rate"),
        "disclaimer": "research_only_not_investment_advice",
        "note": "Token costs are estimates when tracked; not a brokerage ledger.",
    }
