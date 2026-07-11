"""Enrich report frontmatter with tags / quality / skill metadata."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from src.ops.auto_tag import suggest_tags
from src.ops.tags import tag_report
from src.schemas.scorecard import validate_report_structure
from src.tools.reports import read_report, reports_dir

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.S)


def enrich_report_frontmatter(report_name: str, *, write: bool = True) -> dict[str, Any]:
    body = read_report(report_name)
    if body is None:
        return {"error": f"not found: {report_name}"}
    quality = validate_report_structure(body)
    tags = suggest_tags(body)
    tag_report(report_name, tags)

    meta: dict[str, str] = {}
    m = _FM_RE.match(body)
    content = body
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        content = body[m.end() :]
    meta["quality_score"] = str(quality.get("score", ""))
    meta["tags"] = ",".join(tags)
    meta["enriched"] = "true"
    if "disclaimer" not in meta:
        meta["disclaimer"] = "research_only_not_investment_advice"

    fm_lines = ["---"] + [f"{k}: {v}" for k, v in meta.items()] + ["---", ""]
    new_body = "\n".join(fm_lines) + content.lstrip("\n")
    path = reports_dir() / Path(report_name).name
    if write:
        path.write_text(new_body, encoding="utf-8")
    return {
        "report": report_name,
        "meta": meta,
        "quality": quality,
        "tags": tags,
        "written": write,
    }
