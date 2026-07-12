# Live gates & UI smoke

Offline-first by design. **Default CI never spends model/search tokens.**

## Offline (always)

```bash
make check
# or
python scripts/smoke_check.py
python scripts/ui_smoke.py
pytest -q -m "not live and not browser"
python main.py research --mock -V cpo_optics
python main.py demo-journey -V cpo_optics
```

## Live integration (opt-in)

Requires **all** of:

| Env | Purpose |
|-----|---------|
| `CHOKEPOINT_RUN_LIVE_TESTS=1` | Allow live test / live_smoke scripts |
| `CHOKEPOINT_I_ACCEPT_LIVE_COSTS=1` | Accept token/search cost risk |
| Model API key in `.env` | Live agent / provider paths |

```bash
export CHOKEPOINT_RUN_LIVE_TESTS=1
export CHOKEPOINT_I_ACCEPT_LIVE_COSTS=1
python scripts/live_smoke.py
# optional network provider probe:
CHOKEPOINT_LIVE_PROVIDER_PROBE=1 python scripts/live_smoke.py
pytest -q -m live
```

Live smoke **does not** run full multi-agent memos by default (token burn).  
Queue live still needs `--live --i-accept-live-costs` / API flags.

## Playwright UI browser (opt-in)

```bash
pip install -e ".[ui]"
playwright install chromium
export CHOKEPOINT_UI_BROWSER=1
python scripts/ui_smoke.py
pytest -q -m browser
```

Without Playwright installed, `ui_smoke.py` still runs the **TestClient** path.

## Health / doctor signals

`GET /health` returns:

- `config` / `ops` grades  
- `live_ready` / `ops_ok`  
- `gates` (live_tests_enabled, prefer_offline tips)

Research / education only — not investment advice.
