"""Builtin + user research templates."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
BUILTIN_DIR = ROOT / "templates" / "research"


def list_templates() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if not BUILTIN_DIR.is_dir():
        return items
    for p in sorted(BUILTIN_DIR.glob("*.yaml")):
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        items.append(
            {
                "id": p.stem,
                "name": data.get("name") or p.stem,
                "description": data.get("description") or "",
                "mode": data.get("mode") or "full",
                "path": str(p),
            }
        )
    return items


def get_template(template_id: str) -> dict[str, Any] | None:
    path = BUILTIN_DIR / f"{Path(template_id).name}.yaml"
    if not path.is_file():
        # allow stem without checking path traversal beyond name
        matches = list(BUILTIN_DIR.glob(f"{Path(template_id).stem}.yaml"))
        if not matches:
            return None
        path = matches[0]
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    data["id"] = path.stem
    return data


def render_template(template_id: str, variables: dict[str, str] | None = None) -> dict[str, Any]:
    tpl = get_template(template_id)
    if not tpl:
        raise KeyError(f"Unknown template: {template_id}")
    variables = variables or {}
    q = tpl.get("question_template") or tpl.get("prompt") or ""
    for k, v in variables.items():
        q = q.replace("{{" + k + "}}", str(v))
    # leftover placeholders → empty or keep
    return {
        "id": tpl.get("id"),
        "name": tpl.get("name"),
        "mode": tpl.get("mode") or "full",
        "question": q,
        "bilingual": bool(tpl.get("bilingual")),
        "notes": tpl.get("notes") or "",
    }
