#!/usr/bin/env python3
"""Entry point for launchd / cron scheduled watchlist brief.

Usage:
  python scripts/run_scheduled_brief.py
  # installed via: python main.py schedule install --hour 9 --minute 0
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")

    from src.config import clear_settings_cache
    from src.logging_utils import setup_logging
    from src.ops.scheduler import run_scheduled_job_once

    clear_settings_cache()
    setup_logging("INFO")
    result = run_scheduled_job_once()
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 0 if not result.get("error") else 1


if __name__ == "__main__":
    raise SystemExit(main())
