# unit_econ (v5.23.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **unit econ**.

## CLI

```bash
python main.py pro unit_econ
python main.py pro unit_econ --action analyze --text "..."
python main.py pro unit_econ --action add --title "..." --text "..." --symbol NVDA
python main.py pro unit_econ --action list --symbol NVDA
```

## API

`POST /pro/unit_econ` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/unit_econ.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
