"""Process research queue items (mock offline or live LLM via injectible run_fn)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

from src.ops.audit import log_event
from src.ops.research_queue import list_queue, next_queued, set_status
from src.ops.tags import tag_report
from src.pipeline.postprocess import postprocess_memo
from src.tools.reports import save_report_file


RunFn = Callable[[str, str, str | None], dict[str, Any]]
# run_fn(question, mode, skill) -> {report, quality?, ...}


def mock_run_fn(question: str, mode: str, skill: str | None = None) -> dict[str, Any]:
    """Deterministic offline runner for tests / dry-run (no LLM)."""
    body = (
        f"# Queue mock memo\n\n"
        f"## 研究结论\n"
        f"Offline queue worker processed: {question[:200]}\n\n"
        f"## 风险与证伪 / Kill criteria\n"
        f"- Mock kill: thesis fails if primary node is multi-sourced\n\n"
        f"## 来源\n"
        f"- https://example.com/mock-queue\n"
        f"- mode={mode} skill={skill or '-'}\n\n"
        f"| 节点 | 不可替代 | 集中度 | 杠杆 | 真空 | 拐点 | 备注 |\n"
        f"|------|---------|--------|------|------|------|------|\n"
        f"| mock-node | 4 | 4 | 4 | 3 | 3 | offline |\n"
    )
    return {"report": body, "quality": {"score": 70, "pass": True}, "mock": True}


def process_one(
    *,
    run_fn: RunFn | None = None,
    dry_run: bool = False,
    auto_tag: bool = True,
) -> dict[str, Any]:
    """Pop next queued item and process it. dry_run uses mock_run_fn."""
    item = next_queued()
    if not item:
        return {"ok": True, "processed": False, "reason": "queue_empty"}

    item_id = item["id"]
    set_status(item_id, "running")
    fn = mock_run_fn if dry_run or run_fn is None else run_fn
    try:
        result = fn(item["question"], item.get("mode") or "chokepoint_fast", item.get("skill"))
        report = (result or {}).get("report") or ""
        if not report:
            raise RuntimeError("empty report from run_fn")

        pp = postprocess_memo(
            item["question"][:40],
            report,
            mode=item.get("mode") or "chokepoint_fast",
            embed_charts=False,
            min_quality=0,
        )
        path = save_report_file(
            title=item["question"][:40],
            markdown_body=pp["markdown"],
            mode=item.get("mode") or "chokepoint_fast",
            quality=pp.get("quality"),
        )
        report_name = path.rsplit("/", 1)[-1]
        if auto_tag:
            tags = ["queue", "auto"]
            if item.get("skill"):
                tags.append(str(item["skill"]))
            if item.get("source"):
                tags.append(str(item["source"]).split(":")[0])
            tag_report(report_name, tags)

        set_status(item_id, "done", report=report_name)
        log_event(
            "queue_processed",
            detail={
                "id": item_id,
                "report": report_name,
                "dry_run": dry_run or run_fn is None,
                "mode": item.get("mode"),
            },
        )
        return {
            "ok": True,
            "processed": True,
            "id": item_id,
            "report": report_name,
            "path": path,
            "quality": pp.get("quality"),
            "dry_run": dry_run or run_fn is None,
            "at": datetime.now().isoformat(timespec="seconds"),
        }
    except Exception as exc:  # noqa: BLE001
        set_status(item_id, "failed", error=str(exc)[:500])
        log_event("queue_failed", detail={"id": item_id, "error": str(exc)[:200]})
        return {"ok": False, "processed": True, "id": item_id, "error": str(exc)}


def process_batch(
    *,
    n: int = 1,
    run_fn: RunFn | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Process up to n queued items sequentially."""
    n = max(1, min(int(n or 1), 20))
    results = []
    for _ in range(n):
        if not next_queued():
            break
        results.append(process_one(run_fn=run_fn, dry_run=dry_run))
    return {
        "count": len(results),
        "results": results,
        "remaining_queued": len(list_queue(status="queued")),
        "disclaimer": "research_only_not_investment_advice",
    }
