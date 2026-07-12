"""One-command golden path for offline workstation readiness."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src import __version__
from src.ops.demo_journey import run_demo_journey
from src.ops.doctor import run_doctor
from src.ops.research_desk import research_desk_status
from src.ops.vertical_coverage import vertical_coverage_dashboard

DISCLAIMER = "research_only_not_investment_advice"


def run_golden_path(
    *,
    vertical: str = "cpo_optics",
    save_demo: bool = True,
    include_compare_seed: bool = True,
) -> dict[str, Any]:
    """Offline sequence: doctor → desk → vertical coverage → demo journey."""
    steps: list[dict[str, Any]] = []
    doctor = run_doctor()
    steps.append(
        {
            "step": "doctor",
            "ok": doctor.get("ok"),
            "ops_ok": doctor.get("ops_ok"),
            "live_ready": doctor.get("live_ready"),
            "config": doctor.get("config"),
            "ops": doctor.get("ops"),
        }
    )
    desk = research_desk_status()
    steps.append(
        {
            "step": "desk",
            "health": desk.get("workspace_health"),
            "next_actions": (desk.get("next_actions") or [])[:4],
        }
    )
    cov = vertical_coverage_dashboard()
    steps.append(
        {
            "step": "vertical_coverage",
            "with_memos": cov.get("with_memos"),
            "with_pairs": cov.get("with_pairs"),
            "actions": (cov.get("next_actions") or [])[:3],
        }
    )
    # Optionally seed a second memo if only one exists for compare
    demo = run_demo_journey(vertical=vertical, save=save_demo)
    steps.append(
        {
            "step": "demo_journey",
            "vertical": vertical,
            "ok": not any(s.get("error") for s in (demo.get("steps") or []) if isinstance(s, dict)),
            "saved": (demo.get("steps") or [{}])[-2:] if demo.get("steps") else None,
        }
    )
    if include_compare_seed and save_demo:
        # second mock save for pair
        demo2 = run_demo_journey(vertical=vertical, save=True)
        steps.append({"step": "demo_journey_second_pass", "vertical": vertical})
        try:
            from src.ops.compare_export import export_compare_pack

            pack = export_compare_pack(vertical_id=vertical, include_udiff=False)
            steps.append({"step": "compare_export", "pack": pack.get("compare"), "md": pack.get("md_path")})
        except Exception as exc:  # noqa: BLE001
            steps.append({"step": "compare_export", "error": str(exc)[:160]})
    else:
        demo2 = None

    return {
        "version": __version__,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "vertical": vertical,
        "steps": steps,
        "summary": {
            "ops_ok": doctor.get("ops_ok"),
            "live_ready": doctor.get("live_ready"),
            "desk_grade": (desk.get("workspace_health") or {}).get("grade"),
            "verticals_with_memos": cov.get("with_memos"),
        },
        "next": [
            f"python main.py compare-vertical {vertical}",
            "python main.py --server",
            "UI: Desk → Demo / Reports → filter vertical → compare",
        ],
        "disclaimer": DISCLAIMER,
        "note": "Offline golden path — process hygiene only, not investment advice.",
    }
