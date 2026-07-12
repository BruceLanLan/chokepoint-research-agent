# Changelog

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
