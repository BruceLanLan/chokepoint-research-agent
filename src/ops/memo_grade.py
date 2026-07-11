"""Single-memo professional grade combining quality + checklist + evidence density."""

from __future__ import annotations

from typing import Any

from src.ops.checklist import run_checklist
from src.ops.evidence import extract_evidence
from src.schemas.scorecard import extract_scorecard_table, validate_report_structure
from src.tools.reports import read_report


def grade_memo(report_name: str) -> dict[str, Any]:
    body = read_report(report_name)
    if body is None:
        return {"error": f"not found: {report_name}"}
    quality = validate_report_structure(body)
    check = run_checklist(report_name=report_name)
    card = extract_scorecard_table(body)
    ev = extract_evidence(body, report_name=report_name)

    score = int(quality.get("score") or 0)
    if check.get("gate_ok"):
        score = min(100, score + 10)
    else:
        score = max(0, score - 15)
    if len(card.nodes) >= 3:
        score = min(100, score + 5)
    if int(ev.get("url_count") or 0) >= 2:
        score = min(100, score + 5)

    letter = (
        "A"
        if score >= 85
        else "B"
        if score >= 70
        else "C"
        if score >= 55
        else "D"
        if score >= 40
        else "F"
    )
    return {
        "report": report_name,
        "score": score,
        "grade": letter,
        "quality": quality,
        "checklist_gate": check.get("gate_ok"),
        "scorecard_nodes": len(card.nodes),
        "url_count": ev.get("url_count"),
        "domains": list((ev.get("domains") or {}).keys())[:10],
        "disclaimer": "research_only_not_investment_advice",
        "note": "Structure/evidence density grade — not factual accuracy or investment merit.",
    }
