"""v4.6 checklist + eval history."""

from __future__ import annotations

from pathlib import Path

import pytest

GOOD = """# Memo

## 研究结论
Node X is a chokepoint.

## 风险与证伪 / Kill criteria
- Multi-source appears

## 来源
- https://www.sec.gov/x

| 节点 | 不可替代 | 集中度 | 杠杆 | 真空 | 拐点 | 备注 |
|------|---------|--------|------|------|------|------|
| X | 5 | 4 | 5 | 4 | 4 | k |

本报告仅供研究学习，不构成投资建议。
"""


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "reports").mkdir()
    (tmp_path / "data").mkdir()
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path / "reports"))
    from src.config import clear_settings_cache

    clear_settings_cache()
    yield tmp_path
    clear_settings_cache()


def test_checklist_pass(ws):
    from src.config import get_settings
    from src.ops.checklist import run_checklist

    p = Path(get_settings().reports_dir) / "good.md"
    p.write_text(GOOD, encoding="utf-8")
    out = run_checklist(report_name="good.md")
    assert out["gate_ok"] is True
    assert out["passed"] == out["total"]


def test_checklist_fail(ws):
    from src.config import get_settings
    from src.ops.checklist import run_checklist

    p = Path(get_settings().reports_dir) / "bad.md"
    p.write_text("short note without structure", encoding="utf-8")
    out = run_checklist(report_name="bad.md")
    assert out["gate_ok"] is False


def test_eval_history(ws):
    from src.ops.eval_history import eval_trend, record_eval_run

    row = record_eval_run()
    assert row["total"] >= 1
    assert row["failed"] == 0
    trend = eval_trend()
    assert trend["count"] >= 1
    assert trend["latest"]["passed"] == trend["latest"]["total"]
