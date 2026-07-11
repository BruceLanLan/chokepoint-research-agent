"""Coverage book / watchlist store (JSON file-backed)."""

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
    return base / "watchlist.json"


def _load() -> dict[str, Any]:
    p = _path()
    if not p.is_file():
        return {"version": 1, "items": [], "updated_at": None}
    return json.loads(p.read_text(encoding="utf-8"))


def _save(data: dict[str, Any]) -> None:
    data["updated_at"] = datetime.now().isoformat(timespec="seconds")
    _path().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def list_items() -> list[dict[str, Any]]:
    return list(_load().get("items") or [])


def add_item(
    *,
    symbol: str,
    name: str = "",
    thesis: str = "",
    tags: list[str] | None = None,
    priority: str = "medium",
    notes: str = "",
) -> dict[str, Any]:
    data = _load()
    item = {
        "id": uuid.uuid4().hex[:10],
        "symbol": symbol.strip().upper(),
        "name": name.strip(),
        "thesis": thesis.strip(),
        "tags": tags or [],
        "priority": priority if priority in {"low", "medium", "high"} else "medium",
        "notes": notes.strip(),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    data.setdefault("items", []).append(item)
    _save(data)
    return item


def remove_item(item_id: str) -> bool:
    data = _load()
    before = len(data.get("items") or [])
    data["items"] = [i for i in (data.get("items") or []) if i.get("id") != item_id]
    if len(data["items"]) == before:
        return False
    _save(data)
    return True


def get_item(item_id: str) -> dict[str, Any] | None:
    for i in list_items():
        if i.get("id") == item_id:
            return i
    return None


def update_item(item_id: str, **fields: Any) -> dict[str, Any] | None:
    data = _load()
    for i in data.get("items") or []:
        if i.get("id") == item_id:
            for k, v in fields.items():
                if v is not None and k in {
                    "symbol",
                    "name",
                    "thesis",
                    "tags",
                    "priority",
                    "notes",
                }:
                    i[k] = v
            i["updated_at"] = datetime.now().isoformat(timespec="seconds")
            _save(data)
            return i
    return None


def research_question_for(item: dict[str, Any]) -> str:
    sym = item.get("symbol") or ""
    name = item.get("name") or ""
    thesis = item.get("thesis") or ""
    return (
        f"覆盖标的研究：{name} ({sym})\n"
        f"既有论点：{thesis or '（无）'}\n"
        "请用 Chokepoint Theory 判断其是卡点本体还是下游 beta，"
        "给出 Scorecard 候选、关键风险与 kill criteria。"
        "仅供研究，不构成投资建议。"
    )
