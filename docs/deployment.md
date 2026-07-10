# Deployment

## Local CLI

```bash
cp .env.example .env
# fill MODEL + TAVILY keys
python main.py "以 B200 集群为原点，拆解 CPO 卡脖子节点"
```

## Local API

```bash
python main.py --server
# docs: http://127.0.0.1:8000/docs
```

Endpoints:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness |
| POST | `/research` | Sync research → full report |
| POST | `/research/stream` | SSE progress + final |

Example:

```bash
curl -s http://127.0.0.1:8000/research \
  -H 'Content-Type: application/json' \
  -d '{"question":"CPO supply chain chokepoints","save_report":true}'
```

### Production notes

- Put the API behind HTTPS + auth (API key / SSO). Default CORS is open for demos only.
- Research jobs can take **1–10 minutes**; raise reverse-proxy timeouts.
- Store secrets in a vault / platform env, not in git.
- Persist `reports/` volume if you need audit trails.

## Model backends

### Anthropic (e.g. Claude Fable 5)

```env
MODEL_PROVIDER=anthropic
MODEL_NAME=claude-fable-5
ANTHROPIC_API_KEY=sk-ant-...
TAVILY_API_KEY=tvly-...
```

### OpenAI-compatible (DeepSeek, OpenAI, vLLM, …)

```env
MODEL_PROVIDER=openai_compatible
MODEL_NAME=deepseek-chat
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.deepseek.com/v1
TAVILY_API_KEY=tvly-...
```

### EdgeOne Makers AI Gateway

```env
MODEL_PROVIDER=openai_compatible
MODEL_NAME=@makers/deepseek-v4-flash
AI_GATEWAY_API_KEY=sk-...
AI_GATEWAY_BASE_URL=https://ai-gateway.edgeone.link/v1
TAVILY_API_KEY=tvly-...
```

Console: https://console.cloud.tencent.com/edgeone/makers

## EdgeOne Makers (product hosting)

Goal: turn the research agent into a shareable web product.

1. Create a project from **Deep Agents Starter**  
   (`deepagents-research-starter-node`)
2. Port system prompts from `src/prompts/investment.py`
3. Map specialists to Makers subagents
4. Configure gateway + search keys
5. `git push` → automatic deploy

Optional skills:

```bash
npx skills add TencentEdgeOne/edgeone-makers-tools
```

## Docker (optional sketch)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
CMD ["python", "main.py", "--server"]
```

Build/run only after `.env` or `-e` secrets are provided.
