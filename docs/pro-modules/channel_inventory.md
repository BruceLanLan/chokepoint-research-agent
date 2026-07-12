# channel_inventory (v5.27.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **channel inventory**.

## CLI

```bash
python main.py pro channel_inventory
python main.py pro channel_inventory --action analyze --text "..."
python main.py pro channel_inventory --action add --title "..." --text "..." --symbol NVDA
python main.py pro channel_inventory --action list --symbol NVDA
```

## API

`POST /pro/channel_inventory` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/channel_inventory.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
