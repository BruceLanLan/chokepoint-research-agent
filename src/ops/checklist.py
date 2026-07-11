"""Research process checklist — interactive gate before publishing a memo."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.ops.auto_tag import suggest_tags
from src.schemas.scorecard import extract_scorecard_table, validate_report_structure
from src.tools.filings import validate_citations
from src.tools.reports import read_report
import json


DEFAULT_CHECKS = [
    ("has_conclusion", "Contains 研究结论 / conclusion section"),
    ("has_risks", "Contains 风险 / kill criteria"),
    ("has_sources", "Contains 来源 / Sources with URLs"),
    ("has_scorecard", "Scorecard table with ≥1 node"),
    ("min_quality_50", "Structure quality score ≥ 50"),
    ("url_count_1", "At least 1 http(s) URL"),
    ("disclaimer", "Disclaimer present"),
]


def run_checklist(report_name: str | None = None, markdown: str | None = None) -> dict[str, Any]:
    body = markdown
    if report_name and not body:
        body = read_report(report_name)
    if not body:
        return {"error": "report or markdown required"}

    quality = validate_report_structure(body)
    card = extract_scorecard_table(body)
    try:
        cite = json.loads(validate_citations.invoke({"markdown_report": body}))
    except Exception:  # noqa: BLE001
        cite = {}

    results = {
        "has_conclusion": "研究结论" in body or "结论" in body or "Conclusion" in body,
        "has_risks": bool(
            quality.get("hint_hits", 0) >= 1
            or "风险" in body
            or "kill" in body.lower()
            or "证伪" in body
        ),
        "has_sources": "来源" in body or "Sources" in body or "http" in body.lower(),
        "has_scorecard": len(card.nodes) >= 1,
        "min_quality_50": int(quality.get("score") or 0) >= 50,
        "url_count_1": int(quality.get("url_count") or 0) >= 1,
        "disclaimer": "不构成投资建议" in body or "not investment advice" in body.lower(),
    }
    checks = []
    for key, label in DEFAULT_CHECKS:
        ok = bool(results.get(key))
        checks.append({"id": key, "label": label, "ok": ok})
    passed = sum(1 for c in checks if c["ok"])
    return {
        "report": report_name,
        "passed": passed,
        "total": len(checks),
        "gate_ok": passed == len(checks),
        "checks": checks,
        "quality": quality,
        "scorecard_nodes": len(card.nodes),
        "citations": {"unique_urls": cite.get("unique_urls"), "url_count": cite.get("url_count")},
        "suggested_tags": suggest_tags(body),
        "at": datetime.now().isoformat(timespec="seconds"),
        "disclaimer": "research_only_not_investment_advice",
    }
