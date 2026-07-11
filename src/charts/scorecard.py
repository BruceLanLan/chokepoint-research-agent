"""SVG chart widgets for research memos (no heavy deps)."""

from __future__ import annotations

import html
from typing import Any

from src.schemas.scorecard import ChokepointScorecard, NodeScore, extract_scorecard_table


def scorecard_bar_chart_svg(card: ChokepointScorecard, width: int = 640, row_h: int = 28) -> str:
    nodes = card.top_nodes(8) if card.nodes else []
    if not nodes:
        return _empty_svg("No scorecard nodes parsed", width)
    height = 40 + len(nodes) * row_h + 20
    max_total = 25  # 5 dims * 5
    bars = []
    y0 = 36
    for i, n in enumerate(nodes):
        y = y0 + i * row_h
        w = max(2, int((n.total / max_total) * (width - 180)))
        label = html.escape((n.node or "")[:28])
        bars.append(
            f'<text x="8" y="{y + 14}" font-size="11" fill="#334">{label}</text>'
            f'<rect x="160" y="{y}" width="{w}" height="16" rx="3" fill="#3d7fe0"/>'
            f'<text x="{168 + w}" y="{y + 13}" font-size="10" fill="#555">{n.total}/25</text>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#fafbff"/>
  <text x="8" y="20" font-size="13" font-weight="600" fill="#111">Chokepoint Scorecard (total)</text>
  {''.join(bars)}
  <text x="8" y="{height - 6}" font-size="9" fill="#888">Research only — not investment advice</text>
</svg>"""


def price_line_chart_svg(
    points: list[tuple[str, float]],
    title: str = "Price series",
    width: int = 640,
    height: int = 220,
) -> str:
    if len(points) < 2:
        return _empty_svg("Not enough price points", width, height)
    ys = [p[1] for p in points]
    lo, hi = min(ys), max(ys)
    span = (hi - lo) or 1.0
    pad_l, pad_r, pad_t, pad_b = 40, 12, 28, 28
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b
    coords = []
    for i, (_d, v) in enumerate(points):
        x = pad_l + (i / (len(points) - 1)) * plot_w
        y = pad_t + (1 - (v - lo) / span) * plot_h
        coords.append(f"{x:.1f},{y:.1f}")
    poly = " ".join(coords)
    t = html.escape(title[:60])
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#fafbff"/>
  <text x="8" y="18" font-size="13" font-weight="600" fill="#111">{t}</text>
  <polyline fill="none" stroke="#3d7fe0" stroke-width="2" points="{poly}"/>
  <text x="8" y="{height - 8}" font-size="9" fill="#888">lo={lo:.2f} hi={hi:.2f} · research only</text>
</svg>"""


def _empty_svg(msg: str, width: int = 640, height: int = 80) -> str:
    m = html.escape(msg)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
  <rect width="100%" height="100%" fill="#f5f5f5"/>
  <text x="12" y="28" font-size="12" fill="#666">{m}</text>
</svg>"""


def charts_from_memo(markdown: str) -> dict[str, str]:
    card = extract_scorecard_table(markdown)
    return {
        "scorecard_svg": scorecard_bar_chart_svg(card),
        "nodes": len(card.nodes),
    }


def fetch_price_points(symbol: str, period: str = "6mo") -> list[tuple[str, float]]:
    """Best-effort Yahoo history via yfinance."""
    try:
        import yfinance as yf

        from src.tools.research_tools import normalize_symbol

        t = yf.Ticker(normalize_symbol(symbol))
        hist = t.history(period=period)
        if hist is None or hist.empty:
            return []
        pts: list[tuple[str, float]] = []
        for idx, row in hist.iterrows():
            try:
                pts.append((str(idx.date()), float(row["Close"])))
            except Exception:  # noqa: BLE001
                continue
        # downsample to ~60 points
        if len(pts) > 60:
            step = len(pts) // 60
            pts = pts[::step]
        return pts
    except Exception:  # noqa: BLE001
        return []
