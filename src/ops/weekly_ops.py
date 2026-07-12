"""Weekly research ops pack: digest + health + batch review + queue plan (offline)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.ops.batch_review import batch_structure_review
from src.ops.digest import build_workspace_digest
from src.ops.research_queue import enqueue_from_watchlist, queue_summary
from src.ops.workspace_health import workspace_health_score
from src.tools.reports import save_report_file


def run_weekly_ops(
    *,
    save: bool = True,
    enqueue_watchlist: int = 0,
) -> dict[str, Any]:
    digest = build_workspace_digest(save=False)
    health = workspace_health_score()
    review = batch_structure_review(limit=25)
    queue_before = queue_summary()
    enqueued = []
    if enqueue_watchlist and enqueue_watchlist > 0:
        enqueued = enqueue_from_watchlist(limit=enqueue_watchlist)

    md = [
        "# Weekly Research Ops Pack\n\n",
        f"generated_at: {datetime.now().isoformat(timespec='seconds')}\n\n",
        "> Research only — not investment advice.\n\n",
        f"## Workspace health: **{health.get('grade')}** ({health.get('score')})\n\n",
    ]
    for a in health.get("actions") or []:
        md.append(f"- {a}\n")
    md.append("\n## Digest snapshot\n\n")
    md.append(digest.get("markdown") or "")
    md.append("\n\n## Batch structure review\n\n")
    md.append(
        f"- reviewed: {review.get('reviewed')} gate_fail: {review.get('gate_fail_count')} "
        f"pass_rate: {review.get('gate_pass_rate')}\n"
    )
    for f in (review.get("failures") or [])[:8]:
        md.append(f"- FAIL `{f.get('name')}` score={f.get('quality_score')}\n")
    md.append("\n## Queue\n\n")
    md.append(f"- before: {queue_before.get('by_status')}\n")
    if enqueued:
        md.append(f"- enqueued from watchlist: {len(enqueued)}\n")

    vertical_cov = None
    try:
        from src.ops.vertical_coverage import vertical_coverage_dashboard

        vertical_cov = vertical_coverage_dashboard()
        md.append("\n## Vertical coverage\n\n")
        md.append(
            f"- packs with memos: {vertical_cov.get('with_memos')}/"
            f"{vertical_cov.get('packs')}  pairs: {vertical_cov.get('with_pairs')}\n"
        )
        for row in (vertical_cov.get("rows") or [])[:8]:
            md.append(
                f"- `{row.get('vertical_id')}` memos={row.get('memo_count')} "
                f"avg_q={row.get('avg_quality')}\n"
            )
        for a in (vertical_cov.get("next_actions") or [])[:4]:
            md.append(f"- action: {a}\n")
    except Exception:  # noqa: BLE001
        vertical_cov = None

    body = "".join(md)
    path = None
    if save:
        path = save_report_file(
            title=f"weekly_ops_{datetime.now().strftime('%Y%m%d')}",
            markdown_body=body,
            mode="ops",
            quality={"score": health.get("score"), "pass": True},
        )
    return {
        "health": health,
        "review": {
            "reviewed": review.get("reviewed"),
            "gate_fail_count": review.get("gate_fail_count"),
            "gate_pass_rate": review.get("gate_pass_rate"),
        },
        "enqueued": len(enqueued),
        "vertical_coverage": {
            "with_memos": (vertical_cov or {}).get("with_memos"),
            "with_pairs": (vertical_cov or {}).get("with_pairs"),
        }
        if vertical_cov
        else None,
        "saved_path": path,
        "markdown": body,
        "disclaimer": "research_only_not_investment_advice",
    }
