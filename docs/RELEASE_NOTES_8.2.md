# Release notes — v8.2.0

**20-round review loop: simulate users, fix real friction, offline-first demos**

## Why

Running the workstation like a new analyst exposed hard failures (template 422, Tavily crash, live-only research) and soft UX gaps (no mock path, passive desk actions).

## Highlights

- **Mock research** end-to-end: CLI `--mock`, API `mock:true`, UI checkbox (default on)
- **`demo-journey`**: desk → plan → mock memo → vertical suite without LLM
- **Template render** accepts UI `{"vars":…}` payloads
- **web_search** returns guidance instead of raising when Tavily missing
- **doctor --ops-only** for ops surface without key noise
- Thesis create warns when kill criteria empty
- Plan suggests matching deep vertical from topic text

Full round table: [`docs/ITERATION_20_ROUNDS.md`](ITERATION_20_ROUNDS.md)

```bash
python main.py doctor --ops-only
python main.py demo-journey -V cpo_optics
python main.py research --mock -V cpo_optics
python main.py --server
```

142 offline tests. Research / education only — not investment advice.
