"""Feature train v8.7–v10: compare export, thesis link, coverage, golden path."""

from __future__ import annotations

import time

from fastapi.testclient import TestClient

from src.api import app
from src.ops.capabilities import workstation_capabilities
from src.ops.compare_export import export_compare_pack
from src.ops.golden_path import run_golden_path
from src.ops.research_queue import enqueue_vertical
from src.ops.theses import add_thesis, link_compare_to_thesis
from src.ops.vertical_compare import compare_vertical
from src.ops.vertical_coverage import vertical_coverage_dashboard
from src.ops.weekly_ops import run_weekly_ops
from src.tools.reports import save_report_file


def _memo(title: str, nodes: list[str]) -> str:
    rows = "\n".join(f"| {n} | 4 | 4 | 4 | 3 | 3 |" for n in nodes)
    return (
        f"## 1. 研究结论\n{title}\n## 2. Scorecard\n"
        "| 节点 | 不可替代 | 集中度 | 杠杆 | 真空 | 拐点 |\n| --- | --- | --- | --- | --- | --- |\n"
        f"{rows}\n## 6. 风险\nKill criteria: x\n## 8. 来源\nhttps://example.com/{title}\n"
        + ("段。" * 40)
    )


def test_compare_export_and_thesis_link(tmp_path, monkeypatch):
    from src.config import clear_settings_cache, get_settings

    clear_settings_cache()
    monkeypatch.setattr(get_settings(), "reports_dir", tmp_path)
    save_report_file("a", _memo("a", ["ELS", "PIC"]), vertical="cpo_optics", quality={"score": 50})
    time.sleep(0.05)
    save_report_file(
        "b", _memo("b", ["ELS", "PIC", "FAU"]), vertical="cpo_optics", quality={"score": 60}
    )
    pack = export_compare_pack(vertical_id="cpo_optics", include_udiff=False)
    assert pack.get("md_path")
    assert pack.get("json_path")
    cmp = compare_vertical("cpo_optics", include_udiff=False)
    th = add_thesis(title="CPO thesis", statement="CPO wins", kill_criteria=["pluggable cheaper"])
    linked = link_compare_to_thesis(th["id"], cmp)
    assert not linked.get("error")
    assert "ratio" in (linked.get("review_note") or "")


def test_vertical_coverage_and_weekly(tmp_path, monkeypatch):
    from src.config import clear_settings_cache, get_settings

    clear_settings_cache()
    monkeypatch.setattr(get_settings(), "reports_dir", tmp_path)
    save_report_file("h1", _memo("h1", ["HBM"]), vertical="hbm_packaging", quality={"score": 55})
    dash = vertical_coverage_dashboard()
    assert dash["packs"] >= 5
    assert any(r["vertical_id"] == "hbm_packaging" and r["memo_count"] >= 1 for r in dash["rows"])
    w = run_weekly_ops(save=False)
    assert w.get("vertical_coverage") is not None or "Vertical coverage" in (w.get("markdown") or "")


def test_enqueue_vertical_and_capabilities():
    item = enqueue_vertical("cpo_optics")
    assert item.get("vertical_id") == "cpo_optics"
    assert "CPO" in item.get("question", "") or "cpo" in item.get("question", "").lower()
    cap = workstation_capabilities()
    assert cap["features"]["golden_path"]
    assert cap["features"]["vertical_compare"]
    assert cap["counts"]["verticals"] >= 5


def test_golden_path_offline(tmp_path, monkeypatch):
    from src.config import clear_settings_cache, get_settings

    clear_settings_cache()
    monkeypatch.setattr(get_settings(), "reports_dir", tmp_path)
    out = run_golden_path(vertical="power_cooling", save_demo=True, include_compare_seed=True)
    assert out.get("summary")
    steps = [s.get("step") for s in out.get("steps") or []]
    assert "doctor" in steps and "desk" in steps
    assert "demo_journey" in steps


def test_api_train_endpoints(tmp_path, monkeypatch):
    from src.config import clear_settings_cache, get_settings

    clear_settings_cache()
    monkeypatch.setattr(get_settings(), "reports_dir", tmp_path)
    c = TestClient(app)
    assert c.get("/capabilities").status_code == 200
    assert c.get("/verticals/coverage").status_code == 200
    r = c.post("/golden-path", json={"vertical": "specialty_materials", "save": True})
    assert r.status_code == 200
    assert r.json().get("summary")
    # seed pair then export compare
    save_report_file("s1", _memo("s1", ["R"]), vertical="specialty_materials", quality={"score": 40})
    time.sleep(0.05)
    save_report_file("s2", _memo("s2", ["R", "S"]), vertical="specialty_materials", quality={"score": 45})
    r2 = c.post(
        "/reports/compare/export",
        json={"vertical_id": "specialty_materials", "udiff": False},
    )
    assert r2.status_code == 200
    assert r2.json().get("md_path")
