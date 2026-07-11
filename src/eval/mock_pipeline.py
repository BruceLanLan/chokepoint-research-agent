"""Offline mock research pipeline — no LLM calls."""

from __future__ import annotations

from typing import Any

from src.pipeline.postprocess import postprocess_memo
from src.schemas.scorecard import validate_report_structure


MOCK_MEMO = """## 1. 研究结论
观望。示例 mock 研报用于离线流水线测试。

## 2. 系统解构：物理开关 / chokepoint
GPU → 互联 → CPO → ELS

| 节点 | 不可替代 | 集中度 | 杠杆 | 真空 | 拐点 |
| --- | --- | --- | --- | --- | --- |
| ELS | 5 | 4 | 5 | 4 | 3 |
| 对准 | 4 | 3 | 4 | 5 | 3 |

## 6. 风险与证伪条件
Kill criteria: CPO 推迟 24 个月

## 8. 信息来源
[1] https://example.com/mock-cpo

正文补充：mock pipeline 不调用大模型，只验证后处理、质检与图表解析。研究用途不构成投资建议。
""" + ("分析段落。" * 30)


def run_mock_pipeline() -> dict[str, Any]:
    q = validate_report_structure(MOCK_MEMO)
    pp = postprocess_memo("mock_cpo", MOCK_MEMO, mode="chokepoint_fast", embed_charts=True)
    return {
        "structure_pass": q.get("pass"),
        "structure_score": q.get("score"),
        "postprocess_gate": pp.get("gate_ok"),
        "scorecard_nodes": pp.get("scorecard_nodes"),
        "charts": pp.get("charts"),
        "ok": bool(q.get("pass") and pp.get("scorecard_nodes", 0) >= 1),
    }
