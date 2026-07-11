"""Load educational knowledge maps (YAML) into graphs and research seeds."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
MAPS_DIR = ROOT / "knowledge" / "maps"


def list_maps() -> list[dict[str, Any]]:
    if not MAPS_DIR.is_dir():
        return []
    items = []
    for p in sorted(MAPS_DIR.glob("*.yaml")):
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        items.append(
            {
                "id": p.stem,
                "system": data.get("system") or p.stem,
                "path": str(p.resolve()),
                "layers": len(data.get("layers") or []),
            }
        )
    return items


def load_map(map_id: str) -> dict[str, Any] | None:
    path = MAPS_DIR / f"{Path(map_id).stem}.yaml"
    if not path.is_file():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    data["id"] = path.stem
    return data


def map_to_graph(map_id: str) -> dict[str, Any]:
    data = load_map(map_id)
    if not data:
        return {"error": f"unknown map: {map_id}"}
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    sys_id = f"sys:{data.get('id')}"
    nodes.append({"id": sys_id, "label": data.get("system") or map_id, "kind": "system"})

    for li, layer in enumerate(data.get("layers") or []):
        lid = f"layer:{data.get('id')}:{li}"
        nodes.append({"id": lid, "label": layer.get("name") or f"layer{li}", "kind": "layer"})
        edges.append({"from": sys_id, "to": lid, "rel": "contains"})
        for ex in layer.get("examples") or []:
            eid = f"ex:{_safe(str(ex))}"
            nodes.append({"id": eid, "label": str(ex)[:60], "kind": "example"})
            edges.append({"from": lid, "to": eid, "rel": "example"})
        for ci, cand in enumerate(layer.get("candidates") or []):
            if isinstance(cand, dict):
                label = cand.get("node") or cand.get("name") or f"cand{ci}"
                why = cand.get("why") or ""
            else:
                label, why = str(cand), ""
            cid = f"cp:{data.get('id')}:{li}:{ci}"
            nodes.append({"id": cid, "label": str(label)[:80], "kind": "candidate", "why": why})
            edges.append({"from": lid, "to": cid, "rel": "candidate"})

    for i, k in enumerate(data.get("kill_criteria_examples") or []):
        kid = f"kill:{data.get('id')}:{i}"
        nodes.append({"id": kid, "label": str(k)[:80], "kind": "kill"})
        edges.append({"from": sys_id, "to": kid, "rel": "kill_example"})

    return {
        "id": data.get("id"),
        "system": data.get("system"),
        "nodes": nodes,
        "edges": edges,
        "risks": data.get("risks") or [],
        "disclaimer": "research_only_not_investment_advice",
    }


def map_to_mermaid(map_id: str) -> str:
    g = map_to_graph(map_id)
    if g.get("error"):
        return f"# {g['error']}\n"
    lines = ["flowchart TB"]
    for n in g.get("nodes") or []:
        nid = _safe(n["id"])
        label = str(n.get("label") or "").replace('"', "'")[:48]
        kind = n.get("kind")
        if kind == "system":
            lines.append(f'  {nid}[("{label}")]')
        elif kind == "candidate":
            lines.append(f"  {nid}{{{{{label}}}}}")
        elif kind == "kill":
            lines.append(f"  {nid}>{label}]")
        else:
            lines.append(f'  {nid}["{label}"]')
    for e in g.get("edges") or []:
        a, b = _safe(e["from"]), _safe(e["to"])
        lines.append(f"  {a} --> {b}")
    return "\n".join(lines) + "\n"


def map_research_seed(map_id: str) -> dict[str, Any]:
    data = load_map(map_id)
    if not data:
        return {"error": f"unknown map: {map_id}"}
    candidates = []
    for layer in data.get("layers") or []:
        for cand in layer.get("candidates") or []:
            if isinstance(cand, dict):
                candidates.append(cand.get("node") or cand.get("name"))
            else:
                candidates.append(str(cand))
    kills = data.get("kill_criteria_examples") or []
    q = (
        f"以「{data.get('system')}」为系统边界做卡点研究。\n"
        f"优先验证节点：{', '.join(str(c) for c in candidates[:8] if c)}。\n"
        f"必须写清 kill criteria，参考：{'; '.join(str(k) for k in kills[:3])}。\n"
        f"仅研究框架，不构成投资建议。"
    )
    return {
        "map_id": map_id,
        "system": data.get("system"),
        "question": q,
        "mode": "chokepoint_fast",
        "candidates": [c for c in candidates if c],
        "kill_criteria_examples": kills,
        "disclaimer": "research_only_not_investment_advice",
    }


def _safe(raw: str) -> str:
    s = re.sub(r"[^0-9A-Za-z_]", "_", raw)
    if s and s[0].isdigit():
        s = "n_" + s
    return s or "n"
