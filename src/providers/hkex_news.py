"""Best-effort HKEX / HK market news provider (public endpoints)."""

from __future__ import annotations

from typing import Any

import httpx

UA = "Mozilla/5.0 (compatible; ChokepointResearchAgent/2.1; research)"


class HkexNewsProvider:
    name = "hkex_news"

    def search_company(self, query: str) -> list[dict[str, Any]]:
        q = (query or "").strip()
        if not q:
            return []
        # Use eastmoney HK suggest / web search as proxy for HK names
        try:
            url = "https://searchapi.eastmoney.com/api/suggest/get"
            params = {
                "input": q,
                "type": "14",
                "token": "D43BF722C8E33BDC906FB84D85E326E8",
                "count": "10",
            }
            with httpx.Client(timeout=12.0, headers={"User-Agent": UA}) as client:
                r = client.get(url, params=params)
                r.raise_for_status()
                data = r.json() or {}
            table = (data.get("QuotationCodeTable") or {}).get("Data") or []
            out = []
            for it in table[:10]:
                code = str(it.get("Code") or "")
                out.append(
                    {
                        "ticker": code,
                        "name": it.get("Name") or "",
                        "market": it.get("SecurityTypeName") or "HK/other",
                        "source": "hkex_news_via_em_suggest",
                    }
                )
            return out or [{"query": q, "hint": "no suggest hits", "source": "hkex_news"}]
        except Exception as exc:  # noqa: BLE001
            return [{"error": str(exc), "source": "hkex_news"}]

    def recent_filings(
        self, cik: str, form: str | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Treat cik as HK code / keyword; pull EM HK news column best-effort."""
        keyword = (cik or "").strip()
        limit = max(1, min(int(limit or 10), 20))
        try:
            # Eastmoney HK news
            url = "https://np-listapi.eastmoney.com/comm/web/getNewsByColumns"
            params = {
                "client": "web",
                "biz": "web_news_col",
                "column": "344",  # often HK-related columns vary
                "order": "1",
                "page_index": "1",
                "page_size": str(limit),
                "req_trace": "chokepoint-hk",
                "fields": "code,showTime,title,mediaName,summary,url,uniqueUrl",
                "types": "1,20",
            }
            with httpx.Client(timeout=12.0, headers={"User-Agent": UA}) as client:
                r = client.get(url, params=params)
                r.raise_for_status()
                data = r.json() or {}
            rows = ((data.get("data") or {}).get("list")) or []
            out = []
            for it in rows[:limit]:
                title = it.get("title") or ""
                if keyword and keyword.lower() not in title.lower() and not keyword.isdigit():
                    # keep general feed if keyword not in title
                    pass
                out.append(
                    {
                        "title": title,
                        "time": it.get("showTime"),
                        "url": it.get("uniqueUrl") or it.get("url"),
                        "media": it.get("mediaName"),
                        "form": form or "hk_news",
                        "source": "hkex_news_eastmoney",
                        "keyword": keyword,
                    }
                )
            return out or [
                {
                    "hint": "empty HK feed; use web_search",
                    "keyword": keyword,
                    "source": "hkex_news",
                }
            ]
        except Exception as exc:  # noqa: BLE001
            return [{"error": str(exc), "source": "hkex_news"}]
