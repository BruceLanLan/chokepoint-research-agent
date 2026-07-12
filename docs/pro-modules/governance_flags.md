# governance_flags (v5.39.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **governance flags**.

## CLI

```bash
python main.py pro governance_flags
python main.py pro governance_flags --action analyze --text "..."
python main.py pro governance_flags --action add --title "..." --text "..." --symbol NVDA
python main.py pro governance_flags --action list --symbol NVDA
```

## API

`POST /pro/governance_flags` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/governance_flags.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
