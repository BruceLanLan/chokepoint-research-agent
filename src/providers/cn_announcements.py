"""Multi-source A-share / CN market announcement & headline provider.

Sources (best-effort public endpoints, may break / delay):
1. Eastmoney news column
2. Eastmoney stock notice search (by keyword)
3. Sina finance headlines RSS-like JSON (when available)

Educational research aid — not a complete filings terminal.
"""

from __future__ import annotations

import re
from typing import Any

import httpx

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)


class CnAnnouncementProvider:
    name = "cn_announcements"

    def __init__(self, timeout: float = 12.0) -> None:
        self.timeout = timeout

    def search_company(self, query: str) -> list[dict[str, Any]]:
        q = (query or "").strip()
        if not q:
            return []
        # Return multi-source search results as "company/news hits"
        results: list[dict[str, Any]] = []
        results.extend(self._eastmoney_notice_search(q, limit=8))
        results.extend(self._eastmoney_web_search(q, limit=5))
        if not results:
            results.append(
                {
                    "query": q,
                    "hint": "No hits; use web_search(topic=news) or search_cn_company_news",
                    "source": "cn_announcements",
                }
            )
        return results[:20]

    def recent_filings(
        self, cik: str, form: str | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        """cik used as symbol/keyword for CN sources (not SEC CIK)."""
        keyword = (cik or form or "").strip() or "A股"
        limit = max(1, min(int(limit or 10), 30))
        items: list[dict[str, Any]] = []
        items.extend(self._eastmoney_notice_search(keyword, limit=limit))
        items.extend(self._eastmoney_column_news(limit=min(limit, 10)))
        items.extend(self._sina_finance_headlines(keyword, limit=min(limit, 8)))
        # de-dupe by title
        seen: set[str] = set()
        out: list[dict[str, Any]] = []
        for it in items:
            title = (it.get("title") or "").strip()
            if not title or title in seen:
                continue
            seen.add(title)
            out.append(it)
            if len(out) >= limit:
                break
        if not out:
            return [
                {
                    "error": "all CN announcement sources empty/failed",
                    "keyword": keyword,
                    "source": "cn_announcements",
                }
            ]
        return out

    def _eastmoney_column_news(self, limit: int = 10) -> list[dict[str, Any]]:
        try:
            url = "https://np-listapi.eastmoney.com/comm/web/getNewsByColumns"
            params = {
                "client": "web",
                "biz": "web_news_col",
                "column": "350",
                "order": "1",
                "page_index": "1",
                "page_size": str(limit),
                "req_trace": "chokepoint-agent",
                "fields": "code,showTime,title,mediaName,summary,url,uniqueUrl",
                "types": "1,20",
            }
            with httpx.Client(timeout=self.timeout, headers={"User-Agent": UA}) as client:
                r = client.get(url, params=params)
                r.raise_for_status()
                data = r.json() or {}
            rows = ((data.get("data") or {}).get("list")) or []
            out = []
            for it in rows[:limit]:
                out.append(
                    {
                        "title": it.get("title"),
                        "time": it.get("showTime"),
                        "media": it.get("mediaName"),
                        "url": it.get("uniqueUrl") or it.get("url"),
                        "summary": (it.get("summary") or "")[:300],
                        "form": "news_column",
                        "source": "eastmoney_column",
                    }
                )
            return out
        except Exception as exc:  # noqa: BLE001
            return [{"error": f"eastmoney_column: {exc}", "source": "eastmoney_column"}]

    def _eastmoney_notice_search(self, keyword: str, limit: int = 10) -> list[dict[str, Any]]:
        """Stock notice / announcement search via Eastmoney search API (best-effort)."""
        try:
            # Public search endpoint used by EM web (structure may change)
            url = "https://search-api-web.eastmoney.com/search/jsonp"
            # Fallback: notice list by keyword via np-anotice-stock
            notice_url = "https://np-anotice-stock.eastmoney.com/api/security/ann"
            # When symbol is 6-digit, use stock ann endpoint
            code = re.sub(r"\D", "", keyword)
            out: list[dict[str, Any]] = []
            if re.fullmatch(r"\d{6}", code):
                params = {
                    "sr": "-1",
                    "page_size": str(limit),
                    "page_index": "1",
                    "ann_type": "A",
                    "client_source": "web",
                    "f_node": "0",
                    "s_node": "0",
                    "stock_list": code,
                }
                with httpx.Client(timeout=self.timeout, headers={"User-Agent": UA}) as client:
                    r = client.get(notice_url, params=params)
                    r.raise_for_status()
                    data = r.json() or {}
                rows = ((data.get("data") or {}).get("list")) or []
                for it in rows[:limit]:
                    art_code = it.get("art_code") or it.get("artCode") or ""
                    title = it.get("title") or it.get("notice_title") or ""
                    date = it.get("notice_date") or it.get("display_time") or ""
                    link = ""
                    if art_code:
                        link = f"https://data.eastmoney.com/notices/detail/{code}/{art_code}.html"
                    out.append(
                        {
                            "title": title,
                            "time": date,
                            "symbol": code,
                            "url": link,
                            "form": it.get("columns") or it.get("ann_type") or "announcement",
                            "source": "eastmoney_stock_ann",
                        }
                    )
                return out

            # keyword free search via eastmoney search (jsonp-ish)
            search_url = "https://searchapi.eastmoney.com/api/suggest/get"
            params = {
                "input": keyword,
                "type": "14",
                "token": "D43BF722C8E33BDC906FB84D85E326E8",
                "count": str(min(limit, 10)),
            }
            with httpx.Client(timeout=self.timeout, headers={"User-Agent": UA}) as client:
                r = client.get(search_url, params=params)
                r.raise_for_status()
                data = r.json() or {}
            # structure varies; try QuotationCodeTable
            table = (data.get("QuotationCodeTable") or {}).get("Data") or data.get("data") or []
            if isinstance(table, list):
                for it in table[:limit]:
                    out.append(
                        {
                            "title": it.get("Name") or it.get("name") or keyword,
                            "symbol": it.get("Code") or it.get("code") or "",
                            "market": it.get("MktNum") or it.get("SecurityTypeName") or "",
                            "form": "suggest",
                            "source": "eastmoney_suggest",
                            "url": "",
                        }
                    )
            return out
        except Exception as exc:  # noqa: BLE001
            return [{"error": f"eastmoney_notice: {exc}", "source": "eastmoney_notice"}]

    def _eastmoney_web_search(self, keyword: str, limit: int = 5) -> list[dict[str, Any]]:
        try:
            url = "https://search-api-web.eastmoney.com/search/jsonp"
            # Many EM endpoints need cb; try plain info search
            info_url = "https://search-api-web.eastmoney.com/search/jsonp"
            # Simpler: stock news via his news
            news_url = "https://search-api-web.eastmoney.com/search/jsonp"
            _ = (url, info_url, news_url)  # reserved
            # Use np-listapi keyword column fallback via web search on finance
            search = "https://api.so.eastmoney.com/bussiness/Web/GetCMSSearchList"
            params = {
                "type": "20",
                "pageindex": "1",
                "pagesize": str(limit),
                "keyword": keyword,
            }
            with httpx.Client(timeout=self.timeout, headers={"User-Agent": UA}) as client:
                r = client.get(search, params=params)
                if r.status_code != 200:
                    return []
                data = r.json() or {}
            rows = data.get("Data") or data.get("data") or []
            if isinstance(rows, dict):
                rows = rows.get("Items") or rows.get("list") or []
            out = []
            if isinstance(rows, list):
                for it in rows[:limit]:
                    if not isinstance(it, dict):
                        continue
                    out.append(
                        {
                            "title": it.get("Title") or it.get("title"),
                            "time": it.get("ShowTime") or it.get("time"),
                            "url": it.get("Url") or it.get("url"),
                            "summary": (it.get("Content") or it.get("summary") or "")[:240],
                            "form": "cms_search",
                            "source": "eastmoney_cms_search",
                        }
                    )
            return out
        except Exception:  # noqa: BLE001
            return []

    def _sina_finance_headlines(self, keyword: str, limit: int = 8) -> list[dict[str, Any]]:
        try:
            # Sina finance roll news (public)
            url = "https://feed.mix.sina.com.cn/api/roll/get"
            params = {
                "pageid": "153",
                "lid": "2516",
                "k": keyword,
                "num": str(limit),
                "page": "1",
            }
            with httpx.Client(timeout=self.timeout, headers={"User-Agent": UA}) as client:
                r = client.get(url, params=params)
                r.raise_for_status()
                data = r.json() or {}
            rows = ((data.get("result") or {}).get("data")) or []
            out = []
            for it in rows[:limit]:
                out.append(
                    {
                        "title": it.get("title"),
                        "time": it.get("ctime") or it.get("create_date"),
                        "url": it.get("url"),
                        "media": it.get("media_name") or "sina",
                        "summary": (it.get("intro") or it.get("summary") or "")[:240],
                        "form": "headline",
                        "source": "sina_finance_roll",
                    }
                )
            return out
        except Exception as exc:  # noqa: BLE001
            return [{"error": f"sina: {exc}", "source": "sina_finance_roll"}]
