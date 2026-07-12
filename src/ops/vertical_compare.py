"""Compare research memos within the same deep vertical pack.

Builds on structured compare + text ratio; scoped by frontmatter vertical_id.
Research ops only — not investment advice.
"""

from __future__ import annotations

from typing import Any

from src.ops.catalog import filter_catalog
from src.ops.compare_memos import analyze_memo, compare_memos
from src.ops.report_diff import diff_reports
from src.tools.reports import parse_frontmatter, read_report

DISCLAIMER = "research_only_not_investment_advice"


def list_vertical_reports(
    vertical_id: str,
    *,
    limit: int = 20,
    skill: str = "",
) -> list[dict[str, Any]]:
    """Catalog rows for one vertical (newest first)."""
    vid = (vertical_id or "").strip()
    if not vid:
        return []
    return filter_catalog(vertical_id=vid, skill=skill, limit=limit)


def _meta_of(name: str) -> dict[str, str]:
    body = read_report(name)
    if not body:
        return {}
    return parse_frontmatter(body)


def compare_pair(
    name_a: str,
    name_b: str,
    *,
    include_udiff: bool = True,
    context: int = 2,
) -> dict[str, Any]:
    """Structured + text comparison of two memos with vertical lineage check."""
    meta_a = _meta_of(name_a)
    meta_b = _meta_of(name_b)
    if not meta_a and read_report(name_a) is None:
        return {"error": f"not found: {name_a}", "disclaimer": DISCLAIMER}
    if not meta_b and read_report(name_b) is None:
        return {"error": f"not found: {name_b}", "disclaimer": DISCLAIMER}

    va = (meta_a.get("vertical_id") or "").strip()
    vb = (meta_b.get("vertical_id") or "").strip()
    same_vertical = bool(va and vb and va == vb)
    warnings: list[str] = []
    if va and vb and va != vb:
        warnings.append(
            f"vertical_id mismatch: {name_a}={va} vs {name_b}={vb} — comparison still runs"
        )
    if not va or not vb:
        warnings.append("one or both reports lack vertical_id frontmatter")

    structured = compare_memos([name_a, name_b])
    text = diff_reports(name_a, name_b, context=context)
    if text.get("error"):
        return {**text, "disclaimer": DISCLAIMER}

    # Node deltas for analyst focus
    analyses = {a["name"]: a for a in structured.get("reports") or [] if not a.get("error")}
    nodes_a = _node_names(analyses.get(name_a) or {})
    nodes_b = _node_names(analyses.get(name_b) or {})
    only_a = sorted(nodes_a - nodes_b)
    only_b = sorted(nodes_b - nodes_a)
    shared = sorted(nodes_a & nodes_b)

    qa = (analyses.get(name_a) or {}).get("quality") or {}
    qb = (analyses.get(name_b) or {}).get("quality") or {}
    score_a = qa.get("score")
    score_b = qb.get("score")
    delta_q = None
    if isinstance(score_a, (int, float)) and isinstance(score_b, (int, float)):
        delta_q = round(float(score_b) - float(score_a), 1)

    udiff = text.get("udiff") if include_udiff else []
    if include_udiff and udiff is not None:
        udiff = udiff[:200]

    return {
        "a": {
            "name": name_a,
            "vertical_id": va or None,
            "skill": meta_a.get("skill") or None,
            "mode": meta_a.get("mode") or None,
            "quality_score": score_a,
            "node_count": len(nodes_a),
        },
        "b": {
            "name": name_b,
            "vertical_id": vb or None,
            "skill": meta_b.get("skill") or None,
            "mode": meta_b.get("mode") or None,
            "quality_score": score_b,
            "node_count": len(nodes_b),
        },
        "same_vertical": same_vertical,
        "vertical_id": va if same_vertical else None,
        "similarity_ratio": text.get("ratio"),
        "quality_delta_b_minus_a": delta_q,
        "scorecard": {
            "shared_nodes": shared,
            "only_in_a": only_a,
            "only_in_b": only_b,
        },
        "structured": {
            "quality_rank": structured.get("quality_rank"),
            "shared_scorecard_nodes": structured.get("shared_scorecard_nodes"),
            "unique_nodes": structured.get("unique_nodes"),
            "heading_coverage": structured.get("heading_coverage"),
        },
        "udiff": udiff,
        "udiff_truncated": bool(text.get("truncated")) or (include_udiff and len(text.get("udiff") or []) > 200),
        "warnings": warnings,
        "next_actions": _next_actions(same_vertical, only_a, only_b, delta_q, text.get("ratio")),
        "disclaimer": DISCLAIMER,
        "note": "Process comparison of research memos — not investment advice or a signal.",
    }


def _node_names(analysis: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    for n in analysis.get("scorecard_nodes") or []:
        if isinstance(n, dict):
            label = n.get("node") or n.get("name") or n.get("label") or ""
        else:
            label = str(n)
        label = str(label).strip()
        if label:
            out.add(label)
    return out


def _next_actions(
    same_vertical: bool,
    only_a: list[str],
    only_b: list[str],
    delta_q: float | None,
    ratio: float | None,
) -> list[str]:
    acts: list[str] = []
    if not same_vertical:
        acts.append("Prefer comparing two memos with the same vertical_id frontmatter")
    if only_a:
        acts.append(f"Nodes only in A ({len(only_a)}): review if still relevant — e.g. {only_a[0]}")
    if only_b:
        acts.append(f"Nodes only in B ({len(only_b)}): new coverage or renamed — e.g. {only_b[0]}")
    if delta_q is not None and abs(delta_q) >= 5:
        direction = "improved" if delta_q > 0 else "regressed"
        acts.append(f"Quality score {direction} by {abs(delta_q)} points (B − A)")
    if ratio is not None and ratio > 0.92:
        acts.append("High text similarity — check whether B is incremental or duplicate")
    if ratio is not None and ratio < 0.35:
        acts.append("Low similarity — confirm both memos target the same system boundary")
    if not acts:
        acts.append("Align kill criteria and evidence URLs across both memos")
    return acts[:6]


def compare_vertical_latest(
    vertical_id: str,
    *,
    include_udiff: bool = True,
) -> dict[str, Any]:
    """Compare the two most recent memos for a vertical pack."""
    rows = list_vertical_reports(vertical_id, limit=10)
    if len(rows) < 2:
        return {
            "error": f"need at least 2 reports with vertical_id={vertical_id} (found {len(rows)})",
            "vertical_id": vertical_id,
            "available": [r.get("name") for r in rows],
            "hint": "python main.py research --mock -V "
            + (vertical_id or "cpo_optics")
            + "  # run twice to produce a pair",
            "disclaimer": DISCLAIMER,
        }
    a, b = rows[1]["name"], rows[0]["name"]  # older vs newer
    out = compare_pair(a, b, include_udiff=include_udiff)
    out["pair_mode"] = "latest_two"
    out["vertical_id"] = vertical_id
    out["catalog_count"] = len(rows)
    return out


def compare_vertical(
    vertical_id: str | None = None,
    *,
    name_a: str | None = None,
    name_b: str | None = None,
    include_udiff: bool = True,
) -> dict[str, Any]:
    """Entry: either explicit pair or latest two in a vertical."""
    if name_a and name_b:
        out = compare_pair(name_a, name_b, include_udiff=include_udiff)
        if vertical_id and out.get("vertical_id") and out["vertical_id"] != vertical_id:
            out.setdefault("warnings", []).append(
                f"requested vertical_id={vertical_id} but pair resolved differently"
            )
        return out
    if not vertical_id:
        return {
            "error": "provide vertical_id or both name_a and name_b",
            "disclaimer": DISCLAIMER,
        }
    return compare_vertical_latest(vertical_id, include_udiff=include_udiff)
