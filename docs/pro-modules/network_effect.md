# network_effect (v5.49.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **network effect**.

## CLI

```bash
python main.py pro network_effect
python main.py pro network_effect --action analyze --text "..."
python main.py pro network_effect --action add --title "..." --text "..." --symbol NVDA
python main.py pro network_effect --action list --symbol NVDA
```

## API

`POST /pro/network_effect` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/network_effect.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
