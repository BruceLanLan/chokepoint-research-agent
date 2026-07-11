"""Heuristic auto-tagging for research memos (no LLM)."""

from __future__ import annotations

import re
from typing import Any

from src.ops.tags import get_tags, tag_report
from src.skills.loader import list_skill_packs
from src.tools.reports import read_report

# keyword → tag
_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bCPO\b|共封装|co-?packaged", re.I), "cpo"),
    (re.compile(r"\bHBM\b|高带宽存储", re.I), "hbm"),
    (re.compile(r"光互连|silicon photonics|硅光|ELS|激光", re.I), "optics"),
    (re.compile(r"机器人|humanoid|actuator|减速器", re.I), "robotics"),
    (re.compile(r"电力|power delivery|UPS|液冷|cooling", re.I), "power"),
    (re.compile(r"半导体|先进封装|foundry|晶圆", re.I), "semiconductor"),
    (re.compile(r"kill\s*criteria|证伪|杀逻辑", re.I), "has_kills"),
    (re.compile(r"10-[KQ]|8-K|SEC|EDGAR", re.I), "sec"),
    (re.compile(r"公告|上交所|深交所|港交所|HKEX", re.I), "cn_hk_filings"),
    (re.compile(r"风险|red.?team|对抗", re.I), "risk"),
]


def suggest_tags(markdown: str) -> list[str]:
    text = markdown or ""
    tags: list[str] = []
    for pat, tag in _RULES:
        if pat.search(text):
            tags.append(tag)
    # skill pack ids if name/description keywords appear
    for pack in list_skill_packs():
        pid = pack.get("id") or ""
        name = pack.get("name") or ""
        if pid and (pid.replace("_", " ") in text.lower() or name[:6] in text):
            tags.append(pid)
    # dedupe preserve order
    seen = set()
    out = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def auto_tag_report(report_name: str, *, merge: bool = True) -> dict[str, Any]:
    body = read_report(report_name)
    if body is None:
        return {"error": f"not found: {report_name}"}
    suggested = suggest_tags(body)
    if merge:
        existing = get_tags(report_name).get("tags") or []
        suggested = list(dict.fromkeys(list(existing) + suggested))
    return tag_report(report_name, suggested)
