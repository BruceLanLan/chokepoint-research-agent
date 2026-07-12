"""Analysis engines + playbooks tests."""

from __future__ import annotations


def test_text_metrics_battery():
    from src.analysis.text_metrics import metric_00, run_all_metrics

    r = metric_00("chokepoint https://a.com kill criteria 供应链")
    assert r["urls"] >= 1
    allm = run_all_metrics("research memo with sources https://x.com")
    assert allm["count"] == 150
    assert allm["avg_score"] is not None


def test_scorecard_engine():
    from src.analysis.scorecard_engine import analyze_memo_scorecard, compare_scorecards

    md = """
## 研究结论
x
## 风险
kill
## 来源
https://a.com
| 节点 | 不可替代 | 集中度 | 杠杆 | 真空 | 拐点 | 备注 |
| A | 5 | 4 | 5 | 4 | 4 | n |
"""
    a = analyze_memo_scorecard(md)
    assert a["node_count"] >= 1
    c = compare_scorecards(md, md)
    assert "shared_top" in c


def test_playbooks():
    from src.playbooks.registry import get_playbook, list_playbooks

    ids = list_playbooks()
    assert len(ids) >= 15
    pb = get_playbook(ids[0])
    assert pb["questions"]
    assert pb["disclaimer"]
