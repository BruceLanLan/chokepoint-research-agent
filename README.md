# Chokepoint Research Agent

[![CI](https://github.com/BruceLanLan/chokepoint-research-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/BruceLanLan/chokepoint-research-agent/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Release](https://img.shields.io/github/v/release/BruceLanLan/chokepoint-research-agent)](https://github.com/BruceLanLan/chokepoint-research-agent/releases)

**Open-source professional research workstation** for **Chokepoint Theory** — bottom-up supply-chain reverse engineering, multi-agent memo generation, coverage/thesis ops, evidence & quality gates, and offline research tooling.

> *In this system, who is the silent, irreplaceable physical switch?*

| | |
|---|---|
| **Version** | **8.2.0** |
| **Language** | Python ≥ 3.11 |
| **License** | MIT |
| **中文文档** | [README.zh-CN.md](README.zh-CN.md) · [docs/zh/](docs/zh/README.md) |

⚠️ **[Disclaimer](DISCLAIMER.md): research and education only — not investment advice.**  
No brokerage, no order routing, no “buy/sell” product surface.

---

## Table of contents

1. [Positioning](#1-positioning)
2. [Who it is for](#2-who-it-is-for)
3. [Methodology](#3-methodology)
4. [Capability map](#4-capability-map)
5. [Architecture](#5-architecture)
6. [Quick start](#6-quick-start)
7. [Configuration](#7-configuration)
8. [Research workflow](#8-research-workflow)
9. [CLI reference (high level)](#9-cli-reference-high-level)
10. [API & UI](#10-api--ui)
11. [Professional modules (v5.2–v5.51 train)](#11-professional-modules-v52v551-train)
12. [Quality, safety & compliance](#12-quality-safety--compliance)
13. [Project layout](#13-project-layout)
14. [Documentation index](#14-documentation-index)
15. [Development & testing](#15-development--testing)
16. [Roadmap & versioning](#16-roadmap--versioning)
17. [Security](#17-security)
18. [Contributing & license](#18-contributing--license)

---

## 1. Positioning

Most “AI stock bots” optimize for **narrative chat**: Capex stories, EPS whispers, ticker hype.

This repository implements a **research operations stack** closer to how a disciplined supply-chain analyst works:

| Dimension | Typical chat bot | This project |
|-----------|------------------|--------------|
| Question | “Will NVDA beat?” | “Which physical node fails the system if it breaks?” |
| Method | Top-down narrative | **Bottom-up reverse engineering** of a concrete system |
| Output | Unstructured chat | **Versioned memos** + scorecard + kill criteria |
| Process | One model monologue | Lead analyst + specialists + **red-team** |
| Ops | None | Coverage book, theses, evidence, queue, hygiene dashboards |
| Advice | Often implied | **Explicitly refused** (research only) |

**One-line product statement**

> An open-source, framework-first agent that industrializes Chokepoint Theory with workstation primitives: multi-agent research, coverage/thesis registries, evidence ledgers, quality gates, and offline professional modules — without pretending to be a market-data terminal or a broker.

Benchmark *workflows* (not feature parity): Bloomberg/FactSet research ops, AlphaSense-style memo search, analyst wiki discipline — **not** OMS, not live Level-2, not auto-trade.

---

## 2. Who it is for

**Good fit**

- Analysts / PMs building **AI infra, semis, optics, robotics, materials** research notes  
- Teams who want **reproducible memos** (files, tags, lineage, exports)  
- Builders packaging **Chokepoint methodology** into a shareable agent  
- Users who prefer **CLI + API + light UI** over a closed SaaS

**Poor fit**

- Automated trading, signal shops sold as advice  
- Guaranteed alpha or “replace Bloomberg terminal” expectations  
- Anyone unwilling to supply their own model/search API keys

---

## 3. Methodology

Full write-up: [`docs/methodology.md`](docs/methodology.md) · 中文: [`docs/zh/methodology.md`](docs/zh/methodology.md)

### Core idea

Start from a **touchable system** (e.g. GPU rack optical interconnect, humanoid body, power train), then peel layers:

```text
System → modules → components → equipment → materials → geography / policy
```

At each layer score (heuristic 1–5):

1. **Irreplaceability** — physical / process substitution cost  
2. **Concentration** — supplier / capacity concentration  
3. **Downstream leverage** — breakage impact  
4. **Coverage vacuum** — under-researched nodes  
5. **Commercial inflection** — timing of volume ramp  

### Non-negotiables

1. **Research ≠ advice** — no auto-trade, no “buy now”  
2. **Tools own facts** — numbers need sources  
3. **Red-team before publish** — kill criteria on full memos  
4. **Auditability** — reports are files with metadata  
5. **Bilingual docs** for user-facing releases  

Framework essay (not a buy list): [BruceBlue on X](https://x.com/BruceBlue/status/2058901845402325243) · condensed notes: [`knowledge/chokepoint_theory_bruceblue.md`](knowledge/chokepoint_theory_bruceblue.md)

Educational supply-chain sketches: [`knowledge/maps/`](knowledge/maps/) · glossary: [`knowledge/glossary/`](knowledge/glossary/)

---

## 4. Capability map

### A. Multi-agent research core

| Capability | Description |
|------------|-------------|
| Modes | `full` · `chokepoint_fast` · `risk_only` · `compare` |
| Specialists | Mapper, fundamental, news/catalyst, macro/industry, risk-reviewer |
| Runtime | Deep Agents when available; fallback orchestrator otherwise |
| Skills | Domain packs (`semiconductor`, `ai_infra`, robotics, materials, …) |
| Sessions | Multi-turn session memory |
| Post-process | Structure quality, citation check, scorecard charts, metrics |

### B. Research operations layer

| Capability | CLI examples | Purpose |
|------------|--------------|---------|
| Doctor | `doctor` | Env / dependency / ops health |
| Coverage book | `watch *` · `watch bulk` | Symbols, thesis notes, priority |
| Thesis registry | `thesis *` · `thesis-health` · `kill-monitor` | Statement, kills, status history |
| Hypotheses | `hypothesis *` | Pre-thesis scratchpad → promote |
| Templates | `templates` · `--template` | YAML research templates |
| Report catalog | `list-reports` · FTS `index-memos` · `search-memos` | Library + search |
| Evidence | `evidence` · ledger | URLs / claims / domains |
| Graphs | `graph` · `citations` · `maps` | Thesis graph, citation network, knowledge maps |
| Queue | `queue` (mock default; live gated) | Plan batch work, drain offline |
| Quality | `checklist` · `grade-memo` · `batch-review` · `quality-board` | Publish gates |
| Hygiene | `digest` · `workspace-health` · `weekly-ops` · `desk` | Desk rituals |
| Export | HTML/JSON/PDF/DOCX · `export-pack` · snapshot | Portable archives |
| Pro modules | `pro` · `pro-suite` · `pro-dashboard` · `memo-pro` | 50 ops modules (v5.2–v5.51 train) |
| Playbooks / Q / rubrics | `playbook` · `questionnaire` · `rubric` | Process libraries |

### C. Data & extensibility

| Layer | Contents |
|-------|----------|
| Providers | SEC EDGAR, multi-source CN announcements, HKEX-oriented news, Yahoo market (best-effort) |
| Cache | HTTP disk cache, quote history cache, multi-quote batch |
| Plugins | `./plugins/` auto-load · local [marketplace](docs/PLUGIN_MARKETPLACE.md) · [SDK](docs/PLUGIN_SDK.md) |
| Auth | Open · API key · bearer · OIDC JWT plugins |
| Realtime | SSE + WebSocket quote streams (polling-backed; **not** a pro MD terminal) |

### D. Offline-first discipline

Many commands run **without an LLM** (plan, maps, digest, desk, pro-suite, eval, mock-eval, queue mock).  
Live model burns require explicit acceptance (`queue --run --live --i-accept-live-costs`).

---

## 5. Architecture

```text
                    ┌─────────────────────────────────────┐
                    │  CLI (Typer)  ·  FastAPI  ·  Web UI  │
                    └─────────────────┬───────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
   Research agent              Research ops                   Providers
   (modes + skills             (watch / thesis /              (SEC / CN / HK /
    + postprocess)              queue / evidence /             market / plugins)
                                desk / pro train)
          │                           │
          └─────────────┬─────────────┘
                        ▼
              reports/  ·  data/  ·  exports
         (memos, metrics, ledgers, caches — gitignored secrets)
```

Multi-agent path:

```text
User question
     │
     ▼
Lead analyst (plan + synthesize)
     ├── chokepoint-mapper
     ├── fundamental-analyst
     ├── news-catalyst-analyst
     ├── macro-industry-analyst
     └── risk-reviewer (kill criteria)
     │
     ▼
Markdown memo → quality gate → optional PDF/DOCX/HTML/JSON → catalog
```

Details: [`docs/architecture.md`](docs/architecture.md) · workstation guide: [`docs/PROFESSIONAL_WORKSTATION.md`](docs/PROFESSIONAL_WORKSTATION.md)

---

## 6. Quick start

### Requirements

- Python **≥ 3.11**
- Model API (Anthropic **or** OpenAI-compatible: DeepSeek / MiniMax / EdgeOne gateway / …)
- [Tavily](https://tavily.com) (or configured search) for live web research
- Optional: outbound HTTPS for SEC / market providers

### Install

```bash
git clone https://github.com/BruceLanLan/chokepoint-research-agent.git
cd chokepoint-research-agent

python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt

cp .env.example .env
# Edit .env — model keys + TAVILY_API_KEY at minimum for live research
```

### First commands (safe / offline)

```bash
python main.py doctor
python main.py about                 # version + capability snapshot
python main.py desk --md             # research desk status
python main.py maps                  # knowledge maps
python main.py pro                   # list 50 pro modules
python main.py mock-eval
python main.py eval
```

### First live research (costs tokens)

```bash
python main.py research "Map CPO chokepoints for AI GPU racks" \
  --mode chokepoint_fast \
  --skill semiconductor \
  --min-quality 50 \
  --export
```

### Workstation UI (v8)

Professional multi-tab shell: **Desk · Research · Coverage · Theses · Reports · Templates · Search · Knowledge · Analytics · Ops · Jobs · Doctor**, with **EN/ZH** toggle, SSE research stream, and report checklist/grade/export actions.

```bash
python main.py --server
# UI:      http://127.0.0.1:8000/
# OpenAPI: http://127.0.0.1:8000/docs
```

### Docker (API)

```bash
cp .env.example .env   # fill secrets
docker compose up --build
```

### Make targets

```bash
make check     # smoke + unit tests + eval
make server
```

---

## 7. Configuration

Copy [`.env.example`](.env.example). Never commit `.env`.

### Model providers

**Anthropic**

```env
MODEL_PROVIDER=anthropic
MODEL_NAME=claude-sonnet-4-20250514
ANTHROPIC_API_KEY=sk-ant-...
TAVILY_API_KEY=tvly-...
```

**OpenAI-compatible (DeepSeek / OpenAI / vLLM / MiniMax)**

```env
MODEL_PROVIDER=openai_compatible
MODEL_NAME=deepseek-chat
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.deepseek.com/v1
TAVILY_API_KEY=tvly-...
# MiniMax also accepts MINIMAX_API_KEY
```

**EdgeOne Makers gateway**

```env
MODEL_PROVIDER=openai_compatible
MODEL_NAME=@makers/deepseek-v4-flash
AI_GATEWAY_API_KEY=sk-...
AI_GATEWAY_BASE_URL=https://ai-gateway.edgeone.link/v1
TAVILY_API_KEY=tvly-...
```

### Optional ops / auth

| Variable | Purpose |
|----------|---------|
| `API_ACCESS_KEY` | Gate API with `X-API-Key` |
| `API_BEARER_TOKEN` | Bearer auth plugin |
| `OIDC_*` | OIDC JWT validation |
| `MAX_TOKENS_BUDGET` | Soft token budget |
| `WEBHOOK_URL` | Async job completion webhook |
| `CHOKEPOINT_I_ACCEPT_LIVE_COSTS=1` | Allow live LLM queue runs |

Sanitized dump (no secret values): `python main.py config-show`

---

## 8. Research workflow

Recommended **professional loop** (see also `python main.py runbook --md`):

```text
1. Frame     maps --seed · plan · runbook · skill pack
2. Cover     watch / bulk · coverage heat
3. Thesis    thesis · hypothesis · kill criteria
4. Research  research / queue mock → optional live
5. Evidence  evidence · citations · filings tools
6. Gate      checklist · grade-memo · min-quality
7. Archive   tag · lineage · export-pack · docx/pdf
8. Hygiene   desk · digest · weekly-ops · workspace-health
```

### Research modes

| Mode | Specialists | When to use |
|------|-------------|-------------|
| `full` | All five | Deep memo |
| `chokepoint_fast` | Mapper + risk | Cheaper scan |
| `risk_only` | Risk-reviewer | Stress-test a thesis |
| `compare` | Mapper + fundamental + risk | 2–4 names side-by-side |

### Example questions

See [`examples/sample_questions.md`](examples/sample_questions.md).

```text
• CPO / silicon photonics: which layer is the real physical switch?
• Map actuator / harmonic / RV concentration for humanoids
• Is ticker X a chokepoint or merely downstream beta?
• Red-team: “CPO is the only AI interconnect path”
```

---

## 9. CLI reference (high level)

Entry: `python main.py` · help: `python main.py --help` · Chinese CLI notes: [`docs/zh/cli.md`](docs/zh/cli.md)

### Research & eval

```bash
python main.py research "…" --mode full|chokepoint_fast|risk_only|compare
python main.py research "…" --skill semiconductor --min-quality 50 --export
python main.py research --template chokepoint_map --var system="AI CPO" --var context=""
python main.py brief --dry-run
python main.py job "async question" --mode chokepoint_fast
python main.py eval · mock-eval · metrics · eval-record · eval-trend
```

### Ops & quality

```bash
python main.py doctor · desk --md · workspace-health · digest · weekly-ops
python main.py watch add NVDA --priority high
python main.py thesis add --title "…" --statement "…" --kills "…"
python main.py checklist memo.md · grade-memo memo.md · batch-review
python main.py queue --from-map cpo_ai_interconnect
python main.py queue --run 2                    # mock, safe
# python main.py queue --run 1 --live --i-accept-live-costs
```

### Knowledge & pro train

```bash
python main.py maps cpo_ai_interconnect --seed
python main.py pro · pro-suite · pro-dashboard · memo-pro report.md
python main.py playbook saas_infra
python main.py questionnaire management_quality
python main.py glossary CPO
python main.py marketplace --q optics
```

### Export & data

```bash
python main.py pdf --file reports/….md
python main.py docx memo.md · export-pack memo.md · snapshot
python main.py multi-quotes NVDA,AVGO · quote-chart NVDA
python main.py backup · restore · config-show
```

---

## 10. API & UI

| Area | Endpoints (selected) |
|------|----------------------|
| Core | `GET /` UI · `GET /health` · `GET /doctor` · `GET /desk` |
| Research | `POST /research` · `POST /research/stream` · `POST /jobs` |
| Ops | `/watchlist` · `/theses` · `/templates` · `/queue` · `/evidence` · `/graph` |
| Quality | `/checklist/{name}` · `/grade/{name}` · `/batch-review` · `/workspace-health` |
| Pro | `/pro/modules` · `/pro/{id}` · `/pro/suite` · `/pro/dashboard` · `/pro/verticals` · `/memo-pro` |
| Knowledge | `/maps` · `/glossary` · `/marketplace` · `/playbooks` · `/questionnaires` · `/rubrics` |
| Streams | `GET /quotes/stream` · `WS /ws/quotes` · `/charts/*` |

Auth: optional `X-API-Key` / bearer / OIDC depending on env.

```bash
curl -s localhost:8000/desk | jq .
curl -s localhost:8000/research \
  -H 'Content-Type: application/json' \
  -d '{"question":"CPO supply-chain chokepoints","mode":"chokepoint_fast","save_report":true}'
```

Deployment: [`docs/deployment.md`](docs/deployment.md) · EdgeOne: [`docs/edgeone.md`](docs/edgeone.md)

---

## 11. Professional modules (v5.2–v5.51 train)

Fifty offline **research-ops modules** (event calendar, risk matrix, capacity tracker, moat evidence, policy watch, …) ship as a maturity train:

- Catalog: [`docs/VERSIONS_5.2_to_5.51.md`](docs/VERSIONS_5.2_to_5.51.md)  
- Per-module notes: [`docs/pro-modules/`](docs/pro-modules/)  
- Aggregate: `python main.py pro-dashboard` · suite: `python main.py pro-suite`

Also included:

| Library | Command | Count (approx.) |
|---------|---------|-----------------|
| Playbooks | `playbook` | 20 |
| Questionnaires | `questionnaire` | 48 |
| Process rubrics | `rubric` | 28 |
| Text metrics | `metrics-run` | 150 heuristics |

These score **process quality**, not investment performance.

---

## 12. Quality, safety & compliance

| Mechanism | Role |
|-----------|------|
| Structure quality score | Heuristic gate on memo sections / URLs / length |
| `checklist` / `grade-memo` | Publish readiness |
| `min-quality` on research | Fail closed on weak structure |
| Evidence ledger + citations | Source hygiene |
| Live queue gate | Explicit cost acceptance required |
| Audit log | Workstation actions |
| Snapshot / backup | Never includes `.env` |
| Auth plugins | Optional API protection |

**Explicit non-goals:** brokerage, portfolio OMS, guaranteed alpha, regulatory-grade market data.

---

## 13. Project layout

```text
chokepoint-research-agent/
├── main.py                 # Thin Typer entry → src/cli
├── AGENTS.md               # Durable agent/operating rules
├── src/
│   ├── cli/                # CLI packages (research, ops, pro, …)
│   ├── api/                # FastAPI factory + route packages
│   ├── static/             # Professional UI (html/css/js/i18n)
│   ├── agents/             # Multi-agent + fallback
│   ├── prompts/            # Methodology prompts
│   ├── tools/              # Search, filings, export, PDF/DOCX
│   ├── ops/                # Watchlist, theses, queue, desk, …
│   ├── ops/pro/            # 50 pro maturity-train modules
│   ├── playbooks/ · questionnaires/ · rubrics/
│   ├── pipeline/ · charts/ · auth/ · providers/
│   └── plugins/            # Plugin loader
├── skills/pro/             # 50 pro YAML specs
├── skills/pro_verticals/   # Deep vertical packs (CPO, HBM, …)
├── knowledge/              # Maps, essays, glossary
├── templates/research/     # Memo templates
├── docs/                   # Architecture, releases, workstation guides
├── eval/ · tests/
├── reports/ · data/        # Runtime outputs (gitignored content)
└── scripts/                # Schedule / overnight autonomous helpers
```

---

## 14. Documentation index

| Doc | Description |
|-----|-------------|
| [docs/PROFESSIONAL_WORKSTATION.md](docs/PROFESSIONAL_WORKSTATION.md) | Analyst loop & weekly rituals |
| [docs/methodology.md](docs/methodology.md) | Chokepoint methodology |
| [docs/architecture.md](docs/architecture.md) | System design |
| [docs/deployment.md](docs/deployment.md) | Deploy notes |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Product roadmap |
| [docs/PLUGIN_SDK.md](docs/PLUGIN_SDK.md) · [PLUGIN_MARKETPLACE.md](docs/PLUGIN_MARKETPLACE.md) | Extensibility |
| [docs/REMOTE_PLUGIN_DESIGN.md](docs/REMOTE_PLUGIN_DESIGN.md) | Future remote plugins (design only) |
| [docs/VERSIONS_5.2_to_5.51.md](docs/VERSIONS_5.2_to_5.51.md) | 50-module train |
| [docs/AUTONOMOUS_SETUP.md](docs/AUTONOMOUS_SETUP.md) | Unattended agent runs |
| [docs/zh/README.md](docs/zh/README.md) | Chinese docs hub |
| [CHANGELOG.md](CHANGELOG.md) | Release history |
| [DISCLAIMER.md](DISCLAIMER.md) · [SECURITY.md](SECURITY.md) | Legal / security |

---

## 15. Development & testing

```bash
.venv/bin/python -m pytest tests/ -q
python main.py mock-eval
python main.py eval
python main.py pro-suite --text "system chokepoint kill https://example.com"
```

- Tests are **offline** (no live LLM required for CI).  
- CI: GitHub Actions on Python 3.11 / 3.12.  
- Agent operating rules for automation: [`AGENTS.md`](AGENTS.md).

---

## 16. Roadmap & versioning

Ship train highlights:

| Line | Theme |
|------|--------|
| v0.x–v2.x | Workstation core: modes, watch/thesis, schedule, PDF, auth, charts, search |
| v3.x | Cache, post-process, skills, plugin SDK |
| v4.x–v5.x | Evidence, graph, queue, desk hygiene, pro maturity |
| v5.2–v5.51 | **50 pro research-ops modules** |
| v6.0–v6.2 | Train cut, playbooks/rubrics/glossary, desk, multi-quotes |
| Future | Hash-pinned remote plugins (design exists); heavier realtime MD (still research-scoped) |

Full tables: [`docs/ROADMAP.md`](docs/ROADMAP.md) · releases: [GitHub Releases](https://github.com/BruceLanLan/chokepoint-research-agent/releases)

---

## 17. Security

- Never commit `.env`, API keys, or tokens  
- Do not expose the API without auth on untrusted networks  
- Treat fetched web/filing text as **untrusted** (prompt injection)  
- Snapshot/backup paths exclude secrets by design  

See [`SECURITY.md`](SECURITY.md).

---

## 18. Contributing & license

Contributions welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

If you cite this project, link the repository and restate that outputs are **not investment advice**.

**License:** [MIT](LICENSE) © 2026 BruceLanLan

---

### Citation

```text
Chokepoint Research Agent — https://github.com/BruceLanLan/chokepoint-research-agent
Framework inspiration: https://x.com/BruceBlue/status/2058901845402325243
```

### Star

If this improves your research workflow, a star helps others find a **framework-first** alternative to chat-wrapper stock bots.
