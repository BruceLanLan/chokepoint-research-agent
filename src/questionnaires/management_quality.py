"""Questionnaire: management_quality — research process only."""
from __future__ import annotations
from typing import Any
ID = "management_quality"
TITLE = "Management Quality"
ITEMS = [
    {"q": "What is the measurable definition?", "why": "Avoid vague language"},
    {"q": "What primary source would settle disagreement?", "why": "Evidence first"},
    {"q": "What would falsify the bullish process narrative?", "why": "Kill criteria"},
    {"q": "What is the time stamp on the latest hard number?", "why": "Staleness"},
    {"q": "Who is the second-best alternative supplier/path?", "why": "Substitution"},
    {"q": "What is explicitly out of scope?", "why": "Scope control"},
    {"q": "Which stakeholder has incentive to misreport?", "why": "Bias"},
    {"q": "What channel check would change your mind?", "why": "Field evidence"},
]
def run(context: str = "") -> dict[str, Any]:
    return {
        "id": ID, "title": TITLE, "items": ITEMS, "context": context,
        "disclaimer": "research_only_not_investment_advice",
        "note": "Structured questions for research ops — not investment advice.",
    }
