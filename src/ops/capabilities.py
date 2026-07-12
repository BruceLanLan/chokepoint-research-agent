"""Public capability snapshot for about / health / UI."""

from __future__ import annotations

from typing import Any

from src import __version__
from src.ops.live_safety import live_gate_status
from src.ops.pro import PRO_MODULE_IDS
from src.ops.pro.verticals import list_verticals
from src.playbooks.registry import list_playbooks
from src.questionnaires.registry import list_questionnaires
from src.rubrics.registry import list_rubrics
from src.skills.loader import list_skill_packs


def workstation_capabilities() -> dict[str, Any]:
    verts = list_verticals()
    return {
        "name": "Chokepoint Research Workstation",
        "version": __version__,
        "product_line": "research_ops",
        "golden_path": [
            "doctor --ops-only",
            "desk",
            "golden-path -V cpo_optics",
            "research --mock -V …",
            "compare-vertical …",
            "weekly-ops",
        ],
        "counts": {
            "pro_modules": len(PRO_MODULE_IDS),
            "verticals": len(verts),
            "skill_packs": len(list_skill_packs()),
            "playbooks": len(list_playbooks()),
            "questionnaires": len(list_questionnaires()),
            "rubrics": len(list_rubrics()),
        },
        "vertical_ids": [v["id"] for v in verts],
        "features": {
            "mock_research": True,
            "live_research_gated": True,
            "vertical_compare": True,
            "compare_export": True,
            "catalog_filters": True,
            "demo_journey": True,
            "golden_path": True,
            "ui_smoke": True,
        },
        "gates": live_gate_status(),
        "disclaimer": "research_only_not_investment_advice",
    }
