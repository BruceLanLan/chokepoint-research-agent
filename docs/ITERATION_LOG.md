# Iteration Log

Five review → debug → fix → plan → ship cycles after v0.1.0.

## 2026-07-12 — SuperGrok autonomous train (v3.0 → v4.3)

Shipped and tagged on GitHub (`BruceLanLan/chokepoint-research-agent`):

| Tag | Theme |
|-----|--------|
| v3.0.0 | HTTP cache, postprocess, skill packs, mock-eval, plugin SDK |
| v4.0.0 | Evidence ledger, thesis graph, tags, compare, audit, DOCX, coverage, kill monitor |
| v4.1.0 | Citation network, lineage, offline plan, provider health, WS quotes |
| v4.2.0 | Knowledge maps, cost dashboard, brief process health |
| v4.3.0 | SQLite FTS memo index, research queue |
| v4.4.0 | Queue worker, export pack, auto-tag, thesis health, catalog |

Also: GitHub Releases for v3.0–v4.4; jobs.json corrupt-file harden; **83** offline tests green.

Principles unchanged: research-only / not investment advice; secrets never committed.

## Iteration 1 — Foundation correctness + fast mode

### Review
- `web_search` used `InjectedToolArg` for `topic` / `max_results` → model cannot choose `news`/`finance`.
- Fallback + CLI both call `save_research_report` → duplicate files.
- `get_settings` is `lru_cache` with no reload → tests / env changes sticky.
- Unused `os` import; weak preflight validation (missing Tavily only fails mid-run).

### Fix
- Expose `topic` and `max_results` to the model.
- Single save path (CLI/API own persistence; fallback optional flag).
- `clear_settings_cache()` + startup `validate_runtime()`.
- `--mode full|chokepoint_fast|risk_only` for cheaper runs.

### Ship
- Research modes, preflight, tool arg fix, tests.

## Iteration 2 — Observability + report library

### Review
- No structured logging; hard to debug multi-agent runs.
- No way to list past reports via API/CLI.
- No shared run-id / meta on reports.

### Ship
- `src/logging_utils.py`, report index meta, `list` CLI + `/reports` API.

## Iteration 3 — Scorecard schema + quality gates

### Review
- Scorecard free-text only; hard to eval or UI-render.
- No automated quality checks on memo structure.

### Ship
- `src/schemas/scorecard.py`, post-process extractor, `validate_report_structure`.

## Iteration 4 — Lightweight web UI

### Review
- API-only is unfriendly for demos.
- Need read-only report browser + submit form.

### Ship
- `src/static/index.html` + FastAPI static routes.

## Iteration 5 — Hardening + maps + release

### Review
- API has no simple rate/timeout guidance; few knowledge maps.
- Version still 0.1.0 after large feature set.

### Ship
- Extra maps, request timeout notes, API key optional middleware, v0.2.0 release.
