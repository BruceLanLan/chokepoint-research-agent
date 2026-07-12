# peer_set (v5.11.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **peer set**.

## CLI

```bash
python main.py pro peer_set
python main.py pro peer_set --action analyze --text "..."
python main.py pro peer_set --action add --title "..." --text "..." --symbol NVDA
python main.py pro peer_set --action list --symbol NVDA
```

## API

`POST /pro/peer_set` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/peer_set.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
