# Chokepoint Research Agent（卡脖子投研 Agent）

[![CI](https://github.com/BruceLanLan/chokepoint-research-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/BruceLanLan/chokepoint-research-agent/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Release](https://img.shields.io/github/v/release/BruceLanLan/chokepoint-research-agent)](https://github.com/BruceLanLan/chokepoint-research-agent/releases)

**English → [README.md](README.md)** · **当前版本 v4.2.0**

**成熟投研 Agent v3**：多专家 + 运营台 + 定时/PDF + 鉴权/图表/检索 + **技能包** + **后处理管线** + **插件 SDK** + 缓存/指标。  
**研究用途，非投资建议。**  
发布说明：[docs/zh/RELEASE_NOTES_3.0.md](docs/zh/RELEASE_NOTES_3.0.md) · 插件：[docs/zh/PLUGIN_SDK.md](docs/zh/PLUGIN_SDK.md)

> 在这个系统里，谁是那个沉默的、不可替代的物理开关？

⚠️ **[免责声明](DISCLAIMER.md)：仅供研究学习，不构成任何投资建议。**

---

## 目录

1. [项目是做什么的](#1-项目是做什么的)
2. [核心方法论](#2-核心方法论)
3. [系统架构](#3-系统架构)
4. [功能一览（v0.7）](#4-功能一览v07)
5. [快速开始](#5-快速开始)
6. [研究模式](#6-研究模式)
7. [命令行用法](#7-命令行用法)
8. [Web UI 与 API](#8-web-ui-与-api)
9. [环境变量](#9-环境变量)
10. [知识图谱](#10-知识图谱)
11. [目录结构](#11-目录结构)
12. [文档索引](#12-文档索引)
13. [开发与测试](#13-开发与测试)
14. [部署与上线](#14-部署与上线)
15. [版本历史](#15-版本历史)
16. [常见问题](#16-常见问题)
17. [贡献与许可](#17-贡献与许可)

---

## 1. 项目是做什么的

多数「AI 炒股机器人」在聊 NVDA Capex、下季度 EPS。本项目换了一套镜头：

| 常见路径 | 本项目 |
|----------|--------|
| 自上而下讲巨头叙事 | **自下而上**供应链逆向工程 |
| 下季度能不能超预期 | **哪一环断了，整条链会瘫痪** |
| 单个 LLM 写一篇长文 | 主分析师 + 多专家 + **魔鬼代言人** |
| 聊天 Demo | CLI + Web UI + FastAPI，可继续托管上线 |
| 直接给「买什么」 | **教框架、出研报、写 kill criteria** |

适合：

- 做 AI 基建 / 半导体 / 光互联 / 机器人 / 材料的**研究笔记**
- 想把「卡脖子」框架产品化成可分享的 Agent
- 需要可落盘、可质检、可对照、可红蓝对抗的研究流水线

**不适合：** 自动下单、跟单、把输出当投资顾问意见。

---

## 2. 核心方法论

完整说明见：[docs/zh/methodology.md](docs/zh/methodology.md)

### 一句话

从 GPU 集群、机器人整机等**可触摸系统**出发，逐层向下拆：

```text
终端系统 → 模块 → 关键器件 → 设备 → 材料 / 化学品 → 地理与政策节点
```

每一层问：

1. 是否**物理难替代**？  
2. 供给是否**高度集中**？  
3. 断供对下游有没有**杠杆**？  
4. 是否落在**机构覆盖真空**？  
5. 是否接近**商业化放量拐点**？

### 发布前必做红蓝对抗

独立 `risk-reviewer` 扮演魔鬼代言人：攻击路径依赖、估值透支、流动性陷阱与证伪条件（kill criteria）。

### 参考框架文（非荐股清单）

[BruceBlue：拆解 Serenity 的卡脖子算法](https://x.com/BruceBlue/status/2058901845402325243)  
项目内浓缩版：[`knowledge/chokepoint_theory_bruceblue.md`](knowledge/chokepoint_theory_bruceblue.md)

---

## 3. 系统架构

```text
用户问题
   │
   ▼
投研总监（规划 + 综合写报）
   │
   ├── chokepoint-mapper      供应链瓶颈制图 / Scorecard
   ├── fundamental-analyst    基本面、估值、流动性、覆盖真空
   ├── news-catalyst-analyst  新闻催化、预期差
   ├── macro-industry-analyst 宏观、政策、地缘产能
   └── risk-reviewer          魔鬼代言人 / kill criteria
   │
   ▼
Markdown 研报 → reports/（可选 JSON / HTML）
```

运行时：

- **优先** LangChain `deepagents`（多子 Agent）
- **降级** 内置并行编排器（`fallback_orchestrator`）

详见：[docs/zh/architecture.md](docs/zh/architecture.md)

---

## 4. 功能一览（v0.10）

| 能力 | 说明 |
|------|------|
| 多专家研究 | 规划 → 并行专家 → 综合 |
| 研究模式 | `full` / `chokepoint_fast` / `risk_only` / `compare` |
| **环境体检** | `python main.py doctor` |
| **覆盖名单** | `watch list/add/rm/research` + API/UI |
| **论点台账** | `thesis *`（含 kill criteria 状态流转） |
| **研究模板** | `templates/research/*.yaml` + `--template` |
| **研报目录** | `list-reports --q` 检索 frontmatter |
| **自选简报** | `brief` 对 watchlist 批处理快扫 |
| 工具 | 搜索、抓取、Yahoo、A 股/港股、CN 新闻 |
| 知识图谱 | CPO / 机器人 / 稀土 / 电力 / HBM / 光模块 |
| 会话记忆 | `--session` 多轮 |
| 质检 / 导出 | quality score + MD/JSON/**打印友好 HTML** |
| Web 工作台 | 研究 / 覆盖 / 论点 / 研报 / 模板 / Analytics / Jobs / Doctor |
| **SEC 文件** | `sec_search_company` / `sec_recent_filings`（美股） |
| **异步任务** | `job` / `POST /jobs` 后台研究 |
| **工作台统计** | `analytics` / `GET /analytics` |
| 可插拔数据源 | `src/providers/` 注册表 |
| 路线图 | [docs/zh/ROADMAP.md](docs/zh/ROADMAP.md) · [docs/zh/RELEASE_NOTES_1.0.md](docs/zh/RELEASE_NOTES_1.0.md) |

---

## 5. 快速开始

### 5.1 环境要求

- **Python ≥ 3.11**（`deepagents` 要求）
- 模型 API Key（DeepSeek / Anthropic / OpenAI 兼容 / EdgeOne 网关 任选）
- [Tavily](https://tavily.com) API Key（联网搜索）

### 5.2 安装

```bash
git clone https://github.com/BruceLanLan/chokepoint-research-agent.git
cd chokepoint-research-agent

python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt

cp .env.example .env
# 编辑 .env，至少配置：模型 Key + TAVILY_API_KEY
```

macOS 若默认是 Python 3.9，请用 Homebrew 或已安装的 3.11+。

### 5.3 配置 `.env`（三选一）

**DeepSeek（常用、性价比高）：**

```env
MODEL_PROVIDER=openai_compatible
MODEL_NAME=deepseek-chat
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.deepseek.com/v1
TAVILY_API_KEY=tvly-...
```

**Anthropic（长程推理更强，如 Claude Fable 5）：**

```env
MODEL_PROVIDER=anthropic
MODEL_NAME=claude-fable-5
ANTHROPIC_API_KEY=sk-ant-...
TAVILY_API_KEY=tvly-...
```

**EdgeOne Makers AI 网关：**

```env
MODEL_PROVIDER=openai_compatible
MODEL_NAME=@makers/deepseek-v4-flash
AI_GATEWAY_API_KEY=sk-...
AI_GATEWAY_BASE_URL=https://ai-gateway.edgeone.link/v1
TAVILY_API_KEY=tvly-...
```

### 5.4 跑第一条研究

```bash
python main.py "以英伟达 B200 集群为物理原点，逆向拆解 CPO 供应链卡脖子节点，输出 Scorecard 并做红蓝对抗"
```

### 5.5 启动界面

```bash
python main.py --server
# 浏览器打开 http://127.0.0.1:8000/
# API 文档     http://127.0.0.1:8000/docs
```

### 5.6 Docker（可选）

```bash
cp .env.example .env   # 填好密钥
docker compose up --build
# → http://127.0.0.1:8000/
```

---

## 6. 研究模式

| 模式 | 专家组合 | 适用场景 | 成本 |
|------|----------|----------|------|
| `full` | 五专家全开 | 深度个股 / 主题备忘录 | 高 |
| `chokepoint_fast` | 制图 + 风险 | 快速扫卡点 | 中 |
| `risk_only` | 仅风险审查 | 已有论点，要打脸 / 证伪 | 低 |
| `compare` | 制图 + 基本面 + 风险 | 2–4 个标的对照表 | 中高 |

```bash
python main.py "CPO 卡脖子快扫" --mode chokepoint_fast
python main.py "对照 A 与 B 谁更接近物理开关" --mode compare
python main.py "论点：CPO 是唯一路径。请攻击。" --mode risk_only
```

---

## 7. 命令行用法

```bash
# 基础研究
python main.py "你的问题"
python main.py "你的问题" --stream          # 打印中间过程
python main.py "你的问题" --mode compare
python main.py "你的问题" --bilingual       # 追加英文 one-pager
python main.py "你的问题" --export          # 额外导出 JSON/HTML

# 多轮会话
python main.py new-session                  # 打印 session id
python main.py "继续深挖 ELS" --session <id>

# 研报管理
python main.py list-reports

# 离线结构评测（不需要模型 Key）
python main.py eval

# 服务
python main.py --server
python main.py version
```

也可用 Make：

```bash
make check    # smoke + pytest + eval
make server
make eval
```

更多示例问题：[examples/sample_questions.md](examples/sample_questions.md)  
CLI 速查：[docs/zh/cli.md](docs/zh/cli.md)

---

## 8. Web UI 与 API

### Web UI

访问 `http://127.0.0.1:8000/`：

- 选择模式、是否 SSE 流式、是否双语
- 可填 session id 做多轮
- 右侧浏览历史研报

### 主要 API

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/` | Web UI |
| `GET` | `/health` | 健康检查 + 配置告警 |
| `GET` | `/docs` | OpenAPI 文档 |
| `POST` | `/sessions` | 新建 session |
| `GET` | `/reports` | 研报列表 |
| `GET` | `/reports/{name}` | 读取单篇 |
| `POST` | `/research` | 同步研究 |
| `POST` | `/research/stream` | SSE 流式研究 |

请求示例：

```bash
curl -s http://127.0.0.1:8000/research \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "人形机器人关节供应链卡点",
    "mode": "chokepoint_fast",
    "save_report": true,
    "export": true
  }'
```

若设置了 `API_ACCESS_KEY`，请求需带：

```http
X-API-Key: your-key
```

完整部署说明：[docs/zh/deployment.md](docs/zh/deployment.md)

---

## 9. 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `MODEL_PROVIDER` | 是 | `anthropic` 或 `openai_compatible` |
| `MODEL_NAME` | 是 | 模型名 |
| `OPENAI_API_KEY` / `AI_GATEWAY_API_KEY` / `ANTHROPIC_API_KEY` | 视 provider | 模型鉴权 |
| `OPENAI_BASE_URL` / `AI_GATEWAY_BASE_URL` | 兼容接口时 | 网关地址 |
| `TAVILY_API_KEY` | 是* | 联网搜索（*无搜索则研究能力严重下降） |
| `RESEARCH_MODE` | 否 | 默认 `full` |
| `MAX_CONCURRENT_SUBAGENTS` | 否 | 默认 3 |
| `MAX_SEARCHES_PER_SUBAGENT` | 否 | 默认 5 |
| `REPORTS_DIR` | 否 | 默认 `./reports` |
| `BILINGUAL_MEMO` | 否 | 默认 false |
| `EXPORT_HTML_JSON` | 否 | 默认 true |
| `API_ACCESS_KEY` | 否 | 设置后 API 需密钥 |
| `LOG_LEVEL` | 否 | 默认 INFO |
| `REQUEST_TIMEOUT_SECONDS` | 否 | 默认 600（反向代理也要调大） |

模板见：[.env.example](.env.example)

---

## 10. 知识图谱

`knowledge/maps/*.yaml` 是**教育用供应链草图**，Agent 可通过工具加载，再上网核实：

| 文件 | 主题 |
|------|------|
| `cpo_ai_interconnect.yaml` | AI 集群 CPO / 共封装光学 |
| `optical_pluggables.yaml` | 可插拔光模块（CPO 替代路径） |
| `hbm_memory_stack.yaml` | HBM / 先进封装存储 |
| `humanoid_robot_body.yaml` | 人形机器人身体供应链 |
| `rare_earth_magnets.yaml` | 稀土永磁 |
| `power_for_ai_datacenters.yaml` | AI 数据中心电力与散热 |

原则：**草图是假设清单，不是荐股清单。**

---

## 11. 目录结构

```text
chokepoint-research-agent/
├── main.py                 # CLI 入口
├── src/
│   ├── agents/             # Deep Agents + 降级编排
│   ├── prompts/            # 投研 / 卡脖子 Prompt
│   ├── tools/              # 搜索、行情、A股、导出、落盘
│   ├── memory/             # 会话记忆
│   ├── schemas/            # Scorecard / 质检
│   ├── eval/               # 离线评测
│   ├── static/             # Web UI
│   └── api.py              # FastAPI
├── knowledge/              # 方法论 + YAML 地图
├── docs/                   # 英文文档
├── docs/zh/                # 中文文档（本语言包）
├── eval/golden/            # 结构评测样例
├── examples/               # 示例问题
├── reports/                # 生成研报（内容默认不入库）
├── tests/
├── README.md               # 英文主页
├── README.zh-CN.md         # 中文主页（本文件）
└── DISCLAIMER.md
```

---

## 12. 文档索引

| 文档 | 内容 |
|------|------|
| [docs/zh/methodology.md](docs/zh/methodology.md) | 卡脖子方法论 |
| [docs/zh/architecture.md](docs/zh/architecture.md) | 架构与角色契约 |
| [docs/zh/deployment.md](docs/zh/deployment.md) | 本地 / Docker / API 部署 |
| [docs/zh/edgeone.md](docs/zh/edgeone.md) | EdgeOne Makers 上线 |
| [docs/zh/cli.md](docs/zh/cli.md) | 命令行速查 |
| [docs/zh/faq.md](docs/zh/faq.md) | 常见问题 |
| [docs/zh/VERSIONS.md](docs/zh/VERSIONS.md) | 版本说明 v0.1–v0.7 |
| [DISCLAIMER.md](DISCLAIMER.md) | 免责声明（中英） |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 贡献指南 |
| [SECURITY.md](SECURITY.md) | 安全策略 |

英文原文仍在 `docs/*.md`，与中文包对照阅读。

---

## 13. 开发与测试

```bash
# 不依赖在线模型 Key 的检查
make check
# 等价于：
python scripts/smoke_check.py
pytest -q
python main.py eval
```

原则：

1. **教框架，不喊单**  
2. 密钥只放 `.env`，永不提交  
3. 新工具必须写清楚 `description`，方便模型决定何时调用  
4. 对外输出保持免责声明  

---

## 14. 部署与上线

| 路径 | 说明 |
|------|------|
| 本地 CLI | 研究者自用最快 |
| 本地 / 服务器 FastAPI | `python main.py --server`，务必加鉴权 |
| Docker Compose | 见 `docker-compose.yml` |
| EdgeOne Makers | 把 Prompt 迁到 Deep Agents 模板，见 [docs/zh/edgeone.md](docs/zh/edgeone.md) |

生产注意：

- 单次研究可能 **1–10 分钟**，反向代理超时要调大  
- 默认 CORS 偏演示；公网务必配置 `API_ACCESS_KEY` 或网关鉴权  
- 网页工具结果可能含 prompt injection，输出按不可信内容处理  

---

## 15. 版本历史

| 版本 | 主题 |
|------|------|
| v0.1–v0.7 | 多专家核心 → 模式/UI/评测/会话 |
| **v0.8–v0.10** | 运营层 + 工作台 UI + brief |
| **v0.11** | SEC EDGAR + Provider 注册表 + 引用检查 |
| **v0.12** | 异步 Jobs + Analytics |
| **v1.0–v1.20** | 成熟度火车（运营/SEC/Jobs/备份…） |
| **v2.0.0** | 真定时任务 + PDF + 多源 A 股公告 |
| **v2.1–v2.5** | 鉴权 / 图表 / 检索 / HK / SSE 行情流 |
| **v2.6–v3.0** | 缓存 / 后处理 / 技能包 / mock-eval / 插件 SDK |
| **v3.1–v4.0** | 证据账本 / 论点图谱 / 标签 / 对比 / 审计 / DOCX / 覆盖热力 |

详见：[docs/zh/RELEASE_NOTES_3.0.md](docs/zh/RELEASE_NOTES_3.0.md) · [docs/zh/ROADMAP.md](docs/zh/ROADMAP.md)

---

## 16. 常见问题

**Q：一定要 Fable 5 吗？**  
A：不必须。DeepSeek 等兼容接口即可；复杂长程任务可用更强模型。

**Q：A 股数据准吗？**  
A：`get_cn_stock_quote` 走公开接口，**尽力而为、可能延迟/字段缩放差异**，关键数字请交叉验证。

**Q：会不会重复保存研报？**  
A：v0.2+ 已改为单次落盘；CLI/API 负责持久化。

**Q：如何只测框架不烧钱？**  
A：`python main.py eval` 与 `pytest` 不需要真实模型调用。

更多：[docs/zh/faq.md](docs/zh/faq.md)

---

## 17. 贡献与许可

欢迎贡献：工具、Prompt、知识地图、文档、测试。  
见 [CONTRIBUTING.md](CONTRIBUTING.md)。

- License：**[MIT](LICENSE)**  
- 作者：BruceLanLan / BruceBlue  
- 仓库：https://github.com/BruceLanLan/chokepoint-research-agent  

---

**再次强调：本项目输出仅供研究学习，不构成投资建议。投资有风险，决策请独立判断。**
