"""Export all pro-module data stores into a portable zip (no secrets)."""

from __future__ import annotations

import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import get_settings
from src.ops.pro import PRO_MODULE_IDS
from src.ops.pro.registry import invoke_module
from src.ops.pro_dashboard import pro_dashboard


def export_pro_pack() -> dict[str, Any]:
    base = Path(get_settings().reports_dir).parent / "data"
    pro_dir = base / "pro"
    out_dir = base / "export_packs"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = out_dir / f"pro_modules_pack_{ts}.zip"
    dash = pro_dashboard()

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "dashboard.json",
            json.dumps(dash, ensure_ascii=False, indent=2),
        )
        zf.writestr(
            "README.txt",
            "Chokepoint pro-modules export pack\n"
            "Research only — not investment advice.\n"
            "Contains local JSONL notes under data/pro/ if present.\n",
        )
        # per-module summaries always
        for mid in PRO_MODULE_IDS:
            s = invoke_module(mid, action="summarize", limit=50)
            zf.writestr(f"summaries/{mid}.json", json.dumps(s, ensure_ascii=False, indent=2))
        # raw stores if exist
        if pro_dir.is_dir():
            for p in pro_dir.glob("*"):
                if p.is_file() and p.stat().st_size < 5_000_000:
                    zf.write(p, arcname=f"data_pro/{p.name}")

    return {
        "path": str(zip_path.resolve()),
        "size_kb": round(zip_path.stat().st_size / 1024, 1),
        "modules": len(PRO_MODULE_IDS),
        "disclaimer": "research_only_not_investment_advice",
    }
