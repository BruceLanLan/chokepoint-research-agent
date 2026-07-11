"""v2.6–v3.0 pipeline / skills / cache tests."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_postprocess_and_metrics(tmp_path, monkeypatch):
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path / "reports"))
    from src.config import clear_settings_cache
    from src.pipeline.postprocess import metrics_summary, postprocess_memo

    clear_settings_cache()
    md = """## 1. 研究结论
观望 chokepoint
## 风险
Kill criteria: delay
## 来源
https://example.com/a

| 节点 | 不可替代 | 集中度 | 杠杆 | 真空 | 拐点 |
| --- | --- | --- | --- | --- | --- |
| ELS | 5 | 4 | 5 | 4 | 3 |
""" + ("段落" * 40)
    pp = postprocess_memo("t", md, mode="full", embed_charts=True, min_quality=40)
    assert pp["scorecard_nodes"] >= 1
    assert pp["gate_ok"] is True
    assert "Scorecard" in pp["markdown"] or pp["charts"].get("svg_path")
    m = metrics_summary()
    assert m["count"] >= 1


def test_skill_packs():
    from src.skills.loader import list_skill_packs, skill_prompt_suffix

    packs = list_skill_packs()
    ids = {p["id"] for p in packs}
    assert "semiconductor" in ids
    assert "robotics" in ids
    s = skill_prompt_suffix("semiconductor")
    assert "半导体" in s or "HBM" in s


def test_mock_pipeline():
    from src.eval.mock_pipeline import run_mock_pipeline

    r = run_mock_pipeline()
    assert r["ok"] is True


def test_http_cache(tmp_path, monkeypatch):
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path / "reports"))
    from src.cache.http_cache import clear_http_cache, cached_get_json
    from src.config import clear_settings_cache

    clear_settings_cache()
    # use a public tiny JSON if network fails, still test clear
    n = clear_http_cache()
    assert n >= 0
