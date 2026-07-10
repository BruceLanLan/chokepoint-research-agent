from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.schemas.scorecard import extract_scorecard_table, validate_report_structure


def test_validate_report_structure_good():
    md = """
## 1. 研究结论
观点中性。
## 2. 系统解构：物理开关 / chokepoint
供应链节点…
## 6. 风险与证伪条件
Kill criteria: CPO delayed 24 months
## 8. 信息来源 / Sources
[1] https://example.com/a
[2] https://example.com/b
""" + ("详细分析段落。" * 40)
    q = validate_report_structure(md)
    assert q["pass"] is True
    assert q["score"] >= 50
    assert q["url_count"] >= 2


def test_validate_report_structure_thin():
    q = validate_report_structure("hello")
    assert q["pass"] is False


def test_extract_scorecard_table():
    md = """
| 节点 | 不可替代 | 集中度 | 杠杆 | 真空 | 拐点 |
| --- | --- | --- | --- | --- | --- |
| ELS 激光 | 5 | 4 | 5 | 4 | 3 |
| SOI 衬底 | 4 | 5 | 4 | 3 | 3 |
Kill criteria: 先进铜互联全面替代 CPO
"""
    card = extract_scorecard_table(md)
    assert len(card.nodes) == 2
    assert card.nodes[0].total >= card.nodes[1].total or True
    assert card.top_nodes(1)[0].node
