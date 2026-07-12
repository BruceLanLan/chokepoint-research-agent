"""Unified ProEngine — one implementation, many YAML specs (v5.2–v5.51 IDs)."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from src.ops.pro.store import append_jsonl, read_json, read_jsonl, write_json

ROOT = Path(__file__).resolve().parents[3]
SPECS_DIR = ROOT / "skills" / "pro"

DISCLAIMER = "research_only_not_investment_advice"

_DEFAULT_KEYWORDS = [
    "chokepoint",
    "capacity",
    "concentration",
    "kill",
    "evidence",
    "supply",
    "demand",
    "margin",
    "inventory",
    "policy",
    "export",
    "customer",
    "supplier",
    "roadmap",
]


def list_spec_ids() -> list[str]:
    if not SPECS_DIR.is_dir():
        return []
    return sorted(p.stem for p in SPECS_DIR.glob("*.yaml"))


def load_spec(module_id: str) -> dict[str, Any]:
    path = SPECS_DIR / f"{Path(module_id).stem}.yaml"
    if not path.is_file():
        return {
            "id": module_id,
            "title": module_id.replace("_", " ").title(),
            "version_theme": "",
            "description": module_id,
            "keywords": list(_DEFAULT_KEYWORDS),
            "checklist": _default_checklist(),
        }
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    data.setdefault("id", path.stem)
    data.setdefault("title", path.stem.replace("_", " ").title())
    data.setdefault("keywords", list(_DEFAULT_KEYWORDS))
    data.setdefault("checklist", _default_checklist())
    return data


def _default_checklist() -> list[dict[str, str]]:
    return [
        {"id": "scope", "label": "System / scope defined", "hint": "Write system boundary"},
        {"id": "evidence", "label": "Evidence with sources", "hint": "Attach URLs / filings"},
        {"id": "kill", "label": "Kill / falsifiers", "hint": "What would invalidate?"},
        {"id": "nodes", "label": "Physical nodes listed", "hint": "Chokepoint candidates"},
        {"id": "peers", "label": "Peer / substitute map", "hint": "Who else can supply?"},
        {"id": "time", "label": "Time stamp on numbers", "hint": "When was data true?"},
    ]


def _score_text(text: str, keywords: list[str]) -> dict[str, Any]:
    t = (text or "").lower()
    hits = [k for k in keywords if k.lower() in t]
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


def _eval_checklist(text: str, checklist: list[dict[str, Any]]) -> list[dict[str, Any]]:
    t = (text or "").lower()
    out = []
    for c in checklist:
        item = dict(c)
        cid = item.get("id") or ""
        if cid == "evidence":
            item["ok"] = bool(re.search(r"https?://|来源|10-[kq]|公告", text or "", re.I))
        elif cid == "kill":
            item["ok"] = "kill" in t or "证伪" in (text or "") or "风险" in (text or "")
        elif cid == "nodes":
            item["ok"] = "node" in t or "卡点" in (text or "") or "chokepoint" in t
        elif cid == "scope":
            item["ok"] = "system" in t or "边界" in (text or "") or len(text or "") > 80
        elif cid == "peers":
            item["ok"] = "peer" in t or "替代" in (text or "") or "competitor" in t
        elif cid == "time":
            item["ok"] = bool(re.search(r"20\d{2}|q[1-4]|fy\d{2}", t))
        else:
            # domain custom: match any of patterns
            pats = item.get("patterns") or []
            item["ok"] = any(re.search(p, text or "", re.I) for p in pats) if pats else False
        out.append(item)
    return out


class ProEngine:
    def __init__(self, module_id: str):
        self.module_id = Path(module_id).stem
        self.spec = load_spec(self.module_id)
        self._store = f"{self.module_id}.jsonl"
        self._state = f"{self.module_id}_state.json"

    @property
    def title(self) -> str:
        return str(self.spec.get("title") or self.module_id)

    @property
    def version_theme(self) -> str:
        return str(self.spec.get("version_theme") or "")

    @property
    def description(self) -> str:
        return str(self.spec.get("description") or "")

    def add_entry(
        self,
        *,
        title: str,
        body: str = "",
        symbol: str = "",
        tags: list[str] | None = None,
        meta: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        scored = _score_text(f"{title}\n{body}", list(self.spec.get("keywords") or []))
        return append_jsonl(
            self._store,
            {
                "title": title.strip(),
                "body": body.strip(),
                "symbol": symbol.upper().strip(),
                "tags": tags or [],
                "meta": meta or {},
                "score": scored,
                "module": self.module_id,
                "version_theme": self.version_theme,
                "disclaimer": DISCLAIMER,
            },
        )

    def list_entries(self, limit: int = 50, symbol: str | None = None) -> list[dict[str, Any]]:
        rows = read_jsonl(self._store, limit=max(limit, 50))
        if symbol:
            s = symbol.upper()
            rows = [r for r in rows if r.get("symbol") == s]
        return rows[-limit:]

    def summarize(self, limit: int = 100) -> dict[str, Any]:
        rows = self.list_entries(limit=limit)
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
            "module": self.module_id,
            "title": self.title,
            "version_theme": self.version_theme,
            "count": len(rows),
            "avg_density": avg,
            "flag_counts": flags,
            "symbols": symbols,
            "recent": rows[-5:],
            "domain_fields": self.spec.get("fields") or [],
            "disclaimer": DISCLAIMER,
            "note": "Process notes for research ops — not investment advice or a signal.",
        }

    def analyze(
        self, *, text: str = "", symbol: str = "", title: str = ""
    ) -> dict[str, Any]:
        scored = _score_text(text or title, list(self.spec.get("keywords") or []))
        checklist = _eval_checklist(text or title, list(self.spec.get("checklist") or []))
        passed = sum(1 for c in checklist if c.get("ok"))
        return {
            "module": self.module_id,
            "title": self.title,
            "version_theme": self.version_theme,
            "symbol": symbol.upper().strip() if symbol else "",
            "score": scored,
            "checklist": checklist,
            "checklist_passed": passed,
            "checklist_total": len(checklist),
            "gate_ok": passed >= max(3, len(checklist) // 2)
            and not any(str(f).startswith("language_may") for f in scored.get("flags") or []),
            "domain_hints": self.spec.get("focus_questions") or [],
            "disclaimer": DISCLAIMER,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "note": self.description + " — research process only, not investment advice.",
        }

    def set_state(self, **fields: Any) -> dict[str, Any]:
        cur = read_json(self._state, {"version": 1, "fields": {}})
        cur.setdefault("fields", {}).update(fields)
        cur["module"] = self.module_id
        write_json(self._state, cur)
        return cur

    def get_state(self) -> dict[str, Any]:
        return read_json(self._state, {"version": 1, "fields": {}, "module": self.module_id})

    def run(self, *, action: str = "summarize", **kwargs: Any) -> dict[str, Any]:
        action = (action or "summarize").lower()
        if action in {"add", "create"}:
            return self.add_entry(
                title=kwargs.get("title") or kwargs.get("name") or "untitled",
                body=kwargs.get("body") or kwargs.get("text") or "",
                symbol=kwargs.get("symbol") or "",
                tags=kwargs.get("tags"),
                meta=kwargs.get("meta"),
            )
        if action in {"list", "entries"}:
            return {
                "items": self.list_entries(
                    limit=int(kwargs.get("limit") or 50), symbol=kwargs.get("symbol")
                )
            }
        if action in {"analyze", "score"}:
            return self.analyze(
                text=kwargs.get("text") or kwargs.get("body") or "",
                symbol=kwargs.get("symbol") or "",
                title=kwargs.get("title") or "",
            )
        if action in {"state", "get_state"}:
            return self.get_state()
        if action == "set_state":
            fields = {k: v for k, v in kwargs.items() if k not in {"action"}}
            return self.set_state(**fields)
        return self.summarize(limit=int(kwargs.get("limit") or 100))


def invoke_engine(module_id: str, **kwargs: Any) -> dict[str, Any]:
    return ProEngine(module_id).run(**kwargs)
