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
        meta[k.strip()] = v.strip()
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
    q = (query or "").strip().lower()
    items = build_catalog(limit=200)
    if not q:
        return items[:limit]
    hit = []
    for it in items:
        blob = (
            f"{it.get('title')} {it.get('name')} {it.get('preview')} {it.get('mode')} "
            f"{it.get('skill')} {it.get('vertical_id')} {it.get('thesis_id')}"
        ).lower()
        if q in blob:
            hit.append(it)
    return hit[:limit]
