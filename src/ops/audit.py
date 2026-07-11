"""Research audit trail — append-only provenance log for workstation actions."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import get_settings


def _path() -> Path:
    base = Path(get_settings().reports_dir).parent / "data"
    base.mkdir(parents=True, exist_ok=True)
    return base / "audit.jsonl"


def log_event(
    action: str,
    *,
    detail: dict[str, Any] | None = None,
    actor: str = "local",
) -> dict[str, Any]:
    row = {
        "id": uuid.uuid4().hex[:12],
        "at": datetime.now().isoformat(timespec="seconds"),
        "action": action,
        "actor": actor,
        "detail": detail or {},
    }
    path = _path()
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def list_events(limit: int = 50, action: str | None = None) -> list[dict[str, Any]]:
    path = _path()
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").strip().splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if action and row.get("action") != action:
            continue
        rows.append(row)
    return rows[-max(1, min(limit, 1000)) :]


def audit_summary() -> dict[str, Any]:
    rows = list_events(limit=1000)
    by_action: dict[str, int] = {}
    for r in rows:
        a = r.get("action") or "unknown"
        by_action[a] = by_action.get(a, 0) + 1
    return {
        "count": len(rows),
        "by_action": by_action,
        "recent": rows[-10:],
        "disclaimer": "research_only_not_investment_advice",
    }
