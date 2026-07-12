"""Lightweight data store schema migration helper."""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import get_settings

CURRENT = 2


def _data_dir() -> Path:
    d = Path(get_settings().reports_dir).parent / "data"
    d.mkdir(parents=True, exist_ok=True)
    return d


def migrate_data_stores() -> dict[str, Any]:
    """Ensure version markers and backup legacy files once."""
    base = _data_dir()
    marker = base / "schema_version.json"
    prev = 0
    if marker.is_file():
        try:
            prev = int(json.loads(marker.read_text(encoding="utf-8")).get("version") or 0)
        except (json.JSONDecodeError, TypeError, ValueError):
            prev = 0
    actions = []
    if prev < CURRENT:
        bak = base / "backups"
        bak.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        for name in ("theses.json", "watchlist.json", "research_queue.json", "lineage.json"):
            p = base / name
            if p.is_file():
                dest = bak / f"{name}.{ts}.bak"
                shutil.copy2(p, dest)
                actions.append(f"backed_up:{name}")
        # ensure pro dir
        (base / "pro").mkdir(exist_ok=True)
        actions.append("pro_dir_ok")
        marker.write_text(
            json.dumps(
                {
                    "version": CURRENT,
                    "migrated_at": datetime.now().isoformat(timespec="seconds"),
                    "from": prev,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        actions.append(f"schema:{prev}->{CURRENT}")
    return {
        "version": CURRENT,
        "previous": prev,
        "actions": actions,
        "disclaimer": "research_only_not_investment_advice",
    }
