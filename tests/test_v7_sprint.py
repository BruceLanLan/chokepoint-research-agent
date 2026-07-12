"""Consolidation sprint tests: save pipeline, pro engine YAML, thesis links, migrate, evals."""

from __future__ import annotations

from pathlib import Path

import pytest

MD = """# Sprint memo

## 研究结论
System chokepoint with concentration.

## 风险与证伪 / Kill criteria
- Multi-source

## 来源
https://example.com/s

| 节点 | 不可替代 | 集中度 | 杠杆 | 真空 | 拐点 | 备注 |
| A | 5 | 4 | 5 | 4 | 4 | n |

不构成投资建议
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


def test_pro_engine_yaml_backed(ws):
    from src.ops.pro.engine import ProEngine, list_spec_ids
    from src.ops.pro import PRO_MODULE_IDS

    assert len(list_spec_ids()) >= 50
    assert len(PRO_MODULE_IDS) == 50
    eng = ProEngine("risk_matrix")
    out = eng.analyze(text="system chokepoint kill criteria https://x.com risk 2024")
    assert out["gate_ok"] is True
    assert out["domain_hints"]


def test_save_pipeline_and_frontmatter(ws):
    from src.pipeline.save_pipeline import save_research_memo
    from src.tools.reports import parse_frontmatter, read_report

    r = save_research_memo(
        "title",
        MD,
        mode="full",
        skill="semiconductor",
        thesis_id=None,
        auto_tag=True,
        skip_postprocess=False,
    )
    assert Path(r["path"]).is_file()
    body = read_report(r["name"])
    meta = parse_frontmatter(body or "")
    assert meta.get("skill") == "semiconductor"
    assert "quality_score" in meta
    assert r.get("evidence_stored") is True


def test_thesis_links(ws):
    from src.ops.theses import add_thesis
    from src.ops.thesis_links import link_report_to_thesis, links_for_thesis

    t = add_thesis(title="T", statement="S", kill_criteria=["k"])
    link = link_report_to_thesis(t["id"], "memo.md")
    assert link.get("thesis_id") == t["id"]
    assert links_for_thesis(t["id"])


def test_store_migrate(ws):
    from src.ops.store_migrate import migrate_data_stores

    m1 = migrate_data_stores()
    assert m1["version"] >= 2
    m2 = migrate_data_stores()
    assert m2["actions"] == [] or m2["previous"] == m2["version"]


def test_golden_eval_count():
    from src.eval.harness import load_cases, run_all

    cases = load_cases()
    assert len(cases) >= 15
    result = run_all()
    assert result["failed"] == 0


def test_remote_plugin_denied_without_allowlist(ws, monkeypatch):
    from src.plugins.remote_install import install_from_manifest

    monkeypatch.delenv("PLUGIN_ALLOW_HOSTS", raising=False)
    out = install_from_manifest("https://example.com/manifest.json")
    assert out["ok"] is False


def test_verticals_exist():
    from pathlib import Path

    d = Path("skills/pro_verticals")
    assert d.is_dir()
    assert len(list(d.glob("*.yaml"))) >= 5


def test_glossary_no_filler():
    from src.ops.glossary_search import list_glossary_terms

    terms = list_glossary_terms()
    assert not any(t.startswith("research_term_") for t in terms)
    assert "chokepoint" in terms
