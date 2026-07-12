"""SVG chart from local quote_cache history (research utility)."""

from __future__ import annotations

from typing import Any

from src.ops.quote_cache import load_history


def _extract_price(snapshot: dict[str, Any]) -> float | None:
    if not isinstance(snapshot, dict):
        return None
    for k in ("price", "regularMarketPrice", "last", "close", "regularMarketPreviousClose"):
        v = snapshot.get(k)
        try:
            if v is not None:
                return float(v)
        except (TypeError, ValueError):
            continue
    # nested
    for nest in ("quote", "data", "info"):
        inner = snapshot.get(nest)
        if isinstance(inner, dict):
            p = _extract_price(inner)
            if p is not None:
                return p
    return None


def quote_history_svg(symbol: str, *, limit: int = 60, width: int = 720, height: int = 240) -> str:
    rows = load_history(symbol, limit=limit)
    points: list[tuple[int, float]] = []
    for i, r in enumerate(rows):
        price = _extract_price(r.get("snapshot") or {})
        if price is not None:
            points.append((i, price))
    w, h = width, height
    pad = 36
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        f'<rect width="100%" height="100%" fill="#0a0e17"/>',
        f'<text x="16" y="22" fill="#e8eefc" font-size="14" font-family="system-ui,sans-serif">'
        f"Quote cache: {symbol.upper()} (research utility)</text>",
        f'<text x="16" y="{h-10}" fill="#8b9bb8" font-size="10">'
        f"Research only — not investment advice · best-effort local cache</text>",
    ]
    if len(points) < 2:
        parts.append(
            f'<text x="16" y="80" fill="#8b9bb8" font-size="13">'
            f"Need ≥2 priced snapshots in cache (quotes-cache --symbols {symbol})</text>"
        )
        parts.append("</svg>")
        return "\n".join(parts)

    ys = [p for _, p in points]
    ymin, ymax = min(ys), max(ys)
    if ymin == ymax:
        ymin -= 1
        ymax += 1
    xs = [i for i, _ in points]
    xmin, xmax = min(xs), max(xs)

    def sx(x: float) -> float:
        return pad + (x - xmin) / max(1, xmax - xmin) * (w - 2 * pad)

    def sy(y: float) -> float:
        return h - pad - (y - ymin) / (ymax - ymin) * (h - 2 * pad - 20)

    poly = " ".join(f"{sx(i):.1f},{sy(p):.1f}" for i, p in points)
    parts.append(
        f'<polyline fill="none" stroke="#5b9dff" stroke-width="2" points="{poly}"/>'
    )
    parts.append(
        f'<text x="{w-pad}" y="40" fill="#8b9bb8" font-size="11" text-anchor="end">'
        f"n={len(points)} last={ys[-1]:.4g}</text>"
    )
    parts.append("</svg>")
    return "\n".join(parts)


def quote_history_meta(symbol: str, limit: int = 60) -> dict[str, Any]:
    return {
        "symbol": symbol.upper(),
        "svg": quote_history_svg(symbol, limit=limit),
        "points": len(load_history(symbol, limit=limit)),
        "disclaimer": "research_only_not_investment_advice",
    }
