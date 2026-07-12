from __future__ import annotations
import importlib
from pathlib import Path
from typing import Any

def list_rubrics() -> list[str]:
    return sorted(p.stem for p in Path(__file__).parent.glob("*.py") if p.stem not in {"__init__","registry"})

def score_all(text: str) -> dict[str, Any]:
    results = []
    for rid in list_rubrics():
        mod = importlib.import_module(f"src.rubrics.{rid}")
        results.append(mod.score(text))
    avg = round(sum(r["percent"] for r in results)/len(results),1) if results else None
    return {"count": len(results), "avg_percent": avg, "results": results, "disclaimer": "research_only_not_investment_advice"}
