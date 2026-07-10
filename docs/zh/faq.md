# 常见问题 FAQ（中文）

## 安装与环境

### 为什么必须 Python 3.11+？

依赖 `deepagents` 声明 `Requires-Python >= 3.11`。3.9/3.10 无法安装该包。  
可用降级编排器逻辑，但仍建议 3.11+ 以获得完整能力。

### `pip install deepagents` 失败？

检查：

```bash
python --version   # 需 3.11+
pip install -U pip
pip install -r requirements.txt
```

### SOCKS 代理报错？

已依赖 `httpx[socks]`。若仍失败：

```bash
pip install 'httpx[socks]' socksio
```

---

## 配置与密钥

### 最少要配哪些变量？

- 模型：`MODEL_PROVIDER` + 对应 API Key（及 Base URL）  
- 搜索：`TAVILY_API_KEY`  

### 没有 Tavily 能跑吗？

能初始化，但专家几乎无法检索事实，研报质量会崩。强烈建议配置。

### EdgeOne 和 DeepSeek 可以混用吗？

可以。本质是 OpenAI 兼容协议：改 `BASE_URL` + `API_KEY` + `MODEL_NAME` 即可。

---

## 使用

### 一次研究会跑多久？

通常 **1–10 分钟**，取决于模式、模型速度与搜索次数。  
`chokepoint_fast` / `risk_only` 更快。

### `compare` 模式怎么提问？

明确写出 2–4 个名称，例如：

> 对照公司 A 与公司 B 在硅光链路中谁更接近 chokepoint 本体，输出对照表。

### A 股代码怎么写？

- `600519` 或 `600519.SS`  
- `000001` 或 `000001.SZ`  
- 港股：`0700.HK`  

工具会尽量规范化；若失败可改用 `get_market_snapshot`。

### 研报保存在哪？

默认 `./reports/`。可用 `REPORTS_DIR` 修改。  
`list-reports` 或 Web UI 右侧可浏览。

### quality_score 是什么？

启发式结构分（是否有结论/风险/来源/URL/篇幅等），**不是**投资胜率，也不是事实正确性评分。

---

## 安全与合规

### 能当自动交易信号吗？

**不能。** 仅供研究学习。见 `DISCLAIMER.md`。

### 公网部署要注意什么？

1. 设置 `API_ACCESS_KEY`  
2. HTTPS + 反向代理超时  
3. 限流  
4. 不要提交 `.env`  
5. 对工具返回内容保持不信任  

### 网页内容会污染模型吗？

可能（prompt injection）。本项目会截断页面，但仍建议人工审阅关键结论。

---

## 开发

### 如何只跑测试不烧钱？

```bash
make check
# 或
pytest -q && python main.py eval
```

### 如何加新的供应链地图？

在 `knowledge/maps/` 新增 `*.yaml`，保持「教育草图、非荐股」语气。  
Agent 可通过 `list_knowledge_maps` / `load_knowledge_map` 读取。

### 如何加新工具？

1. 在 `src/tools/` 写 `@tool`  
2. 加入 `researcher_tools()` / `all_tools()`  
3. 写清 docstring，补测试  

---

## 故障排查

| 现象 | 可能原因 | 处理 |
|------|----------|------|
| Agent 初始化失败 | 缺模型 Key | 检查 `.env` |
| 搜索报错 | 缺 Tavily | 配置 `TAVILY_API_KEY` |
| 一直很慢 | full 模式 + 强模型 | 改 `chokepoint_fast` |
| UI 调不通 API | 设了 API Key 但前端没填 | 在 UI 填 X-API-Key |
| A 股报价空 | 接口字段/代码格式 | 换后缀或改用 Yahoo 工具 |

仍有问题：在 GitHub 开 Issue  
https://github.com/BruceLanLan/chokepoint-research-agent/issues
