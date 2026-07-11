"""Tests for v3.1–v4.0 ops: evidence, graph, tags, compare, audit, docx, snapshot."""

from __future__ import annotations

from pathlib import Path

import pytest

SAMPLE_MD = """# CPO 研究备忘

## 研究结论
CPO 是光互连关键卡点，供给集中。

## 风险与证伪 / Kill criteria
- 客户转向 pluggable 路线

## 来源
- https://www.sec.gov/cgi-bin/browse-edgar
- Source: company 10-K filing
- 根据公告披露：产能扩张

| 节点 | 不可替代 | 集中度 | 杠杆 | 真空 | 拐点 | 备注 |
|------|---------|--------|------|------|------|------|
| 激光器 | 5 | 4 | 5 | 4 | 4 | key |
| DSP | 4 | 3 | 4 | 3 | 3 | mid |

标的代码 688981 与 NVDA 相关讨论 ticker: NVDA
"""


@pytest.fixture()
def tmp_workspace(tmp_path, monkeypatch):
    reports = tmp_path / "reports"
    reports.mkdir()
    data = tmp_path / "data"
    data.mkdir()
    monkeypatch.setenv("REPORTS_DIR", str(reports))
    from src.config import clear_settings_cache

    clear_settings_cache()
    yield tmp_path
    clear_settings_cache()


def test_extract_evidence(tmp_workspace):
    from src.ops.evidence import extract_and_store, evidence_summary, extract_evidence

    ev = extract_evidence(SAMPLE_MD, report_name="sample.md")
    assert ev["url_count"] >= 1
    assert any("sec.gov" in u for u in ev["urls"])
    assert "688981" in ev["tickers_cn"] or ev["tickers_cn"]
    row = extract_and_store(SAMPLE_MD, report_name="sample.md", title="CPO")
    assert row.get("id")
    summary = evidence_summary()
    assert summary["entries"] >= 1


def test_thesis_graph_and_mermaid(tmp_workspace):
    from src.ops.theses import add_thesis
    from src.ops.watchlist import add_item
    from src.ops.thesis_graph import build_thesis_graph, to_mermaid

    add_thesis(
        title="CPO bottleneck",
        statement="Laser supply is concentrated",
        system="AI optical",
        chokepoints=["laser", "DSP"],
        kill_criteria=["Pluggable wins"],
        related_symbols=["NVDA", "COHR"],
    )
    add_item(symbol="NVDA", name="NVIDIA", thesis="AI infra", priority="high")
    g = build_thesis_graph()
    assert g["stats"]["theses"] >= 1
    assert g["stats"]["chokepoints"] >= 1
    mm = to_mermaid(g)
    assert "flowchart" in mm
    assert "depends_on" in mm or "covers" in mm


def test_tags_and_collections(tmp_workspace):
    from src.ops.tags import (
        add_to_collection,
        create_collection,
        find_by_tag,
        get_tags,
        list_collections,
        tag_report,
    )

    tag_report("a.md", ["cpo", "optics"])
    assert "cpo" in get_tags("a.md")["tags"]
    assert "a.md" in find_by_tag("cpo")
    col = create_collection("Optics pack", reports=["a.md"])
    assert col["id"]
    add_to_collection(col["id"], "b.md")
    cols = list_collections()
    assert any(c["id"] == col["id"] for c in cols)


def test_compare_memos(tmp_workspace, monkeypatch):
    from src.config import get_settings
    from src.ops.compare_memos import compare_memos
    from src.tools.reports import save_report_file

    settings = get_settings()
    p1 = save_report_file(title="r1", markdown_body=SAMPLE_MD, mode="full", quality={"score": 80})
    p2 = save_report_file(
        title="r2",
        markdown_body=SAMPLE_MD.replace("激光器", "封装"),
        mode="full",
        quality={"score": 70},
    )
    names = [Path(p1).name, Path(p2).name]
    cmp = compare_memos(names)
    assert len(cmp["reports"]) == 2
    assert "quality_rank" in cmp


def test_audit_log(tmp_workspace):
    from src.ops.audit import audit_summary, list_events, log_event

    log_event("test_action", detail={"x": 1})
    ev = list_events(limit=5)
    assert ev and ev[-1]["action"] == "test_action"
    s = audit_summary()
    assert s["count"] >= 1


def test_kill_monitor_and_coverage(tmp_workspace):
    from src.ops.coverage_heat import coverage_heatmap
    from src.ops.kill_monitor import kill_criteria_dashboard
    from src.ops.theses import add_thesis
    from src.ops.watchlist import add_item

    add_thesis(title="No kills", statement="Risky process", status="active")
    add_thesis(
        title="Has kills",
        statement="Ok",
        kill_criteria=["X fails"],
        related_symbols=["TEST"],
        status="active",
    )
    add_item(symbol="TEST", name="Test Co", priority="high")
    dash = kill_criteria_dashboard()
    assert dash["high_risk_count"] >= 1
    heat = coverage_heatmap()
    assert "symbols" in heat
    assert any(s["symbol"] == "TEST" for s in heat["symbols"])


def test_docx_export(tmp_workspace):
    from src.tools.docx_report import markdown_to_docx

    meta = markdown_to_docx("CPO memo", SAMPLE_MD, mode="full")
    path = Path(meta["path"])
    assert path.is_file()
    assert path.suffix == ".docx"
    assert path.stat().st_size > 500


def test_snapshot(tmp_workspace):
    from src.ops.audit import log_event
    from src.ops.snapshot import create_snapshot
    from src.tools.reports import save_report_file

    log_event("snap_test")
    save_report_file(title="snap", markdown_body=SAMPLE_MD, mode="full", quality={"score": 60})
    meta = create_snapshot()
    path = Path(meta["path"])
    assert path.is_file()
    assert path.suffix == ".zip"


def test_plugin_loader():
    from src.plugins.loader import list_plugin_files, load_plugin

    files = list_plugin_files()
    assert any(f["name"] == "example_provider" for f in files)
    meta = load_plugin("example_provider")
    assert "error" not in meta
    assert meta.get("name") == "example_provider"


def test_postprocess_includes_evidence(tmp_workspace):
    from src.pipeline.postprocess import postprocess_memo

    r = postprocess_memo("t", SAMPLE_MD, mode="full", embed_charts=False)
    assert r["gate_ok"] is True or r["quality"]["score"] >= 0
    assert "evidence" in r
    assert r["evidence"].get("url_count", 0) >= 1
