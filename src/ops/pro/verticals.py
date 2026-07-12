"""Deep vertical packs — domain process specs under skills/pro_verticals/.

Use these for CPO / HBM / power / robotics / materials coverage depth.
Not an industry encyclopedia: prefer skill packs for light coverage.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
VERTICALS_DIR = ROOT / "skills" / "pro_verticals"

DISCLAIMER = "research_only_not_investment_advice"


def list_verticals(*, full: bool = False) -> list[dict[str, Any]]:
    """List vertical packs (summary by default)."""
    if not VERTICALS_DIR.is_dir():
        return []
    items: list[dict[str, Any]] = []
    for p in sorted(VERTICALS_DIR.glob("*.yaml")):
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        data["id"] = p.stem
        if full:
            items.append(data)
        else:
            items.append(
                {
                    "id": p.stem,
                    "title": data.get("title") or p.stem,
                    "version": data.get("version"),
                    "summary": (data.get("summary") or "")[:240],
                    "modules": data.get("modules") or [],
                    "keywords": (data.get("keywords") or [])[:12],
                    "node_count": len(data.get("physical_nodes") or []),
                    "kill_count": len(data.get("kill_criteria") or []),
                    "disclaimer": data.get("disclaimer") or DISCLAIMER,
                }
            )
    return items


def load_vertical(vertical_id: str) -> dict[str, Any] | None:
    path = VERTICALS_DIR / f"{Path(vertical_id).stem}.yaml"
    if not path.is_file():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    data["id"] = path.stem
    data.setdefault("disclaimer", DISCLAIMER)
    return data


def vertical_ids() -> list[str]:
    return [v["id"] for v in list_verticals()]


def suggest_vertical(text: str, *, limit: int = 3) -> list[dict[str, Any]]:
    """Rank verticals by keyword hits in free text (offline, no LLM)."""
    t = (text or "").lower()
    if not t.strip():
        return []
    scored: list[tuple[int, dict[str, Any]]] = []
    for v in list_verticals(full=True):
        kws = [str(k).lower() for k in (v.get("keywords") or [])]
        hits = [k for k in kws if k and k in t]
        # also match id / title tokens
        for tok in (v.get("id") or "", v.get("title") or ""):
            for part in str(tok).lower().replace("/", " ").split():
                if len(part) > 2 and part in t and part not in hits:
                    hits.append(part)
        if hits:
            scored.append((len(hits), {**_summary(v), "matched_keywords": hits}))
    scored.sort(key=lambda x: (-x[0], x[1].get("id") or ""))
    return [s[1] for s in scored[:limit]]


def _summary(v: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": v.get("id"),
        "title": v.get("title"),
        "modules": v.get("modules") or [],
        "node_count": len(v.get("physical_nodes") or []),
        "kill_count": len(v.get("kill_criteria") or []),
    }


def vertical_prompt_suffix(vertical_id: str | None) -> str:
    """Inject domain process constraints into the lead agent system prompt."""
    if not vertical_id:
        return ""
    v = load_vertical(vertical_id)
    if not v:
        return ""
    lines = [
        f"\n# Deep vertical pack: {v.get('title') or vertical_id}\n",
        "Use this pack as process hygiene for physical chokepoint research. "
        "Not investment advice.\n",
    ]
    if v.get("summary"):
        lines.append(f"\nSummary: {str(v['summary']).strip()}\n")
    if v.get("system_boundary"):
        lines.append(f"\n## System boundary\n{str(v['system_boundary']).strip()}\n")
    nodes = v.get("physical_nodes") or []
    if nodes:
        lines.append("\n## Physical nodes to stress-test\n")
        for n in nodes:
            if isinstance(n, dict):
                lines.append(f"- **{n.get('id') or '?'}** — {n.get('label') or ''}\n")
                for q in n.get("questions") or []:
                    lines.append(f"  - {q}\n")
            else:
                lines.append(f"- {n}\n")
    kills = v.get("kill_criteria") or []
    if kills:
        lines.append("\n## Kill / falsifier criteria (must address)\n")
        for k in kills:
            lines.append(f"- {k}\n")
    ev = v.get("evidence_checklist") or []
    if ev:
        lines.append("\n## Evidence checklist\n")
        for e in ev:
            if isinstance(e, dict):
                lines.append(f"- {e.get('label') or e}: {e.get('hint') or ''}\n")
            else:
                lines.append(f"- {e}\n")
    focus = v.get("focus_questions") or []
    if focus:
        lines.append("\n## Focus questions\n")
        for q in focus:
            lines.append(f"- {q}\n")
    peers = v.get("peer_set_hints") or []
    if peers:
        lines.append("\n## Peer / substitute map hints\n")
        for p in peers:
            lines.append(f"- {p}\n")
    mods = v.get("modules") or []
    if mods:
        lines.append(
            f"\nPreferred pro modules for post-memo suite: {', '.join(str(m) for m in mods)}\n"
        )
    lines.append(f"\nDisclaimer: {v.get('disclaimer') or DISCLAIMER}\n")
    return "".join(lines)


def scaffold_research_question(
    vertical_id: str,
    *,
    system: str = "",
    context: str = "",
) -> dict[str, Any]:
    """Build a ready-to-run research question from a vertical pack."""
    v = load_vertical(vertical_id)
    if not v:
        return {"error": f"unknown vertical: {vertical_id}"}
    boundary = system.strip() or str(v.get("system_boundary") or v.get("title") or vertical_id).strip()
    title = v.get("title") or vertical_id
    node_lines = []
    for n in v.get("physical_nodes") or []:
        if isinstance(n, dict):
            node_lines.append(f"- {n.get('label') or n.get('id')}")
        else:
            node_lines.append(f"- {n}")
    kill_lines = [f"- {k}" for k in (v.get("kill_criteria") or [])]
    focus_lines = [f"- {q}" for q in (v.get("focus_questions") or [])]
    q = (
        f"以「{boundary}」为系统边界，使用垂直研究包 **{title}**（{vertical_id}）做卡点逆向工程：\n"
        f"1) 确认/收紧系统边界\n"
        f"2) 对下列物理节点逐一评估可替代性、产能与单点依赖：\n"
        + ("\n".join(node_lines) if node_lines else "- （包内节点）\n")
        + "\n3) 输出 Chokepoint Scorecard（节点、维度 1–5、依据）\n"
        "4) 明确回应下列 kill criteria（能否证伪、监控指标）：\n"
        + ("\n".join(kill_lines) if kill_lines else "- （补充杀逻辑）\n")
        + "\n5) 重点问题：\n"
        + ("\n".join(focus_lines) if focus_lines else "- 真正的卡点在哪一层？\n")
        + "\n6) 来源列表（URL/公告/纪要时间戳）\n"
    )
    if context.strip():
        q += f"\n附加上下文：{context.strip()}\n"
    q += "\n仅供研究学习，不构成投资建议。"
    return {
        "vertical_id": vertical_id,
        "title": title,
        "mode": "chokepoint_fast",
        "question": q,
        "modules": v.get("modules") or [],
        "suggested_skill": _suggested_skill(vertical_id),
        "disclaimer": DISCLAIMER,
    }


def _suggested_skill(vertical_id: str) -> str | None:
    """Map vertical → light skill pack when available."""
    mapping = {
        "cpo_optics": "semiconductor",
        "hbm_packaging": "semiconductor",
        "power_cooling": "ai_infra",
        "robotics_actuators": "robotics",
        "specialty_materials": "materials_chem",
    }
    sid = mapping.get(Path(vertical_id).stem)
    if not sid:
        return None
    try:
        from src.skills.loader import load_skill_pack

        return sid if load_skill_pack(sid) else None
    except Exception:  # noqa: BLE001
        return sid


def run_vertical_suite(
    vertical_id: str,
    *,
    text: str = "",
    symbol: str = "",
    title: str = "vertical_suite",
) -> dict[str, Any]:
    """Run pro analyze only on modules listed in the vertical pack."""
    from src.ops.pro.registry import invoke_module

    v = load_vertical(vertical_id)
    if not v:
        return {"error": f"unknown vertical: {vertical_id}", "disclaimer": DISCLAIMER}
    modules = [str(m) for m in (v.get("modules") or [])]
    if not modules:
        return {
            "error": "vertical has no modules list",
            "vertical_id": vertical_id,
            "disclaimer": DISCLAIMER,
        }
    # Enrich analyze text with vertical kill/focus hints for denser offline scoring
    enrich = text
    if v.get("kill_criteria"):
        enrich += "\nkill criteria: " + "; ".join(str(k) for k in v["kill_criteria"][:5])
    if v.get("focus_questions"):
        enrich += "\nfocus: " + "; ".join(str(q) for q in v["focus_questions"][:4])
    results = []
    gates_ok = 0
    for mid in modules:
        out = invoke_module(
            mid,
            action="analyze",
            text=enrich,
            symbol=symbol,
            title=title,
        )
        ok = bool(out.get("gate_ok"))
        if ok:
            gates_ok += 1
        results.append(
            {
                "module": mid,
                "gate_ok": ok,
                "checklist_passed": out.get("checklist_passed"),
                "checklist_total": out.get("checklist_total"),
                "density": (out.get("score") or {}).get("density_score"),
                "flags": (out.get("score") or {}).get("flags"),
            }
        )
    n = len(results)
    return {
        "vertical_id": vertical_id,
        "title": v.get("title"),
        "modules": n,
        "gates_ok": gates_ok,
        "gate_rate": round(gates_ok / n, 3) if n else None,
        "results": results,
        "physical_nodes": [
            (n.get("id") if isinstance(n, dict) else n) for n in (v.get("physical_nodes") or [])
        ],
        "disclaimer": DISCLAIMER,
        "note": "Vertical-scoped offline suite — process hygiene, not investment advice.",
    }


def desk_vertical_block() -> dict[str, Any]:
    """Compact block for research desk / about."""
    items = list_verticals()
    return {
        "count": len(items),
        "ids": [i["id"] for i in items],
        "items": items,
        "hint": "Use: research --vertical cpo_optics  |  progrp verticals --show cpo_optics  |  GET /pro/verticals",
    }
