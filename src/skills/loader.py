"""Domain skill packs — extra prompt fragments + suggested tools for verticals."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = ROOT / "skills" / "packs"


def list_skill_packs() -> list[dict[str, Any]]:
    if not SKILLS_DIR.is_dir():
        return []
    items = []
    for p in sorted(SKILLS_DIR.glob("*.yaml")):
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        items.append(
            {
                "id": p.stem,
                "name": data.get("name") or p.stem,
                "description": data.get("description") or "",
                "tags": data.get("tags") or [],
            }
        )
    return items


def load_skill_pack(pack_id: str) -> dict[str, Any] | None:
    path = SKILLS_DIR / f"{Path(pack_id).stem}.yaml"
    if not path.is_file():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    data["id"] = path.stem
    return data


def skill_prompt_suffix(pack_id: str | None) -> str:
    if not pack_id:
        return ""
    pack = load_skill_pack(pack_id)
    if not pack:
        return ""
    extra = pack.get("system_suffix") or pack.get("prompt") or ""
    focus = pack.get("focus_questions") or []
    lines = [f"\n# Domain skill pack: {pack.get('name') or pack_id}\n", str(extra), "\n"]
    if focus:
        lines.append("重点问题：\n")
        for q in focus:
            lines.append(f"- {q}\n")
    return "".join(lines)
