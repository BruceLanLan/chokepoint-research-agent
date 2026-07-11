"""Bundle a research memo + side artifacts into a portable zip pack."""

from __future__ import annotations

import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import get_settings
from src.ops.evidence import extract_evidence
from src.ops.lineage import lineage_for
from src.ops.tags import get_tags
from src.pipeline.postprocess import postprocess_memo
from src.tools.reports import read_report, reports_dir


def build_export_pack(report_name: str) -> dict[str, Any]:
    body = read_report(report_name)
    if body is None:
        return {"error": f"not found: {report_name}"}

    pp = postprocess_memo(report_name, body, mode="full", embed_charts=False)
    evidence = extract_evidence(body, report_name=report_name)
    lineage = lineage_for(report_name)
    tags = get_tags(report_name)

    out_dir = Path(get_settings().reports_dir).parent / "data" / "export_packs"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = Path(report_name).stem[:50]
    zip_path = out_dir / f"pack_{safe}_{ts}.zip"

    meta = {
        "report": report_name,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "quality": pp.get("quality"),
        "evidence_summary": {
            "url_count": evidence.get("url_count"),
            "domains": evidence.get("domains"),
            "tickers_cn": evidence.get("tickers_cn"),
            "tickers_us": evidence.get("tickers_us"),
        },
        "lineage": lineage,
        "tags": tags,
        "disclaimer": "research_only_not_investment_advice",
    }

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("memo.md", body)
        zf.writestr("meta.json", json.dumps(meta, ensure_ascii=False, indent=2))
        zf.writestr("evidence.json", json.dumps(evidence, ensure_ascii=False, indent=2))
        zf.writestr(
            "README.txt",
            "Chokepoint Research Agent export pack\n"
            "Research only — not investment advice.\n"
            f"Source report: {report_name}\n",
        )
        # attach sibling html/json/pdf/docx if present
        base = reports_dir()
        stem = Path(report_name).stem
        for ext in (".html", ".json", ".pdf", ".docx", ".svg"):
            for p in base.glob(f"*{stem}*{ext}"):
                if p.is_file() and p.stat().st_size < 8_000_000:
                    zf.write(p, arcname=f"siblings/{p.name}")
                    break
        charts = base / "charts"
        if charts.is_dir():
            for p in sorted(charts.glob("*.svg"))[:5]:
                zf.write(p, arcname=f"charts/{p.name}")

    return {
        "path": str(zip_path.resolve()),
        "size_kb": round(zip_path.stat().st_size / 1024, 1),
        "report": report_name,
        "meta_keys": list(meta.keys()),
    }
