#!/usr/bin/env python3
"""Scheduled research-queue tick (mock processing only — no LLM by default)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")


def main() -> int:
    from src.config import clear_settings_cache
    from src.ops.schedule_queue import scheduled_queue_tick

    clear_settings_cache()
    n = 1
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            n = 1
    out = scheduled_queue_tick(n=n, live=False)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
