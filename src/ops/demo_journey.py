"""Offline end-to-end demo journey for new users (no LLM)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.ops.pro.verticals import list_verticals, run_vertical_suite, scaffold_research_question
from src.ops.research_desk import research_desk_status
from src.ops.research_plan import build_research_plan
from src.eval.mock_pipeline import MOCK_MEMO, run_mock_pipeline
from src.pipeline.save_pipeline import save_research_memo
from src.schemas.scorecard import validate_report_structure


def run_demo_journey(*, vertical: str = "cpo_optics", save: bool = True) -> dict[str, Any]:
    """Simulate a professional weekly path offline."""
    steps: list[dict[str, Any]] = []
    desk0 = research_desk_status()
    steps.append({"step": "desk_before", "health": desk0.get("workspace_health")})

    verts = list_verticals()
    steps.append({"step": "list_verticals", "count": len(verts), "ids": [v["id"] for v in verts]})

    plan = build_research_plan(f"Demo system for {vertical}", vertical=vertical)
    steps.append(
        {
            "step": "plan",
            "vertical": plan.get("vertical"),
            "mode": plan.get("mode"),
            "seed_preview": (plan.get("seed_question") or "")[:180],
        }
    )

    sc = scaffold_research_question(vertical)
    steps.append({"step": "scaffold", "ok": not sc.get("error"), "mode": sc.get("mode")})

    mock = run_mock_pipeline()
    report = f"# Demo journey vertical={vertical}\n\n{MOCK_MEMO}"
    quality = validate_report_structure(report)
    saved = None
    if save:
        saved = save_research_memo(
            f"demo_{vertical}",
            report,
            mode="chokepoint_fast",
            skill=sc.get("suggested_skill"),
            vertical=vertical,
            skip_postprocess=False,
            min_quality=0,
            auto_tag=True,
            pro_suite=False,
        )
    suite = run_vertical_suite(
        vertical,
        text=report + " kill criteria system boundary https://example.com capacity nodes",
        symbol="DEMO",
    )
    steps.append(
        {
            "step": "mock_memo",
            "structure_score": quality.get("score"),
            "saved_path": (saved or {}).get("path") if isinstance(saved, dict) else saved,
            "mock_pipeline": {
                "structure_score": mock.get("structure_score"),
                "gate": mock.get("postprocess_gate"),
            },
        }
    )
    steps.append(
        {
            "step": "vertical_suite",
            "modules": suite.get("modules"),
            "gates_ok": suite.get("gates_ok"),
            "gate_rate": suite.get("gate_rate"),
        }
    )

    desk1 = research_desk_status()
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "vertical": vertical,
        "steps": steps,
        "desk_after": {
            "health": desk1.get("workspace_health"),
            "next_actions": desk1.get("next_actions"),
        },
        "disclaimer": "research_only_not_investment_advice",
        "note": "Offline demo journey — process hygiene only, not investment advice.",
    }
