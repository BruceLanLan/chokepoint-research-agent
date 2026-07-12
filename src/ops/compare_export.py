"""Export vertical compare results to reports/ (markdown + json)."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.ops.vertical_compare import compare_vertical
from src.tools.reports import reports_dir, save_report_file

DISCLAIMER = "research_only_not_investment_advice"


def compare_to_markdown(result: dict[str, Any]) -> str:
    a = result.get("a") or {}
    b = result.get("b") or {}
    sc = result.get("scorecard") or {}
    lines = [
        "# Vertical memo compare\n\n",
        f"generated_at: {datetime.now().isoformat(timespec='seconds')}\n\n",
        f"> {DISCLAIMER.replace('_', ' ')}\n\n",
        f"**A:** `{a.get('name')}` vertical={a.get('vertical_id')} q={a.get('quality_score')}\n\n",
        f"**B:** `{b.get('name')}` vertical={b.get('vertical_id')} q={b.get('quality_score')}\n\n",
        f"- same_vertical: {result.get('same_vertical')}\n",
        f"- similarity_ratio: {result.get('similarity_ratio')}\n",
        f"- quality_delta (B−A): {result.get('quality_delta_b_minus_a')}\n\n",
        "## Scorecard nodes\n\n",
        f"- shared: {', '.join(sc.get('shared_nodes') or []) or '—'}\n",
        f"- only A: {', '.join(sc.get('only_in_a') or []) or '—'}\n",
        f"- only B: {', '.join(sc.get('only_in_b') or []) or '—'}\n\n",
        "## Next actions\n\n",
    ]
    for act in result.get("next_actions") or []:
        lines.append(f"- {act}\n")
    if result.get("warnings"):
        lines.append("\n## Warnings\n\n")
        for w in result["warnings"]:
            lines.append(f"- {w}\n")
    udiff = result.get("udiff") or []
    if udiff:
        lines.append("\n## Diff (truncated)\n\n```diff\n")
        for line in udiff[:120]:
            lines.append(line + "\n")
        lines.append("```\n")
    lines.append("\n*Process compare only — not investment advice.*\n")
    return "".join(lines)


def export_compare_pack(
    *,
    vertical_id: str | None = None,
    name_a: str | None = None,
    name_b: str | None = None,
    include_udiff: bool = True,
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run compare (unless result provided) and write md+json under reports/."""
    cmp = result or compare_vertical(
        vertical_id,
        name_a=name_a,
        name_b=name_b,
        include_udiff=include_udiff,
    )
    if cmp.get("error"):
        return cmp
    md = compare_to_markdown(cmp)
    vid = cmp.get("vertical_id") or vertical_id or "pair"
    title = f"compare_{vid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    path = save_report_file(
        title,
        md,
        mode="compare",
        vertical=vid if isinstance(vid, str) else None,
        quality={"score": 80, "pass": True},
        extra_meta={
            "compare_a": (cmp.get("a") or {}).get("name"),
            "compare_b": (cmp.get("b") or {}).get("name"),
            "similarity_ratio": cmp.get("similarity_ratio"),
        },
    )
    json_path = Path(path).with_suffix(".compare.json")
    json_path.write_text(json.dumps(cmp, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "md_path": path,
        "json_path": str(json_path.resolve()),
        "compare": {
            "similarity_ratio": cmp.get("similarity_ratio"),
            "a": (cmp.get("a") or {}).get("name"),
            "b": (cmp.get("b") or {}).get("name"),
            "vertical_id": cmp.get("vertical_id"),
        },
        "disclaimer": DISCLAIMER,
    }
