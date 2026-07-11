# Release notes — v0.11 → v1.0.0-rc1

## Positioning

Toward a **mature research agent**: pluggable data providers, US SEC filings tools, async jobs, workspace analytics — still **research-only, not investment advice**.

中文 → [zh/RELEASE_NOTES_1.0.md](./zh/RELEASE_NOTES_1.0.md)

---

## v0.11 — Data depth

- Provider registry (`src/providers/`) for market + filings plugins
- **SEC EDGAR** tools: `sec_search_company`, `sec_recent_filings` (public, fair-access UA)
- `validate_citations` heuristic for memo quality
- Wired into agent toolkits + full-mode prompt guidance

## v0.12 — Ops maturity

- **Async jobs**: `POST /jobs`, `GET /jobs`, `GET /jobs/{id}`, CLI `job`
- **Analytics**: `GET /analytics`, CLI `analytics`
- UI tabs: Analytics + Jobs
- Provider list endpoint `GET /providers`

## v1.0.0-rc1 — Hardening

- Version alignment, bilingual README/roadmap updates
- Expanded tests for providers/jobs/analytics
- Documented path to GA (auth plugins, filings connectors beyond SEC)

---

## Upgrade

```bash
git pull
pip install -r requirements.txt
python main.py doctor
python main.py providers
python main.py --server
```

SEC tools need outbound HTTPS to `sec.gov` / `data.sec.gov`.

## Non-goals (still)

- Brokerage / auto-trading
- Investment advice claims
