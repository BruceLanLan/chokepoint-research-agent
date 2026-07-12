"""v8.6 — same-vertical memo compare."""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.api import app
from src.ops.vertical_compare import compare_pair, compare_vertical, list_vertical_reports
from src.tools.reports import save_report_file


def _memo(title: str, nodes: list[str], extra: str = "") -> str:
    rows = "\n".join(f"| {n} | 4 | 4 | 4 | 3 | 3 |" for n in nodes)
    return f"""## 1. 研究结论
{title}
## 2. Scorecard
| 节点 | 不可替代 | 集中度 | 杠杆 | 真空 | 拐点 |
| --- | --- | --- | --- | --- | --- |
{rows}
## 6. 风险与证伪条件
Kill criteria: test falsifier
## 8. 信息来源
[1] https://example.com/{title.replace(' ', '-')}
{extra}
""" + ("分析。" * 40)


def test_compare_pair_same_vertical(tmp_path, monkeypatch):
    from src.config import clear_settings_cache, get_settings

    clear_settings_cache()
    monkeypatch.setattr(get_settings(), "reports_dir", tmp_path)
    p1 = save_report_file(
        "older_cpo",
        _memo("older", ["ELS", "PIC"]),
        vertical="cpo_optics",
        skill="semiconductor",
        mode="chokepoint_fast",
        quality={"score": 60},
    )
    p2 = save_report_file(
        "newer_cpo",
        _memo("newer", ["ELS", "PIC", "FAU"], extra="new fiber attach"),
        vertical="cpo_optics",
        skill="semiconductor",
        mode="chokepoint_fast",
        quality={"score": 72},
    )
    a = p1.split("/")[-1]
    b = p2.split("/")[-1]
    out = compare_pair(a, b)
    assert out.get("same_vertical") is True
    assert out.get("vertical_id") == "cpo_optics"
    assert out.get("similarity_ratio") is not None
    sc = out.get("scorecard") or {}
    assert "ELS" in (sc.get("shared_nodes") or []) or "els" in str(sc).lower() or sc.get(
        "shared_nodes"
    ) is not None
    assert out.get("next_actions")


def test_compare_vertical_latest(tmp_path, monkeypatch):
    from src.config import clear_settings_cache, get_settings
    import time

    clear_settings_cache()
    monkeypatch.setattr(get_settings(), "reports_dir", tmp_path)
    save_report_file("v1", _memo("v1", ["HBM", "TSV"]), vertical="hbm_packaging", quality={"score": 50})
    time.sleep(0.05)
    save_report_file(
        "v2", _memo("v2", ["HBM", "TSV", "CoWoS"]), vertical="hbm_packaging", quality={"score": 55}
    )
    rows = list_vertical_reports("hbm_packaging")
    assert len(rows) >= 2
    out = compare_vertical("hbm_packaging")
    assert not out.get("error")
    assert out.get("pair_mode") == "latest_two"
    assert out.get("a", {}).get("name")
    assert out.get("b", {}).get("name")


def test_api_compare_endpoints(tmp_path, monkeypatch):
    from src.config import clear_settings_cache, get_settings
    import time

    clear_settings_cache()
    monkeypatch.setattr(get_settings(), "reports_dir", tmp_path)
    save_report_file("p1", _memo("p1", ["A"]), vertical="power_cooling", quality={"score": 40})
    time.sleep(0.05)
    save_report_file("p2", _memo("p2", ["A", "B"]), vertical="power_cooling", quality={"score": 45})
    c = TestClient(app)
    r = c.get("/reports/by-vertical/power_cooling")
    assert r.status_code == 200
    assert r.json()["count"] >= 2
    r2 = c.get("/reports/compare", params={"vertical_id": "power_cooling"})
    assert r2.status_code == 200
    body = r2.json()
    assert "similarity_ratio" in body
    assert body.get("scorecard")
    names = [x["name"] for x in r.json()["items"][:2]]
    r3 = c.post("/reports/compare", json={"a": names[1], "b": names[0]})
    assert r3.status_code == 200
    assert r3.json().get("a")


def test_compare_needs_two_reports(tmp_path, monkeypatch):
    from src.config import clear_settings_cache, get_settings

    clear_settings_cache()
    monkeypatch.setattr(get_settings(), "reports_dir", tmp_path)
    save_report_file("only", _memo("only", ["X"]), vertical="robotics_actuators")
    out = compare_vertical("robotics_actuators")
    assert out.get("error")
