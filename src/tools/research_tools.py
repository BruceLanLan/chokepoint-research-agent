"""Research tools: web search, page fetch, market snapshot, report save."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx
from langchain.tools import tool
from markdownify import markdownify

from src.config import get_settings


def _tavily_client():
    from tavily import TavilyClient

    settings = get_settings()
    if not settings.tavily_api_key:
        return None
    return TavilyClient(api_key=settings.tavily_api_key)


def fetch_webpage_content(url: str, timeout: float = 12.0, max_chars: int = 12000) -> str:
    """Fetch a URL and convert HTML to markdown (truncated)."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
    }
    try:
        with httpx.Client(follow_redirects=True, timeout=timeout) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            content_type = resp.headers.get("content-type", "")
            if (
                "html" in content_type
                or url.endswith((".html", ".htm"))
                or "<html" in resp.text[:200].lower()
            ):
                text = markdownify(resp.text)
            else:
                text = resp.text
            text = re.sub(r"\n{3,}", "\n\n", text).strip()
            if len(text) > max_chars:
                text = text[:max_chars] + "\n\n...[truncated]..."
            return text
    except Exception as exc:  # noqa: BLE001
        return f"Error fetching {url}: {exc}"


@tool(parse_docstring=True)
def web_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
) -> str:
    """Search the web for investment-related information.

    Args:
        query: Search query (Chinese or English). Be specific: ticker, company, date range.
        max_results: Max results to return (1-8, default 5).
        topic: Topic filter: general | news | finance. Use finance for filings/valuation,
            news for catalysts, general for technical supply-chain queries.

    Returns:
        Formatted search hits with title, url, snippet.
    """
    client = _tavily_client()
    if client is None:
        return (
            "Search unavailable: TAVILY_API_KEY not configured. "
            "Continue with filings tools, knowledge maps, and explicit offline evidence. "
            "Get a key at https://tavily.com — research only, not investment advice."
        )
    try:
        max_results = max(1, min(int(max_results or 5), 8))
    except (TypeError, ValueError):
        max_results = 5
    topic = topic if topic in {"general", "news", "finance"} else "general"

    raw = client.search(
        query,
        max_results=max_results,
        topic=topic,
        include_raw_content=False,
    )
    results = raw.get("results") or []
    if not results:
        return f"No results for query: {query}"

    blocks: list[str] = []
    for i, item in enumerate(results, 1):
        title = item.get("title") or "(no title)"
        url = item.get("url") or ""
        content = (item.get("content") or "").strip()
        score = item.get("score")
        header = f"### [{i}] {title}\nURL: {url}"
        if score is not None:
            try:
                header += f"\nRelevance: {float(score):.3f}"
            except (TypeError, ValueError):
                pass
        blocks.append(f"{header}\n\n{content}")

    return f"Search results for `{query}` (topic={topic}):\n\n" + "\n\n---\n\n".join(blocks)


@tool(parse_docstring=True)
def fetch_url(url: str) -> str:
    """Fetch full webpage content as markdown for deeper reading.

    Args:
        url: Absolute http(s) URL to fetch.

    Returns:
        Markdown text content (truncated if long).
    """
    if not url.startswith(("http://", "https://")):
        return "Invalid URL: must start with http:// or https://"
    body = fetch_webpage_content(url)
    return f"# Source: {url}\n\n{body}"


def normalize_symbol(symbol: str) -> str:
    """Normalize ticker strings for Yahoo Finance."""
    symbol = symbol.strip().upper()
    if re.fullmatch(r"\d{6}", symbol):
        return f"{symbol}.SS" if symbol.startswith(("5", "6", "9")) else f"{symbol}.SZ"
    return symbol


@tool(parse_docstring=True)
def get_market_snapshot(symbol: str) -> str:
    """Get a late-ish market snapshot via Yahoo Finance (best effort).

    Args:
        symbol: Ticker symbol. Examples: AAPL, NVDA, TSLA, 9988.HK, 0700.HK, 600519.SS, 000001.SZ

    Returns:
        JSON-like text with price, change, market cap, PE, 52w range when available.
    """
    try:
        import yfinance as yf
    except ImportError:
        return "yfinance not installed; skip market snapshot."

    symbol = normalize_symbol(symbol)

    try:
        t = yf.Ticker(symbol)
        info: dict[str, Any] = {}
        try:
            fi = t.fast_info
            info.update(
                {
                    "last_price": getattr(fi, "last_price", None),
                    "previous_close": getattr(fi, "previous_close", None),
                    "market_cap": getattr(fi, "market_cap", None),
                    "year_high": getattr(fi, "year_high", None),
                    "year_low": getattr(fi, "year_low", None),
                    "currency": getattr(fi, "currency", None),
                }
            )
        except Exception:  # noqa: BLE001
            pass

        try:
            meta = t.info or {}
            for key in (
                "shortName",
                "longName",
                "sector",
                "industry",
                "trailingPE",
                "forwardPE",
                "priceToBook",
                "dividendYield",
                "fiftyTwoWeekHigh",
                "fiftyTwoWeekLow",
                "averageVolume",
                "currency",
                "exchange",
                "quoteType",
            ):
                if key in meta and meta[key] is not None:
                    info.setdefault(key, meta[key])
            if "currentPrice" in meta:
                info.setdefault("last_price", meta["currentPrice"])
            if "marketCap" in meta:
                info.setdefault("market_cap", meta["marketCap"])
        except Exception:  # noqa: BLE001
            pass

        if not info:
            return f"No market data found for {symbol}. Try another ticker format."

        payload = {
            "symbol": symbol,
            "as_of_utc": datetime.now(timezone.utc).isoformat(),
            "data": info,
            "note": "Yahoo Finance 数据可能有延迟，A股/港股代码格式需带交易所后缀。",
        }
        return json.dumps(payload, ensure_ascii=False, indent=2, default=str)
    except Exception as exc:  # noqa: BLE001
        return f"Market snapshot failed for {symbol}: {exc}"


@tool(parse_docstring=True)
def save_research_report(title: str, markdown_body: str) -> str:
    """Save the final research report to the reports directory.

    Args:
        title: Short title used in filename, e.g. "NVDA_2026Q2" or "宁德时代深度".
        markdown_body: Full markdown report content.

    Returns:
        Absolute path of the saved report file.
    """
    from src.tools.reports import save_report_file

    path = save_report_file(title=title, markdown_body=markdown_body)
    return f"Report saved: {path}"


@tool(parse_docstring=True)
def list_saved_reports(limit: int = 20) -> str:
    """List recently saved research reports.

    Args:
        limit: Max number of reports to list (default 20).

    Returns:
        Text listing of report filenames with timestamps.
    """
    from src.tools.reports import list_reports

    items = list_reports(limit=limit)
    if not items:
        return "No reports found in reports/."
    lines = [f"- {it['name']}  ({it['size_kb']} KB, {it['modified']})" for it in items]
    return "Saved reports:\n" + "\n".join(lines)


def all_tools():
    """Tools available to lead + sub agents."""
    from src.tools.charts_tool import render_price_chart, render_scorecard_chart
    from src.tools.cn_filings import cn_company_suggest, cn_search_announcements
    from src.tools.filings import sec_recent_filings, sec_search_company, validate_citations
    from src.tools.knowledge import list_knowledge_maps, load_knowledge_map
    from src.tools.market_cn import get_cn_stock_quote, search_cn_company_news

    return [
        web_search,
        fetch_url,
        get_market_snapshot,
        get_cn_stock_quote,
        search_cn_company_news,
        cn_search_announcements,
        cn_company_suggest,
        sec_search_company,
        sec_recent_filings,
        validate_citations,
        render_scorecard_chart,
        render_price_chart,
        save_research_report,
        list_saved_reports,
        list_knowledge_maps,
        load_knowledge_map,
    ]


def researcher_tools():
    """Tools for specialist researchers (no save needed usually)."""
    from src.tools.charts_tool import render_price_chart, render_scorecard_chart
    from src.tools.cn_filings import cn_company_suggest, cn_search_announcements
    from src.tools.filings import sec_recent_filings, sec_search_company, validate_citations
    from src.tools.knowledge import list_knowledge_maps, load_knowledge_map
    from src.tools.market_cn import get_cn_stock_quote, search_cn_company_news

    return [
        web_search,
        fetch_url,
        get_market_snapshot,
        get_cn_stock_quote,
        search_cn_company_news,
        cn_search_announcements,
        cn_company_suggest,
        sec_search_company,
        sec_recent_filings,
        validate_citations,
        render_scorecard_chart,
        render_price_chart,
        list_knowledge_maps,
        load_knowledge_map,
    ]
