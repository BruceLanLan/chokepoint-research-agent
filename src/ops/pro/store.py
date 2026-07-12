"""JSONL store helper for pro modules."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import get_settings


def data_file(name: str) -> Path:
    base = Path(get_settings().reports_dir).parent / "data" / "pro"
    base.mkdir(parents=True, exist_ok=True)
    return base / name


def append_jsonl(name: str, row: dict[str, Any]) -> dict[str, Any]:
    row = {
        "id": row.get("id") or uuid.uuid4().hex[:10],
        "at": datetime.now().isoformat(timespec="seconds"),
        **row,
    }
    path = data_file(name)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def read_jsonl(name: str, limit: int = 100) -> list[dict[str, Any]]:
    path = data_file(name)
    if not path.is_file():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").strip().splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows[-max(1, min(limit, 2000)):]


def write_json(name: str, data: dict[str, Any]) -> Path:
    path = data_file(name)
    data = {**data, "updated_at": datetime.now().isoformat(timespec="seconds")}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def read_json(name: str, default: dict[str, Any] | None = None) -> dict[str, Any]:
    path = data_file(name)
    if not path.is_file():
        return default or {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default or {}
