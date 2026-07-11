"""Best-effort A-share announcement provider (Eastmoney list sample).

Educational — not a complete filings terminal.
"""

from __future__ import annotations

from typing import Any

import httpx


class CnAnnouncementProvider:
    name = "cn_announcements"

    def search_company(self, query: str) -> list[dict[str, Any]]:
        # No dedicated free search; return guidance for agent tools
        return [
            {
                "query": query,
                "hint": "Use search_cn_company_news or web_search for CN announcements",
                "source": "cn_announcements",
            }
        ]

    def recent_filings(
        self, cik: str, form: str | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        # cik unused; fetch general CN market news column as weak signal
        limit = max(1, min(int(limit or 10), 20))
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
            with httpx.Client(timeout=12.0) as client:
                r = client.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
                r.raise_for_status()
                data = r.json() or {}
            items = ((data.get("data") or {}).get("list")) or []
            out = []
            for it in items[:limit]:
                out.append(
                    {
                        "title": it.get("title"),
                        "time": it.get("showTime"),
                        "media": it.get("mediaName"),
                        "url": it.get("uniqueUrl") or it.get("url"),
                        "form": form or "news",
                        "source": "cn_announcements_eastmoney",
                        "note": "Headline feed sample; not exchange filing dump.",
                    }
                )
            return out
        except Exception as exc:  # noqa: BLE001
            return [{"error": str(exc), "source": "cn_announcements"}]
