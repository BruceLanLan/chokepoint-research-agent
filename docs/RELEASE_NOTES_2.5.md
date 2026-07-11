# Release notes — v2.1 → v2.5.0 (roadmap completion)

Completes remaining roadmap items after v2.0: **auth plugins**, **chart widgets**, **local memo search**, **more exchange/news providers**, **quote SSE stream**.

中文 → [zh/RELEASE_NOTES_2.5.md](./zh/RELEASE_NOTES_2.5.md)

---

## v2.1 — Auth plugins

| Plugin | Config |
|--------|--------|
| `open` | default when no secrets set |
| `api_key` | `API_ACCESS_KEY` / `X-API-Key` |
| `bearer` | `API_BEARER_TOKEN` / `Authorization: Bearer …` |
| `oidc` | `OIDC_ISSUER` + `OIDC_AUDIENCE` (+ optional `OIDC_JWKS_URL`); needs `PyJWT` |

Code: `src/auth/`. API: `GET /auth/plugins`.

## v2.2 — Chart widgets

- SVG **scorecard bar chart** from memo tables
- SVG **price series** via Yahoo history
- Tools: `render_scorecard_chart`, `render_price_chart`
- HTML export embeds scorecard chart when parseable
- CLI: `python main.py chart scorecard --report …` / `chart price --symbol NVDA`
- API: `GET /charts/scorecard?name=…`

## v2.3 — Local memo search

- Lightweight **TF-IDF** over `reports/*.md` (no vector DB required)
- CLI: `python main.py search-memos "CPO kill criteria"`
- API: `GET /search/memos?q=…`
- UI tab: **Search 检索**

## v2.4 — More exchanges / streams

- Provider **`hkex_news`** (HK-oriented headlines via public EM feeds)
- Multi-source CN announcements retained/expanded
- **Quote SSE stream**: `GET /quotes/stream?symbol=AAPL&interval=5` (polling, not a full MD terminal)

## v2.5 — Polish

- Bilingual README + roadmap updates
- Tests for auth / search / charts / providers
- Version **2.5.0**

---

## Upgrade

```bash
git pull
pip install -r requirements.txt
# optional OIDC
# pip install PyJWT cryptography
python main.py doctor
python main.py search-memos "chokepoint"
python main.py --server
```

**Research only — not investment advice.**
