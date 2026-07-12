"""Playbook: saas infra — research process only."""

from __future__ import annotations
from typing import Any

PLAYBOOK_ID = "saas_infra"
TITLE = "Saas Infra"
DISCLAIMER = "research_only_not_investment_advice"

QUESTIONS = [
    "What is the system boundary?",
    "Which physical or contractual nodes are hard to substitute?",
    "What would falsify the core thesis (kill criteria)?",
    "Where is evidence weak or one-source?",
    "What capacity / policy timelines matter?",
    "Who are substitutes and dual sources?",
    "What numbers need dates and primary sources?",
    "What is out of scope for this memo?",
]

STEPS = [
    {"step": 1, "name": "Frame", "actions": ["Define system", "Cut scope"]},
    {"step": 2, "name": "Map", "actions": ["List nodes", "Draft scorecard"]},
    {"step": 3, "name": "Evidence", "actions": ["Filings", "Announcements", "Channel"]},
    {"step": 4, "name": "Red team", "actions": ["Kill criteria", "Peer review"]},
    {"step": 5, "name": "Publish gate", "actions": ["checklist", "grade-memo", "export-pack"]},
]


def run(context: str = "") -> dict[str, Any]:
    return {
        "playbook": PLAYBOOK_ID,
        "title": TITLE,
        "context": context,
        "questions": QUESTIONS,
        "steps": STEPS,
        "disclaimer": DISCLAIMER,
        "note": "Process playbook for research ops — not investment advice.",
    }
