# Chokepoint Research Agent

[![CI](https://github.com/BruceLanLan/chokepoint-research-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/BruceLanLan/chokepoint-research-agent/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Release](https://img.shields.io/github/v/release/BruceLanLan/chokepoint-research-agent)](https://github.com/BruceLanLan/chokepoint-research-agent/releases)

**Mature research agent (v3.0.0)** powered by **Chokepoint Theory** — multi-agent research, filings, scheduling, PDF, auth, charts, memo search, **skill packs**, **post-process pipeline**, **plugin SDK**. Not investment advice.

> *In this system, who is the silent, irreplaceable physical switch?*  
> 在这个系统里，谁是那个沉默的、不可替代的物理开关？

**中文主文档 → [README.zh-CN.md](README.zh-CN.md)** · **中文文档目录 → [docs/zh/README.md](docs/zh/README.md)**  
**Roadmap → [docs/ROADMAP.md](docs/ROADMAP.md)** · **Release notes → [docs/RELEASE_NOTES_0.10.md](docs/RELEASE_NOTES_0.10.md)**

⚠️ **[Disclaimer](DISCLAIMER.md): research/education only — not investment advice.**

---

## Why this project

Most “AI stock bots” chat about NVDA Capex. This project is a **research ops workstation**:

| Pro-tool capability | Here |
|---------------------|------|
| Coverage book | Watchlist CLI + API + UI |
| Thesis registry | Kill-criteria tracked theses |
| Analyst templates | Builtin YAML templates |
| Report library | Catalog search + exports |
| Multi-agent synthesis | Lead + specialists + red-team |
| Environment health | `python main.py doctor` |
| Scheduled-style digest | `python main.py brief` |
| US filings | SEC EDGAR tools (`sec_search_company` / `sec_recent_filings`) |
| Async research | `python main.py job "..."` + `/jobs` |
| Workspace analytics | `python main.py analytics` |

Methodology:

- Framework essay (not a buy list): [BruceBlue on X](https://x.com/BruceBlue/status/2058901845402325243)
- [`docs/methodology.md`](docs/methodology.md) · [`knowledge/maps/`](knowledge/maps/)

---

## Architecture

```text
User question
     │
     ▼
Lead Investment Analyst (plan + synthesize)
     │
     ├── chokepoint-mapper      # supply-chain map + scorecard
     ├── fundamental-analyst    # business, financials, liquidity
     ├── news-catalyst-analyst  # events & narrative gap
     ├── macro-industry-analyst # policy, geo, capacity
     └── risk-reviewer          # red-team / kill criteria
     │
     ▼
Markdown research memo → reports/
```

See full detail in [`docs/architecture.md`](docs/architecture.md).

---

## Quick start

### Requirements

- **Python ≥ 3.11**
- Model API key (Anthropic / OpenAI-compatible / EdgeOne gateway)
- [Tavily](https://tavily.com) API key for web search

### Install

```bash
git clone https://github.com/BruceLanLan/chokepoint-research-agent.git
cd chokepoint-research-agent

python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt

cp .env.example .env
# edit .env — at least MODEL keys + TAVILY_API_KEY
```

### Docker (API only)

```bash
cp .env.example .env   # fill secrets
docker compose up --build
# → http://127.0.0.1:8000/docs
```

### Configure `.env`

**Option A — Anthropic (strong long-horizon reasoning)**

```env
MODEL_PROVIDER=anthropic
MODEL_NAME=claude-fable-5
ANTHROPIC_API_KEY=sk-ant-...
TAVILY_API_KEY=tvly-...
```

**Option B — OpenAI-compatible (DeepSeek / OpenAI / vLLM)**

```env
MODEL_PROVIDER=openai_compatible
MODEL_NAME=deepseek-chat
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.deepseek.com/v1
TAVILY_API_KEY=tvly-...
```

**Option C — EdgeOne Makers AI Gateway**

```env
MODEL_PROVIDER=openai_compatible
MODEL_NAME=@makers/deepseek-v4-flash
AI_GATEWAY_API_KEY=sk-...
AI_GATEWAY_BASE_URL=https://ai-gateway.edgeone.link/v1
TAVILY_API_KEY=tvly-...
```

### Run research

```bash
python main.py "以英伟达 B200 集群为物理原点，逆向拆解 CPO 供应链卡脖子节点，输出 Chokepoint Scorecard 并做红蓝对抗"

# faster path: mapper + risk only
python main.py "CPO chokepoints" --mode chokepoint_fast

# multi-name comparison table
python main.py "对照 A 与 B 谁更接近光互联 chokepoint" --mode compare

# red-team an existing thesis
python main.py "论点：CPO 是唯一路径。请打脸。" --mode risk_only

# multi-turn session memory
python main.py new-session
python main.py "继续深挖 ELS" --session <id>

# bilingual one-pager + full export
python main.py "HBM 供应链卡点" --bilingual --export

# health + coverage book + templates (v0.8+)
python main.py doctor
python main.py watch add NVDA --name "NVIDIA" --thesis "AI GPU stack" --priority high
python main.py templates
python main.py research --template chokepoint_map --var system="AI optical interconnect" --var context=""
python main.py list-reports --q CPO
python main.py brief --dry-run

# offline structure evals
python main.py eval

# workstation UI + API
python main.py --server
# → http://127.0.0.1:8000/      (multi-panel UI)
# → http://127.0.0.1:8000/docs  (OpenAPI)
```

```bash
make check     # smoke + unit tests + eval
make server
```

### Research modes

| Mode | Specialists | Use when |
|------|-------------|----------|
| `full` | all 5 | deep memo |
| `chokepoint_fast` | mapper + risk | cheaper scan |
| `risk_only` | risk-reviewer | stress-test a thesis |
| `compare` | mapper + fundamental + risk | 2–4 names side-by-side |

### Workstation modules (v0.8–v0.10)

| Module | CLI | API |
|--------|-----|-----|
| Doctor | `doctor` | `GET /doctor` |
| Watchlist | `watch *` | `/watchlist` |
| Theses | `thesis *` | `/theses` |
| Templates | `templates` / `--template` | `/templates` |
| Catalog | `list-reports --q` | `/reports?q=` |
| Brief | `brief` | `POST /brief` |
| Jobs | `job` | `/jobs` |
| Analytics | `analytics` | `/analytics` |
| Providers | `providers` | `/providers` |
| Schedule | `schedule *` | `/schedule/*` |
| PDF | `pdf --file …` | `/export/pdf` |

### v2.0 highlights

```bash
# real daily brief (macOS launchd + prints cron line)
python main.py schedule install --hour 9 --minute 0 --limit 3
python main.py schedule status
python main.py schedule run          # run once now (costs tokens)

# pretty PDF
python main.py pdf --file reports/xxx.md --title "CPO Memo"

# A-share multi-source announcements (via agent tools / provider)
python main.py providers
```

### v2.1–v2.5 (roadmap done)

```bash
python main.py search-memos "CPO kill criteria"
python main.py chart scorecard --report some_report.md
python main.py chart price --symbol NVDA --period 6mo
# Auth: set API_ACCESS_KEY or API_BEARER_TOKEN or OIDC_* in .env
```

```bash
python main.py skills
python main.py research "CPO 卡点" --skill semiconductor --mode chokepoint_fast --min-quality 50
python main.py mock-eval
python main.py metrics
```

Roadmap: [`docs/ROADMAP.md`](docs/ROADMAP.md) · **v3.0 notes:** [`docs/RELEASE_NOTES_3.0.md`](docs/RELEASE_NOTES_3.0.md) · Plugins: [`docs/PLUGIN_SDK.md`](docs/PLUGIN_SDK.md)

---

## Example questions

See [`examples/sample_questions.md`](examples/sample_questions.md).

```text
• CPO / silicon photonics: which layer is the real physical switch?
• Map harmonic / RV / actuator concentration for humanoids
• Is company X a chokepoint or just downstream beta?
• Red-team: “CPO is the only AI interconnect path”
```

---

## Project layout

```text
chokepoint-research-agent/
├── main.py                 # CLI (Typer) + server entry
├── src/
│   ├── agents/             # Deep Agents + fallback orchestrator
│   ├── prompts/            # Chokepoint methodology prompts
│   ├── tools/              # Search, market, knowledge maps, save
│   ├── api.py              # FastAPI + SSE
│   └── config.py
├── knowledge/              # Methodology notes + YAML maps
├── docs/                   # Architecture, deployment, methodology
├── examples/               # Sample research questions
├── reports/                # Generated memos (gitignored content)
├── tests/                  # Unit tests (no live API)
├── DISCLAIMER.md
└── LICENSE
```

---

## API

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Lightweight web UI |
| `GET` | `/health` | Health + config warnings |
| `GET` | `/reports` | List saved memos |
| `GET` | `/reports/{name}` | Read one memo |
| `POST` | `/research` | Full research (JSON, `mode` field) |
| `POST` | `/research/stream` | SSE progress + final report |

Optional header: `X-API-Key` when `API_ACCESS_KEY` is set in env.

```bash
curl -s localhost:8000/research \
  -H 'Content-Type: application/json' \
  -d '{"question":"CPO supply-chain chokepoints 2026","save_report":true}'
```

Deployment notes: [`docs/deployment.md`](docs/deployment.md).

---

## Roadmap

- [x] Multi-agent deep research (Deep Agents + fallback)
- [x] Chokepoint methodology prompts + scorecard template
- [x] Local knowledge maps (YAML) as tool context
- [x] CLI + FastAPI/SSE + lightweight UI
- [x] Research modes (`full` / `chokepoint_fast` / `risk_only`)
- [x] Report quality heuristics + scorecard table parse
- [x] CI (Python 3.11 / 3.12)
- [ ] Richer A-share / HK filings tools
- [ ] Eval harness with golden questions
- [ ] EdgeOne Makers template packaging

Contributions welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## Security

- Do not commit `.env` or API keys
- Do not expose the demo API to the public internet without auth
- Web pages can contain prompt-injection content; treat tool output as untrusted

See [`SECURITY.md`](SECURITY.md).

---

## Citation / reference

If you use this project in writing or research tooling, please link the repository and note that outputs are **not investment advice**.

Framework inspiration (independent essay): [x.com/BruceBlue/status/2058901845402325243](https://x.com/BruceBlue/status/2058901845402325243)

---

## License

[MIT](LICENSE) © 2026 BruceLanLan

---

## Star History

If this helps your research workflow, a star is appreciated — it helps others find a **framework-first** alternative to chat-wrapper stock bots.
