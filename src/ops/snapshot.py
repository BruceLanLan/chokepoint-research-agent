"""Workspace snapshot — zip data + recent report index (no secrets)."""

from __future__ import annotations

import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import get_settings
from src.ops.analytics import workspace_analytics
from src.ops.catalog import build_catalog


def create_snapshot(out_dir: Path | None = None) -> dict[str, Any]:
    settings = get_settings()
    root = Path(settings.reports_dir).parent
    data_dir = root / "data"
    reports_dir = Path(settings.reports_dir)
    out = out_dir or (root / "data" / "snapshots")
    out.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = out / f"workspace_snapshot_{ts}.zip"

    manifest = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "analytics": workspace_analytics(),
        "catalog_preview": build_catalog(limit=30),
        "disclaimer": "research_only_not_investment_advice",
        "note": "Secrets (.env) are never included",
    }

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        # include safe data/*.json and *.jsonl (not .env)
        if data_dir.is_dir():
            for p in data_dir.rglob("*"):
                if not p.is_file():
                    continue
                if p.suffix.lower() not in {".json", ".jsonl", ".md", ".csv", ".yml", ".yaml"}:
                    continue
                if p.name.startswith("."):
                    continue
                # skip large caches
                if "cache" in p.parts or "http_cache" in p.parts:
                    continue
                if p.stat().st_size > 5_000_000:
                    continue
                arc = f"data/{p.relative_to(data_dir)}"
                zf.write(p, arcname=arc)
        # include sample + latest few report md (not all binaries)
        if reports_dir.is_dir():
            mds = sorted(
                [p for p in reports_dir.glob("*.md")],
                key=lambda x: x.stat().st_mtime,
                reverse=True,
            )[:15]
            for p in mds:
                zf.write(p, arcname=f"reports/{p.name}")

    return {
        "path": str(zip_path.resolve()),
        "size_kb": round(zip_path.stat().st_size / 1024, 1),
        "manifest_keys": list(manifest.keys()),
    }
