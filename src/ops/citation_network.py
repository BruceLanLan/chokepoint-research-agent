"""Citation network — domain co-occurrence across research memos."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.config import get_settings
from src.ops.evidence import extract_evidence

_URL_RE = re.compile(r"https?://[^\s\)\]\>\"']+", re.I)


def _domain(url: str) -> str:
    host = re.sub(r"^https?://", "", url).split("/")[0].lower()
    return host.rstrip(".")


def build_citation_network(limit_reports: int = 80) -> dict[str, Any]:
    out_dir = Path(get_settings().reports_dir)
    if not out_dir.is_dir():
        return {"nodes": [], "edges": [], "stats": {"reports": 0}}

    files = sorted(
        [p for p in out_dir.glob("*.md") if p.name != "SAMPLE_REPORT_FORMAT.md"],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )[: max(1, min(limit_reports, 200))]

    domain_docs: dict[str, set[str]] = defaultdict(set)
    domain_count: Counter[str] = Counter()
    pair_count: Counter[tuple[str, str]] = Counter()

    for p in files:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        urls = [_domain(u.rstrip(".,;:!?）)")) for u in _URL_RE.findall(text)]
        domains = sorted({d for d in urls if d and "." in d})
        for d in domains:
            domain_docs[d].add(p.name)
            domain_count[d] += 1
        for i, a in enumerate(domains):
            for b in domains[i + 1 :]:
                pair = (a, b) if a < b else (b, a)
                pair_count[pair] += 1

    top_domains = [d for d, _ in domain_count.most_common(40)]
    nodes = [
        {
            "id": d,
            "label": d,
            "kind": "domain",
            "count": domain_count[d],
            "reports": sorted(domain_docs[d])[:8],
        }
        for d in top_domains
    ]
    edges = []
    for (a, b), w in pair_count.most_common(80):
        if a in top_domains and b in top_domains:
            edges.append({"from": a, "to": b, "weight": w, "rel": "co_cited"})

    return {
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "reports_scanned": len(files),
            "unique_domains": len(domain_count),
            "top_domain": top_domains[0] if top_domains else None,
        },
        "disclaimer": "research_only_not_investment_advice",
    }


def citation_mermaid(limit_reports: int = 40) -> str:
    g = build_citation_network(limit_reports=limit_reports)
    lines = ["flowchart LR"]
    for n in g.get("nodes") or []:
        nid = re.sub(r"[^0-9A-Za-z_]", "_", n["id"])
        if nid and nid[0].isdigit():
            nid = "d_" + nid
        label = str(n["label"])[:40].replace('"', "'")
        lines.append(f'  {nid}["{label} ({n["count"]})"]')
    for e in (g.get("edges") or [])[:40]:
        a = re.sub(r"[^0-9A-Za-z_]", "_", e["from"])
        b = re.sub(r"[^0-9A-Za-z_]", "_", e["to"])
        if a and a[0].isdigit():
            a = "d_" + a
        if b and b[0].isdigit():
            b = "d_" + b
        lines.append(f"  {a} ---|{e['weight']}| {b}")
    return "\n".join(lines) + "\n"
