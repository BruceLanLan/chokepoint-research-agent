"""Report tags / collections store (local JSON)."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import get_settings


def _path() -> Path:
    base = Path(get_settings().reports_dir).parent / "data"
    base.mkdir(parents=True, exist_ok=True)
    return base / "report_tags.json"


def _load() -> dict[str, Any]:
    p = _path()
    if not p.is_file():
        return {"version": 1, "tags": {}, "collections": {}}
    return json.loads(p.read_text(encoding="utf-8"))


def _save(data: dict[str, Any]) -> None:
    data["updated_at"] = datetime.now().isoformat(timespec="seconds")
    _path().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def tag_report(report_name: str, tags: list[str]) -> dict[str, Any]:
    data = _load()
    clean = sorted({t.strip().lower() for t in tags if t and t.strip()})
    data.setdefault("tags", {})[report_name] = clean
    _save(data)
    return {"report": report_name, "tags": clean}


def get_tags(report_name: str | None = None) -> dict[str, Any]:
    data = _load()
    tags = data.get("tags") or {}
    if report_name:
        return {"report": report_name, "tags": tags.get(report_name, [])}
    return {"tags": tags}


def find_by_tag(tag: str) -> list[str]:
    t = tag.strip().lower()
    data = _load()
    return [name for name, tags in (data.get("tags") or {}).items() if t in tags]


def create_collection(name: str, reports: list[str] | None = None, note: str = "") -> dict[str, Any]:
    data = _load()
    key = name.strip().lower().replace(" ", "_")
    item = {
        "id": key,
        "name": name.strip(),
        "reports": list(reports or []),
        "note": note,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    data.setdefault("collections", {})[key] = item
    _save(data)
    return item


def list_collections() -> list[dict[str, Any]]:
    data = _load()
    return list((data.get("collections") or {}).values())


def add_to_collection(collection_id: str, report_name: str) -> dict[str, Any] | None:
    data = _load()
    col = (data.get("collections") or {}).get(collection_id)
    if not col:
        return None
    reps = list(col.get("reports") or [])
    if report_name not in reps:
        reps.append(report_name)
    col["reports"] = reps
    col["updated_at"] = datetime.now().isoformat(timespec="seconds")
    data["collections"][collection_id] = col
    _save(data)
    return col
