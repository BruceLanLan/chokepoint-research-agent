"""Watchlist batch brief — sequential lightweight research questions."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

from src.ops.watchlist import list_items, research_question_for
from src.schemas.scorecard import validate_report_structure
from src.tools.reports import save_report_file


def build_brief_questions(limit: int = 10) -> list[dict[str, Any]]:
    items = list_items()
    # high priority first
    order = {"high": 0, "medium": 1, "low": 2}
    items = sorted(items, key=lambda x: order.get(x.get("priority") or "medium", 1))
    out = []
    for it in items[: max(1, min(limit, 50))]:
        out.append(
            {
                "item": it,
                "question": research_question_for(it),
                "mode": "chokepoint_fast",
            }
        )
    return out


def process_health_section() -> str:
    """Markdown section: kill-criteria process risks + coverage cold symbols."""
    lines = ["\n## Process health (ops)\n"]
    try:
        from src.ops.kill_monitor import kill_criteria_dashboard

        km = kill_criteria_dashboard()
        lines.append(f"- high_process_risk_theses: **{km.get('high_risk_count', 0)}**\n")
        for tid in (km.get("active_without_kills") or [])[:8]:
            lines.append(f"  - active without kill criteria: `{tid}`\n")
    except Exception as exc:  # noqa: BLE001
        lines.append(f"- kill monitor unavailable: {exc}\n")
    try:
        from src.ops.coverage_heat import coverage_heatmap

        heat = coverage_heatmap()
        cold = [s for s in (heat.get("symbols") or []) if s.get("heat") == "cold"][:8]
        lines.append(f"- cold coverage symbols: **{len(cold)}**\n")
        for s in cold:
            lines.append(f"  - `{s.get('symbol')}` reports={s.get('report_count')}\n")
    except Exception as exc:  # noqa: BLE001
        lines.append(f"- coverage heat unavailable: {exc}\n")
    lines.append("\n> Ops checks are process hygiene, not investment signals.\n")
    return "".join(lines)


def run_brief(
    *,
    invoke_fn: Callable[[str, str], str],
    limit: int = 5,
    save: bool = True,
) -> dict[str, Any]:
    """invoke_fn(question, mode) -> report markdown."""
    jobs = build_brief_questions(limit=limit)
    sections: list[str] = [
        f"# Watchlist Research Brief\n",
        f"generated_at: {datetime.now().isoformat(timespec='seconds')}\n",
        f"items: {len(jobs)}\n",
        "\n> Research only — not investment advice. 仅供研究学习，不构成投资建议。\n",
        process_health_section(),
    ]
    results = []
    for job in jobs:
        it = job["item"]
        q = job["question"]
        mode = job["mode"]
        try:
            report = invoke_fn(q, mode)
        except Exception as exc:  # noqa: BLE001
            report = f"(failed: {exc})"
        quality = validate_report_structure(report)
        results.append(
            {
                "symbol": it.get("symbol"),
                "id": it.get("id"),
                "quality": quality,
                "chars": len(report or ""),
            }
        )
        sections.append(f"\n---\n\n## {it.get('name') or ''} ({it.get('symbol')})\n\n")
        sections.append(report or "(empty)")
        sections.append("\n")

    body = "".join(sections)
    path = None
    if save and jobs:
        path = save_report_file(
            title=f"watchlist_brief_{datetime.now().strftime('%Y%m%d')}",
            markdown_body=body,
            mode="brief",
            quality={"score": "", "pass": True},
        )
    return {"results": results, "report": body, "saved_path": path, "count": len(jobs)}
