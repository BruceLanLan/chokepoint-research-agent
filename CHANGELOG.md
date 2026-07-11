# Changelog

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
