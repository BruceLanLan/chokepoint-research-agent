"""Thesis graph — nodes for theses, chokepoints, symbols; Mermaid export."""

from __future__ import annotations

import re
from typing import Any

from src.ops.theses import list_theses
from src.ops.watchlist import list_items


def build_thesis_graph() -> dict[str, Any]:
    theses = list_theses()
    watch = list_items()
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add_node(nid: str, label: str, kind: str, **extra: Any) -> None:
        if nid in seen:
            return
        seen.add(nid)
        nodes.append({"id": nid, "label": label, "kind": kind, **extra})

    for t in theses:
        tid = f"thesis:{t.get('id')}"
        add_node(
            tid,
            str(t.get("title") or t.get("id")),
            "thesis",
            status=t.get("status"),
            system=t.get("system") or "",
        )
        for cp in t.get("chokepoints") or []:
            cp = str(cp).strip()
            if not cp:
                continue
            cid = f"cp:{cp.lower()}"
            add_node(cid, cp, "chokepoint")
            edges.append({"from": tid, "to": cid, "rel": "depends_on"})
        for sym in t.get("related_symbols") or []:
            sym = str(sym).strip().upper()
            if not sym:
                continue
            sid = f"sym:{sym}"
            add_node(sid, sym, "symbol")
            edges.append({"from": tid, "to": sid, "rel": "covers"})
        for i, kill in enumerate(t.get("kill_criteria") or []):
            kid = f"kill:{t.get('id')}:{i}"
            add_node(kid, str(kill)[:80], "kill_criterion", thesis_id=t.get("id"))
            edges.append({"from": tid, "to": kid, "rel": "invalidated_by"})

    for w in watch:
        sym = str(w.get("symbol") or "").strip().upper()
        if not sym:
            continue
        sid = f"sym:{sym}"
        add_node(sid, sym, "symbol", priority=w.get("priority"))
        wid = f"watch:{w.get('id')}"
        add_node(wid, w.get("name") or sym, "watchlist", priority=w.get("priority"))
        edges.append({"from": wid, "to": sid, "rel": "tracks"})
        note = (w.get("thesis") or "").strip()
        if note:
            # soft link: if any thesis title/statement contains symbol, already covered
            for t in theses:
                if sym in [s.upper() for s in (t.get("related_symbols") or [])]:
                    edges.append(
                        {
                            "from": f"thesis:{t.get('id')}",
                            "to": sid,
                            "rel": "covers",
                        }
                    )

    # dedupe edges
    edge_keys = set()
    uniq_edges = []
    for e in edges:
        k = (e["from"], e["to"], e["rel"])
        if k in edge_keys:
            continue
        edge_keys.add(k)
        uniq_edges.append(e)

    return {
        "nodes": nodes,
        "edges": uniq_edges,
        "stats": {
            "nodes": len(nodes),
            "edges": len(uniq_edges),
            "theses": sum(1 for n in nodes if n["kind"] == "thesis"),
            "chokepoints": sum(1 for n in nodes if n["kind"] == "chokepoint"),
            "symbols": sum(1 for n in nodes if n["kind"] == "symbol"),
        },
        "disclaimer": "research_only_not_investment_advice",
    }


def to_mermaid(graph: dict[str, Any] | None = None) -> str:
    g = graph or build_thesis_graph()
    lines = ["flowchart LR"]
    kind_shape = {
        "thesis": ('["', '"]'),
        "chokepoint": ('{{', '}}'),
        "symbol": ("((", "))"),
        "kill_criterion": (">", "]"),
        "watchlist": ("([", "])"),
    }
    for n in g.get("nodes") or []:
        nid = _safe_id(n["id"])
        label = str(n.get("label") or n["id"]).replace('"', "'")[:48]
        left, right = kind_shape.get(n.get("kind") or "", ('["', '"]'))
        lines.append(f'  {nid}{left}{label}{right}')
    for e in g.get("edges") or []:
        a = _safe_id(e["from"])
        b = _safe_id(e["to"])
        rel = str(e.get("rel") or "")
        lines.append(f"  {a} -->|{rel}| {b}")
    return "\n".join(lines) + "\n"


def _safe_id(raw: str) -> str:
    s = re.sub(r"[^0-9A-Za-z_]", "_", raw)
    if s and s[0].isdigit():
        s = "n_" + s
    return s or "node"
