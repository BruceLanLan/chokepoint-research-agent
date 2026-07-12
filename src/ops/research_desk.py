"""Unified research desk status — one command for professional ops snapshot."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.ops.pro_dashboard import pro_dashboard
from src.ops.workspace_health import workspace_health_score
from src.ops.quality_board import quality_leaderboard
from src.ops.research_queue import queue_summary
from src.ops.kill_monitor import kill_criteria_dashboard
from src.ops.marketplace import marketplace_index
from src.playbooks.registry import list_playbooks
from src.questionnaires.registry import list_questionnaires
from src.rubrics.registry import list_rubrics
from src import __version__


def research_desk_status() -> dict[str, Any]:
    health = workspace_health_score()
    pro = pro_dashboard()
    q = quality_leaderboard(limit=10)
    queue = queue_summary()
    kills = kill_criteria_dashboard()
    mkt = marketplace_index()
    providers = {}
    try:
        from src.ops.provider_health import probe_providers

        providers = probe_providers(live=False)
    except Exception:  # noqa: BLE001
        providers = {"error": "unavailable"}

    return {
        "version": __version__,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace_health": {
            "score": health.get("score"),
            "grade": health.get("grade"),
            "actions": health.get("actions"),
        },
        "pro_ops": {
            "modules": pro.get("modules"),
            "active_modules": pro.get("active_modules"),
            "total_entries": pro.get("total_entries"),
            "avg_density_global": pro.get("avg_density_global"),
        },
        "quality": {
            "avg_score": q.get("avg_score"),
            "count": q.get("count"),
        },
        "queue": queue.get("by_status"),
        "kill_monitor_high_risk": kills.get("high_risk_count"),
        "providers": providers.get("providers") or providers,
        "catalog": {
            "marketplace_listings": (mkt.get("counts") or {}).get("listings"),
            "playbooks": len(list_playbooks()),
            "questionnaires": len(list_questionnaires()),
            "rubrics": len(list_rubrics()),
            "pro_yaml_specs": True,
        },
        "next_actions": _next_actions(health, pro, kills, queue),
        "disclaimer": "research_only_not_investment_advice",
        "note": "Research desk status — process hygiene, not P&L or advice.",
    }


def _next_actions(health, pro, kills, queue) -> list[str]:
    acts = list(health.get("actions") or [])
    if int(pro.get("active_modules") or 0) < 3:
        acts.append("Seed pro modules: pro <module> --action add / memo-pro bridge")
    if int(kills.get("high_risk_count") or 0) > 0:
        acts.append("Fix theses missing kill criteria (kill-monitor)")
    queued = int((queue.get("by_status") or {}).get("queued") or 0)
    if queued:
        acts.append(f"Drain queue with mock: queue --run {min(queued, 3)}")
    if not acts:
        acts.append("Run weekly-ops + pro-suite on latest memo")
    return acts[:8]


def research_desk_markdown() -> str:
    s = research_desk_status()
    lines = [
        f"# Research Desk Status (v{s['version']})\n\n",
        f"generated_at: {s['generated_at']}\n\n",
        f"**Workspace health:** {s['workspace_health']['grade']} "
        f"({s['workspace_health']['score']})\n\n",
        f"**Pro modules:** active {s['pro_ops']['active_modules']}/"
        f"{s['pro_ops']['modules']} entries={s['pro_ops']['total_entries']}\n\n",
        f"**Queue:** {s['queue']}\n\n",
        f"**Catalog:** playbooks={s['catalog']['playbooks']} "
        f"questionnaires={s['catalog']['questionnaires']} "
        f"rubrics={s['catalog']['rubrics']}\n\n",
        "## Next actions\n",
    ]
    for a in s["next_actions"]:
        lines.append(f"- {a}\n")
    lines.append("\n> Research only — not investment advice.\n")
    return "".join(lines)
