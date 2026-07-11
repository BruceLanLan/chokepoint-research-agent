"""SVG coverage heat strip for watchlist density."""

from __future__ import annotations

from typing import Any

from src.ops.coverage_heat import coverage_heatmap


def coverage_heat_svg(max_items: int = 24) -> str:
    data = coverage_heatmap()
    rows = (data.get("symbols") or [])[:max_items]
    colors = {"hot": "#ff6b6b", "warm": "#f0b429", "cold": "#3d5a80"}
    w = 720
    row_h = 28
    h = 60 + row_h * max(1, len(rows))
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        f'<rect width="100%" height="100%" fill="#0a0e17"/>',
        f'<text x="16" y="28" fill="#e8eefc" font-size="16" font-family="system-ui,sans-serif">'
        f"Coverage heat (research density)</text>",
        f'<text x="16" y="48" fill="#8b9bb8" font-size="11" font-family="system-ui,sans-serif">'
        f"Research only — not investment advice</text>",
    ]
    if not rows:
        parts.append(
            f'<text x="16" y="90" fill="#8b9bb8" font-size="13">Empty watchlist</text>'
        )
    for i, r in enumerate(rows):
        y = 64 + i * row_h
        heat = r.get("heat") or "cold"
        score = int(r.get("coverage_score") or 0)
        bar_w = min(420, 40 + score * 55)
        parts.append(
            f'<rect x="16" y="{y}" width="{bar_w}" height="18" rx="4" fill="{colors.get(heat, "#3d5a80")}" opacity="0.85"/>'
        )
        label = f'{r.get("symbol")}  thesis={r.get("thesis_count")} reports={r.get("report_count")} [{heat}]'
        parts.append(
            f'<text x="24" y="{y + 13}" fill="#0a0e17" font-size="11" font-family="ui-monospace,monospace">{_esc(label)}</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts)


def _esc(s: str) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def coverage_chart_meta() -> dict[str, Any]:
    return {
        "svg": coverage_heat_svg(),
        "data": coverage_heatmap(),
        "disclaimer": "research_only_not_investment_advice",
    }
