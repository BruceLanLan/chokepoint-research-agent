"""Score thesis registry process quality (not investment merit)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.ops.theses import list_theses


def score_thesis(t: dict[str, Any]) -> dict[str, Any]:
    score = 0
    notes: list[str] = []
    kills = t.get("kill_criteria") or []
    cps = t.get("chokepoints") or []
    syms = t.get("related_symbols") or []
    reviews = t.get("reviews") or []
    status = t.get("status") or "active"

    if (t.get("statement") or "").strip():
        score += 15
    else:
        notes.append("missing statement")
    if (t.get("system") or "").strip():
        score += 10
    else:
        notes.append("missing system boundary")
    if kills:
        score += min(25, 10 + 5 * len(kills))
    else:
        notes.append("no kill criteria")
        if status == "active":
            score -= 15
    if cps:
        score += min(20, 5 * len(cps))
    else:
        notes.append("no chokepoints listed")
    if syms:
        score += min(15, 5 * len(syms))
    else:
        notes.append("no related symbols")
    if reviews:
        score += min(15, 5 * len(reviews))
    else:
        notes.append("no status reviews yet")
    if status == "invalidated":
        score = min(score, 60)  # closed theses cap
        notes.append("invalidated — historical only")

    score = max(0, min(100, score))
    grade = (
        "A"
        if score >= 80
        else "B"
        if score >= 60
        else "C"
        if score >= 40
        else "D"
        if score >= 20
        else "F"
    )
    return {
        "id": t.get("id"),
        "title": t.get("title"),
        "status": status,
        "process_score": score,
        "grade": grade,
        "notes": notes,
        "kill_count": len(kills),
        "chokepoint_count": len(cps),
    }


def thesis_health_report() -> dict[str, Any]:
    items = [score_thesis(t) for t in list_theses()]
    items.sort(key=lambda x: x["process_score"])
    avg = round(sum(i["process_score"] for i in items) / len(items), 1) if items else None
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "count": len(items),
        "avg_process_score": avg,
        "weakest": items[:5],
        "items": items,
        "disclaimer": "research_only_not_investment_advice",
        "note": "Scores process completeness, not alpha or valuation.",
    }
