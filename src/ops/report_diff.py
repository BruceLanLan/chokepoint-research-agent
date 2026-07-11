"""Diff two research memos (text-level)."""

from __future__ import annotations

import difflib
from pathlib import Path
from typing import Any

from src.tools.reports import read_report, reports_dir


def diff_reports(name_a: str, name_b: str, context: int = 3) -> dict[str, Any]:
    a = read_report(name_a)
    b = read_report(name_b)
    if a is None:
        return {"error": f"not found: {name_a}"}
    if b is None:
        return {"error": f"not found: {name_b}"}
    lines_a = a.splitlines()
    lines_b = b.splitlines()
    udiff = list(
        difflib.unified_diff(
            lines_a,
            lines_b,
            fromfile=name_a,
            tofile=name_b,
            lineterm="",
            n=context,
        )
    )
    sm = difflib.SequenceMatcher(None, a, b)
    return {
        "a": name_a,
        "b": name_b,
        "ratio": round(sm.ratio(), 4),
        "lines_a": len(lines_a),
        "lines_b": len(lines_b),
        "udiff": udiff[:500],
        "truncated": len(udiff) > 500,
    }


def list_report_names(limit: int = 50) -> list[str]:
    d = reports_dir()
    files = sorted(d.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    return [p.name for p in files if p.name != "SAMPLE_REPORT_FORMAT.md"][:limit]
