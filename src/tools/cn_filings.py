"""LangChain tools wrapping multi-source CN announcements."""

from __future__ import annotations

import json

from langchain.tools import tool

from src.providers.base import get_registry


@tool(parse_docstring=True)
def cn_search_announcements(keyword: str, limit: int = 10) -> str:
    """Search Chinese A-share / market announcements and headlines (multi-source).

    Args:
        keyword: Stock code (6-digit) or company/theme keyword, e.g. 600519, 宁德时代, 固态电池
        limit: Max items (1-30)

    Returns:
        JSON list with title/time/url/source from Eastmoney / Sina etc.
    """
    prov = get_registry().filings("cn_announcements")
    if not prov:
        return "CN announcements provider unavailable"
    # recent_filings treats arg as keyword/symbol
    items = prov.recent_filings(keyword, limit=limit)
    return json.dumps(items, ensure_ascii=False, indent=2)


@tool(parse_docstring=True)
def cn_company_suggest(query: str) -> str:
    """Suggest CN companies / symbols for a query via announcement provider search.

    Args:
        query: Company name or code fragment

    Returns:
        JSON suggestion list
    """
    prov = get_registry().filings("cn_announcements")
    if not prov:
        return "CN announcements provider unavailable"
    hits = prov.search_company(query)
    return json.dumps(hits, ensure_ascii=False, indent=2)
