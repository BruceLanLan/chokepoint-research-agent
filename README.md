# Chokepoint Research Agent

[![CI](https://github.com/BruceLanLan/chokepoint-research-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/BruceLanLan/chokepoint-research-agent/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Release](https://img.shields.io/github/v/release/BruceLanLan/chokepoint-research-agent)](https://github.com/BruceLanLan/chokepoint-research-agent/releases)

**多专家投研 Agent** — 用 **Chokepoint Theory（供应链瓶颈 / 卡脖子）** 做自下而上的深度研究，而不是复述大市值共识叙事。

> *In this system, who is the silent, irreplaceable physical switch?*  
> 在这个系统里，谁是那个沉默的、不可替代的物理开关？

**English:** Multi-agent investment *research* system (Deep Agents + specialist analysts).  
**中文主文档 → [README.zh-CN.md](README.zh-CN.md)**（推荐中文用户阅读）  
**中文文档目录 → [docs/zh/README.md](docs/zh/README.md)**

⚠️ **[免责声明](DISCLAIMER.md)：仅供研究学习，不构成投资建议。**

---

## Why this project

Most “AI stock bots” chat about NVDA Capex. This project is built around a different lens:

| Default market lens | This agent |
|---------------------|------------|
| Top-down mega-cap narratives | Bottom-up **supply-chain reverse engineering** |
| “What will beat next quarter?” | “Which node freezes the whole stack if cut?” |
| Single LLM essay | Lead + specialists + **devil’s advocate** |
| Demo chatbot | CLI + FastAPI + EdgeOne-ready prompts |

Methodology notes:

- Framework essay (reference, not a buy list): [BruceBlue on X](https://x.com/BruceBlue/status/2058901845402325243)
- Project write-up: [`docs/methodology.md`](docs/methodology.md)
- Knowledge sketches: [`knowledge/maps/`](knowledge/maps/)

Inspired by multi-agent deep research patterns (plan → parallel subagents → synthesize) and long-horizon verification loops.

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

# offline structure evals
python main.py eval

# list saved memos
python main.py list-reports

# API + web UI (SSE streaming supported)
python main.py --server
# → http://127.0.0.1:8000/      (UI)
# → http://127.0.0.1:8000/docs  (OpenAPI)
```

Or:

```bash
make check     # smoke + unit tests (no live keys)
make server    # FastAPI + UI
```

### Research modes

| Mode | Specialists | Use when |
|------|-------------|----------|
| `full` | all 5 | deep memo |
| `chokepoint_fast` | mapper + risk | cheaper scan |
| `risk_only` | risk-reviewer | stress-test a thesis |
| `compare` | mapper + fundamental + risk | 2–4 names side-by-side |

Version history: [`docs/VERSIONS.md`](docs/VERSIONS.md) · EdgeOne: [`docs/edgeone.md`](docs/edgeone.md)

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
