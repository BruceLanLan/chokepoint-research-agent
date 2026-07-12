# scenario_tree (v5.9.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **scenario tree**.

## CLI

```bash
python main.py pro scenario_tree
python main.py pro scenario_tree --action analyze --text "..."
python main.py pro scenario_tree --action add --title "..." --text "..." --symbol NVDA
python main.py pro scenario_tree --action list --symbol NVDA
```

## API

`POST /pro/scenario_tree` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/scenario_tree.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
