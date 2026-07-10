#!/usr/bin/env python3
"""Import-level smoke check (no API keys required for structure checks)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    from src.prompts.investment import LEAD_ANALYST_PROMPT, RISK_REVIEWER_PROMPT
    from src.tools.knowledge import list_knowledge_maps
    from src.tools.research_tools import all_tools, researcher_tools

    assert "投研总监" in LEAD_ANALYST_PROMPT or "Lead" in LEAD_ANALYST_PROMPT
    assert "风险" in RISK_REVIEWER_PROMPT or "Devil" in RISK_REVIEWER_PROMPT
    assert "物理开关" in LEAD_ANALYST_PROMPT or "Chokepoint" in LEAD_ANALYST_PROMPT
    assert len(all_tools()) >= 8
    assert len(researcher_tools()) >= 5
    maps = list_knowledge_maps.invoke({}).lower()
    assert "cpo" in maps
    assert "hbm" in maps or "rare_earth" in maps

    from src.config import Settings
    from src.eval.harness import run_all
    from src.schemas.scorecard import validate_report_structure

    s = Settings(openai_api_key="sk", openai_base_url="https://x", tavily_api_key="t")
    assert s.validate_runtime() == []
    assert validate_report_structure("研究结论 风险 来源 https://a.com " + "x" * 400)["score"] >= 40
    ev = run_all()
    assert ev["failed"] == 0

    env = ROOT / ".env"
    if env.exists():
        from dotenv import load_dotenv

        load_dotenv(env)
        try:
            from src.agents.research_agent import build_investment_agent
            from src.config import get_settings

            s = get_settings()
            try:
                s.resolved_api_key()
                agent = build_investment_agent(s)
                print("OK: agent built:", type(agent))
            except Exception as exc:  # noqa: BLE001
                print("SKIP agent build (keys/deps):", exc)
        except Exception as exc:  # noqa: BLE001
            print("SKIP:", exc)
    else:
        print("No .env yet — structure checks only")

    print("smoke_check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
