#!/usr/bin/env python3
"""Opt-in live smoke — refuses to run without explicit cost + live test gates.

  CHOKEPOINT_RUN_LIVE_TESTS=1 \\
  CHOKEPOINT_I_ACCEPT_LIVE_COSTS=1 \\
  python scripts/live_smoke.py

Does NOT run full multi-agent research by default (token burn).
Optional: CHOKEPOINT_LIVE_RESEARCH=1 for one mock-gated check only still prefers mock.
Set CHOKEPOINT_LIVE_PROVIDER_PROBE=1 to hit provider live probes.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    from src.ops.live_safety import (
        assert_live_allowed,
        live_costs_accepted,
        live_gate_status,
        live_tests_enabled,
    )

    if not live_tests_enabled():
        print("REFUSED: set CHOKEPOINT_RUN_LIVE_TESTS=1")
        print("Prefer offline:", live_gate_status()["prefer_offline"])
        return 2
    if not live_costs_accepted(flag=False):
        print("REFUSED: set CHOKEPOINT_I_ACCEPT_LIVE_COSTS=1")
        return 2

    ok = assert_live_allowed(flag=False)
    print("gate ok:", ok["ok"], "est tokens:", ok["estimate"].get("est_total_tokens"))

    from src.config import clear_settings_cache, get_settings
    from src.ops.doctor import run_doctor
    from src.ops.provider_health import probe_providers

    clear_settings_cache()
    settings = get_settings()
    problems = settings.validate_runtime(require_tavily=False)
    print("settings issues:", problems or "none")
    print("doctor live_ready:", run_doctor().get("live_ready"))

    print("providers offline probe:", probe_providers(live=False))
    if (os.environ.get("CHOKEPOINT_LIVE_PROVIDER_PROBE") or "").strip().lower() in {
        "1",
        "true",
        "yes",
    }:
        print("providers LIVE probe:", probe_providers(live=True))
    else:
        print("skip live provider probe (set CHOKEPOINT_LIVE_PROVIDER_PROBE=1)")

    print("live_smoke passed (no full research memo invoked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
