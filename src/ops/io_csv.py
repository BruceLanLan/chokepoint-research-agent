"""CSV import/export for watchlist."""

from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path
from typing import Any

from src.ops.watchlist import add_item, list_items


def export_watchlist_csv(path: str | Path | None = None) -> str:
    items = list_items()
    buf = StringIO()
    w = csv.DictWriter(
        buf,
        fieldnames=["id", "symbol", "name", "thesis", "priority", "tags", "notes"],
    )
    w.writeheader()
    for it in items:
        w.writerow(
            {
                "id": it.get("id"),
                "symbol": it.get("symbol"),
                "name": it.get("name"),
                "thesis": it.get("thesis"),
                "priority": it.get("priority"),
                "tags": "|".join(it.get("tags") or []),
                "notes": it.get("notes"),
            }
        )
    text = buf.getvalue()
    if path:
        Path(path).write_text(text, encoding="utf-8")
    return text


def import_watchlist_csv(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    if not p.is_file():
        return {"error": f"not found: {p}", "added": 0}
    added = 0
    with p.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sym = (row.get("symbol") or "").strip()
            if not sym:
                continue
            tags = [t for t in (row.get("tags") or "").split("|") if t.strip()]
            add_item(
                symbol=sym,
                name=row.get("name") or "",
                thesis=row.get("thesis") or "",
                priority=row.get("priority") or "medium",
                tags=tags,
                notes=row.get("notes") or "",
            )
            added += 1
    return {"added": added, "path": str(p)}
