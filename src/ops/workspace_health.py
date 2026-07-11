"""Composite workspace health score for the research workstation."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.ops.coverage_heat import coverage_heatmap
from src.ops.kill_monitor import kill_criteria_dashboard
from src.ops.quality_board import quality_leaderboard
from src.ops.research_queue import queue_summary
from src.ops.thesis_health import thesis_health_report
from src.ops.analytics import workspace_analytics


def workspace_health_score() -> dict[str, Any]:
    """0–100 process/hygiene score — not investment performance."""
    analytics = workspace_analytics()
    kills = kill_criteria_dashboard()
    theses = thesis_health_report()
    quality = quality_leaderboard(limit=20)
    heat = coverage_heatmap()
    queue = queue_summary()

    score = 50  # baseline
    components: list[dict[str, Any]] = []

    # reports present
    rc = int(analytics.get("reports_count") or 0)
    r_pts = min(15, rc * 2)
    score += r_pts - 5  # slight penalty if zero
    components.append({"id": "reports", "points": r_pts - 5, "detail": f"reports={rc}"})

    # quality avg
    qavg = quality.get("avg_score")
    if qavg is None:
        q_pts = -5
    elif qavg >= 70:
        q_pts = 15
    elif qavg >= 50:
        q_pts = 8
    else:
        q_pts = 0
    score += q_pts
    components.append({"id": "memo_quality", "points": q_pts, "detail": f"avg={qavg}"})

    # kill criteria process risk
    high = int(kills.get("high_risk_count") or 0)
    k_pts = 15 if high == 0 else max(-15, 10 - high * 8)
    score += k_pts
    components.append({"id": "kill_process", "points": k_pts, "detail": f"high_risk={high}"})

    # thesis process avg
    tavg = theses.get("avg_process_score")
    if tavg is None:
        t_pts = 0
    elif tavg >= 60:
        t_pts = 15
    elif tavg >= 40:
        t_pts = 8
    else:
        t_pts = -5
    score += t_pts
    components.append({"id": "thesis_process", "points": t_pts, "detail": f"avg={tavg}"})

    # coverage heat — penalize many cold symbols
    cold = sum(1 for s in (heat.get("symbols") or []) if s.get("heat") == "cold")
    hot = sum(1 for s in (heat.get("symbols") or []) if s.get("heat") == "hot")
    c_pts = min(10, hot * 3) - min(10, cold * 2)
    score += c_pts
    components.append({"id": "coverage", "points": c_pts, "detail": f"hot={hot} cold={cold}"})

    # queue backlog soft signal
    queued = int((queue.get("by_status") or {}).get("queued") or 0)
    failed = int((queue.get("by_status") or {}).get("failed") or 0)
    q_pts2 = 5 if queued <= 5 else 0
    q_pts2 -= min(10, failed * 3)
    score += q_pts2
    components.append({"id": "queue", "points": q_pts2, "detail": f"queued={queued} failed={failed}"})

    score = max(0, min(100, score))
    grade = (
        "A"
        if score >= 85
        else "B"
        if score >= 70
        else "C"
        if score >= 55
        else "D"
        if score >= 40
        else "F"
    )
    actions = []
    if high:
        actions.append("Add kill criteria to active theses (kill-monitor)")
    if cold:
        actions.append("Research or archive cold coverage symbols")
    if qavg is not None and qavg < 60:
        actions.append("Improve memo structure (checklist / min-quality gate)")
    if not actions:
        actions.append("Maintain hygiene: digest weekly, eval-record, mock queue dry-runs")

    return {
        "score": score,
        "grade": grade,
        "components": components,
        "actions": actions,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "disclaimer": "research_only_not_investment_advice",
        "note": "Process/hygiene score for the research workstation — not alpha or P&L.",
    }
