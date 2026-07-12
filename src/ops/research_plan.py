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
    vertical: str | None = None,
) -> dict[str, Any]:
    """Produce a structured investigation plan without calling a model."""
    skill_meta = load_skill_pack(skill) if skill else None
    if skill_meta is None and skill:
        # soft fallback: empty skill
        skill_meta = {"id": skill, "name": skill, "focus_nodes": [], "suggested_kill_criteria": []}

    # Auto-suggest deep vertical from topic text
    suggested_verticals: list[dict[str, Any]] = []
    vertical_meta = None
    try:
        from src.ops.pro.verticals import load_vertical, scaffold_research_question, suggest_vertical

        suggested_verticals = suggest_vertical(topic, limit=3)
        vid = vertical or ((suggested_verticals[0]["id"] if suggested_verticals else None))
        if vid:
            vertical_meta = load_vertical(vid)
            if not skill and vertical_meta:
                from src.ops.pro.verticals import _suggested_skill

                skill = skill or _suggested_skill(vid)
                skill_meta = load_skill_pack(skill) if skill else skill_meta
    except Exception:  # noqa: BLE001
        vertical_meta = None

    tpl_vars = {
        "system": topic,
        "context": (skill_meta or {}).get("description") or "",
        "vertical_id": (vertical_meta or {}).get("id") or vertical or "",
    }
    rendered = None
    try:
        # Prefer vertical coverage template when a pack matches
        use_tpl = template_id
        if vertical_meta and template_id == "chokepoint_map":
            use_tpl = "vertical_coverage"
        rendered = render_template(use_tpl, tpl_vars)
        template_id = use_tpl
    except Exception:  # noqa: BLE001
        rendered = {
            "question": f"Chokepoint map for: {topic}",
            "mode": mode or "chokepoint_fast",
        }

    # Enrich seed question with vertical scaffold when available
    if vertical_meta:
        try:
            from src.ops.pro.verticals import scaffold_research_question

            sc = scaffold_research_question(
                vertical_meta["id"], system=topic, context=str(tpl_vars.get("context") or "")
            )
            if sc.get("question"):
                rendered["question"] = sc["question"]
                rendered["mode"] = sc.get("mode") or rendered.get("mode")
        except Exception:  # noqa: BLE001
            pass

    focus = list((skill_meta or {}).get("focus_nodes") or [])
    if vertical_meta:
        for n in vertical_meta.get("physical_nodes") or []:
            if isinstance(n, dict):
                focus.append(n.get("label") or n.get("id"))
            else:
                focus.append(str(n))
    kills = list((skill_meta or {}).get("suggested_kill_criteria") or [])
    if vertical_meta:
        kills.extend(list(vertical_meta.get("kill_criteria") or []))
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
    if vertical_meta:
        steps.insert(
            1,
            {
                "step": "1b",
                "title": f"Apply vertical pack: {vertical_meta.get('title')}",
                "action": (
                    f"Load pack `{vertical_meta.get('id')}` — stress its physical nodes "
                    "and kill criteria before free-form narrative."
                ),
                "modules": vertical_meta.get("modules") or [],
            },
        )

    return {
        "topic": topic,
        "skill": (skill_meta or {}).get("id") if skill_meta else skill,
        "vertical": (vertical_meta or {}).get("id"),
        "suggested_verticals": suggested_verticals,
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
