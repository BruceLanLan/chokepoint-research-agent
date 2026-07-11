"""Evidence ledger — extract and persist sources/claims from research memos."""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import get_settings

_URL_RE = re.compile(r"https?://[^\s\)\]\>\"']+", re.I)
_TICKER_RE = re.compile(r"\b([A-Z]{1,5})(?:\s*/\s*[A-Z]{1,5})?\b")
_CN_TICKER_RE = re.compile(r"\b([0-9]{6})(?:\.(?:SH|SZ|BJ))?\b", re.I)
_CLAIM_MARKERS = re.compile(
    r"(?:根据|据|来源|Source|According to|reported|披露|公告)[:：]?\s*(.+)",
    re.I,
)


def _data_dir() -> Path:
    base = Path(get_settings().reports_dir).parent / "data"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _ledger_path() -> Path:
    return _data_dir() / "evidence_ledger.jsonl"


def extract_evidence(markdown: str, *, report_name: str = "") -> dict[str, Any]:
    """Parse URLs, tickers, and claim-like lines from a memo (no LLM)."""
    text = markdown or ""
    urls = sorted(set(_URL_RE.findall(text)))
    # strip trailing punctuation from URLs
    urls = [u.rstrip(".,;:!?）)") for u in urls]

    domains: dict[str, int] = {}
    for u in urls:
        try:
            host = re.sub(r"^https?://", "", u).split("/")[0].lower()
            domains[host] = domains.get(host, 0) + 1
        except Exception:  # noqa: BLE001
            continue

    cn = sorted(set(m.upper() if "." in m else m for m in _CN_TICKER_RE.findall(text)))
    # crude US tickers from common contexts only (avoid noise)
    us: list[str] = []
    for m in re.finditer(
        r"(?:ticker|symbol|标的|代码|美股)[:：\s]+([A-Z]{1,5})\b",
        text,
        re.I,
    ):
        us.append(m.group(1).upper())
    us = sorted(set(us))

    claims: list[dict[str, str]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or len(line) < 12:
            continue
        if _CLAIM_MARKERS.search(line) or ("http" in line.lower() and len(line) < 240):
            claims.append({"text": line[:400], "kind": "source_line"})
        if len(claims) >= 40:
            break

    return {
        "report_name": report_name,
        "url_count": len(urls),
        "urls": urls[:80],
        "domains": domains,
        "tickers_cn": cn[:30],
        "tickers_us": us[:30],
        "claims": claims,
        "extracted_at": datetime.now().isoformat(timespec="seconds"),
        "disclaimer": "research_only_not_investment_advice",
    }


def append_evidence(entry: dict[str, Any]) -> dict[str, Any]:
    row = {
        "id": uuid.uuid4().hex[:10],
        **entry,
        "appended_at": datetime.now().isoformat(timespec="seconds"),
    }
    path = _ledger_path()
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def extract_and_store(markdown: str, *, report_name: str = "", title: str = "") -> dict[str, Any]:
    ev = extract_evidence(markdown, report_name=report_name)
    if title:
        ev["title"] = title
    return append_evidence(ev)


def list_evidence(limit: int = 50, report_name: str | None = None) -> list[dict[str, Any]]:
    path = _ledger_path()
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").strip().splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if report_name and row.get("report_name") != report_name:
            continue
        rows.append(row)
    return rows[-max(1, min(limit, 500)) :]


def evidence_summary() -> dict[str, Any]:
    rows = list_evidence(limit=500)
    all_urls: set[str] = set()
    domain_counts: dict[str, int] = {}
    for r in rows:
        for u in r.get("urls") or []:
            all_urls.add(u)
        for d, c in (r.get("domains") or {}).items():
            domain_counts[d] = domain_counts.get(d, 0) + int(c)
    top_domains = sorted(domain_counts.items(), key=lambda x: -x[1])[:15]
    return {
        "entries": len(rows),
        "unique_urls": len(all_urls),
        "top_domains": [{"domain": d, "count": c} for d, c in top_domains],
        "recent": rows[-5:],
        "disclaimer": "research_only_not_investment_advice",
    }
