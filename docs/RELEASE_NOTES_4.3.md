# Release notes — v4.3.0

SQLite FTS memo index + local research queue (plan work offline before burning tokens).

中文 → [zh/RELEASE_NOTES_4.3.md](./zh/RELEASE_NOTES_4.3.md)

```bash
python main.py index-memos --q CPO
python main.py queue --from-map cpo_ai_interconnect
python main.py queue --from-watchlist --limit 5
python main.py queue --summary
python main.py queue --add "红蓝对抗：ELS 是否可替代" --mode risk_only
```

API: `POST /index/memos`, `GET /index/search?q=`, `GET|POST /queue`

**Research only — not investment advice.**
