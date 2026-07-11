# 发布说明 — v2.1 → v2.5.0（路线图收官）

补齐 v2.0 之后路线图剩余项：**鉴权插件、图表组件、本地研报检索、更多市场源、行情 SSE**。

English → [../RELEASE_NOTES_2.5.md](../RELEASE_NOTES_2.5.md)

---

## v2.1 鉴权插件

| 插件 | 配置 |
|------|------|
| `open` | 未配置密钥时默认（仅本地演示） |
| `api_key` | `API_ACCESS_KEY` |
| `bearer` | `API_BEARER_TOKEN` |
| `oidc` | `OIDC_ISSUER` + `OIDC_AUDIENCE`（可选 JWKS；需 PyJWT） |

## v2.2 图表

- Scorecard 条形 SVG、价格折线 SVG
- CLI `chart`、HTML 导出嵌入、API `/charts/scorecard`

## v2.3 本地研报检索

- TF-IDF 检索历史备忘录
- `search-memos` / `/search/memos` / UI「Search」

## v2.4 更多市场源 + 行情流

- `hkex_news` Provider
- `/quotes/stream` SSE 轮询行情（尽力而为）

## v2.5 打磨

- 双语文档、测试、版本 **2.5.0**

---

**仅供研究学习，不构成投资建议。**
