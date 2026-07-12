"""Investment thesis registry (research notebook, not advice)."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from src.config import get_settings

Status = Literal["active", "watching", "invalidated", "archived"]


def _path() -> Path:
    base = Path(get_settings().reports_dir).parent / "data"
    base.mkdir(parents=True, exist_ok=True)
    return base / "theses.json"


def _load() -> dict[str, Any]:
    p = _path()
    if not p.is_file():
        return {"version": 1, "items": [], "updated_at": None}
    return json.loads(p.read_text(encoding="utf-8"))


def _save(data: dict[str, Any]) -> None:
    data["updated_at"] = datetime.now().isoformat(timespec="seconds")
    _path().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def list_theses(status: str | None = None) -> list[dict[str, Any]]:
    items = list(_load().get("items") or [])
    if status:
        items = [t for t in items if t.get("status") == status]
    return items


def add_thesis(
    *,
    title: str,
    statement: str,
    system: str = "",
    chokepoints: list[str] | None = None,
    kill_criteria: list[str] | None = None,
    related_symbols: list[str] | None = None,
    status: Status = "active",
) -> dict[str, Any]:
    data = _load()
    item = {
        "id": uuid.uuid4().hex[:10],
        "title": title.strip(),
        "statement": statement.strip(),
        "system": system.strip(),
        "chokepoints": chokepoints or [],
        "kill_criteria": kill_criteria or [],
        "related_symbols": [s.upper() for s in (related_symbols or [])],
        "status": status if status in {"active", "watching", "invalidated", "archived"} else "active",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "reviews": [],
    }
    if not item["kill_criteria"]:
        item["process_warning"] = (
            "No kill criteria — thesis will show as high process risk in kill-monitor. "
            "Add falsifiers before relying on this notebook entry."
        )
    data.setdefault("items", []).append(item)
    _save(data)
    return item


def set_status(thesis_id: str, status: Status, note: str = "") -> dict[str, Any] | None:
    data = _load()
    for t in data.get("items") or []:
        if t.get("id") == thesis_id:
            t["status"] = status
            t["updated_at"] = datetime.now().isoformat(timespec="seconds")
            t.setdefault("reviews", []).append(
                {
                    "at": datetime.now().isoformat(timespec="seconds"),
                    "status": status,
                    "note": note,
                }
            )
            _save(data)
            return t
    return None


def get_thesis(thesis_id: str) -> dict[str, Any] | None:
    for t in list_theses():
        if t.get("id") == thesis_id:
            return t
    return None


def research_question_for(thesis: dict[str, Any], mode: str = "risk_only") -> str:
    kills = "\n".join(f"- {k}" for k in (thesis.get("kill_criteria") or []))
    cps = ", ".join(thesis.get("chokepoints") or []) or "（未标注）"
    if mode == "risk_only":
        return (
            f"红蓝对抗 / 论点压力测试\n"
            f"标题：{thesis.get('title')}\n"
            f"论点：{thesis.get('statement')}\n"
            f"系统：{thesis.get('system')}\n"
            f"主张卡点：{cps}\n"
            f"已有 kill criteria：\n{kills or '- （无）'}\n"
            "请做魔鬼代言人：找反证、路径依赖、数据疑点，并更新/强化 kill criteria。"
            "仅供研究，不构成投资建议。"
        )
    return (
        f"深度研究论点：{thesis.get('title')}\n"
        f"{thesis.get('statement')}\n"
        f"系统边界：{thesis.get('system')}\n"
        f"相关代码：{', '.join(thesis.get('related_symbols') or [])}\n"
        "请用 Chokepoint 框架展开，并给出 Scorecard 与风险。"
        "仅供研究，不构成投资建议。"
    )
