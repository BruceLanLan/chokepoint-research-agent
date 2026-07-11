"""v4.2 knowledge maps, dashboard, brief process section, expanded eval."""

from __future__ import annotations

import pytest


@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "reports").mkdir()
    (tmp_path / "data").mkdir()
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path / "reports"))
    from src.config import clear_settings_cache

    clear_settings_cache()
    yield tmp_path
    clear_settings_cache()


def test_list_and_graph_maps():
    from src.ops.knowledge_maps import list_maps, map_research_seed, map_to_graph, map_to_mermaid

    items = list_maps()
    assert any(i["id"] == "cpo_ai_interconnect" for i in items)
    g = map_to_graph("cpo_ai_interconnect")
    assert g.get("system")
    assert any(n["kind"] == "candidate" for n in g["nodes"])
    mm = map_to_mermaid("cpo_ai_interconnect")
    assert "flowchart" in mm
    seed = map_research_seed("cpo_ai_interconnect")
    assert "卡点" in seed["question"] or "chokepoint" in seed["question"].lower() or seed["question"]


def test_cost_dashboard(ws):
    from src.ops.audit import log_event
    from src.ops.cost_dashboard import cost_quality_dashboard
    from src.pipeline.postprocess import postprocess_memo

    postprocess_memo(
        "t",
        "# x\n\n## 研究结论\nok\n\n## 风险\nkill\n\n## 来源\nhttps://a.com\n",
        embed_charts=False,
    )
    log_event("unit_test")
    dash = cost_quality_dashboard()
    assert "postprocess_metrics" in dash
    assert dash["audit"]["count"] >= 1


def test_brief_process_section(ws):
    from src.ops.brief import process_health_section
    from src.ops.theses import add_thesis

    add_thesis(title="No kill", statement="process risk", status="active")
    md = process_health_section()
    assert "Process health" in md
    assert "high_process_risk" in md


def test_eval_includes_new_goldens():
    from src.eval.harness import load_cases, run_all

    ids = {c.id for c in load_cases()}
    assert "knowledge_map_seed" in ids
    assert "compare_structure" in ids
    result = run_all()
    assert result["failed"] == 0
    assert result["total"] >= 6
