# Chokepoint Research Agent（卡脖子投研工作台）

[![CI](https://github.com/BruceLanLan/chokepoint-research-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/BruceLanLan/chokepoint-research-agent/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Release](https://img.shields.io/github/v/release/BruceLanLan/chokepoint-research-agent)](https://github.com/BruceLanLan/chokepoint-research-agent/releases)

**开源专业投研工作台**：基于 **卡脖子理论（Chokepoint Theory）** 的自下而上供应链逆向工程，多专家研报生成，覆盖簿 / 论点库 / 证据账本 / 质检门禁，以及大量可离线运行的专业研究模块。

> 在这个系统里，谁是那个沉默的、不可替代的物理开关？

| | |
|---|---|
| **版本** | **6.3.0** |
| **语言** | Python ≥ 3.11 |
| **许可** | MIT |
| **English** | [README.md](README.md) |

⚠️ **[免责声明](DISCLAIMER.md)：仅供研究学习，不构成任何投资建议。**  
不做券商对接、不下单、不提供「买卖点」产品形态。

---

## 目录

1. [定位](#1-定位)
2. [适合谁 / 不适合谁](#2-适合谁--不适合谁)
3. [方法论](#3-方法论)
4. [能力全景](#4-能力全景)
5. [架构](#5-架构)
6. [快速开始](#6-快速开始)
7. [配置](#7-配置)
8. [研究工作流](#8-研究工作流)
9. [命令行概览](#9-命令行概览)
10. [API 与 UI](#10-api-与-ui)
11. [专业模块火车](#11-专业模块火车)
12. [质量与安全](#12-质量与安全)
13. [目录结构](#13-目录结构)
14. [文档索引](#14-文档索引)
15. [开发与测试](#15-开发与测试)
16. [版本与路线图](#16-版本与路线图)
17. [安全](#17-安全)
18. [贡献与许可](#18-贡献与许可)

---

## 1. 定位

多数「AI 炒股机器人」优化的是**叙事聊天**：Capex、EPS、股价故事。

本仓库实现的是**研究运营栈（Research Ops）**，更接近纪律型供应链分析师的工作方式：

| 维度 | 常见聊天 Bot | 本项目 |
|------|--------------|--------|
| 问题 | 「NVDA 会超预期吗？」 | 「哪一个物理节点断了，系统会瘫痪？」 |
| 方法 | 自上而下叙事 | **自下而上**拆可触摸系统 |
| 产出 | 无结构闲聊 | **可落盘研报** + Scorecard + 杀逻辑 |
| 过程 | 单模型独白 | 主分析师 + 多专家 + **魔鬼代言人** |
| 运营 | 无 | 覆盖簿、论点库、证据、队列、卫生看板 |
| 建议 | 常暗示买卖 | **明确拒绝**（仅研究） |

**一句话产品陈述**

> 开源、框架优先的投研 Agent：把卡脖子方法论工程化为多专家研究 + 工作台原语（覆盖 / 论点 / 证据 / 质检 / 归档），而不是行情终端或券商。

对标的是 **Bloomberg/FactSet 的研究流程、AlphaSense 式检索、分析师 Wiki 纪律**——不是 OMS，不是 Level-2，不是自动交易。

---

## 2. 适合谁 / 不适合谁

**适合**

- 做 **AI 基建 / 半导体 / 光互联 / 机器人 / 材料** 研究笔记的人  
- 需要 **可复现研报**（文件、标签、谱系、导出）的小团队  
- 想把「卡脖子」框架产品化成可分享 Agent 的开发者  
- 习惯 **CLI + API + 轻量 UI** 的用户  

**不适合**

- 自动下单、信号跟单、当投资顾问用  
- 期望「替代 Bloomberg 数据终端」  
- 不愿自备模型 / 搜索 API Key  

---

## 3. 方法论

完整说明：[docs/zh/methodology.md](docs/zh/methodology.md) · English: [docs/methodology.md](docs/methodology.md)

### 核心思路

从**可触摸系统**出发（如 GPU 光互连、人形机器人本体、供电链路），逐层下拆：

```text
系统 → 模块 → 关键器件 → 设备 → 材料 → 地理 / 政策
```

每层启发式打分（1–5）：

1. **不可替代性**  
2. **集中度**  
3. **下游杠杆**  
4. **覆盖真空**  
5. **商业化拐点**  

### 不可妥协原则

1. **研究 ≠ 建议**  
2. **工具负责事实**（数字要有来源）  
3. **发布前红蓝对抗**（kill criteria）  
4. **可审计**（研报是带元数据的文件）  
5. **用户可见能力双语文档**  

框架文（非荐股清单）：[BruceBlue on X](https://x.com/BruceBlue/status/2058901845402325243)  
浓缩笔记：[`knowledge/chokepoint_theory_bruceblue.md`](knowledge/chokepoint_theory_bruceblue.md)  
供应链草图：[`knowledge/maps/`](knowledge/maps/) · 术语表：[`knowledge/glossary/`](knowledge/glossary/)

---

## 4. 能力全景

### A. 多专家研究核心

- 模式：`full` / `chokepoint_fast` / `risk_only` / `compare`  
- 角色：卡点制图、基本面、催化、宏观行业、风险（杀逻辑）  
- 技能包：半导体、AI 基建、机器人、材料等  
- 后处理：结构质检、引用检查、Scorecard 图、指标  

### B. 研究运营层

| 能力 | 示例命令 | 作用 |
|------|----------|------|
| 体检 | `doctor` · `desk` | 环境与工作台状态 |
| 覆盖簿 | `watch` | 标的与论点笔记 |
| 论点库 | `thesis` · `kill-monitor` | 状态与杀逻辑 |
| 证据 | `evidence` · `citations` | URL / 声明 / 共现 |
| 队列 | `queue`（默认 mock） | 规划批量研究 |
| 质检 | `checklist` · `grade-memo` · `batch-review` | 发布门禁 |
| 卫生 | `digest` · `weekly-ops` · `workspace-health` | 周度运营 |
| 专业模块 | `pro` · `pro-suite` · `pro-dashboard` | 50 模块火车 |
| 导出 | PDF/DOCX/HTML · `export-pack` | 归档 |

### C. 数据与扩展

- 提供方：SEC、多源 A 股公告、港股新闻取向、Yahoo 行情（尽力而为）  
- 插件：`./plugins/` · [插件 SDK](docs/zh/PLUGIN_SDK.md) · [本地 marketplace](docs/PLUGIN_MARKETPLACE.md)  
- 鉴权：API Key / Bearer / OIDC  
- 行情流：SSE / WebSocket（底层轮询，**不是**专业行情终端）  

### D. 离线优先

大量命令**不调用 LLM**（plan、maps、desk、pro-suite、eval、queue mock 等）。  
真烧模型需显式确认（`queue --run --live --i-accept-live-costs`）。

---

## 5. 架构

```text
用户
 │
 ▼
CLI / FastAPI / Web UI
 │
 ├── 研究 Agent（模式 + 技能 + 后处理）
 ├── 研究运营（覆盖 / 论点 / 队列 / 证据 / desk / pro）
 └── 数据提供方（SEC / A股 / HK / 行情 / 插件）
 │
 ▼
reports/ · data/ · 导出物
```

多专家路径：

```text
问题 → 总监规划 → 五类专家 → 风险红队 → Markdown 研报 → 质检 → 归档
```

详见：[docs/zh/architecture.md](docs/zh/architecture.md) · 工作台指南：[docs/PROFESSIONAL_WORKSTATION.md](docs/PROFESSIONAL_WORKSTATION.md)

---

## 6. 快速开始

### 环境

- Python **≥ 3.11**  
- 模型 API（Anthropic 或 OpenAI 兼容：DeepSeek / MiniMax / EdgeOne 等）  
- 实时联网研究需要 Tavily 等搜索 Key  

### 安装

```bash
git clone https://github.com/BruceLanLan/chokepoint-research-agent.git
cd chokepoint-research-agent

python3.11 -m venv .venv
source .venv/bin/activate
pip install -U pip && pip install -r requirements.txt

cp .env.example .env
# 编辑 .env：至少模型 Key + TAVILY_API_KEY（若要做 live research）
```

### 先跑安全/离线命令

```bash
python main.py doctor
python main.py about
python main.py desk --md
python main.py pro
python main.py mock-eval
```

### 第一次真实研究（耗 token）

```bash
python main.py research "拆解 AI GPU 机柜 CPO 卡点" \
  --mode chokepoint_fast \
  --skill semiconductor \
  --min-quality 50 \
  --export
```

### 启动工作台

```bash
python main.py --server
# UI http://127.0.0.1:8000/  ·  OpenAPI /docs
```

---

## 7. 配置

复制 `.env.example`，**切勿提交 `.env`**。

**Anthropic**

```env
MODEL_PROVIDER=anthropic
MODEL_NAME=claude-sonnet-4-20250514
ANTHROPIC_API_KEY=sk-ant-...
TAVILY_API_KEY=tvly-...
```

**OpenAI 兼容（DeepSeek / MiniMax 等）**

```env
MODEL_PROVIDER=openai_compatible
MODEL_NAME=deepseek-chat
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.deepseek.com/v1
TAVILY_API_KEY=tvly-...
```

**可选**：`API_ACCESS_KEY` / `API_BEARER_TOKEN` / `OIDC_*` / `CHOKEPOINT_I_ACCEPT_LIVE_COSTS`

脱敏配置：`python main.py config-show`

---

## 8. 研究工作流

推荐闭环（亦见 `runbook --md`）：

```text
定界 → 覆盖 → 论点/杀逻辑 → 研究 → 证据 → 门禁 → 归档 → 周度卫生
```

| 模式 | 适用 |
|------|------|
| `full` | 深度备忘 |
| `chokepoint_fast` | 低成本快扫 |
| `risk_only` | 红蓝对抗 |
| `compare` | 2–4 标的对照 |

示例问题见 [`examples/sample_questions.md`](examples/sample_questions.md)。

---

## 9. 命令行概览

```bash
# 研究
python main.py research "…" --mode chokepoint_fast --skill semiconductor

# 运营
python main.py desk --md
python main.py watch add NVDA --priority high
python main.py thesis add --title "…" --statement "…" --kills "…"
python main.py queue --from-map cpo_ai_interconnect
python main.py queue --run 2

# 质检 / 卫生
python main.py checklist xxx.md
python main.py grade-memo xxx.md
python main.py weekly-ops
python main.py workspace-health

# 专业库
python main.py pro
python main.py pro-suite --text "system chokepoint kill https://x.com"
python main.py playbook · questionnaire · glossary · marketplace

# 导出
python main.py export-pack xxx.md · pdf · docx · snapshot
```

完整中文 CLI：[docs/zh/cli.md](docs/zh/cli.md)

---

## 10. API 与 UI

| 类别 | 端点示例 |
|------|----------|
| 核心 | `GET /` · `/health` · `/doctor` · `/desk` |
| 研究 | `POST /research` · `/research/stream` · `/jobs` |
| 运营 | `/watchlist` · `/theses` · `/queue` · `/evidence` · `/graph` |
| Pro | `/pro/modules` · `/pro/suite` · `/pro/dashboard` · `/memo-pro` |
| 知识 | `/maps` · `/glossary` · `/marketplace` · `/playbooks` |

```bash
curl -s localhost:8000/desk | jq .
```

部署：[docs/zh/deployment.md](docs/zh/deployment.md)

---

## 11. 专业模块火车

**v5.2.0–v5.51.0** 共 **50** 个离线研究运营模块（事件日历、风险矩阵、产能笔记、护城河证据、政策观察……）：

- 目录：[docs/VERSIONS_5.2_to_5.51.md](docs/VERSIONS_5.2_to_5.51.md)  
- 模块说明：[docs/pro-modules/](docs/pro-modules/)  
- 命令：`pro` / `pro-suite` / `pro-dashboard` / `memo-pro`  

另含：约 20 个 playbook、48 个问卷、28 个过程评分量表、150 项文本启发式指标——评的是**过程质量**，不是投资收益。

---

## 12. 质量与安全

- 结构质检 / checklist / grade-memo / min-quality  
- 证据账本与引用检查  
- Live 队列费用门禁  
- 审计日志；snapshot **永不**打包 `.env`  
- 可选 API 鉴权  

**明确不做：** 券商、OMS、承诺 Alpha、监管级行情。

---

## 13. 目录结构

```text
main.py · AGENTS.md
src/agents · prompts · tools · ops · ops/pro · playbooks
   questionnaires · rubrics · analysis · providers · api · static
knowledge/maps · glossary · essays
skills/packs · templates/research · plugins
docs/ · eval/ · tests/ · scripts/
reports/ · data/   # 运行时输出（密钥不入库）
```

---

## 14. 文档索引

| 文档 | 说明 |
|------|------|
| [docs/zh/README.md](docs/zh/README.md) | 中文文档中心 |
| [docs/PROFESSIONAL_WORKSTATION.md](docs/PROFESSIONAL_WORKSTATION.md) | 专业工作台闭环 |
| [docs/zh/methodology.md](docs/zh/methodology.md) | 方法论 |
| [docs/zh/architecture.md](docs/zh/architecture.md) | 架构 |
| [docs/zh/ROADMAP.md](docs/zh/ROADMAP.md) | 路线图 |
| [docs/zh/cli.md](docs/zh/cli.md) | 命令速查 |
| [docs/AUTONOMOUS_SETUP.md](docs/AUTONOMOUS_SETUP.md) | 自主/过夜运行 |
| [CHANGELOG.md](CHANGELOG.md) | 变更历史 |
| [DISCLAIMER.md](DISCLAIMER.md) | 免责声明 |

---

## 15. 开发与测试

```bash
.venv/bin/python -m pytest tests/ -q
python main.py mock-eval
python main.py eval
```

- CI：Python 3.11 / 3.12，离线测试为主  
- 自动化规则：[AGENTS.md](AGENTS.md)

---

## 16. 版本与路线图

| 阶段 | 主题 |
|------|------|
| v0–v2 | 工作台核心：模式、覆盖/论点、定时、PDF、鉴权、图表、检索 |
| v3 | 缓存、后处理、技能包、插件 SDK |
| v4–v5 | 证据、图谱、队列、卫生看板、成熟度 |
| v5.2–v5.51 | **50 专业模块火车** |
| v6.0–v6.2 | 火车收口、desk、术语表、多标的行情 |
| 未来 | 哈希钉扎远程插件（设计文档已有）；更重实时数据（仍限研究场景） |

发布页：https://github.com/BruceLanLan/chokepoint-research-agent/releases

---

## 17. 安全

- 不提交密钥；公网暴露 API 必须开鉴权  
- 抓取文本按**不可信**处理（提示注入）  
- 详见 [SECURITY.md](SECURITY.md)

---

## 18. 贡献与许可

欢迎贡献：[CONTRIBUTING.md](CONTRIBUTING.md) · [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

引用请附仓库链接，并注明输出**不是投资建议**。

**License:** [MIT](LICENSE) © 2026 BruceLanLan

```text
Chokepoint Research Agent
https://github.com/BruceLanLan/chokepoint-research-agent
```

若对研究工作流有帮助，欢迎 Star——帮助更多人找到**框架优先**、而非聊天套壳的投研 Agent。
