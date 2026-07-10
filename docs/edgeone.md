# EdgeOne Makers packaging notes

Goal: host the **Chokepoint** multi-agent research product on
[EdgeOne Makers](https://console.cloud.tencent.com/edgeone/makers).

## Recommended path

1. Create project from template **Deep Agents Starter**
   (`deepagents-research-starter-node`).
2. Port prompts from `src/prompts/investment.py`:
   - Lead → 投研总监 (+ mode suffixes)
   - Subagents → chokepoint / fundamental / news / macro / risk
3. Map tools:
   - Platform `web_search` (WSA) ↔ our `web_search`
   - Keep CN quote tools as Cloud Function if outbound HTTP allowed
4. Env:
   - `AI_GATEWAY_API_KEY`
   - `AI_GATEWAY_BASE_URL=https://ai-gateway.edgeone.link/v1`
   - Optional `WSA_API_KEY`
5. UI: either Makers default chat UI or embed this repo’s `/` static page via static hosting.

## Prompt pack (copy/paste)

See also:

- `src/prompts/investment.py` — source of truth
- `knowledge/chokepoint_theory_bruceblue.md` — methodology DNA
- `knowledge/maps/*.yaml` — educational supply-chain sketches

## Modes to expose in product UI

| Mode | Product label |
|------|----------------|
| full | 深度投研 |
| chokepoint_fast | 卡脖子快扫 |
| risk_only | 红蓝对抗 |
| compare | 多标的对照 |

## Compliance banner (required)

> 本服务仅供研究学习，不构成投资建议。Research only — not investment advice.

## Skills

```bash
npx skills add TencentEdgeOne/edgeone-makers-tools
```

Ask the coding agent: *“Port chokepoint-research-agent prompts into Deep Agents starter and deploy.”*
