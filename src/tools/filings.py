"""LangChain tools for SEC filings and citation checks."""

from __future__ import annotations

import json
import re

from langchain.tools import tool

from src.providers.base import get_registry


@tool(parse_docstring=True)
def sec_search_company(query: str) -> str:
    """Search SEC EDGAR company tickers / names (US public companies).

    Args:
        query: Ticker or company name fragment, e.g. NVDA, NVIDIA, 0001045810

    Returns:
        JSON list of matches with ticker, name, CIK.
    """
    prov = get_registry().filings("sec_edgar")
    if not prov:
        return "SEC provider unavailable"
    hits = prov.search_company(query)
    return json.dumps(hits, ensure_ascii=False, indent=2)


@tool(parse_docstring=True)
def sec_recent_filings(cik_or_ticker: str, form: str = "", limit: int = 8) -> str:
    """Fetch recent SEC filings for a CIK or US ticker.

    Args:
        cik_or_ticker: CIK (10-digit) or ticker like AAPL / NVDA
        form: Optional form filter, e.g. 10-K, 10-Q, 8-K (empty = all)
        limit: Max filings to return (1-30)

    Returns:
        JSON list of filings with dates and SEC URLs when available.
    """
    prov = get_registry().filings("sec_edgar")
    if not prov:
        return "SEC provider unavailable"
    q = cik_or_ticker.strip()
    cik = q
    if not re.fullmatch(r"\d{1,10}", re.sub(r"\D", "", q)) or not q.isdigit():
        # resolve ticker → cik
        hits = prov.search_company(q)
        if hits and "cik" in hits[0]:
            cik = hits[0]["cik"]
        elif hits and hits[0].get("error"):
            return json.dumps(hits, ensure_ascii=False)
        else:
            return json.dumps({"error": f"Could not resolve CIK for {q}", "hits": hits[:5]})
    filings = prov.recent_filings(cik, form=form or None, limit=limit)
    return json.dumps(filings, ensure_ascii=False, indent=2)


@tool(parse_docstring=True)
def validate_citations(markdown_report: str) -> str:
    """Heuristic citation quality check for a research memo.

    Args:
        markdown_report: Full or partial markdown text of the memo.

    Returns:
        JSON with url_count, has_kill_criteria, missing_sections hints, score.
    """
    text = markdown_report or ""
    urls = re.findall(r"https?://[^\s\)\]]+", text)
    has_kill = bool(re.search(r"kill\s*criteria|证伪|杀逻辑", text, re.I))
    has_risk = "风险" in text or re.search(r"\brisk", text, re.I)
    has_sources = "来源" in text or re.search(r"sources?", text, re.I)
    has_chokepoint = bool(re.search(r"chokepoint|卡脖子|物理开关|供应链", text, re.I))
    score = 0
    score += min(30, 5 * len(set(urls)))
    score += 20 if has_kill else 0
    score += 15 if has_risk else 0
    score += 15 if has_sources else 0
    score += 20 if has_chokepoint else 0
    payload = {
        "score": min(100, score),
        "unique_urls": len(set(urls)),
        "urls_sample": list(dict.fromkeys(urls))[:10],
        "has_kill_criteria": has_kill,
        "has_risk_section": bool(has_risk),
        "has_sources_section": bool(has_sources),
        "has_chokepoint_framing": has_chokepoint,
        "pass": score >= 50 and has_kill and len(urls) >= 1,
        "note": "Heuristic only — not factual correctness.",
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
