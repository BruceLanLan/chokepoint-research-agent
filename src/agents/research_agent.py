"""Build the multi-agent investment research deep agent."""

from __future__ import annotations

from typing import Any, Literal

from src.config import ResearchMode, Settings, get_settings
from src.prompts.investment import (
    BILINGUAL_EXTRA,
    CHOKEPOINT_MAPPER_PROMPT,
    COMPARE_MODE_EXTRA,
    FUNDAMENTAL_ANALYST_PROMPT,
    LEAD_ANALYST_PROMPT,
    MACRO_INDUSTRY_ANALYST_PROMPT,
    NEWS_CATALYST_ANALYST_PROMPT,
    RISK_REVIEWER_PROMPT,
)
from src.tools.research_tools import all_tools, researcher_tools

Mode = ResearchMode


def _fmt(template: str, **kwargs: Any) -> str:
    return template.format(**kwargs)


def _mode_suffix(mode: Mode, bilingual: bool = False) -> str:
    if mode == "chokepoint_fast":
        base = (
            "\n\n# 本轮运行模式：chokepoint_fast\n"
            "只委派 chokepoint-mapper 与 risk-reviewer。"
            "输出仍需含 Scorecard + 红蓝对抗 + 来源。跳过完整财务深潜。\n"
        )
    elif mode == "risk_only":
        base = (
            "\n\n# 本轮运行模式：risk_only\n"
            "用户会提供已有论点；主要调用 risk-reviewer 做魔鬼代言人。"
            "必要时用一次搜索核实关键反证。\n"
        )
    elif mode == "compare":
        base = "\n\n" + COMPARE_MODE_EXTRA + "\n委派：chokepoint + fundamental + risk（并行对照）。\n"
    else:
        base = "\n\n# 本轮运行模式：full（完整多专家流程）\n"
        base += (
            "A股/港股优先 get_cn_stock_quote / search_cn_company_news；"
            "美股 get_market_snapshot；美股文件 sec_search_company / sec_recent_filings；"
            "搜索 web_search；写完可用 validate_citations 自检。\n"
        )
    if bilingual:
        base += "\n" + BILINGUAL_EXTRA
    return base


def build_investment_agent(
    settings: Settings | None = None,
    mode: Mode | None = None,
):
    """Create the lead investment agent with specialist sub-agents.

    Prefers `deepagents.create_deep_agent` when installed.
    Falls back to the built-in parallel orchestrator otherwise.
    """
    settings = settings or get_settings()
    mode = mode or settings.research_mode

    try:
        return _build_deep_agent(settings, mode=mode)
    except Exception as exc:  # noqa: BLE001
        print(f"[chokepoint-agent] deepagents unavailable ({exc}); using fallback orchestrator")
        from src.agents.fallback_orchestrator import build_fallback_agent

        return build_fallback_agent(settings, mode=mode)


def _subagent_specs(max_s: int, mode: Mode) -> list[dict[str, Any]]:
    chokepoint = {
        "name": "chokepoint-mapper",
        "description": (
            "供应链瓶颈制图员：Bottom-Up 逆向工程、Chokepoint Scorecard、"
            "物理/地理不可替代节点。适合 AI 基建、半导体、CPO、机器人、稀土材料。"
        ),
        "system_prompt": _fmt(CHOKEPOINT_MAPPER_PROMPT, max_searches=max_s),
        "tools": researcher_tools(),
    }
    fundamental = {
        "name": "fundamental-analyst",
        "description": (
            "基本面分析师：商业模式、财务、估值、竞争格局、机构覆盖真空。"
        ),
        "system_prompt": _fmt(FUNDAMENTAL_ANALYST_PROMPT, max_searches=max_s),
        "tools": researcher_tools(),
    }
    news = {
        "name": "news-catalyst-analyst",
        "description": "新闻与催化分析师：事件时间线、舆情与预期差。",
        "system_prompt": _fmt(NEWS_CATALYST_ANALYST_PROMPT, max_searches=max_s),
        "tools": researcher_tools(),
    }
    macro = {
        "name": "macro-industry-analyst",
        "description": "宏观/政策/行业分析师：景气、出口管制、地缘产能与传导。",
        "system_prompt": _fmt(MACRO_INDUSTRY_ANALYST_PROMPT, max_searches=max_s),
        "tools": researcher_tools(),
    }
    risk = {
        "name": "risk-reviewer",
        "description": (
            "魔鬼代言人：空头论据、路径依赖、流动性陷阱、kill criteria。"
            "综合写报前必须至少调用一次。"
        ),
        "system_prompt": RISK_REVIEWER_PROMPT,
        "tools": researcher_tools(),
    }

    if mode == "chokepoint_fast":
        return [chokepoint, risk]
    if mode == "risk_only":
        return [risk]
    if mode == "compare":
        return [chokepoint, fundamental, risk]
    return [chokepoint, fundamental, news, macro, risk]


def _build_deep_agent(settings: Settings, mode: Mode = "full"):
    from deepagents import create_deep_agent

    from src.agents.model import build_model

    model = build_model(settings)
    max_s = settings.max_searches_per_subagent
    max_c = settings.max_concurrent_subagents

    lead_prompt = _fmt(LEAD_ANALYST_PROMPT, max_concurrent=max_c) + _mode_suffix(
        mode, bilingual=settings.bilingual_memo
    )
    subagents = _subagent_specs(max_s, mode)

    return create_deep_agent(
        model=model,
        tools=all_tools(),
        system_prompt=lead_prompt,
        subagents=subagents,
    )


def extract_final_text(result: dict[str, Any]) -> str:
    """Pull the last AI message content from an agent invoke result."""
    messages = result.get("messages") or []
    for msg in reversed(messages):
        content = getattr(msg, "content", None)
        if not content:
            continue
        if isinstance(content, str) and content.strip():
            return content
        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, str):
                    parts.append(block)
                elif isinstance(block, dict) and block.get("type") == "text":
                    parts.append(block.get("text", ""))
                elif hasattr(block, "text"):
                    parts.append(block.text)
            text = "".join(parts).strip()
            if text:
                return text
    return "(No final answer produced)"
