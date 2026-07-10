"""Fallback multi-agent orchestrator when deepagents is unavailable."""

from __future__ import annotations

import concurrent.futures
from dataclasses import dataclass
from typing import Any, Callable

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool

from src.agents.model import build_model
from src.config import ResearchMode, Settings, get_settings
from src.logging_utils import get_logger
from src.prompts.investment import (
    BILINGUAL_EXTRA,
    CHOKEPOINT_MAPPER_PROMPT,
    COMPARE_MODE_EXTRA,
    FUNDAMENTAL_ANALYST_PROMPT,
    LEAD_ANALYST_PROMPT,
    MACRO_INDUSTRY_ANALYST_PROMPT,
    NEWS_CATALYST_ANALYST_PROMPT,
    RISK_REVIEWER_PROMPT,
    SYNTHESIS_PROMPT,
)
from src.tools.resilience import get_cost_tracker
from src.tools.research_tools import researcher_tools

log = get_logger("chokepoint.fallback")


@dataclass
class Specialist:
    name: str
    title: str
    system_prompt: str


ALL_SPECIALISTS = [
    Specialist("chokepoint", "供应链瓶颈制图员", CHOKEPOINT_MAPPER_PROMPT),
    Specialist("fundamental", "基本面分析师", FUNDAMENTAL_ANALYST_PROMPT),
    Specialist("news", "新闻催化分析师", NEWS_CATALYST_ANALYST_PROMPT),
    Specialist("macro", "宏观行业分析师", MACRO_INDUSTRY_ANALYST_PROMPT),
]


def specialists_for_mode(mode: ResearchMode) -> list[Specialist]:
    if mode == "chokepoint_fast":
        return [s for s in ALL_SPECIALISTS if s.name == "chokepoint"]
    if mode == "risk_only":
        return []
    if mode == "compare":
        return [s for s in ALL_SPECIALISTS if s.name in {"chokepoint", "fundamental"}]
    return list(ALL_SPECIALISTS)


class FallbackInvestmentAgent:
    """Simple invoke/stream-compatible agent object."""

    def __init__(
        self,
        model: BaseChatModel,
        settings: Settings,
        mode: ResearchMode = "full",
        *,
        auto_save: bool = False,
    ):
        self.model = model
        self.settings = settings
        self.mode = mode
        self.auto_save = auto_save
        self.tools = researcher_tools()
        self._tools_by_name = {t.name: t for t in self.tools}

    def invoke(self, payload: dict[str, Any]) -> dict[str, Any]:
        question = _extract_question(payload)
        report = run_research_pipeline(
            question=question,
            model=self.model,
            settings=self.settings,
            tools=self.tools,
            tools_by_name=self._tools_by_name,
            mode=self.mode,
        )
        if self.auto_save:
            try:
                from src.tools.reports import save_report_file

                path = save_report_file(title=question[:40], markdown_body=report, mode=self.mode)
                report = report + f"\n\n---\n_Report saved: {path}_"
            except Exception as exc:  # noqa: BLE001
                log.warning("auto_save failed: %s", exc)
        return {"messages": [type("M", (), {"content": report, "type": "ai"})()]}

    def stream(self, payload: dict[str, Any], stream_mode: str = "updates"):
        question = _extract_question(payload)
        chunks: list[tuple[str, str]] = []

        def on_event(node: str, text: str) -> None:
            chunks.append((node, text))

        report = run_research_pipeline(
            question=question,
            model=self.model,
            settings=self.settings,
            tools=self.tools,
            tools_by_name=self._tools_by_name,
            mode=self.mode,
            on_event=on_event,
        )
        for node, text in chunks:
            yield {node: {"messages": [type("M", (), {"content": text, "type": "ai"})()]}}
        yield {
            "model": {
                "messages": [type("M", (), {"content": report, "type": "ai"})()]
            }
        }


def build_fallback_agent(
    settings: Settings | None = None,
    mode: ResearchMode = "full",
) -> FallbackInvestmentAgent:
    settings = settings or get_settings()
    model = build_model(settings)
    return FallbackInvestmentAgent(model, settings, mode=mode, auto_save=False)


def run_research_pipeline(
    question: str,
    model: BaseChatModel,
    settings: Settings,
    tools: list[BaseTool],
    tools_by_name: dict[str, BaseTool],
    mode: ResearchMode = "full",
    on_event: Callable[[str, str], None] | None = None,
) -> str:
    def emit(node: str, text: str) -> None:
        log.info("node=%s chars=%s", node, len(text or ""))
        if on_event:
            on_event(node, text)

    max_s = settings.max_searches_per_subagent
    specialists = specialists_for_mode(mode)
    max_workers = min(settings.max_concurrent_subagents, max(len(specialists), 1))

    findings: dict[str, str] = {}
    plan = ""

    if mode != "risk_only":
        lead_sys = LEAD_ANALYST_PROMPT.format(max_concurrent=max_workers)
        if mode == "compare":
            lead_sys += "\n" + COMPARE_MODE_EXTRA
        plan_msg = model.invoke(
            [
                SystemMessage(content=lead_sys),
                HumanMessage(
                    content=(
                        f"用户问题：{question}\n\n模式：{mode}\n"
                        "请先给出研究计划（2–4 步），并说明将派给哪些专家。"
                        "只输出计划，不要开始写完整研报。"
                    )
                ),
            ]
        )
        plan = _content_to_str(plan_msg.content)
        get_cost_tracker().add_llm(prompt_chars=len(lead_sys) + len(question), completion_chars=len(plan))
        emit("plan", plan)

        def run_one(spec: Specialist) -> tuple[str, str]:
            sys = spec.system_prompt.format(max_searches=max_s)
            task = (
                f"【研究任务】\n用户原始问题：{question}\n\n"
                f"总监计划摘要：\n{plan[:1500]}\n\n"
                f"请以{spec.title}身份完成你的部分，使用工具检索事实，输出结构化发现与 Sources。"
            )
            text = _tool_loop(
                model=model,
                system=sys,
                user=task,
                tools=tools,
                tools_by_name=tools_by_name,
                max_steps=max_s + 2,
            )
            return spec.name, text

        if specialists:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
                futures = [pool.submit(run_one, s) for s in specialists]
                for fut in concurrent.futures.as_completed(futures):
                    name, text = fut.result()
                    findings[name] = text
                    emit(name, text[:1000])

    # Risk reviewer always (except pure empty)
    risk_input = "\n\n".join(f"### {k}\n{v}" for k, v in findings.items()) or question
    risk = _tool_loop(
        model=model,
        system=RISK_REVIEWER_PROMPT,
        user=(
            f"用户问题：{question}\n\n模式：{mode}\n"
            f"以下是其他分析师结论（可能为空，则直接审查用户论点）：\n\n{risk_input}"
        ),
        tools=tools,
        tools_by_name=tools_by_name,
        max_steps=4 if mode != "risk_only" else 6,
    )
    findings["risk"] = risk
    emit("risk", risk[:1000])

    all_findings = "\n\n".join(f"## {k}\n{v}" for k, v in findings.items())
    bilingual = BILINGUAL_EXTRA if settings.bilingual_memo else ""
    if mode == "compare":
        bilingual = (bilingual + "\n" + COMPARE_MODE_EXTRA).strip()
    synth = model.invoke(
        [
            SystemMessage(content="你是投研总监，负责综合写报。"),
            HumanMessage(
                content=SYNTHESIS_PROMPT.format(
                    question=question,
                    findings=all_findings,
                    bilingual=bilingual,
                )
            ),
        ]
    )
    report = _content_to_str(synth.content)
    get_cost_tracker().add_llm(prompt_chars=len(all_findings), completion_chars=len(report))
    emit("final", report)
    return report


def _tool_loop(
    model: BaseChatModel,
    system: str,
    user: str,
    tools: list[BaseTool],
    tools_by_name: dict[str, BaseTool],
    max_steps: int = 6,
) -> str:
    llm = model.bind_tools(tools)
    messages: list[Any] = [SystemMessage(content=system), HumanMessage(content=user)]
    final = ""

    for _ in range(max_steps):
        ai = llm.invoke(messages)
        messages.append(ai)
        tool_calls = getattr(ai, "tool_calls", None) or []
        if not tool_calls:
            final = _content_to_str(ai.content)
            break
        for tc in tool_calls:
            name = tc.get("name") if isinstance(tc, dict) else tc["name"]
            args = tc.get("args") if isinstance(tc, dict) else tc.get("args", {})
            tc_id = tc.get("id") if isinstance(tc, dict) else tc.get("id", name)
            tool = tools_by_name.get(name)
            if tool is None:
                result = f"Unknown tool: {name}"
            else:
                try:
                    from src.tools.resilience import get_cost_tracker, with_retry

                    @with_retry(attempts=3, base_delay=0.5)
                    def _invoke():
                        return tool.invoke(args or {})

                    result = _invoke()
                    get_cost_tracker().add_tool(name)
                except Exception as exc:  # noqa: BLE001
                    result = f"Tool error ({name}): {exc}"
            messages.append(
                ToolMessage(content=str(result)[:20000], tool_call_id=tc_id or name)
            )
        final = _content_to_str(ai.content)
    else:
        wrap = model.invoke(
            messages
            + [
                HumanMessage(
                    content="请基于已有工具结果，直接输出最终结构化结论与 Sources，不要再调用工具。"
                )
            ]
        )
        final = _content_to_str(wrap.content)

    return final or "(empty specialist output)"


def _content_to_str(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
            elif hasattr(block, "text"):
                parts.append(getattr(block, "text", ""))
        return "".join(parts)
    return str(content)


def _extract_question(payload: dict[str, Any]) -> str:
    messages = payload.get("messages") or []
    if not messages:
        return ""
    last = messages[-1]
    if isinstance(last, dict):
        return str(last.get("content") or "")
    return str(getattr(last, "content", "") or "")
