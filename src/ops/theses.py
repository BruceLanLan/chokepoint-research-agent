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


def append_review_note(
    thesis_id: str,
    note: str,
    *,
    kind: str = "note",
    meta: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Append a process review note without forcing status change."""
    data = _load()
    for t in data.get("items") or []:
        if t.get("id") == thesis_id:
            entry = {
                "at": datetime.now().isoformat(timespec="seconds"),
                "status": t.get("status") or "active",
                "kind": kind,
                "note": (note or "").strip(),
            }
            if meta:
                entry["meta"] = meta
            t.setdefault("reviews", []).append(entry)
            t["updated_at"] = datetime.now().isoformat(timespec="seconds")
            _save(data)
            return t
    return None


def link_compare_to_thesis(
    thesis_id: str,
    compare_result: dict[str, Any],
) -> dict[str, Any]:
    """Store a compact compare summary on the thesis review trail."""
    if compare_result.get("error"):
        return {"error": compare_result["error"]}
    a = (compare_result.get("a") or {}).get("name")
    b = (compare_result.get("b") or {}).get("name")
    ratio = compare_result.get("similarity_ratio")
    delta = compare_result.get("quality_delta_b_minus_a")
    note = (
        f"Memo compare A={a} B={b} ratio={ratio} Δq={delta} "
        f"vertical={compare_result.get('vertical_id')}"
    )
    acts = compare_result.get("next_actions") or []
    if acts:
        note += " | next: " + "; ".join(str(x) for x in acts[:3])
    t = append_review_note(
        thesis_id,
        note,
        kind="compare",
        meta={
            "a": a,
            "b": b,
            "similarity_ratio": ratio,
            "quality_delta_b_minus_a": delta,
            "vertical_id": compare_result.get("vertical_id"),
        },
    )
    if not t:
        return {"error": f"thesis not found: {thesis_id}"}
    return {"thesis_id": thesis_id, "review_note": note, "thesis": t}


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
