"""Flatten a memo into Notion-friendly plain blocks (copy-paste / API-ready)."""

from __future__ import annotations

import re
from typing import Any

from src.tools.reports import read_report


def memo_to_notion_blocks(markdown: str, *, title: str = "") -> dict[str, Any]:
    """Convert markdown to a simple block list Notion-like JSON (local, no API)."""
    blocks: list[dict[str, Any]] = []
    if title:
        blocks.append({"type": "heading_1", "text": title})
    blocks.append(
        {
            "type": "callout",
            "text": "Research only — not investment advice / 仅供研究学习，不构成投资建议",
        }
    )
    for raw in (markdown or "").splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("# "):
            blocks.append({"type": "heading_1", "text": line[2:].strip()})
        elif line.startswith("## "):
            blocks.append({"type": "heading_2", "text": line[3:].strip()})
        elif line.startswith("### "):
            blocks.append({"type": "heading_3", "text": line[4:].strip()})
        elif line.startswith(("- ", "* ")):
            blocks.append({"type": "bulleted_list_item", "text": line[2:].strip()})
        elif re.match(r"^\d+\.\s+", line):
            blocks.append({"type": "numbered_list_item", "text": re.sub(r"^\d+\.\s+", "", line)})
        elif line.startswith("|") and "|" in line[1:]:
            blocks.append({"type": "table_row_text", "text": line})
        else:
            blocks.append({"type": "paragraph", "text": re.sub(r"[*_`]+", "", line)})
    plain = "\n".join(
        (b.get("text") or "") if b["type"] != "callout" else f"> {b.get('text')}" for b in blocks
    )
    return {
        "blocks": blocks,
        "plain_text": plain,
        "block_count": len(blocks),
        "disclaimer": "research_only_not_investment_advice",
        "note": "Local structure only — paste into Notion or wire via Notion API yourself.",
    }


def export_report_for_notion(report_name: str) -> dict[str, Any]:
    body = read_report(report_name)
    if body is None:
        return {"error": f"not found: {report_name}"}
    # strip frontmatter
    text = re.sub(r"^---\s*\n.*?\n---\s*\n", "", body, count=1, flags=re.S)
    return memo_to_notion_blocks(text, title=report_name)
