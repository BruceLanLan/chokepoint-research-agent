# 部署指南（中文）

## 本地 CLI

```bash
cp .env.example .env
# 填写模型 Key + TAVILY_API_KEY

python main.py "你的研究问题"
python main.py "CPO 卡点" --mode chokepoint_fast
```

---

## 本地 API + Web UI

```bash
python main.py --server
# 或
make server
```

| 地址 | 用途 |
|------|------|
| http://127.0.0.1:8000/ | Web UI |
| http://127.0.0.1:8000/docs | OpenAPI |
| http://127.0.0.1:8000/health | 健康检查 |

### 主要接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 存活与配置告警 |
| POST | `/sessions` | 新建会话 |
| GET | `/reports` | 列表 |
| GET | `/reports/{name}` | 读取 |
| POST | `/research` | 同步研究 |
| POST | `/research/stream` | SSE 流式 |

### 请求示例

```bash
curl -s http://127.0.0.1:8000/research \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "稀土永磁供应链卡点",
    "mode": "full",
    "save_report": true,
    "export": true,
    "bilingual": false
  }'
```

带鉴权：

```bash
curl -s http://127.0.0.1:8000/research \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: your-secret' \
  -d '{"question":"test","mode":"risk_only"}'
```

在 `.env` 中设置：

```env
API_ACCESS_KEY=your-secret
```

---

## Docker

```bash
cp .env.example .env
docker compose up --build
```

- 端口：`8000`  
- 研报目录挂载：`./reports`  

镜像定义见仓库根目录 `Dockerfile`。

---

## 模型后端

### Anthropic

```env
MODEL_PROVIDER=anthropic
MODEL_NAME=claude-fable-5
ANTHROPIC_API_KEY=sk-ant-...
TAVILY_API_KEY=tvly-...
```

### OpenAI 兼容（DeepSeek 等）

```env
MODEL_PROVIDER=openai_compatible
MODEL_NAME=deepseek-chat
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.deepseek.com/v1
TAVILY_API_KEY=tvly-...
```

### EdgeOne AI Gateway

```env
MODEL_PROVIDER=openai_compatible
MODEL_NAME=@makers/deepseek-v4-flash
AI_GATEWAY_API_KEY=sk-...
AI_GATEWAY_BASE_URL=https://ai-gateway.edgeone.link/v1
TAVILY_API_KEY=tvly-...
```

---

## 生产建议

1. **超时**：单次研究 1–10 分钟，Nginx/Caddy `proxy_read_timeout` 建议 ≥ 600s。  
2. **鉴权**：公网必须 `API_ACCESS_KEY` 或网关鉴权；勿裸奔 CORS `*`。  
3. **密钥**：用平台密钥管理，不要把 `.env` 打进镜像层。  
4. **存储**：持久化 `reports/` 与（如需）`data/sessions/`。  
5. **合规页脚**：UI/API 响应保持「非投资建议」声明。  
6. **注入风险**：网页抓取内容不可信，避免把原始 HTML 直接当系统指令。  

---

## EdgeOne Makers

见：[edgeone.md](./edgeone.md)

---

## 健康检查

```bash
curl -s http://127.0.0.1:8000/health | jq
```

`config_warnings` 非空时，通常是缺模型 Key 或 Tavily Key。
