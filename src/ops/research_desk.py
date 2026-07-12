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
            "verticals": _verticals_catalog(),
        },
        "verticals": _verticals_catalog(),
        "vertical_coverage": _vertical_coverage_brief(),
        "next_actions": _next_actions(health, pro, kills, queue),
        "disclaimer": "research_only_not_investment_advice",
        "note": "Research desk status — process hygiene, not P&L or advice.",
    }


def _vertical_coverage_brief() -> dict[str, Any]:
    try:
        from src.ops.vertical_coverage import vertical_coverage_dashboard

        d = vertical_coverage_dashboard()
        return {
            "packs": d.get("packs"),
            "with_memos": d.get("with_memos"),
            "with_pairs": d.get("with_pairs"),
            "next_actions": (d.get("next_actions") or [])[:3],
        }
    except Exception:  # noqa: BLE001
        return {}


def _verticals_catalog() -> dict[str, Any]:
    try:
        from src.ops.pro.verticals import desk_vertical_block

        return desk_vertical_block()
    except Exception:  # noqa: BLE001
        return {"count": 0, "ids": []}


def _next_actions(health, pro, kills, queue) -> list[str]:
    acts = list(health.get("actions") or [])
    if int(pro.get("active_modules") or 0) < 3:
        acts.append("Seed pro modules: pro <module> --action add / memo-pro bridge")
    if int(kills.get("high_risk_count") or 0) > 0:
        acts.append("Fix theses missing kill criteria (kill-monitor)")
    queued = int((queue.get("by_status") or {}).get("queued") or 0)
    if queued:
        acts.append(f"Drain queue with mock: queue --run {min(queued, 3)}")
    verts = _verticals_catalog()
    if int(verts.get("count") or 0) > 0 and int(pro.get("active_modules") or 0) < 3:
        sample = (verts.get("ids") or ["cpo_optics"])[0]
        acts.append(
            f"Deep vertical: research --vertical {sample}  or  pro-suite --vertical {sample}"
        )
    try:
        from src.ops.vertical_coverage import vertical_coverage_dashboard

        vc = vertical_coverage_dashboard()
        if int(vc.get("with_pairs") or 0) < 1 and verts.get("ids"):
            acts.append(f"Build compare pair: golden-path -V {verts['ids'][0]}")
        elif int(vc.get("with_pairs") or 0) >= 1 and verts.get("ids"):
            acts.append(f"compare-vertical {verts['ids'][0]}  (or export compare pack)")
    except Exception:  # noqa: BLE001
        pass
    if not acts:
        acts.append("Run weekly-ops + pro-suite on latest memo")
        if verts.get("ids"):
            acts.append(f"Or vertical suite: pro-suite --vertical {verts['ids'][0]}")
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
        f"rubrics={s['catalog']['rubrics']} "
        f"verticals={s.get('verticals', {}).get('count', 0)}\n\n",
        "## Next actions\n",
    ]
    for a in s["next_actions"]:
        lines.append(f"- {a}\n")
    lines.append("\n> Research only — not investment advice.\n")
    return "".join(lines)
