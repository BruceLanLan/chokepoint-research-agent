"""Unit tests that do not require live API keys."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_chokepoint_method_in_lead_prompt():
    from src.prompts.investment import CHOKEPOINT_METHOD, LEAD_ANALYST_PROMPT

    assert "物理开关" in CHOKEPOINT_METHOD or "Chokepoint" in CHOKEPOINT_METHOD
    assert "卡脖子" in LEAD_ANALYST_PROMPT or "Chokepoint" in LEAD_ANALYST_PROMPT
    assert "kill" in LEAD_ANALYST_PROMPT.lower() or "证伪" in LEAD_ANALYST_PROMPT


def test_prompt_format_placeholders():
    from src.prompts.investment import (
        CHOKEPOINT_MAPPER_PROMPT,
        FUNDAMENTAL_ANALYST_PROMPT,
        LEAD_ANALYST_PROMPT,
        SYNTHESIS_PROMPT,
    )

    assert "{max_concurrent}" in LEAD_ANALYST_PROMPT
    lead = LEAD_ANALYST_PROMPT.format(max_concurrent=3)
    assert "3" in lead

    assert "{max_searches}" in CHOKEPOINT_MAPPER_PROMPT
    assert "{max_searches}" in FUNDAMENTAL_ANALYST_PROMPT

    synth = SYNTHESIS_PROMPT.format(question="Q?", findings="F", bilingual="")
    assert "Q?" in synth and "F" in synth


def test_tools_export():
    from src.tools.research_tools import all_tools, researcher_tools

    names = {t.name for t in all_tools()}
    assert "web_search" in names
    assert "fetch_url" in names
    assert "get_market_snapshot" in names
    assert "save_research_report" in names
    assert len(researcher_tools()) >= 3


def test_extract_final_text():
    from src.agents.research_agent import extract_final_text

    class Msg:
        def __init__(self, content):
            self.content = content

    result = {"messages": [Msg("hello report")]}
    assert extract_final_text(result) == "hello report"
    assert extract_final_text({}) == "(No final answer produced)"


def test_settings_defaults():
    from src.config import Settings

    s = Settings(
        model_provider="openai_compatible",
        model_name="test-model",
        openai_api_key="sk-x",
        openai_base_url="https://example.com/v1",
    )
    assert s.resolved_api_key() == "sk-x"
    assert s.resolved_base_url() == "https://example.com/v1"
    assert s.max_concurrent_subagents >= 1
