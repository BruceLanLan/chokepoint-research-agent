"""Backup / restore local research data (watchlist, theses, sessions, jobs)."""

from __future__ import annotations

import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import get_settings


def _data_dir() -> Path:
    return Path(get_settings().reports_dir).parent / "data"


def create_backup(dest_dir: Path | None = None) -> dict[str, Any]:
    data = _data_dir()
    data.mkdir(parents=True, exist_ok=True)
    out_dir = dest_dir or (data / "backups")
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = out_dir / f"backup_{ts}.zip"
    files = []
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in data.rglob("*"):
            if p.is_file() and "backups" not in p.parts:
                arc = p.relative_to(data)
                zf.write(p, arcname=str(arc))
                files.append(str(arc))
        meta = {
            "created_at": datetime.now().isoformat(),
            "files": files,
            "disclaimer": "research_data_backup_not_advice",
        }
        zf.writestr("_backup_meta.json", json.dumps(meta, ensure_ascii=False, indent=2))
    return {"path": str(path.resolve()), "files": files, "count": len(files)}


def restore_backup(zip_path: str | Path, *, overwrite: bool = True) -> dict[str, Any]:
    zp = Path(zip_path)
    if not zp.is_file():
        return {"error": f"not found: {zp}"}
    data = _data_dir()
    data.mkdir(parents=True, exist_ok=True)
    restored = []
    with zipfile.ZipFile(zp, "r") as zf:
        for name in zf.namelist():
            if name.endswith("/") or name == "_backup_meta.json":
                continue
            target = data / name
            if target.exists() and not overwrite:
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(zf.read(name))
            restored.append(name)
    return {"restored": restored, "count": len(restored), "to": str(data)}
