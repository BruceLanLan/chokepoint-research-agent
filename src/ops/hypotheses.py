"""Lightweight research hypotheses (pre-thesis scratchpad)."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from src.config import get_settings

Status = Literal["open", "testing", "promoted", "rejected"]


def _path() -> Path:
    base = Path(get_settings().reports_dir).parent / "data"
    base.mkdir(parents=True, exist_ok=True)
    return base / "hypotheses.json"


def _load() -> dict[str, Any]:
    p = _path()
    if not p.is_file():
        return {"version": 1, "items": []}
    raw = p.read_text(encoding="utf-8").strip()
    if not raw:
        return {"version": 1, "items": []}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {"version": 1, "items": []}
    if not isinstance(data, dict):
        return {"version": 1, "items": []}
    data.setdefault("items", [])
    return data


def _save(data: dict[str, Any]) -> None:
    data["updated_at"] = datetime.now().isoformat(timespec="seconds")
    _path().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def add_hypothesis(
    statement: str,
    *,
    system: str = "",
    evidence_needed: list[str] | None = None,
    related_thesis_id: str | None = None,
) -> dict[str, Any]:
    data = _load()
    item = {
        "id": uuid.uuid4().hex[:10],
        "statement": statement.strip(),
        "system": system.strip(),
        "evidence_needed": evidence_needed or [],
        "related_thesis_id": related_thesis_id,
        "status": "open",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    data["items"].append(item)
    _save(data)
    return item


def list_hypotheses(status: str | None = None) -> list[dict[str, Any]]:
    items = list(_load().get("items") or [])
    if status:
        items = [i for i in items if i.get("status") == status]
    return items


def set_hypothesis_status(hid: str, status: Status, note: str = "") -> dict[str, Any] | None:
    data = _load()
    for it in data.get("items") or []:
        if it.get("id") == hid:
            it["status"] = status
            it["updated_at"] = datetime.now().isoformat(timespec="seconds")
            it.setdefault("notes", []).append(
                {"at": it["updated_at"], "status": status, "note": note}
            )
            _save(data)
            return it
    return None


def promote_to_thesis(hid: str) -> dict[str, Any]:
    """Create a thesis from a hypothesis (still research notebook, not advice)."""
    from src.ops.theses import add_thesis

    items = list_hypotheses()
    hyp = next((i for i in items if i.get("id") == hid), None)
    if not hyp:
        return {"error": "hypothesis not found"}
    thesis = add_thesis(
        title=(hyp.get("statement") or "")[:80],
        statement=hyp.get("statement") or "",
        system=hyp.get("system") or "",
        kill_criteria=["(define kill criteria)"],
        status="watching",
    )
    set_hypothesis_status(hid, "promoted", note=f"thesis:{thesis.get('id')}")
    return {"hypothesis": hid, "thesis": thesis}
