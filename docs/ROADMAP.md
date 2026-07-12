# Product Roadmap — Chokepoint Research Agent

> Target: a **professional research workstation**, not a chat toy.  
> Benchmarks: Bloomberg/FactSet *research workflow*, Koyfin/TIKR *fundamentals*, AlphaSense *search*, Perplexity Finance *synthesis*, TradingView *monitoring*.

**中文版 → [zh/ROADMAP.md](./zh/ROADMAP.md)**

---

## 1. Competitive positioning

| Capability | Pro platforms | Us (v0.7) | Gap |
|------------|---------------|-----------|-----|
| Multi-source market data | Live terminals, filings | Best-effort public APIs | High |
| Structured research process | Analyst templates | Multi-agent + modes | Medium → closing |
| Watchlist / coverage book | Standard | None → **v0.8** | Closing |
| Thesis tracking + kill criteria | Internal wiki / Notion | Prompt-only → **v0.8** | Closing |
| Report library & search | Enterprise DMS | Folder dump → **v0.8** | Closing |
| Dashboards | Full BI | Single page → **v0.9** | Closing |
| Scheduled briefs | Alerts / digests | None → **v0.10** | Closing |
| Auth / multi-user / RBAC | Enterprise | Optional API key | Later |
| Portfolio P&amp;L / OMS | Core product | Out of scope (compliance) | Never as “advice” |

**Positioning statement:**  
*An open-source, framework-first research agent that industrializes Chokepoint Theory (bottom-up supply-chain reverse engineering) with professional workflow primitives: coverage book, thesis registry, templates, report catalog, and scheduled briefs.*

---

## 2. Principles (non-negotiable)

1. **Research ≠ advice** — no auto-trade, no “buy now”.  
2. **Tools own facts** — numbers need sources.  
3. **Red-team before publish** — kill criteria required on full memos.  
4. **Auditability** — reports are versioned files with metadata.  
5. **Bilingual docs** for every user-facing release.

---

## 3. Release train

| Version | Theme | Status |
|---------|--------|--------|
| v0.7 | Multi-agent core + modes + UI shell | Shipped |
| **v0.8** | Coverage book, thesis registry, report catalog, `doctor` | This cycle |
| **v0.9** | Research workstation UI + templates API | This cycle |
| **v0.10** | Scheduled brief, print-ready export, expanded evals | Shipped |
| **v0.11** | SEC EDGAR + provider registry + citation check | **Shipped** |
| **v0.12** | Async jobs + workspace analytics | **Shipped** |
| **v1.0.0-rc1** | Hardening / bilingual docs / tests | **Shipped** |
| **v1.1–v1.20** | Maturity train (ops/diff/backup/…) | **Shipped** |
| **v2.0.0** | launchd/cron, pretty PDF, multi-source CN ann | **Shipped** |
| **v2.1** | Auth plugins (API key / bearer / OIDC) | **Shipped** |
| **v2.2** | Chart widgets (SVG scorecard + price) | **Shipped** |
| **v2.3** | Local TF-IDF memo search | **Shipped** |
| **v2.4** | HKEX provider + quote SSE stream | **Shipped** |
| **v2.5.0** | Polish, bilingual docs, tests | **Shipped** |
| **v2.6–v2.9** | Cache, postprocess, skills, mock-eval/CI | **Shipped** |
| **v3.0.0** | Plugin SDK docs + maturity cut | **Shipped** |
| **v3.1–v3.9** | Evidence, graph, tags, compare, audit, docx, coverage | **Shipped** |
| **v4.0.0** | Research ops maturity cut | **Shipped** |
| **v4.1.0** | Citations, lineage, plan, provider health, WS quotes | **Shipped** |
| **v4.2.0** | Knowledge maps, cost dashboard, brief process health | **Shipped** |
| **v4.3.0** | FTS memo index + research queue | **Shipped** |
| **v4.4.0** | Queue worker, export pack, auto-tag, thesis health, catalog | **Shipped** |
| **v4.5.0** | Workspace digest, map compare, hypotheses, enrich frontmatter | **Shipped** |
| **v4.6.0** | Checklist gate, eval history/trend | **Shipped** |
| **v4.7.0** | Local marketplace, live queue safety, quotes caps | **Shipped** |
| **v4.8–v4.9** | Quote cache, workspace health, runbook, batch review | **Shipped** |
| **v5.0.0** | Professional workstation maturity cut | **Shipped** |
| **v5.1.0** | Memo grade + watchlist quote refresh | **Shipped** |
| **v5.2–v5.51** | 50 pro research-ops modules | **Shipped** |
| **v6.0.0** | Train cut + playbooks + metrics battery | **Shipped** |
| **v6.1.0** | Research desk, pro dashboard, memo-pro, glossary | **Shipped** |
| **v6.2.0** | Multi-quotes batch + remote plugin design doc | **Shipped** |
| v6.3 | Optional remote plugin install (hash-pinned) | Future |

---

## 4. v0.8 — Research operations layer

- [x] `main.py doctor` — config / dependency health  
- [x] Watchlist (JSON store + CLI + API)  
- [x] Thesis registry (statement, nodes, kill criteria, status)  
- [x] Report catalog index (scan reports/ with frontmatter)  
- [x] Research templates (builtin YAML)  
- [x] Docs + bilingual README delta  

---

## 5. v0.9 — Workstation UI

- [x] Multi-panel dashboard (Research / Watchlist / Theses / Reports / Templates)  
- [x] Run research from template or watchlist item  
- [x] REST for watchlist/thesis/templates/catalog  
- [x] Docs  

---

## 6. v0.10 — Automation & polish

- [x] `brief` command — batch watchlist digest  
- [x] Print-optimized HTML export  
- [x] Expanded golden evals  
- [x] CHANGELOG + version bump  

---

## 7. Later / done

- [x] SEC EDGAR / exchange filing snippets  
- [x] Plugin interface for data vendors (`src/providers`)  
- [x] Team auth plugins (API key / bearer / OIDC JWT)  
- [x] Local search over past memos (TF-IDF)  
- [x] Chart widgets in reports (SVG)  
- [x] Evidence ledger, thesis graph, tags/collections, structured compare  
- [x] Kill monitor, coverage heat, audit trail, workspace snapshot, DOCX  
- [x] Plugin auto-discovery from `./plugins/`  
- [~] Real-time quotes via **SSE polling** (full websockets → v4.1)  
- [ ] Plugin marketplace / third-party packages  


---

## 8. Success metrics (product quality)

| Metric | Target |
|--------|--------|
| Offline tests | Always green |
| Time-to-first-memo (docs) | &lt; 10 min setup |
| Structure quality score on golden set | 100% pass |
| Modes covered by docs | full/fast/risk/compare |
| Explicit disclaimer surfaces | CLI, UI, API, exports |

---

## 9. Explicit non-goals

- Brokerage integration  
- Signal generation sold as investment advice  
- Guaranteed alpha claims  
