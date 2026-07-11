"""SEC EDGAR public filings provider (no API key).

User-Agent is required by SEC fair-access policy.
Docs: https://www.sec.gov/os/accessing-edgar-data
"""

from __future__ import annotations

import re
from typing import Any

import httpx

SEC_UA = "ChokepointResearchAgent/1.0 (research; contact=research@localhost)"


class SecEdgarProvider:
    name = "sec_edgar"

    def __init__(self, timeout: float = 20.0) -> None:
        self.timeout = timeout
        self._headers = {
            "User-Agent": SEC_UA,
            "Accept": "application/json",
        }

    def search_company(self, query: str) -> list[dict[str, Any]]:
        q = (query or "").strip()
        if not q:
            return []
        # Company tickers JSON is large but public; prefer ticker search first
        url = "https://www.sec.gov/files/company_tickers.json"
        try:
            with httpx.Client(timeout=self.timeout, headers=self._headers) as client:
                r = client.get(url)
                r.raise_for_status()
                data = r.json() or {}
        except Exception as exc:  # noqa: BLE001
            return [{"error": f"SEC tickers fetch failed: {exc}"}]

        q_up = q.upper()
        hits: list[dict[str, Any]] = []
        for _k, row in data.items():
            ticker = str(row.get("ticker") or "").upper()
            title = str(row.get("title") or "")
            cik = str(row.get("cik_str") or row.get("cik") or "")
            if q_up == ticker or q_up in title.upper() or q_up in cik:
                hits.append(
                    {
                        "ticker": ticker,
                        "name": title,
                        "cik": cik.zfill(10),
                        "source": "sec_company_tickers",
                    }
                )
            if len(hits) >= 15:
                break
        return hits

    def recent_filings(
        self, cik: str, form: str | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        cik_n = re.sub(r"\D", "", cik).zfill(10)
        url = f"https://data.sec.gov/submissions/CIK{cik_n}.json"
        try:
            with httpx.Client(timeout=self.timeout, headers=self._headers) as client:
                r = client.get(url)
                r.raise_for_status()
                data = r.json() or {}
        except Exception as exc:  # noqa: BLE001
            return [{"error": f"SEC submissions failed: {exc}", "cik": cik_n}]

        recent = (data.get("filings") or {}).get("recent") or {}
        forms = recent.get("form") or []
        dates = recent.get("filingDate") or []
        accessions = recent.get("accessionNumber") or []
        primaries = recent.get("primaryDocument") or []
        descs = recent.get("primaryDocDescription") or []

        out: list[dict[str, Any]] = []
        form_f = (form or "").upper().strip()
        for i, f in enumerate(forms):
            if form_f and str(f).upper() != form_f:
                continue
            acc = accessions[i] if i < len(accessions) else ""
            acc_nodash = acc.replace("-", "")
            doc = primaries[i] if i < len(primaries) else ""
            link = ""
            if acc_nodash and doc:
                link = f"https://www.sec.gov/Archives/edgar/data/{int(cik_n)}/{acc_nodash}/{doc}"
            out.append(
                {
                    "form": f,
                    "filing_date": dates[i] if i < len(dates) else "",
                    "accession": acc,
                    "description": descs[i] if i < len(descs) else "",
                    "url": link,
                    "cik": cik_n,
                    "company": data.get("name"),
                    "source": "sec_edgar",
                }
            )
            if len(out) >= max(1, min(limit, 50)):
                break
        return out
