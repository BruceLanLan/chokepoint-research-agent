"""Second-pass peer review helper (wraps risk framing)."""

from __future__ import annotations


def peer_review_question(memo_or_thesis: str) -> str:
    return (
        "【同行复审 / Peer review — devil's advocate】\n"
        "请对以下投研备忘录或论点做独立第二意见：\n"
        "1) 事实与推断是否混淆\n"
        "2) 卡脖子评分是否过高/过低\n"
        "3) 最强 3 条反证\n"
        "4) kill criteria 是否可操作\n"
        "5) 还缺哪些必须的公开数据\n"
        "输出结构：复审结论 / 主要问题 / 建议修改 / 更新后的 kill criteria / Sources\n"
        "仅供研究学习，不构成投资建议。\n\n"
        f"—— 原文 ——\n{memo_or_thesis}"
    )
