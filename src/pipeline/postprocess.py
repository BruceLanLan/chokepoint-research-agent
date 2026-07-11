"""Post-process research memos: charts, citations, quality gate, metrics."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.charts.scorecard import charts_from_memo
from src.config import get_settings
from src.schemas.scorecard import extract_scorecard_table, validate_report_structure
from src.tools.filings import validate_citations


def postprocess_memo(
    title: str,
    markdown: str,
    *,
    mode: str = "full",
    embed_charts: bool = True,
    min_quality: int = 0,
) -> dict[str, Any]:
    """Enrich and validate a memo. Does not call LLMs."""
    quality = validate_report_structure(markdown)
    card = extract_scorecard_table(markdown)
    try:
        cite = json.loads(validate_citations.invoke({"markdown_report": markdown}))
    except Exception:  # noqa: BLE001
        cite = {}

    charts_meta: dict[str, Any] = {"nodes": len(card.nodes)}
    chart_path = None
    enriched = markdown
    if embed_charts and card.nodes:
        charts = charts_from_memo(markdown)
        out_dir = Path(get_settings().reports_dir) / "charts"
        out_dir.mkdir(parents=True, exist_ok=True)
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in title)[:40]
        chart_path = out_dir / f"scorecard_{safe}_{datetime.now().strftime('%H%M%S')}.svg"
        chart_path.write_text(charts["scorecard_svg"], encoding="utf-8")
        charts_meta["svg_path"] = str(chart_path.resolve())
        # append note (not raw SVG into md for portability)
        if "scorecard chart" not in markdown.lower() and "Scorecard 图" not in markdown:
            enriched = (
                markdown.rstrip()
                + f"\n\n## Scorecard 图\n\n- SVG: `{chart_path.name}` "
                f"(reports/charts/)\n"
            )

    gate_ok = quality.get("score", 0) >= min_quality if min_quality else True
    if min_quality and not quality.get("pass"):
        gate_ok = False

    result = {
        "title": title,
        "mode": mode,
        "markdown": enriched,
        "quality": quality,
        "citations": cite,
        "scorecard_nodes": len(card.nodes),
        "charts": charts_meta,
        "gate_ok": gate_ok,
        "min_quality": min_quality,
        "processed_at": datetime.now().isoformat(timespec="seconds"),
        "disclaimer": "research_only_not_investment_advice",
    }
    _append_metrics(result)
    return result


def _append_metrics(row: dict[str, Any]) -> None:
    path = Path(get_settings().reports_dir).parent / "data" / "metrics.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    slim = {
        "at": row.get("processed_at"),
        "mode": row.get("mode"),
        "quality": (row.get("quality") or {}).get("score"),
        "gate_ok": row.get("gate_ok"),
        "scorecard_nodes": row.get("scorecard_nodes"),
        "urls": (row.get("citations") or {}).get("unique_urls"),
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(slim, ensure_ascii=False) + "\n")


def metrics_summary(limit: int = 100) -> dict[str, Any]:
    path = Path(get_settings().reports_dir).parent / "data" / "metrics.jsonl"
    if not path.is_file():
        return {"count": 0, "rows": []}
    lines = path.read_text(encoding="utf-8").strip().splitlines()[-limit:]
    rows = []
    for line in lines:
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    scores = [r["quality"] for r in rows if isinstance(r.get("quality"), (int, float))]
    return {
        "count": len(rows),
        "quality_avg": round(sum(scores) / len(scores), 1) if scores else None,
        "gate_pass_rate": (
            round(sum(1 for r in rows if r.get("gate_ok")) / len(rows), 3) if rows else None
        ),
        "recent": rows[-10:],
    }
