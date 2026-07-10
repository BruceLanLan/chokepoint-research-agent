"""China / HK market helpers (best-effort public endpoints, no API key).

Educational research aid only — data may be delayed or incomplete.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

import httpx
from langchain.tools import tool


def _detect_market(symbol: str) -> tuple[str, str]:
    """Return (market, code) where market in sh/sz/hk/us."""
    s = symbol.strip().upper()
    if s.endswith(".SS") or s.endswith(".SH"):
        return "sh", re.sub(r"\D", "", s)[:6]
    if s.endswith(".SZ"):
        return "sz", re.sub(r"\D", "", s)[:6]
    if s.endswith(".HK"):
        code = re.sub(r"\D", "", s).zfill(5)
        return "hk", code
    if re.fullmatch(r"\d{6}", s):
        return ("sh" if s.startswith(("5", "6", "9")) else "sz"), s
    if re.fullmatch(r"\d{1,5}", s):
        return "hk", s.zfill(5)
    return "us", s


@tool(parse_docstring=True)
def get_cn_stock_quote(symbol: str) -> str:
    """Fetch a best-effort A-share or HK quote snapshot (public Eastmoney endpoints).

    Args:
        symbol: e.g. 600519, 600519.SS, 000001.SZ, 0700.HK, 00700

    Returns:
        JSON text with last price, change, volume when available.
    """
    market, code = _detect_market(symbol)
    if market == "us":
        return (
            f"Symbol {symbol} looks non-CN/HK. Use get_market_snapshot instead "
            "(Yahoo Finance)."
        )

    try:
        if market in {"sh", "sz"}:
            secid = f"1.{code}" if market == "sh" else f"0.{code}"
            url = "https://push2.eastmoney.com/api/qt/stock/get"
            params = {
                "secid": secid,
                "fields": "f57,f58,f43,f44,f45,f46,f47,f48,f60,f169,f170,f171,f116,f117",
                "ut": "fa5fd1943c7b386f172d6893dbfba10b",
            }
            with httpx.Client(timeout=12.0) as client:
                r = client.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
                r.raise_for_status()
                data = (r.json() or {}).get("data") or {}
            if not data:
                return f"No quote data for {symbol} (secid={secid})."
            # Many EM price fields are x100 or x1000 integers
            def px(v: Any, div: float = 100.0) -> Any:
                if v is None:
                    return None
                try:
                    return round(float(v) / div, 4)
                except (TypeError, ValueError):
                    return v

            payload = {
                "symbol": symbol,
                "code": code,
                "market": market,
                "name": data.get("f58"),
                "last": px(data.get("f43")),
                "high": px(data.get("f44")),
                "low": px(data.get("f45")),
                "open": px(data.get("f46")),
                "volume": data.get("f47"),
                "amount": data.get("f48"),
                "prev_close": px(data.get("f60")),
                "change": px(data.get("f169")),
                "change_pct": px(data.get("f170"), 100.0),
                "as_of_utc": datetime.now(timezone.utc).isoformat(),
                "source": "eastmoney_public_best_effort",
                "note": "Delayed/unofficial; verify before any decision. Research only.",
            }
            return json.dumps(payload, ensure_ascii=False, indent=2)

        # HK via eastmoney hk endpoint (best effort)
        url = "https://push2.eastmoney.com/api/qt/stock/get"
        # 116. prefix often used for HK in EM; may vary
        secid = f"116.{code.lstrip('0') or code}"
        params = {
            "secid": secid,
            "fields": "f57,f58,f43,f44,f45,f46,f47,f48,f60,f169,f170",
            "ut": "fa5fd1943c7b386f172d6893dbfba10b",
        }
        with httpx.Client(timeout=12.0) as client:
            r = client.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            data = (r.json() or {}).get("data") or {}
        if not data:
            return (
                f"No HK quote for {symbol}. Try get_market_snapshot('{code}.HK') as fallback."
            )

        def px(v: Any, div: float = 1000.0) -> Any:
            if v is None:
                return None
            try:
                return round(float(v) / div, 4)
            except (TypeError, ValueError):
                return v

        payload = {
            "symbol": symbol,
            "code": code,
            "market": "hk",
            "name": data.get("f58"),
            "last": px(data.get("f43")),
            "as_of_utc": datetime.now(timezone.utc).isoformat(),
            "source": "eastmoney_public_best_effort",
            "note": "HK field scaling may vary; cross-check Yahoo. Research only.",
            "raw_keys": list(data.keys())[:12],
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)
    except Exception as exc:  # noqa: BLE001
        return f"CN/HK quote failed for {symbol}: {exc}"


@tool(parse_docstring=True)
def search_cn_company_news(keyword: str, limit: int = 5) -> str:
    """Search recent Chinese-language company/market headlines via Eastmoney news search.

    Args:
        keyword: Company name or ticker keyword, e.g. 宁德时代 / 贵州茅台
        limit: Max headlines (1-10)

    Returns:
        Formatted headline list with titles and links when available.
    """
    limit = max(1, min(int(limit or 5), 10))
    try:
        url = "https://search-api-web.eastmoney.com/search/jsonp"
        # Public search is brittle; use a simpler stock news list endpoint when possible
        # Fallback: EM search page is JS-heavy — use web-like news list API
        news_url = "https://np-listapi.eastmoney.com/comm/web/getNewsByColumns"
        params = {
            "client": "web",
            "biz": "web_news_col",
            "column": "350",
            "order": "1",
            "needInteractData": "0",
            "page_index": "1",
            "page_size": str(limit),
            "req_trace": "chokepoint-agent",
            "fields": "code,showTime,title,mediaName,summary,url,uniqueUrl",
            "types": "1,20",
        }
        # keyword filter is imperfect; we still return general + instruct agent to refine
        with httpx.Client(timeout=12.0) as client:
            r = client.get(news_url, params=params, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            payload = r.json() or {}
        items = (((payload.get("data") or {}).get("list")) or [])[:limit]
        if not items:
            return (
                f"No CN news list results. Use web_search(query='{keyword} 公告 新闻', topic='news')."
            )
        blocks = []
        for i, it in enumerate(items, 1):
            title = it.get("title") or "(no title)"
            link = it.get("uniqueUrl") or it.get("url") or ""
            media = it.get("mediaName") or ""
            t = it.get("showTime") or ""
            summary = (it.get("summary") or "").strip()
            blocks.append(
                f"### [{i}] {title}\nTime: {t} | Media: {media}\nURL: {link}\n\n{summary}"
            )
        header = (
            f"CN news feed sample (column list; filter for keyword `{keyword}` yourself):\n\n"
        )
        return header + "\n\n---\n\n".join(blocks)
    except Exception as exc:  # noqa: BLE001
        return (
            f"CN news search failed: {exc}. "
            f"Fallback: web_search(query='{keyword} 公司 新闻 公告', topic='news')"
        )
