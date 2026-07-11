"""Offline workspace digest — no LLM, pure local aggregation."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.ops.analytics import workspace_analytics
from src.ops.coverage_heat import coverage_heatmap
from src.ops.kill_monitor import kill_criteria_dashboard
from src.ops.quality_board import quality_leaderboard
from src.ops.research_queue import queue_summary
from src.ops.thesis_health import thesis_health_report
from src.tools.reports import save_report_file


def build_workspace_digest(*, save: bool = False) -> dict[str, Any]:
    analytics = workspace_analytics()
    kills = kill_criteria_dashboard()
    heat = coverage_heatmap()
    theses = thesis_health_report()
    quality = quality_leaderboard(limit=15)
    queue = queue_summary()

    cold = [s for s in (heat.get("symbols") or []) if s.get("heat") == "cold"][:8]
    lines = [
        "# Workspace Research Digest\n",
        f"generated_at: {datetime.now().isoformat(timespec='seconds')}\n\n",
        "> Research only — not investment advice. 仅供研究学习，不构成投资建议。\n\n",
        "## Snapshot\n",
        f"- reports: **{analytics.get('reports_count')}** (avg quality {analytics.get('quality_avg')})\n",
        f"- watchlist: **{analytics.get('watchlist_count')}**\n",
        f"- theses: **{analytics.get('theses_count')}**\n",
        f"- queue queued: **{(queue.get('by_status') or {}).get('queued', 0)}**\n",
        f"- thesis process avg: **{theses.get('avg_process_score')}**\n",
        f"- high process-risk theses: **{kills.get('high_risk_count')}**\n\n",
        "## Cold coverage\n",
    ]
    if not cold:
        lines.append("- (none or empty watchlist)\n")
    for s in cold:
        lines.append(
            f"- `{s.get('symbol')}` heat=cold reports={s.get('report_count')} thesis={s.get('thesis_count')}\n"
        )
    lines.append("\n## Weakest theses (process)\n")
    for t in (theses.get("weakest") or [])[:5]:
        lines.append(
            f"- [{t.get('grade')}] `{t.get('id')}` {t.get('title')} score={t.get('process_score')} — {', '.join(t.get('notes') or [])}\n"
        )
    lines.append("\n## Top structure-quality memos\n")
    for r in (quality.get("top") or [])[:5]:
        lines.append(f"- score={r.get('score')} `{r.get('name')}` mode={r.get('mode')}\n")
    lines.append(
        "\n## Next actions (process hygiene)\n"
        "1. Add kill criteria to active theses flagged high risk\n"
        "2. Cover cold symbols or archive them from watchlist\n"
        "3. `python main.py queue --from-watchlist` then `--run` mock before live\n"
        "4. Tag + export-pack important memos for archival\n"
    )
    body = "".join(lines)
    path = None
    if save:
        path = save_report_file(
            title=f"workspace_digest_{datetime.now().strftime('%Y%m%d')}",
            markdown_body=body,
            mode="digest",
            quality={"score": "", "pass": True},
        )
    return {
        "markdown": body,
        "saved_path": path,
        "stats": {
            "reports": analytics.get("reports_count"),
            "high_risk_theses": kills.get("high_risk_count"),
            "cold_symbols": len(cold),
            "queue": queue.get("by_status"),
        },
        "disclaimer": "research_only_not_investment_advice",
    }
