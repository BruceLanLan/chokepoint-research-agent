# Release notes — v4.4.0

Queue worker (mock/live), portable export packs, auto-tag, thesis process health, sanitized config, Notion-friendly export, plugin catalog, bulk watchlist, quality board.

中文 → [zh/RELEASE_NOTES_4.4.md](./zh/RELEASE_NOTES_4.4.md)

## Workflow

```bash
# Plan work without burning tokens
python main.py queue --from-map cpo_ai_interconnect
python main.py queue --add "红蓝对抗 ELS" --mode risk_only --skill semiconductor

# Process with offline mock (safe)
python main.py queue --run 2

# Real LLM (costs tokens) — only when ready
# python main.py queue --run 1 --live

python main.py export-pack some_memo.md
python main.py auto-tag some_memo.md
python main.py thesis-health
python main.py quality-board
python main.py config-show
python main.py notion-export some_memo.md
python main.py plugin-catalog
python main.py watch bulk NVDA,AVGO,COHR --priority high

# Optional cron-safe queue tick (mock only)
python scripts/run_scheduled_queue.py 1
```

## API

- `POST /queue/run` `{"n":1,"live":false}`
- `POST /export-pack` `{"report":"x.md"}`
- `POST /auto-tag`, `GET /thesis-health`, `GET /config`
- `GET /notion-export/{name}`, `GET /plugin-catalog`
- `POST /watchlist/bulk`, `GET /quality-board`

**Research only — not investment advice.**
