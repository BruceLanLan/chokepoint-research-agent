"""Kill-criteria monitor — surface active theses that need review pressure-tests."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.ops.theses import list_theses


def kill_criteria_dashboard() -> dict[str, Any]:
    theses = list_theses()
    items = []
    for t in theses:
        status = t.get("status") or "active"
        kills = list(t.get("kill_criteria") or [])
        reviews = list(t.get("reviews") or [])
        last_review = reviews[-1] if reviews else None
        risk = "low"
        if status == "active" and not kills:
            risk = "high"  # active thesis without kill criteria is a process failure
        elif status == "active" and kills and not reviews:
            risk = "medium"
        elif status == "watching":
            risk = "medium"
        elif status == "invalidated":
            risk = "closed"
        items.append(
            {
                "id": t.get("id"),
                "title": t.get("title"),
                "status": status,
                "kill_count": len(kills),
                "kill_criteria": kills,
                "review_count": len(reviews),
                "last_review": last_review,
                "process_risk": risk,
                "symbols": t.get("related_symbols") or [],
            }
        )
    items.sort(
        key=lambda x: {"high": 0, "medium": 1, "low": 2, "closed": 3}.get(
            x["process_risk"], 9
        )
    )
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "items": items,
        "high_risk_count": sum(1 for i in items if i["process_risk"] == "high"),
        "active_without_kills": [
            i["id"] for i in items if i["process_risk"] == "high"
        ],
        "disclaimer": "research_only_not_investment_advice",
    }
