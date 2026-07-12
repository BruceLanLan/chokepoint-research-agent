# Changelog

## 10.0.0 — 2026-07-12

**Milestone: Chokepoint Research Workstation 1.0**

Consolidates the v8.7–v9.5 train into a stable major surface for coverage ops.

### Highlights
- Golden path offline ritual (`golden-path` CLI + `POST /golden-path`)
- Vertical coverage dashboard + weekly-ops integration
- Compare pack export + thesis review linking
- Queue enqueue by vertical scaffold
- `/capabilities` product snapshot; UI golden path / coverage / compare export; Alt+tab hotkeys
- 167 offline tests green

See `docs/RELEASE_NOTES_10.0.md`.


## 9.5.0 — 2026-07-12

### Added
- Desk: Golden path + Vertical coverage buttons
- Reports: export compare pack from UI
- Keyboard: Alt+D/R/W/T/P/O tab jumps


## 9.4.0 — 2026-07-12

### Added
- `GET /capabilities` and richer `GET /about` via `workstation_capabilities()`


## 9.3.0 — 2026-07-12

### Added
- Desk embeds `vertical_coverage` brief + next actions for pairs/compare


## 9.2.0 — 2026-07-12

### Added
- `weekly-ops` markdown section: vertical coverage rows + actions


## 9.1.0 — 2026-07-12

### Added
- `enqueue_vertical` + API `POST /queue` with `vertical` / `vertical_id`


## 9.0.0 — 2026-07-12

### Added
- `golden-path` CLI + service: doctor → desk → coverage → demo ×2 → compare export


## 8.9.0 — 2026-07-12

### Added
- `vertical_coverage` dashboard (`vertical-coverage` CLI, `GET /verticals/coverage`)


## 8.8.0 — 2026-07-12

### Added
- `link_compare_to_thesis` / `append_review_note`; CLI `--thesis-id` on compare-vertical


## 8.7.0 — 2026-07-12

### Added
- Compare pack export (`compare_export`, `POST /reports/compare/export`, CLI `--export`)


## 8.6.0 — 2026-07-12

### Added
- **Vertical memo compare** (`src/ops/vertical_compare.py`): structured + text ratio + scorecard node deltas
- API: `GET/POST /reports/compare`, `GET /reports/by-vertical/{id}`
- CLI: `compare-vertical [id] [--a --b | latest] [--list]`
- UI Reports: pick A/B, compare pair, or latest pair in filtered vertical

### Tests
- 162 passed (`test_v86_vertical_compare.py`)


## 8.5.0 — 2026-07-12

### Added
- Catalog **filter** by `vertical_id` / `skill` / `mode` / free text + **facets** API
- UI Reports tab: vertical/skill/mode dropdowns + count
- Live research **cost gate** for non-mock paths (`i_accept_live_costs` / env / CLI flag)
- API returns **402** when live research is blocked; UI checkbox “I accept live costs”

### Changed
- `assert_live_research_allowed()` for memo/stream (separate from queue live gate)

### Tests
- 158 passed (`test_v85_catalog_live_gate.py`)


## 8.4.0 — 2026-07-12

### Added
- Live gates: `live_tests_enabled`, `browser_tests_enabled`, `live_gate_status()`
- Opt-in **live** tests (`@pytest.mark.live`) + `scripts/live_smoke.py` (fail-closed)
- Offline **UI smoke** `scripts/ui_smoke.py` (TestClient); optional Playwright via `.[ui]` + `CHOKEPOINT_UI_BROWSER=1`
- `GET /health` surfaces config/ops grades, `live_ready`, `gates`
- Docs: `docs/LIVE_AND_UI_SMOKE.md`
- Makefile: `ui-smoke`, `live-smoke`; CI runs ui-smoke + excludes live/browser markers

### Changed
- Health pill shows cfg/ops grades and live vs ops mode

### Tests
- 153 passed, 2 skipped (opt-in live/browser)


## 8.3.0 — 2026-07-12

### Added
- Report frontmatter **`vertical_id`** (+ skill) on save pipeline, mock research, export bundle
- Catalog exposes `skill` / `vertical_id` / `thesis_id` for search & UI tags
- Doctor **config** vs **ops** scores (`config.grade`, `ops.grade`, `live_ready`, `ops_ok`)
- Verticals + pro_specs checks in ops bucket; Tavily missing is **warn** (soft-fail search)

### Changed
- Export MD uses canonical `save_report_file` frontmatter (no bare body-only MD)
- CLI doctor table shows bucket column + dual scores
- UI reports show vertical tag when present

### Tests
- 147 offline tests (`test_v83_frontmatter_doctor.py`)


## 8.2.0 — 2026-07-12

20-round review / user-sim / fix / iterate hardening.

### Fixed
- Template render accepts `{"vars":{…}}` (UI no longer 422)
- `web_search` soft-fails without Tavily instead of crashing the agent
- Research API 503 guidance for missing keys; empty question 422 with scaffold hint
- FastAPI lifespan (remove on_event deprecation)

### Added
- Offline **`mock` research** (API `mock:true`, CLI `--mock`, UI default checked)
- **`demo-journey`** CLI + `POST /demo-journey` golden path without LLM
- `doctor --ops-only` ignores missing model/search keys
- Plan auto-suggests deep vertical from topic text
- Thesis `process_warning` when kill criteria missing
- UI: watch delete, thesis status buttons, desk demo + clickable actions, dynamic verticals
- `docs/ITERATION_20_ROUNDS.md`, `tests/test_v82_journeys.py`

### Tests
- 142 offline tests green


## 8.1.0 — 2026-07-12

**Use deep verticals, don't broaden industry catalog.**

### Added
- `src/ops/pro/verticals.py` — load / list / suggest / scaffold / vertical-scoped suite
- CLI: `research --vertical`, `pro-suite --vertical`, `progrp verticals --show|--scaffold|--suggest`
- API: `GET /pro/verticals/{id}`, `POST .../scaffold`, suite accepts `vertical`
- Research agent injects vertical process constraints (nodes, kills, evidence)
- Desk surfaces vertical catalog + next-action hints
- Template `vertical_coverage`; UI vertical select + “Fill from vertical”
- Tests: `tests/test_v81_verticals.py`

### Fixed
- `POST /pro/suite` no longer captured by `/pro/{module_id}`


## 8.0.0 — 2026-07-12

Hardening + professional workstation UI (plan Phase 4).

### Added
- **Professional UI/UX**: multi-tab shell (Desk / Research / Coverage / Theses / Reports / Templates / Search / Knowledge / Analytics / Ops / Jobs / Doctor), design system CSS, bilingual **EN/ZH** toggle (`src/static/js/i18n.js` + `app.js`)
- API package split: `src/api/` (`factory`, `deps`, `routes/{core,research,coverage,reports,pro,knowledge,ops}`)
- CLI package split: `src/cli/` (`common`, `research`, `watch`, `thesis`, `ops`, `pro`, `export`, `core`); thin `main.py`
- Domain-deep **vertical packs** (CPO, HBM, power/cooling, robotics actuators, specialty materials) with physical nodes, kill criteria, evidence checklists

### Changed
- `GET /pro/verticals` resolves packs from repo `skills/pro_verticals/` after package move
- Version surface **8.0.0**

### Tests
- 121 offline tests green


## 7.0.0 — 2026-07-12

Consolidation sprint executing `docs/REVIEW_AND_PLAN_6.3.md` Phases 0–3.

### Added
- **ProEngine** + 50 YAML specs (`skills/pro/*.yaml`) + 5 vertical packs
- Unified **save pipeline** (evidence, audit, auto-tag, thesis link, optional pro-suite)
- Report frontmatter: skill, thesis_id, watch_ids, quality
- CLI groups: `ops`, `progrp`, `export` (+ golden path tip in doctor)
- Schedule kinds: `weekly_ops`, `queue_mock`
- Hash-pinned **remote plugin install** (`plugins --install`, needs PLUGIN_ALLOW_HOSTS)
- Thesis↔report hard links (`thesis_links`, graph --links)
- Store schema migrate (`ops migrate` / doctor)
- UI **Desk** tab + report actions (check/grade/pack)
- Golden evals ≥16; glossary filler culled; `docs/PROVIDERS.md`

### Changed
- Pro modules are thin shims over YAML-backed engine (depth ↑, clone code ↓)


## 6.3.0 — 2026-07-12

### Added
- Professional **README** rewrite (EN + ZH): positioning, capability map, workflow, CLI/API index
- `about` CLI + `GET /about` capability snapshot

### Changed
- README no longer stuck on stale v0.x feature lists; documents v6 workstation surface


## 6.2.0 — 2026-07-12

### Added
- Multi-symbol quote batch (`multi-quotes`, `/quotes/multi`)
- Remote plugin install **design doc** (`docs/REMOTE_PLUGIN_DESIGN.md`) — not implemented


## 6.1.0 — 2026-07-12

### Added
- **Research desk** unified status (`desk`, `/desk`)
- **Pro dashboard** across 50 modules (`pro-dashboard`, `/pro/dashboard`)
- **Memo → pro bridge** (`memo-pro`, `/memo-pro`)
- **Pro pack export** zip (`pro-export`, `/pro/export`)
- **Glossary search** (`glossary`, `/glossary`)
- **Quote history SVG** (`quote-chart`, `/charts/quote-history`)
- API: questionnaires + rubrics list/score
- UI Ops: desk, pro dashboard, glossary
- Tests: `test_v61_desk.py`


## 6.0.0 — 2026-07-12

**50-version maturity train complete** (v5.2.0–v5.51.0 modules + v6.0.0 cut).

### Added
- 50 professional research-ops modules under `src/ops/pro/` (event calendar → platform risk)
- CLI: `pro`, `pro-suite`, `playbook`, `metrics-run`
- API: `/pro/modules`, `/pro/{id}`, `/pro/suite`, `/playbooks`
- 20 research playbooks under `src/playbooks/`
- Analysis engines: scorecard_engine, 150 text metrics
- 10 extra knowledge maps, 8 skill packs, 5 templates, 20 eval fixtures
- Docs: `docs/VERSIONS_5.2_to_5.51.md`, `docs/pro-modules/*`, essays
- Tests: pro train (50 modules) + analysis/playbooks

### Scale
- Codebase expanded toward ~2–3× prior LOC with workstation depth


## 5.1.0 — 2026-07-12

### Added
- Watchlist quote refresh: `quotes-cache --from-watchlist`
- Single-memo grade: `grade-memo`, `/grade/{name}`


## 5.0.0 — 2026-07-12

Professional research workstation maturity cut (v4.8–v5.0).

### Added
- **Workspace health** composite score (`workspace-health`, `/workspace-health`)
- **Research runbook / SOP** offline (`runbook`, `/runbook`)
- **Batch structure review** (`batch-review`, `/batch-review`)
- **Weekly ops pack** (`weekly-ops`, `/weekly-ops`)
- **Multi-symbol quote cache** (`quotes-cache`, `/quotes/cache`)
- UI Analytics: health, quality board, batch review, weekly ops
- Docs: `docs/PROFESSIONAL_WORKSTATION.md`
- CI: workspace-health smoke + eval history artifact

### Positioning
- Research **ops** workstation (coverage → thesis → evidence → gate → archive)
- Still **not** a market-data terminal or investment advice product

## 4.7.0 — 2026-07-12

### Added
- **Local marketplace** index (`marketplace`, `/marketplace`) — plugins/skills/templates/maps
- **Live queue safety**: `--estimate-live`, require `--i-accept-live-costs` or `CHOKEPOINT_I_ACCEPT_LIVE_COSTS=1`
- **Quotes capabilities** doc API (`/quotes/capabilities`)
- CI: `eval-record` + marketplace/live-safety smoke
- UI Ops: marketplace, live estimate, enqueue map, checklist, quotes caps
- Docs: `docs/PLUGIN_MARKETPLACE.md`

## 4.6.0 — 2026-07-12

### Added
- Publish **checklist** gate (`checklist`, `/checklist/{name}`)
- **Eval history** + trend (`eval-record`, `eval-trend`, `/eval/record`, `/eval/trend`)
- Doctor shows research queue status

## 4.5.0 — 2026-07-12

### Added
- Offline **workspace digest** (`digest`, `/digest`)
- **Knowledge map compare** (`compare-maps`, `/maps/compare`)
- **Hypotheses** scratchpad → promote to thesis (`hypothesis`, `/hypotheses`)
- **Report frontmatter enrich** with quality + tags (`enrich-report`, `/reports/{name}/enrich`)
- UI Ops: workspace digest button

## 4.4.0 — 2026-07-12

### Added
- **Queue worker**: `queue --run N` (mock) / `--run N --live` (LLM); `POST /queue/run`
- **Export pack** zip (memo + evidence + lineage + tags): `export-pack`, `/export-pack`
- **Auto-tag** heuristics: `auto-tag`, `/auto-tag`
- **Thesis process health** scores: `thesis-health`, `/thesis-health`
- **Sanitized config**: `config-show`, `/config` (secrets → set/missing)
- **Notion-friendly export**: `notion-export`, `/notion-export/{name}`
- **Plugin catalog**: `plugin-catalog`, `/plugin-catalog`
- **Watchlist bulk add**: `watch bulk NVDA,AAPL`, `/watchlist/bulk`
- **Quality leaderboard**: `quality-board`, `/quality-board`
- **Scheduled queue tick** (mock only): `scripts/run_scheduled_queue.py`
- Skill pack: `materials_chem`
- UI Ops: queue run, thesis health, plugin catalog

### Fixed
- Research queue JSON load hardened against empty/corrupt files

## 4.3.0 — 2026-07-12

### Added
- SQLite FTS memo index (`index-memos`, `/index/memos`, `/index/search`)
- Research queue for batch planning (`queue`, `/queue`) — no LLM until run
- GitHub Releases published for v3.0–v4.2

## 4.2.0 — 2026-07-12

### Added
- Knowledge maps graph/seed from `knowledge/maps/*.yaml` (`maps`, `/maps`)
- Cost/quality dashboard (`dashboard`, `/dashboard`)
- Brief process-health section (kill monitor + cold coverage)
- Golden evals: `knowledge_map_seed`, `compare_structure`

## 4.1.0 — 2026-07-12

### Added
- Citation / domain co-occurrence network (`citations`, `/citations`)
- Report lineage chains (`lineage`, `/lineage`)
- Offline research plan generator (`plan`, `/plan`) — no LLM
- Provider health probes (`provider-health`, `/providers/health`)
- Coverage heat SVG (`/charts/coverage`)
- WebSocket quote stream `/ws/quotes` (polling-backed)
- UI Ops: citations, provider health, offline plan, coverage image

## 4.0.0 — 2026-07-12

Research ops maturity wave (v3.1–v4.0).

### Added
- **Evidence ledger** — extract URLs/claims/tickers; `evidence`, `/evidence`
- **Thesis graph** — theses ↔ chokepoints ↔ symbols; Mermaid export; `graph`, `/graph`
- **Structured memo compare** — `compare-memos`, `/compare-memos`
- **Report tags & collections** — `tag`, `collections`, `/tags`, `/collections`
- **Kill-criteria monitor** — process-risk dashboard; `kill-monitor`, `/kill-monitor`
- **Coverage heat map** — watchlist × theses × reports; `coverage`, `/coverage`
- **Audit trail** — append-only actions log; `audit`, `/audit`
- **Workspace snapshot** zip (no secrets); `snapshot`, `/snapshot`
- **DOCX export** (stdlib OOXML); `docx`, `/export/docx`; auto in export bundle
- **Plugin auto-loader** for `./plugins/`; `plugins`, `/plugins`
- Skill packs: `ai_infra`, `biotech_tools`
- UI **Ops** tab (graph / coverage / kill / evidence / audit / snapshot)
- Tests: `tests/test_v4_ops.py`

### Changed
- Post-process pipeline includes evidence summary fields
- Research save path writes audit + evidence ledger entries

## 3.0.0 — 2026-07-12

Optimization wave to v3.0.

### Added
- HTTP disk cache for public data (SEC tickers)
- Memo post-process pipeline (charts, citations metrics, quality gate)
- Domain skill packs (semiconductor / robotics / energy_power)
- Offline `mock-eval` + CI step
- Plugin SDK docs + example provider
- CLI: `skills`, `metrics`, `clear-cache`, `mock-eval`; research `--skill` / `--min-quality`

### Changed
- Research path auto post-processes memos before save/export
- Roadmap marks v2.6–v3.0 shipped

## 2.5.0 — 2026-07-12

Roadmap completion train (v2.1–v2.5).

### Added
- Auth plugins: open / API key / bearer / OIDC JWT (`src/auth`)
- SVG chart widgets (scorecard + price) + CLI `chart` + HTML embed
- Local TF-IDF memo search (`search-memos`, `/search/memos`, UI tab)
- HKEX-oriented news provider; quote SSE stream `/quotes/stream`
- Docs: RELEASE_NOTES_2.5 EN/ZH

## 2.0.0 — 2026-07-11

### Added
- **Real scheduling**: launchd (macOS) + cron helpers (`schedule install/status/uninstall/run`)
- **Pretty PDF**: fpdf2 generator, CLI `pdf`, API `/export/pdf`, auto in export bundle
- **A-share multi-source announcements**: Eastmoney notice/CMS + Sina roll; tools `cn_search_announcements`
- Docker compose profiles (`api` / `cron` sidecar)
- Docs: RELEASE_NOTES_2.0 EN/ZH

### Notes
- Research only — not investment advice
- Scheduled jobs use local model/search keys; monitor cost

## 1.20.0 — 2026-07-11

Twenty-version maturity train (v1.1–v1.20). See `docs/VERSIONS_1.1_to_1.20.md`.

### Highlights
- Report diff, watchlist CSV, thesis export, backup/restore
- API rate limit + request id / version headers
- Peer-review CLI, checklist template, token budget, webhooks
- CN announcements provider, expanded golden evals
- Bilingual docs for the full train

## 1.0.0-rc1 — 2026-07-11

Mature research-agent RC.

### Added
- Provider registry (`src/providers/`)
- SEC EDGAR company search + recent filings tools
- `validate_citations` tool
- Async research jobs (CLI `job`, REST `/jobs`)
- Workspace analytics (CLI `analytics`, REST `/analytics`)
- UI: Analytics + Jobs panels
- Docs: RELEASE_NOTES_1.0 EN/ZH, roadmap updates

### Notes
- Still research-only; not investment advice
- SEC access requires outbound HTTPS + compliant User-Agent

## 0.10.0 — 2026-07-11

Professional workstation cycle (v0.8–v0.10).

### Added
- Product roadmap EN/ZH (`docs/ROADMAP.md`)
- `doctor` health checks
- Watchlist / coverage book (CLI + API + UI)
- Thesis registry with status + kill criteria
- Report catalog search
- Builtin research templates (`templates/research/`)
- Multi-panel workstation UI
- `brief` watchlist batch digest
- Print-optimized HTML export
- Ops tests

### Changed
- Version alignment to 0.10.0
- Bilingual README updates

## 0.7.0 — 2026-07-10

Five major versions stack (0.3–0.7): China tools, sessions, export, EdgeOne docs, polish.

## 0.2.0 / 0.1.0

See git history / older release notes.
