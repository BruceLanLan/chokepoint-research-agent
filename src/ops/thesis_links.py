"""Hard links between theses and research reports."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import get_settings
from src.ops.theses import get_thesis, list_theses


def _path() -> Path:
    base = Path(get_settings().reports_dir).parent / "data"
    base.mkdir(parents=True, exist_ok=True)
    return base / "thesis_report_links.json"


def _load() -> dict[str, Any]:
    p = _path()
    if not p.is_file():
        return {"version": 1, "links": []}
    raw = p.read_text(encoding="utf-8").strip()
    if not raw:
        return {"version": 1, "links": []}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {"version": 1, "links": []}
    data.setdefault("links", [])
    return data


def _save(data: dict[str, Any]) -> None:
    data["updated_at"] = datetime.now().isoformat(timespec="seconds")
    _path().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def link_report_to_thesis(
    thesis_id: str,
    report_name: str,
    *,
    rel: str = "supports",
) -> dict[str, Any]:
    if not get_thesis(thesis_id):
        return {"error": f"thesis not found: {thesis_id}"}
    data = _load()
    link = {
        "thesis_id": thesis_id,
        "report": report_name,
        "rel": rel,
        "at": datetime.now().isoformat(timespec="seconds"),
    }
    # dedupe
    for existing in data["links"]:
        if existing.get("thesis_id") == thesis_id and existing.get("report") == report_name:
            existing.update(link)
            _save(data)
            return existing
    data["links"].append(link)
    _save(data)
    return link


def links_for_thesis(thesis_id: str) -> list[dict[str, Any]]:
    return [l for l in _load().get("links") or [] if l.get("thesis_id") == thesis_id]


def links_for_report(report_name: str) -> list[dict[str, Any]]:
    return [l for l in _load().get("links") or [] if l.get("report") == report_name]


def graph_edges() -> dict[str, Any]:
    links = _load().get("links") or []
    theses = {t.get("id"): t.get("title") for t in list_theses()}
    return {
        "links": links,
        "thesis_titles": theses,
        "count": len(links),
        "disclaimer": "research_only_not_investment_advice",
    }
