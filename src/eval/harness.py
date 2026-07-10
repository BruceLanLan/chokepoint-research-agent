"""Offline eval harness for prompt/structure regressions (no live LLM required)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from src.schemas.scorecard import extract_scorecard_table, validate_report_structure

ROOT = Path(__file__).resolve().parents[2]
GOLDEN_DIR = ROOT / "eval" / "golden"


@dataclass
class EvalCase:
    id: str
    question: str
    fixture_report: str
    min_quality: int = 50
    require_scorecard: bool = False
    require_urls: int = 0


def load_cases() -> list[EvalCase]:
    cases: list[EvalCase] = []
    if not GOLDEN_DIR.is_dir():
        return cases
    for path in sorted(GOLDEN_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        cases.append(
            EvalCase(
                id=data.get("id") or path.stem,
                question=data.get("question") or "",
                fixture_report=data.get("fixture_report") or "",
                min_quality=int(data.get("min_quality") or 50),
                require_scorecard=bool(data.get("require_scorecard")),
                require_urls=int(data.get("require_urls") or 0),
            )
        )
    return cases


def run_case(case: EvalCase) -> dict[str, Any]:
    q = validate_report_structure(case.fixture_report)
    card = extract_scorecard_table(case.fixture_report)
    ok = q["score"] >= case.min_quality and q["pass"]
    if case.require_scorecard and not card.nodes:
        ok = False
    if case.require_urls and q["url_count"] < case.require_urls:
        ok = False
    return {
        "id": case.id,
        "ok": ok,
        "quality": q,
        "scorecard_nodes": len(card.nodes),
        "question": case.question,
    }


def run_all() -> dict[str, Any]:
    cases = load_cases()
    results = [run_case(c) for c in cases]
    passed = sum(1 for r in results if r["ok"])
    return {
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "results": results,
    }
