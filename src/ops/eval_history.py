"""Persist offline eval runs for trend tracking."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import get_settings
from src.eval.harness import run_all


def _path() -> Path:
    base = Path(get_settings().reports_dir).parent / "data"
    base.mkdir(parents=True, exist_ok=True)
    return base / "eval_history.jsonl"


def record_eval_run() -> dict[str, Any]:
    result = run_all()
    row = {
        "at": datetime.now().isoformat(timespec="seconds"),
        "total": result.get("total"),
        "passed": result.get("passed"),
        "failed": result.get("failed"),
        "failed_ids": [r["id"] for r in (result.get("results") or []) if not r.get("ok")],
    }
    with _path().open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {**row, "result": result}


def eval_trend(limit: int = 20) -> dict[str, Any]:
    p = _path()
    if not p.is_file():
        return {"count": 0, "runs": [], "note": "No eval history yet — run eval-record"}
    rows = []
    for line in p.read_text(encoding="utf-8").strip().splitlines()[-limit:]:
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    rates = []
    for r in rows:
        t = r.get("total") or 0
        if t:
            rates.append(round((r.get("passed") or 0) / t, 3))
    return {
        "count": len(rows),
        "pass_rates": rates,
        "latest": rows[-1] if rows else None,
        "runs": rows,
        "disclaimer": "research_only_not_investment_advice",
    }
