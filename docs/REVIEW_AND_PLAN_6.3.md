# Project review & plan — Chokepoint Research Agent v6.3

**Date:** 2026-07-12  
**Scope:** Full product / architecture / quality review (not a single PR diff).  
**Baseline:** v6.3.0 · 113 offline tests green · ~26k LOC under `src/` · 78 CLI commands · 105 API routes  

**Disclaimer:** Research workstation review only — not investment advice.

---

## 1. Executive summary

| Dimension | Rating | Notes |
|-----------|--------|-------|
| Product positioning | **Strong** | Clear “research ops ≠ trading bot”; README now professional |
| Methodology fidelity | **Strong** | Chokepoint scorecard + kill criteria + multi-agent red-team |
| Feature breadth | **Very high** | Ops surface is unusually wide for an open-source agent |
| Feature depth / differentiation | **Mixed** | Core research path solid; many pro modules are template-similar |
| Engineering hygiene | **Good** | Offline CI, doctor, live-cost gates, no secrets in git |
| Architecture maintainability | **At risk** | Monolithic `main.py` / `api.py`; flat `ops/` explosion |
| UX / discoverability | **Medium** | CLI is powerful but overwhelming; UI lags API |
| Data quality / providers | **Medium** | Best-effort public sources; not a terminal |
| Path to “professional analyst daily driver” | **Clear but needs focus** | Consolidate > accumulate |

**Bottom line:** The project has crossed from “demo multi-agent memo writer” into a **credible research-ops workstation skeleton**. The next 1–2 major versions should **consolidate, deepen, and productize the golden path**, not add another 50 shallow modules.

---

## 2. What is working well

### 2.1 Product spine (do not break)

1. **Methodology-first multi-agent research** — modes, specialists, risk-reviewer, skill packs, post-process gates.  
2. **Research ops primitives** — watchlist, theses + kills, evidence, queue (mock-first), checklist/grade, desk/weekly-ops.  
3. **Audit & safety culture** — disclaimers, live LLM cost gate, snapshot excludes `.env`, optional auth plugins.  
4. **Offline discipline** — large surface runs without LLM; CI can stay green without keys.  
5. **Docs recovery** — v6.3 README (EN/ZH) finally matches the real capability surface.

### 2.2 Quantitative footprint (healthy signals)

| Metric | Value |
|--------|------:|
| CLI command decorators | ~78 |
| API routes | ~105 |
| `src/ops` modules | ~65 |
| Pro train modules | 50 |
| Playbooks / questionnaires / rubrics | 20 / 48 / 28 |
| Offline tests | 113 |
| UI tabs | 10 |

### 2.3 Competitive niche (defend this)

Open-source agents that **force kill criteria + physical scorecard + coverage book** are rare. That is the moat — not “more JSONL note types.”

---

## 3. Findings (ordered by severity)

### P0 — Product / architecture risks

| ID | Finding | Why it matters | Recommendation |
|----|---------|----------------|----------------|
| P0-1 | **`main.py` (~1.8k LOC) and `api.py` (~1.6k LOC) are god files** | Every feature increases merge conflict & cognitive load; onboarding cost high | Split into `cli/` and `api/routes/` packages by domain (research, ops, pro, export) |
| P0-2 | **Pro modules (v5.2–v5.51) share nearly identical logic** | 50 “versions” inflate surface without domain depth; users cannot tell modules apart | Collapse to a **parameterized base** + thin domain configs (keywords, checklists, schemas); keep 50 IDs as config, one engine |
| P0-3 | **Command surface ≫ discoverable workflows** | Analysts need 3 paths, not 78 peers | Promote **golden path** in CLI help groups / `desk` recommendations; deprecate or nest rarely used commands under `pro` / `ops` |

### P1 — Quality & UX gaps

| ID | Finding | Recommendation |
|----|---------|----------------|
| P1-1 | UI covers ~10 tabs; many API surfaces (pro, glossary, desk, rubrics) only in Ops dump | Add **Desk** as first-class tab; surface checklist/grade on Reports |
| P1-2 | Golden eval set is thin (~6 cases) vs product breadth | Expand golden memos per mode + one pro-suite regression |
| P1-3 | Provider quality is “best effort”; failures become stub quotes | Explicit provider SLA docs + doctor live probes optional; never present stubs as prices without `stub:true` UI badge |
| P1-4 | `doctor` can fail on missing model/search keys (expected) | Separate **config doctor** vs **ops doctor** so empty keys don’t look like product broken |
| P1-5 | JSONL stores under `data/` have no migration / schema version | Add store schema_version + backup on write for pro/theses/watchlist |
| P1-6 | AUTONOMOUS_LOG “Next up” still mentions pre-6.2 items | Keep log current each ship (process debt) |

### P2 — Depth opportunities (not bugs)

| ID | Opportunity |
|----|-------------|
| P2-1 | Thesis ↔ report ↔ evidence **hard links** (IDs in frontmatter) instead of soft text search |
| P2-2 | Memo-pro bridge is powerful but not on default research save path |
| P2-3 | Real scheduling exists for brief; not yet for `weekly-ops` / queue mock ticks |
| P2-4 | Remote plugins designed, not implemented — good; implement only with hash pin + allowlist |
| P2-5 | Glossary has filler `research_term_NNN` entries — cull or mark experimental |
| P2-6 | English UI still mixed CN labels — optional EN-first mode |

### P3 — Explicit non-goals (confirm stay out)

- Brokerage / OMS / portfolio P&L sold as advice  
- Regulatory-grade market data guarantees  
- Silent live LLM burns  
- “50 more generated modules” without domain content  

---

## 4. Architecture assessment

```text
Current shape:

  CLI (flat) ──┐
  API (flat) ──┼── ops/* (many peers) ── data/*.json(l)
  UI (partial)─┘         │
                    pro/* (50 clones)
                    playbooks / questionnaires / rubrics
```

**Target shape (v7):**

```text
  cli/
    research.py · ops.py · pro.py · export.py
  api/
    routes/research.py · ops.py · pro.py · knowledge.py
  domain/
    research/   # agent, postprocess, modes
    coverage/   # watch, heat, quotes
    thesis/     # theses, kills, hypotheses
    evidence/   # ledger, citations, filings
    quality/    # checklist, grade, batch-review
    pro/        # single engine + YAML specs
  ui/           # desk-first SPA or progressive enhancement
```

Principles:

1. **Golden path first** — research → gate → archive → desk  
2. **One engine, many specs** for pro/questionnaire/rubric families  
3. **ID graph** between thesis / report / evidence / queue item  
4. **Offline default, live explicit**  

---

## 5. Product strategy (next 6–12 weeks)

### North star

> A solo analyst can run a **weekly Chokepoint coverage process** end-to-end without reading 70 CLI help pages — and leave an auditable trail.

### Strategy pillars

| Pillar | Goal | Anti-goal |
|--------|------|-----------|
| **A. Consolidate** | Fewer entry points, clearer IA | More top-level commands |
| **B. Deepen** | Domain-specific pro specs (CPO, HBM, power) that differ in substance | Template clones |
| **C. Integrate** | Research save auto-writes evidence + optional pro notes + audit | Manual glue only |
| **D. Prove** | Golden evals + fixture suite + desk score as CI artifact | Only unit tests of helpers |
| **E. Extend carefully** | Hash-pinned plugins when needed | Remote code free-for-all |

---

## 6. Release plan

### Phase 0 — Stabilize (v6.4.x, ~1 week)

- [ ] Group CLI help into Typer sub-apps: `research`, `ops`, `pro`, `export` (keep aliases)  
- [ ] Cull or tag glossary `research_term_*` as experimental  
- [ ] Fix AUTONOMOUS_LOG next-up drift  
- [ ] Expand golden evals to ≥15 (modes + bilingual structure)  
- [ ] Document provider limitations in one page (`docs/PROVIDERS.md`)  

**Exit:** New contributor finds “day-1 path” in <10 minutes via README + `about` + `desk`.

### Phase 1 — Golden path productization (v6.5–v6.8)

- [ ] Research save pipeline always: postprocess → evidence extract → audit → optional auto-tag  
- [ ] Frontmatter IDs: `thesis_id`, `watch_ids`, `skill`, `quality_score`  
- [ ] UI: **Desk** tab (health, next actions, queue, kill-monitor)  
- [ ] UI: Reports row actions — checklist / grade / export-pack  
- [ ] `weekly-ops` installable on schedule (alongside brief)  
- [ ] Memo-pro optional flag on `research --pro-suite`  

**Exit:** One command sequence covers weekly hygiene without hunting commands.

### Phase 2 — Pro engine refactor (v6.9–v7.0)

- [ ] Single `ProEngine` + `skills/pro/*.yaml` (keywords, checklist, schema)  
- [ ] Keep 50 module IDs for compatibility; drop 50 near-duplicate `.py` files  
- [ ] Domain-deep YAMLs for: CPO/optics, HBM/packaging, power/cooling, robotics actuators, materials  
- [ ] Pro dashboard becomes meaningful (schema-filled fields, not only density scores)  

**Exit:** LOC of pro stack **down**, domain usefulness **up**; tests still cover 50 IDs.

### Phase 3 — Integration depth (v7.1–v7.4)

- [ ] Thesis graph linked to real report IDs + evidence entries  
- [ ] Queue worker: mock default; live still gated; cost estimate in UI  
- [ ] Provider health in desk; stub quotes never look “real” in UI  
- [ ] Optional remote plugin install per `REMOTE_PLUGIN_DESIGN.md` (hash + allowlist)  
- [ ] EN/CN UI language toggle  

**Exit:** Analyst can track one thesis from hypothesis → research → invalidate with full lineage.

### Phase 4 — Hardening (v7.5–v8.0)

- [ ] Split `main.py` / `api.py` fully  
- [ ] Store migrations + backup-on-write  
- [ ] Typed settings validation report  
- [ ] Performance: FTS default for search; catalog pagination  
- [ ] Security review: auth defaults for non-local bind  
- [ ] Package entrypoints / versioned OpenAPI export  

**Exit:** “v8 professional workstation” — maintainable, documented, boringly reliable.

---

## 7. Prioritized backlog (next 10 work items)

| # | Item | Phase | Effort | Impact |
|---|------|-------|--------|--------|
| 1 | CLI command grouping + `desk` as default “what next” | 0–1 | M | High |
| 2 | Expand golden evals (modes + structure) | 0 | M | High |
| 3 | Research save auto evidence + audit (already partial) complete path | 1 | M | High |
| 4 | UI Desk tab + report actions | 1 | L | High |
| 5 | Pro engine + YAML specs (compat IDs) | 2 | L | High |
| 6 | Domain-deep pro YAMLs (5 verticals) | 2 | M | High |
| 7 | Schedule weekly-ops | 1 | S | Med |
| 8 | Providers.md + stub UX | 0–1 | S | Med |
| 9 | Cull glossary filler terms | 0 | S | Med |
| 10 | Hash-pinned remote plugin install (optional) | 3 | L | Med |

---

## 8. Success metrics (product)

| Metric | Target |
|--------|--------|
| Offline tests | Always green on CI |
| Time-to-first-memo (docs) | < 10 minutes |
| Golden structure pass rate | 100% on suite |
| Commands needed for weekly hygiene | ≤ 5 documented |
| Pro modules with **distinct** domain checklists | ≥ 10 deep (not 50 clones) |
| Explicit disclaimer surfaces | CLI, UI, API, exports |
| Live research accidental burns | 0 (gate holds) |

---

## 9. Risks & mitigations

| Risk | Mitigation |
|------|------------|
| Feature bloat continues | Freeze new top-level CLI without removing/nesting one |
| Generated modules confuse users | Refactor to YAML; market “50 process lenses” not “50 products” |
| Provider flakiness | Offline stubs labeled; doctor live optional |
| Token cost surprises | Keep mock-first queue; estimate-live; budget settings |
| Maintainability cliff | Phase 2–4 architecture split mandatory before v8 |

---

## 10. Recommendation for immediate next sprint

**Do not** start another 50-module generation pass.

**Do** ship a **consolidation sprint (v6.4)**:

1. CLI help groups + refresh AUTONOMOUS_LOG  
2. Golden eval expansion  
3. Providers doc + glossary cull  
4. Optional: schedule weekly-ops  

Then **v6.5–v7.0**: golden path + pro engine refactor.

That sequence maximizes “professional research agent” credibility faster than raw LOC growth.

---

## 11. Appendix — current golden path (document this everywhere)

```bash
python main.py doctor
python main.py about
python main.py desk --md
python main.py maps cpo_ai_interconnect --seed
python main.py research "…" --mode chokepoint_fast --skill semiconductor --min-quality 50 --export
python main.py checklist <memo.md>
python main.py grade-memo <memo.md>
python main.py export-pack <memo.md>
python main.py weekly-ops
```

**Research only — not investment advice.**
