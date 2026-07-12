"""Report catalog — index markdown reports with frontmatter metadata."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import get_settings


_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)


def _parse_frontmatter(text: str) -> dict[str, str]:
    m = _FM_RE.match(text)
    meta: dict[str, str] = {}
    if not m:
        return meta
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta


def build_catalog(limit: int = 100) -> list[dict[str, Any]]:
    out_dir = Path(get_settings().reports_dir)
    if not out_dir.is_dir():
        return []
    files = sorted(
        [p for p in out_dir.glob("*.md") if p.name != "SAMPLE_REPORT_FORMAT.md"],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )[: max(1, min(int(limit or 100), 500))]
    items: list[dict[str, Any]] = []
    for p in files:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        meta = _parse_frontmatter(text)
        st = p.stat()
        preview = re.sub(r"^---.*?---\s*", "", text, count=1, flags=re.S)[:280].replace("\n", " ")
        items.append(
            {
                "name": p.name,
                "path": str(p.resolve()),
                "title": meta.get("title") or p.stem,
                "mode": meta.get("mode") or "",
                "skill": meta.get("skill") or "",
                "vertical_id": meta.get("vertical_id") or "",
                "thesis_id": meta.get("thesis_id") or "",
                "quality_score": meta.get("quality_score") or "",
                "generated_at": meta.get("generated_at") or "",
                "size_kb": round(st.st_size / 1024, 1),
                "modified": datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
                "preview": preview,
            }
        )
    return items


def search_catalog(query: str, limit: int = 50) -> list[dict[str, Any]]:
    return filter_catalog(q=query, limit=limit)


def filter_catalog(
    *,
    q: str = "",
    vertical_id: str = "",
    skill: str = "",
    mode: str = "",
    limit: int = 50,
    scan_limit: int = 300,
) -> list[dict[str, Any]]:
    """Filter catalog by free text and/or frontmatter fields."""
    items = build_catalog(limit=scan_limit)
    qn = (q or "").strip().lower()
    vid = (vertical_id or "").strip().lower()
    sk = (skill or "").strip().lower()
    md = (mode or "").strip().lower()
    hit: list[dict[str, Any]] = []
    for it in items:
        if vid and (it.get("vertical_id") or "").lower() != vid:
            continue
        if sk and (it.get("skill") or "").lower() != sk:
            continue
        if md and (it.get("mode") or "").lower() != md:
            continue
        if qn:
            blob = (
                f"{it.get('title')} {it.get('name')} {it.get('preview')} {it.get('mode')} "
                f"{it.get('skill')} {it.get('vertical_id')} {it.get('thesis_id')}"
            ).lower()
            if qn not in blob:
                continue
        hit.append(it)
    return hit[: max(1, min(int(limit or 50), 200))]


def catalog_facets(*, scan_limit: int = 300) -> dict[str, Any]:
    """Distinct vertical_id / skill / mode values for UI filters."""
    items = build_catalog(limit=scan_limit)
    verticals: dict[str, int] = {}
    skills: dict[str, int] = {}
    modes: dict[str, int] = {}
    for it in items:
        v = (it.get("vertical_id") or "").strip()
        s = (it.get("skill") or "").strip()
        m = (it.get("mode") or "").strip()
        if v:
            verticals[v] = verticals.get(v, 0) + 1
        if s:
            skills[s] = skills.get(s, 0) + 1
        if m:
            modes[m] = modes.get(m, 0) + 1
    return {
        "verticals": sorted(
            [{"id": k, "count": c} for k, c in verticals.items()],
            key=lambda x: (-x["count"], x["id"]),
        ),
        "skills": sorted(
            [{"id": k, "count": c} for k, c in skills.items()],
            key=lambda x: (-x["count"], x["id"]),
        ),
        "modes": sorted(
            [{"id": k, "count": c} for k, c in modes.items()],
            key=lambda x: (-x["count"], x["id"]),
        ),
        "total_scanned": len(items),
        "disclaimer": "research_only_not_investment_advice",
    }
