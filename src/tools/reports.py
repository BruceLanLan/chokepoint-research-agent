"""Report persistence and listing."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import get_settings


def reports_dir() -> Path:
    d = Path(get_settings().reports_dir)
    d.mkdir(parents=True, exist_ok=True)
    return d


def _yaml_escape(val: str) -> str:
    s = str(val).replace("\n", " ").strip()
    if any(c in s for c in ":#{}[]&*?|>!%@`'\""):
        return '"' + s.replace('"', '\\"') + '"'
    return s


def save_report_file(
    title: str,
    markdown_body: str,
    *,
    mode: str = "full",
    quality: dict[str, Any] | None = None,
    skill: str | None = None,
    vertical: str | None = None,
    thesis_id: str | None = None,
    watch_ids: list[str] | None = None,
    extra_meta: dict[str, Any] | None = None,
) -> str:
    out_dir = reports_dir()
    safe = re.sub(r"[^\w\u4e00-\u9fff\-]+", "_", title.strip())[:80] or "report"
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = out_dir / f"{ts}_{safe}.md"
    q = quality or {}
    meta: dict[str, Any] = {
        "title": title,
        "generated_at": datetime.now().isoformat(),
        "generator": "chokepoint-research-agent",
        "mode": mode,
        "quality_score": q.get("score", ""),
        "disclaimer": "research_only_not_investment_advice",
    }
    if skill:
        meta["skill"] = skill
    if vertical:
        meta["vertical_id"] = vertical
    if thesis_id:
        meta["thesis_id"] = thesis_id
    if watch_ids:
        meta["watch_ids"] = ",".join(watch_ids)
    if extra_meta:
        for k, v in extra_meta.items():
            if v is not None and v != "":
                meta[k] = v
    lines = ["---"]
    for k, v in meta.items():
        lines.append(f"{k}: {_yaml_escape(v)}")
    lines.append("---")
    lines.append("")
    header = "\n".join(lines) + "\n"
    footer = (
        "\n\n---\n"
        "*本报告由 AI 投研 Agent 生成，仅供研究学习，不构成投资建议。*\n"
    )
    body = markdown_body.strip()
    if "不构成投资建议" not in body and "not investment advice" not in body.lower():
        body = body + footer
    path.write_text(header + body + "\n", encoding="utf-8")
    return str(path.resolve())


def list_reports(limit: int = 20) -> list[dict[str, Any]]:
    out_dir = reports_dir()
    files = sorted(
        [p for p in out_dir.glob("*.md") if p.name != "SAMPLE_REPORT_FORMAT.md"],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )[: max(1, min(int(limit or 20), 100))]
    items: list[dict[str, Any]] = []
    for p in files:
        st = p.stat()
        items.append(
            {
                "name": p.name,
                "path": str(p.resolve()),
                "size_kb": round(st.st_size / 1024, 1),
                "modified": datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
            }
        )
    return items


def read_report(name: str) -> str | None:
    """Read a report by filename (no path traversal)."""
    safe = Path(name).name
    path = reports_dir() / safe
    if not path.is_file() or path.suffix != ".md":
        return None
    return path.read_text(encoding="utf-8")


def parse_frontmatter(markdown: str) -> dict[str, str]:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", markdown or "", re.S)
    meta: dict[str, str] = {}
    if not m:
        return meta
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip().strip('"')
    return meta
