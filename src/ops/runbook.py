"""Professional research runbook / SOP (offline, no LLM)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.ops.workspace_health import workspace_health_score
from src.skills.loader import list_skill_packs
from src.ops.knowledge_maps import list_maps


def professional_runbook(*, system: str = "") -> dict[str, Any]:
    """Generate a Chokepoint-oriented research SOP for analysts using this agent."""
    health = workspace_health_score()
    sys = system.strip() or "（填写系统边界，例如：AI GPU 集群光互连 / CPO）"
    steps = [
        {
            "phase": "0. Framing",
            "items": [
                f"Write the system boundary: {sys}",
                "State what question is *not* being answered (scope cut)",
                "Pick mode: chokepoint_fast | full | risk_only | compare",
                "Optional: skill pack + knowledge map seed",
            ],
        },
        {
            "phase": "1. Map",
            "items": [
                "Enumerate physical / supply-chain nodes top-down then bottom-up",
                "Mark candidates with low substitutability",
                "Build scorecard (irreplaceability / concentration / leverage / vacuum / inflection)",
            ],
        },
        {
            "phase": "2. Evidence",
            "items": [
                "Primary sources first: filings, exchanges, company announcements",
                "Run tools: SEC / CN announcements / HKEX / web search as available",
                "Store evidence ledger; reject orphan numbers without sources",
            ],
        },
        {
            "phase": "3. Red team",
            "items": [
                "Write kill criteria *before* narrative hardens",
                "risk_only pass or peer-review checklist",
                "Promote hypotheses → theses only with kills + symbols",
            ],
        },
        {
            "phase": "4. Publish gate",
            "items": [
                "python main.py checklist <memo.md>",
                "min-quality gate / postprocess metrics",
                "tag + lineage + export-pack for archival",
            ],
        },
        {
            "phase": "5. Ops hygiene",
            "items": [
                "Update watchlist / coverage heat",
                "python main.py digest",
                "python main.py workspace-health",
                "Queue mock runs before any --live burns",
            ],
        },
    ]
    return {
        "title": "Chokepoint Research Runbook",
        "system": sys,
        "workspace_grade": health.get("grade"),
        "workspace_score": health.get("score"),
        "steps": steps,
        "available_skills": [s.get("id") for s in list_skill_packs()],
        "available_maps": [m.get("id") for m in list_maps()],
        "cli_cheatsheet": [
            'python main.py maps <id> --seed',
            'python main.py plan "system" --skill semiconductor',
            'python main.py research "..." --mode chokepoint_fast --skill semiconductor --min-quality 50',
            "python main.py checklist <report.md>",
            "python main.py queue --run 1   # mock",
            "python main.py digest && python main.py workspace-health",
        ],
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "disclaimer": "research_only_not_investment_advice",
        "note": "SOP for research process quality — not investment advice.",
    }


def runbook_markdown(system: str = "") -> str:
    rb = professional_runbook(system=system)
    lines = [
        f"# {rb['title']}\n\n",
        f"system: {rb['system']}\n",
        f"workspace_health: {rb['workspace_grade']} ({rb['workspace_score']})\n\n",
        "> Research only — not investment advice. 仅供研究学习，不构成投资建议。\n\n",
    ]
    for phase in rb["steps"]:
        lines.append(f"## {phase['phase']}\n")
        for it in phase["items"]:
            lines.append(f"- {it}\n")
        lines.append("\n")
    lines.append("## CLI cheatsheet\n")
    for c in rb["cli_cheatsheet"]:
        lines.append(f"- `{c}`\n")
    return "".join(lines)
