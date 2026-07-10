# 架构说明（中文）

## 总览

```text
                    ┌─────────────────────────┐
  用户问题 ────────►│  投研总监 Lead Analyst   │
                    │  规划 + 综合写报         │
                    └───────────┬─────────────┘
                                │ 并行委派
     ┌──────────────┬───────────┼───────────┬──────────────┐
     ▼              ▼           ▼           ▼              ▼
 chokepoint    fundamental    news       macro         risk
   制图           基本面       催化        宏观          审查
     │              │           │           │              │
     └──────────────┴─────┬─────┴───────────┴──────────────┘
                          ▼
                    Markdown 研报
                          │
                          ▼
               reports/（md / json / html）
```

Mermaid 版见英文文档 [`../architecture.md`](../architecture.md)。

---

## 设计原则

1. **框架优先于代码**：教「如何找物理开关」，不硬编码荐股清单。  
2. **事实尽量走工具**：价格、新闻、网页由工具获取，模型禁止瞎编关键数字。  
3. **独立风险上下文**：风险审查员像「全新上下文验证子代理」，专挑刺。  
4. **双运行时**：优先 Deep Agents；失败则降级内置并行编排。  

---

## 运行路径

| 路径 | 何时 | 入口 |
|------|------|------|
| Deep Agents | Python≥3.11 且 `deepagents` 可用 | `src/agents/research_agent.py` |
| Fallback | 导入/API 不兼容时 | `src/agents/fallback_orchestrator.py` |
| CLI | 本地研究 | `main.py` |
| HTTP / UI | 产品化 | `src/api.py` + `src/static/` |

---

## 专家契约

| 角色 | 必须回答 |
|------|----------|
| chokepoint-mapper | 系统树 + Scorecard + 路径依赖 |
| fundamental-analyst | 商业模式、财务、流动性、覆盖真空 |
| news-catalyst-analyst | 时间线、催化、叙事差 |
| macro-industry-analyst | 政策/地缘/Capex 如何传到节点 |
| risk-reviewer | 最强空头论据 + kill criteria |

### 模式对专家的裁剪

| 模式 | 启用专家 |
|------|----------|
| `full` | 全部 |
| `chokepoint_fast` | mapper + risk |
| `risk_only` | risk |
| `compare` | mapper + fundamental + risk |

---

## 工具层

| 工具 | 作用 |
|------|------|
| `web_search` | Tavily 搜索（topic: general/news/finance） |
| `fetch_url` | 抓取网页转 Markdown |
| `get_market_snapshot` | Yahoo 行情（美股等） |
| `get_cn_stock_quote` | A 股 / 港股尽力报价 |
| `search_cn_company_news` | 中文资讯辅助 |
| `list/load_knowledge_map` | 本地 YAML 供应链草图 |
| `save_research_report` / 导出 | 落盘 md/json/html |

---

## 研报合同（完整模式）

1. 一页纸结论  
2. 系统解构 / 物理开关  
3. 公司或主题画像  
4. 基本面与估值  
5. 催化与信息流  
6. 行业与政策  
7. 红蓝对抗 + kill criteria  
8. 来源  

质检：`validate_report_structure`（启发式，非事实正确性证明）。

---

## 会话与成本

- **Session**：`data/sessions/*.json`（相对 `REPORTS_DIR` 父目录）  
- **CostTracker**：粗算 token / 重试次数，**不是**云厂商账单  

---

## 相关代码

| 路径 | 职责 |
|------|------|
| `src/prompts/investment.py` | Prompt 与方法论块 |
| `src/agents/research_agent.py` | 组装 Deep Agent |
| `src/agents/fallback_orchestrator.py` | 降级流水线 |
| `src/schemas/scorecard.py` | Scorecard 与质检 |
| `src/memory/sessions.py` | 多轮记忆 |
| `src/api.py` | HTTP API |
