from __future__ import annotations
import importlib
from pathlib import Path
from typing import Any

def list_questionnaires() -> list[str]:
    return sorted(
        p.stem
        for p in Path(__file__).parent.glob("*.py")
        if p.stem not in {"__init__", "registry"}
    )

def get_questionnaire(qid: str) -> dict[str, Any]:
    return importlib.import_module(f"src.questionnaires.{qid}").run()
