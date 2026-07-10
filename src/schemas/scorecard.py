"""Chokepoint scorecard schema + report structure helpers."""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, Field


class NodeScore(BaseModel):
    node: str
    irreplaceability: int = Field(ge=1, le=5, default=3)
    concentration: int = Field(ge=1, le=5, default=3)
    downstream_leverage: int = Field(ge=1, le=5, default=3)
    coverage_vacuum: int = Field(ge=1, le=5, default=3)
    commercial_inflection: int = Field(ge=1, le=5, default=3)
    notes: str = ""

    @property
    def total(self) -> int:
        return (
            self.irreplaceability
            + self.concentration
            + self.downstream_leverage
            + self.coverage_vacuum
            + self.commercial_inflection
        )


class ChokepointScorecard(BaseModel):
    system: str = ""
    nodes: list[NodeScore] = Field(default_factory=list)
    kill_criteria: list[str] = Field(default_factory=list)

    def top_nodes(self, n: int = 3) -> list[NodeScore]:
        return sorted(self.nodes, key=lambda x: x.total, reverse=True)[:n]


REQUIRED_SECTIONS_ZH = [
    "研究结论",
    "风险",
    "来源",
]

REQUIRED_HINTS = [
    r"kill\s*criteria|证伪|杀逻辑",
    r"chokepoint|卡脖子|物理开关|供应链",
    r"http|www\.|来源|Sources",
]


def validate_report_structure(markdown: str) -> dict[str, Any]:
    """Heuristic quality gate for research memos (not a factuality check)."""
    text = markdown or ""
    missing_sections = [s for s in REQUIRED_SECTIONS_ZH if s not in text]
    hints_ok = [bool(re.search(p, text, re.I)) for p in REQUIRED_HINTS]
    sources = re.findall(r"https?://\S+", text)
    score = 0
    score += max(0, 40 - 10 * len(missing_sections))
    score += 20 * sum(1 for h in hints_ok if h) // max(len(hints_ok), 1)
    score += min(20, 4 * len(sources))
    if len(text) > 800:
        score += 20
    elif len(text) > 300:
        score += 10
    score = min(100, score)
    return {
        "score": score,
        "missing_sections": missing_sections,
        "hint_hits": sum(hints_ok),
        "url_count": len(sources),
        "char_count": len(text),
        "pass": score >= 50 and not missing_sections,
    }


def extract_scorecard_table(markdown: str) -> ChokepointScorecard:
    """Best-effort parse of a markdown table with score columns."""
    nodes: list[NodeScore] = []
    for line in (markdown or "").splitlines():
        if "|" not in line or re.search(r"---", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6:
            continue
        if any(h in cells[0] for h in ("节点", "node", "Node", "环节")):
            continue
        nums: list[int] = []
        for c in cells[1:6]:
            m = re.search(r"[1-5]", c)
            if m:
                nums.append(int(m.group()))
        if len(nums) < 5:
            continue
        nodes.append(
            NodeScore(
                node=cells[0][:120],
                irreplaceability=nums[0],
                concentration=nums[1],
                downstream_leverage=nums[2],
                coverage_vacuum=nums[3],
                commercial_inflection=nums[4],
                notes=cells[6] if len(cells) > 6 else "",
            )
        )
    kills = re.findall(r"(?:Kill criteria|证伪条件|杀逻辑)[:：\s]*(.+)", markdown or "", re.I)
    return ChokepointScorecard(nodes=nodes, kill_criteria=kills[:5])
