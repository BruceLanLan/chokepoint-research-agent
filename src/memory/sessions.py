"""Lightweight file-backed session memory for multi-turn research."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import get_settings


def _sessions_dir() -> Path:
    d = Path(get_settings().reports_dir).parent / "data" / "sessions"
    d.mkdir(parents=True, exist_ok=True)
    return d


def new_session_id() -> str:
    return uuid.uuid4().hex[:12]


def session_path(session_id: str) -> Path:
    safe = "".join(c for c in session_id if c.isalnum() or c in "-_")[:64]
    return _sessions_dir() / f"{safe}.json"


def load_session(session_id: str) -> dict[str, Any]:
    path = session_path(session_id)
    if not path.is_file():
        return {
            "id": session_id,
            "created_at": datetime.now().isoformat(),
            "turns": [],
            "notes": [],
        }
    return json.loads(path.read_text(encoding="utf-8"))


def append_turn(
    session_id: str,
    *,
    question: str,
    report: str,
    mode: str,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    data = load_session(session_id)
    data.setdefault("turns", []).append(
        {
            "at": datetime.now().isoformat(),
            "question": question,
            "mode": mode,
            "report_preview": (report or "")[:2000],
            "report_chars": len(report or ""),
            "meta": meta or {},
        }
    )
    data["updated_at"] = datetime.now().isoformat()
    path = session_path(session_id)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def session_context_block(session_id: str | None, max_turns: int = 3) -> str:
    if not session_id:
        return ""
    data = load_session(session_id)
    turns = data.get("turns") or []
    if not turns:
        return f"(session {session_id}: empty)"
    recent = turns[-max_turns:]
    parts = [f"## Prior session context ({session_id})"]
    for t in recent:
        parts.append(f"### Q\n{t.get('question')}\n### Preview\n{t.get('report_preview')}")
    return "\n\n".join(parts)
