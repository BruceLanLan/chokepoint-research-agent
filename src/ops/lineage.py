"""Report lineage — link related memos into research chains."""

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
    return base / "lineage.json"


def _load() -> dict[str, Any]:
    p = _path()
    if not p.is_file():
        return {"version": 1, "chains": [], "links": []}
    return json.loads(p.read_text(encoding="utf-8"))


def _save(data: dict[str, Any]) -> None:
    data["updated_at"] = datetime.now().isoformat(timespec="seconds")
    _path().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def link_reports(
    parent: str,
    child: str,
    *,
    rel: str = "follows",
    note: str = "",
) -> dict[str, Any]:
    data = _load()
    link = {
        "id": uuid.uuid4().hex[:10],
        "parent": parent,
        "child": child,
        "rel": rel,
        "note": note,
        "at": datetime.now().isoformat(timespec="seconds"),
    }
    data.setdefault("links", []).append(link)
    _save(data)
    return link


def create_chain(name: str, reports: list[str] | None = None, note: str = "") -> dict[str, Any]:
    data = _load()
    chain = {
        "id": uuid.uuid4().hex[:10],
        "name": name.strip(),
        "reports": list(reports or []),
        "note": note,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    data.setdefault("chains", []).append(chain)
    # sequential follows links
    reps = chain["reports"]
    for a, b in zip(reps, reps[1:], strict=False):
        data.setdefault("links", []).append(
            {
                "id": uuid.uuid4().hex[:10],
                "parent": a,
                "child": b,
                "rel": "sequence",
                "note": f"chain:{chain['id']}",
                "at": datetime.now().isoformat(timespec="seconds"),
            }
        )
    _save(data)
    return chain


def list_lineage() -> dict[str, Any]:
    data = _load()
    return {
        "chains": data.get("chains") or [],
        "links": data.get("links") or [],
        "disclaimer": "research_only_not_investment_advice",
    }


def lineage_for(report_name: str) -> dict[str, Any]:
    data = _load()
    links = data.get("links") or []
    parents = [l for l in links if l.get("child") == report_name]
    children = [l for l in links if l.get("parent") == report_name]
    chains = [
        c
        for c in (data.get("chains") or [])
        if report_name in (c.get("reports") or [])
    ]
    return {
        "report": report_name,
        "parents": parents,
        "children": children,
        "chains": chains,
    }
