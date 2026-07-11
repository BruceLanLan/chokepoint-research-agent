"""Structured multi-memo comparison (quality, sections, scorecard, citations)."""

from __future__ import annotations

import json
from typing import Any

from src.schemas.scorecard import extract_scorecard_table, validate_report_structure
from src.tools.filings import validate_citations
from src.tools.reports import read_report


def _section_headings(md: str) -> list[str]:
    heads = []
    for line in (md or "").splitlines():
        if line.startswith("#"):
            heads.append(line.lstrip("#").strip()[:80])
    return heads


def analyze_memo(name: str) -> dict[str, Any]:
    body = read_report(name)
    if body is None:
        return {"name": name, "error": "not found"}
    quality = validate_report_structure(body)
    card = extract_scorecard_table(body)
    try:
        cite = json.loads(validate_citations.invoke({"markdown_report": body}))
    except Exception:  # noqa: BLE001
        cite = {}
    return {
        "name": name,
        "chars": len(body),
        "lines": body.count("\n") + 1,
        "quality": quality,
        "scorecard_nodes": [n.model_dump() if hasattr(n, "model_dump") else n for n in card.nodes],
        "node_count": len(card.nodes),
        "headings": _section_headings(body),
        "citations": {
            "unique_urls": cite.get("unique_urls"),
            "url_count": cite.get("url_count") or cite.get("total_urls"),
        },
    }


def compare_memos(names: list[str]) -> dict[str, Any]:
    analyses = [analyze_memo(n) for n in names if n]
    ok = [a for a in analyses if not a.get("error")]
    # section set comparison
    heading_sets = {a["name"]: set(a.get("headings") or []) for a in ok}
    all_heads: set[str] = set()
    for s in heading_sets.values():
        all_heads |= s
    matrix = {
        h: {name: (h in heads) for name, heads in heading_sets.items()} for h in sorted(all_heads)
    }
    # scorecard node names
    node_sets = {}
    for a in ok:
        names_n = []
        for n in a.get("scorecard_nodes") or []:
            if isinstance(n, dict):
                names_n.append(str(n.get("node") or n.get("name") or ""))
            else:
                names_n.append(str(n))
        node_sets[a["name"]] = set(x for x in names_n if x)
    shared_nodes: set[str] | None = None
    for s in node_sets.values():
        shared_nodes = s if shared_nodes is None else (shared_nodes & s)
    shared_nodes = shared_nodes or set()

    quality_rank = sorted(
        [(a["name"], (a.get("quality") or {}).get("score")) for a in ok],
        key=lambda x: (x[1] is None, -(x[1] or 0)),
    )
    return {
        "reports": analyses,
        "heading_coverage": matrix,
        "shared_scorecard_nodes": sorted(shared_nodes),
        "unique_nodes": {
            name: sorted(s - shared_nodes) for name, s in node_sets.items()
        },
        "quality_rank": [{"name": n, "score": s} for n, s in quality_rank],
        "disclaimer": "research_only_not_investment_advice",
    }
