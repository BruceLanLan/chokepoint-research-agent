"""Rates/FX sensitivity notes

Version theme: v5.36.0 maturity train.
Research process helper only — not investment advice.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from src.ops.pro.store import append_jsonl, read_json, read_jsonl, write_json

TITLE = "Rates Fx Link"
VERSION_THEME = "v5.36.0"
DESCRIPTION = """Rates/FX sensitivity notes"""
DISCLAIMER = "research_only_not_investment_advice"
_STORE = "rates_fx_link.jsonl"
_STATE = "rates_fx_link_state.json"

_KEYWORDS = [
    "chokepoint", "capacity", "concentration", "kill", "evidence",
    "supply", "demand", "margin", "ASP", "inventory", "policy",
    "export", "customer", "supplier", "roadmap", "patent",
]


def _score_text(text: str) -> dict[str, Any]:
    t = (text or "").lower()
    hits = [k for k in _KEYWORDS if k.lower() in t]
    dens = min(100, 10 * len(hits) + min(40, len(t) // 50))
    flags = []
    if "buy" in t or "sell" in t or "加仓" in t or "买入" in t:
        flags.append("language_may_sound_like_advice_rewrite_as_research")
    if not re.search(r"https?://|来源|source", text or "", re.I):
        flags.append("missing_source_hint")
    if "kill" not in t and "证伪" not in (text or "") and "风险" not in (text or ""):
        flags.append("missing_risk_or_kill_hint")
    return {
        "keyword_hits": hits,
        "density_score": dens,
        "flags": flags,
        "char_count": len(text or ""),
    }


def add_entry(
    *,
    title: str,
    body: str = "",
    symbol: str = "",
    tags: list[str] | None = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Append a structured research note for this module."""
    scored = _score_text(f"{title}\n{body}")
    row = append_jsonl(
        _STORE,
        {
            "title": title.strip(),
            "body": body.strip(),
            "symbol": symbol.upper().strip(),
            "tags": tags or [],
            "meta": meta or {},
            "score": scored,
            "module": "rates_fx_link",
            "version_theme": VERSION_THEME,
            "disclaimer": DISCLAIMER,
        },
    )
    return row


def list_entries(limit: int = 50, symbol: str | None = None) -> list[dict[str, Any]]:
    rows = read_jsonl(_STORE, limit=max(limit, 50))
    if symbol:
        s = symbol.upper()
        rows = [r for r in rows if r.get("symbol") == s]
    return rows[-limit:]


def summarize(limit: int = 100) -> dict[str, Any]:
    rows = list_entries(limit=limit)
    flags: dict[str, int] = {}
    dens = []
    symbols: dict[str, int] = {}
    for r in rows:
        sc = r.get("score") or {}
        dens.append(sc.get("density_score") or 0)
        for f in sc.get("flags") or []:
            flags[f] = flags.get(f, 0) + 1
        sym = r.get("symbol") or ""
        if sym:
            symbols[sym] = symbols.get(sym, 0) + 1
    avg = round(sum(dens) / len(dens), 1) if dens else None
    return {
        "module": "rates_fx_link",
        "title": TITLE,
        "version_theme": VERSION_THEME,
        "count": len(rows),
        "avg_density": avg,
        "flag_counts": flags,
        "symbols": symbols,
        "recent": rows[-5:],
        "disclaimer": DISCLAIMER,
        "note": "Process notes for research ops — not investment advice or a signal.",
    }


def set_state(**fields: Any) -> dict[str, Any]:
    cur = read_json(_STATE, {"version": 1, "fields": {}})
    cur.setdefault("fields", {}).update(fields)
    cur["module"] = "rates_fx_link"
    write_json(_STATE, cur)
    return cur


def get_state() -> dict[str, Any]:
    return read_json(_STATE, {"version": 1, "fields": {}, "module": "rates_fx_link"})


def analyze(*, text: str = "", symbol: str = "", title: str = "") -> dict[str, Any]:
    """Offline analyze helper: score text and optionally persist."""
    scored = _score_text(text or title)
    checklist = [
        {"id": "scope", "label": "System / scope defined", "hint": "Write system boundary"},
        {"id": "evidence", "label": "Evidence with sources", "hint": "Attach URLs / filings"},
        {"id": "kill", "label": "Kill / falsifiers", "hint": "What would invalidate the view?"},
        {"id": "nodes", "label": "Physical nodes listed", "hint": "Chokepoint candidates"},
        {"id": "peers", "label": "Peer / substitute map", "hint": "Who else can supply?"},
        {"id": "time", "label": "Time stamp on numbers", "hint": "When was capacity data true?"},
    ]
    # auto-check from text
    t = (text or title or "").lower()
    for c in checklist:
        if c["id"] == "evidence":
            c["ok"] = bool(re.search(r"https?://|来源|10-[kq]|公告", text or title or "", re.I))
        elif c["id"] == "kill":
            c["ok"] = "kill" in t or "证伪" in (text or "") or "风险" in (text or "")
        elif c["id"] == "nodes":
            c["ok"] = "node" in t or "卡点" in (text or "") or "chokepoint" in t
        elif c["id"] == "scope":
            c["ok"] = "system" in t or "边界" in (text or "") or len(text or "") > 80
        elif c["id"] == "peers":
            c["ok"] = "peer" in t or "替代" in (text or "") or "competitor" in t
        elif c["id"] == "time":
            c["ok"] = bool(re.search(r"20\d{2}|q[1-4]|fy\d{2}", t))
        else:
            c["ok"] = False
    passed = sum(1 for c in checklist if c.get("ok"))
    return {
        "module": "rates_fx_link",
        "title": TITLE,
        "version_theme": VERSION_THEME,
        "symbol": symbol.upper().strip() if symbol else "",
        "score": scored,
        "checklist": checklist,
        "checklist_passed": passed,
        "checklist_total": len(checklist),
        "gate_ok": passed >= 4 and not any(
            f.startswith("language_may") for f in scored.get("flags") or []
        ),
        "disclaimer": DISCLAIMER,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "note": DESCRIPTION + " — research process only, not investment advice.",
    }


def run(*, action: str = "summarize", **kwargs: Any) -> dict[str, Any]:
    """Dispatcher used by registry."""
    action = (action or "summarize").lower()
    if action in {"add", "create"}:
        return add_entry(
            title=kwargs.get("title") or kwargs.get("name") or "untitled",
            body=kwargs.get("body") or kwargs.get("text") or "",
            symbol=kwargs.get("symbol") or "",
            tags=kwargs.get("tags"),
            meta=kwargs.get("meta"),
        )
    if action in {"list", "entries"}:
        return {"items": list_entries(limit=int(kwargs.get("limit") or 50), symbol=kwargs.get("symbol"))}
    if action in {"analyze", "score"}:
        return analyze(
            text=kwargs.get("text") or kwargs.get("body") or "",
            symbol=kwargs.get("symbol") or "",
            title=kwargs.get("title") or "",
        )
    if action in {"state", "get_state"}:
        return get_state()
    if action == "set_state":
        fields = {k: v for k, v in kwargs.items() if k not in {"action"}}
        return set_state(**fields)
    return summarize(limit=int(kwargs.get("limit") or 100))
