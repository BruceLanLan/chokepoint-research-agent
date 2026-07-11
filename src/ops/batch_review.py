"""Batch structure peer-review over recent memos (offline, no LLM)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.ops.catalog import build_catalog
from src.ops.checklist import run_checklist
from src.schemas.scorecard import validate_report_structure
from src.tools.reports import read_report


def batch_structure_review(limit: int = 20) -> dict[str, Any]:
    items = build_catalog(limit=max(1, min(limit, 100)))
    rows = []
    for it in items:
        name = it.get("name") or ""
        body = read_report(name) or ""
        quality = validate_report_structure(body) if body else {"score": 0, "pass": False}
        check = run_checklist(report_name=name) if body else {"gate_ok": False, "passed": 0, "total": 0}
        rows.append(
            {
                "name": name,
                "mode": it.get("mode"),
                "quality_score": quality.get("score"),
                "structure_pass": quality.get("pass"),
                "checklist_gate": check.get("gate_ok"),
                "checklist_passed": f"{check.get('passed')}/{check.get('total')}",
                "modified": it.get("modified"),
            }
        )
    rows.sort(key=lambda r: (not r.get("checklist_gate"), -(r.get("quality_score") or 0)))
    fail = [r for r in rows if not r.get("checklist_gate")]
    return {
        "reviewed": len(rows),
        "gate_fail_count": len(fail),
        "gate_pass_rate": round((len(rows) - len(fail)) / len(rows), 3) if rows else None,
        "failures": fail[:15],
        "all": rows,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "disclaimer": "research_only_not_investment_advice",
        "note": "Structure/process review only — not factual accuracy or investment merit.",
    }
