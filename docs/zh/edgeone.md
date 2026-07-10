# EdgeOne Makers 上线指南（中文）

目标：把「卡脖子投研 Agent」做成可分享的在线服务。  
平台：[腾讯云 EdgeOne Makers](https://console.cloud.tencent.com/edgeone/makers)

---

## 推荐路径

1. 用模板 **Deep Agents Starter**（`deepagents-research-starter-node`）创建项目。  
2. 把本仓库 Prompt 迁过去：  
   - 来源：`src/prompts/investment.py`  
   - Lead = 投研总监  
   - Subagents = 制图 / 基本面 / 新闻 / 宏观 / 风险  
3. 工具映射：  
   - 平台联网搜索 ↔ `web_search`  
   - A 股报价等可作为云函数 HTTP 工具挂载  
4. 环境变量：  
   - `AI_GATEWAY_API_KEY`  
   - `AI_GATEWAY_BASE_URL=https://ai-gateway.edgeone.link/v1`  
   - 可选 `WSA_API_KEY`  
5. 前端：用 Makers 默认对话 UI，或托管本仓库静态页 `src/static/index.html`。

---

## 产品侧建议暴露的模式

| 模式 | 产品文案 |
|------|----------|
| full | 深度投研 |
| chokepoint_fast | 卡脖子快扫 |
| risk_only | 红蓝对抗 |
| compare | 多标的对照 |

---

## 必挂合规文案

> 本服务仅供研究学习，不构成投资建议。  
> Research only — not investment advice.

---

## 可复制素材

| 素材 | 路径 |
|------|------|
| Prompt 真源 | `src/prompts/investment.py` |
| 方法论 | `knowledge/chokepoint_theory_bruceblue.md` |
| 供应链草图 | `knowledge/maps/*.yaml` |
| 架构 | `docs/zh/architecture.md` |

---

## Skills 辅助开发

```bash
npx skills add TencentEdgeOne/edgeone-makers-tools
```

对编码 Agent 说：

> 把 chokepoint-research-agent 的投研多 Agent Prompt 接到 EdgeOne Deep Agents 模板上，并配置网关后部署。

---

## 注意

- 长任务超时与计费要按 Makers 配额规划。  
- 公网分享务必限流 + 鉴权。  
- 不要在前端写死模型 Key。  
