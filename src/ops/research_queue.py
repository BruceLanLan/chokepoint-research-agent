"""Local research queue — plan batch work without running LLM yet."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from src.config import get_settings

Status = Literal["queued", "running", "done", "failed", "cancelled"]


def _path() -> Path:
    base = Path(get_settings().reports_dir).parent / "data"
    base.mkdir(parents=True, exist_ok=True)
    return base / "research_queue.json"


def _load() -> dict[str, Any]:
    p = _path()
    if not p.is_file():
        return {"version": 1, "items": []}
    return json.loads(p.read_text(encoding="utf-8"))


def _save(data: dict[str, Any]) -> None:
    data["updated_at"] = datetime.now().isoformat(timespec="seconds")
    _path().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def enqueue(
    question: str,
    *,
    mode: str = "chokepoint_fast",
    skill: str | None = None,
    priority: int = 50,
    source: str = "manual",
) -> dict[str, Any]:
    data = _load()
    item = {
        "id": uuid.uuid4().hex[:10],
        "question": question.strip(),
        "mode": mode,
        "skill": skill,
        "priority": int(priority),
        "status": "queued",
        "source": source,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "result_report": None,
        "error": None,
    }
    data.setdefault("items", []).append(item)
    _save(data)
    return item


def enqueue_from_watchlist(limit: int = 10) -> list[dict[str, Any]]:
    from src.ops.watchlist import list_items, research_question_for

    order = {"high": 0, "medium": 1, "low": 2}
    items = sorted(list_items(), key=lambda x: order.get(x.get("priority") or "medium", 1))
    out = []
    for it in items[: max(1, min(limit, 50))]:
        out.append(
            enqueue(
                research_question_for(it),
                mode="chokepoint_fast",
                priority=10 if it.get("priority") == "high" else 50,
                source=f"watchlist:{it.get('symbol')}",
            )
        )
    return out


def enqueue_from_map(map_id: str) -> dict[str, Any]:
    from src.ops.knowledge_maps import map_research_seed

    seed = map_research_seed(map_id)
    if seed.get("error"):
        raise KeyError(seed["error"])
    return enqueue(
        seed["question"],
        mode=seed.get("mode") or "chokepoint_fast",
        source=f"map:{map_id}",
        priority=20,
    )


def list_queue(status: str | None = None) -> list[dict[str, Any]]:
    items = list(_load().get("items") or [])
    if status:
        items = [i for i in items if i.get("status") == status]
    return sorted(items, key=lambda x: (x.get("priority", 50), x.get("created_at") or ""))


def set_status(item_id: str, status: Status, *, error: str | None = None, report: str | None = None) -> dict[str, Any] | None:
    data = _load()
    for it in data.get("items") or []:
        if it.get("id") == item_id:
            it["status"] = status
            it["updated_at"] = datetime.now().isoformat(timespec="seconds")
            if error is not None:
                it["error"] = error
            if report is not None:
                it["result_report"] = report
            _save(data)
            return it
    return None


def next_queued() -> dict[str, Any] | None:
    for it in list_queue(status="queued"):
        return it
    return None


def queue_summary() -> dict[str, Any]:
    items = list_queue()
    by: dict[str, int] = {}
    for it in items:
        s = it.get("status") or "unknown"
        by[s] = by.get(s, 0) + 1
    return {
        "total": len(items),
        "by_status": by,
        "next": next_queued(),
        "disclaimer": "research_only_not_investment_advice",
    }
