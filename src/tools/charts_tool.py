"""Agent tools + helpers for chart widgets."""

from __future__ import annotations

from pathlib import Path

from langchain.tools import tool

from src.charts.scorecard import charts_from_memo, fetch_price_points, price_line_chart_svg
from src.config import get_settings


@tool(parse_docstring=True)
def render_scorecard_chart(markdown_report: str) -> str:
    """Parse a memo scorecard table and render an SVG bar chart (saved under reports/charts).

    Args:
        markdown_report: Markdown text containing a scorecard table

    Returns:
        Path to SVG file or message if empty
    """
    charts = charts_from_memo(markdown_report)
    if charts.get("nodes", 0) == 0:
        return "No scorecard nodes found to chart."
    out_dir = Path(get_settings().reports_dir) / "charts"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "scorecard_latest.svg"
    path.write_text(charts["scorecard_svg"], encoding="utf-8")
    return f"SVG saved: {path.resolve()} (nodes={charts['nodes']})"


@tool(parse_docstring=True)
def render_price_chart(symbol: str, period: str = "6mo") -> str:
    """Render a simple SVG price chart from Yahoo history.

    Args:
        symbol: Ticker e.g. AAPL, NVDA, 0700.HK
        period: yfinance period string (1mo, 3mo, 6mo, 1y)

    Returns:
        Path to SVG or error message
    """
    pts = fetch_price_points(symbol, period=period)
    if len(pts) < 2:
        return f"No price history for {symbol}"
    svg = price_line_chart_svg(pts, title=f"{symbol} ({period})")
    out_dir = Path(get_settings().reports_dir) / "charts"
    out_dir.mkdir(parents=True, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in symbol)
    path = out_dir / f"price_{safe}.svg"
    path.write_text(svg, encoding="utf-8")
    return f"SVG saved: {path.resolve()} points={len(pts)}"
