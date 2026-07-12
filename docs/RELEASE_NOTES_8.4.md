# Release notes — v8.4.0

**Fail-closed live gates + offline UI smoke**

## Offline (default / CI)

```bash
make check
python scripts/ui_smoke.py
pytest -q -m "not live and not browser"
```

## Live (explicit only)

```bash
export CHOKEPOINT_RUN_LIVE_TESTS=1
export CHOKEPOINT_I_ACCEPT_LIVE_COSTS=1
python scripts/live_smoke.py   # refuses without both envs
```

## Browser (optional)

```bash
pip install -e ".[ui]" && playwright install chromium
CHOKEPOINT_UI_BROWSER=1 python scripts/ui_smoke.py
```

## Also

- `/health` → config/ops grades + `live_ready` + gate tips  
- UI health pill: `OK · ops · cfg A/ops A · v8.4.0`  
- See `docs/LIVE_AND_UI_SMOKE.md`

153 offline tests green. Research only — not investment advice.
