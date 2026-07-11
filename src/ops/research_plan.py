"""Offline research plan generator (no LLM) from skill packs + templates."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.ops.templates import list_templates, render_template
from src.skills.loader import list_skill_packs, load_skill_pack


def build_research_plan(
    topic: str,
    *,
    skill: str | None = None,
    template_id: str = "chokepoint_map",
    mode: str | None = None,
) -> dict[str, Any]:
    """Produce a structured investigation plan without calling a model."""
    skill_meta = load_skill_pack(skill) if skill else None
    if skill_meta is None and skill:
        # soft fallback: empty skill
        skill_meta = {"id": skill, "name": skill, "focus_nodes": [], "suggested_kill_criteria": []}

    tpl_vars = {
        "system": topic,
        "context": (skill_meta or {}).get("description") or "",
    }
    rendered = None
    try:
        rendered = render_template(template_id, tpl_vars)
    except Exception:  # noqa: BLE001
        rendered = {
            "question": f"Chokepoint map for: {topic}",
            "mode": mode or "chokepoint_fast",
        }

    focus = list((skill_meta or {}).get("focus_nodes") or [])
    kills = list((skill_meta or {}).get("suggested_kill_criteria") or [])
    steps = [
        {
            "step": 1,
            "title": "Define system boundary",
            "action": f"Write the system under study for «{topic}» and list primary demand drivers.",
        },
        {
            "step": 2,
            "title": "Map physical nodes",
            "action": "Enumerate supply-chain nodes; prefer components with low substitutability.",
            "focus_nodes": focus,
        },
        {
            "step": 3,
            "title": "Scorecard",
            "action": "Score irreplaceability / concentration / leverage / vacuum / inflection (1–5).",
        },
        {
            "step": 4,
            "title": "Evidence pass",
            "action": "Attach filings, announcements, capacity data; prefer primary sources.",
        },
        {
            "step": 5,
            "title": "Red-team / kill criteria",
            "action": "Write falsifiers before any bullish narrative hardens.",
            "suggested_kill_criteria": kills,
        },
        {
            "step": 6,
            "title": "Compare & catalog",
            "action": "Diff vs prior memos; tag + link lineage; store evidence ledger.",
        },
    ]

    return {
        "topic": topic,
        "skill": (skill_meta or {}).get("id"),
        "template_id": template_id,
        "mode": mode or rendered.get("mode") or (skill_meta or {}).get("default_mode") or "chokepoint_fast",
        "seed_question": rendered.get("question"),
        "steps": steps,
        "available_skills": [s["id"] for s in list_skill_packs()],
        "available_templates": [t["id"] for t in list_templates()],
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "disclaimer": "research_only_not_investment_advice",
        "note": "Offline plan only — not investment advice; run research to produce a memo.",
    }
