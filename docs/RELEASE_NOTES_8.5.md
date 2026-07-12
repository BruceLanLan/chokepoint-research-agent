# Release notes — v8.5.0

**Catalog filters + fail-closed live research**

## Report filters

```bash
curl -s 'localhost:8000/reports?vertical_id=cpo_optics'
curl -s 'localhost:8000/reports/facets'
```

UI **Reports** tab: filter by vertical / skill / mode.

## Live research gate

Non-mock research requires cost acceptance:

```bash
# Offline (default, free)
python main.py research --mock -V cpo_optics

# Live (explicit)
python main.py research "…" --i-accept-live-costs
# or CHOKEPOINT_I_ACCEPT_LIVE_COSTS=1
```

API without accept → **402**. UI: uncheck Mock only with “I accept live costs”.

See `docs/LIVE_AND_UI_SMOKE.md`.

158 offline tests. Research only — not investment advice.
