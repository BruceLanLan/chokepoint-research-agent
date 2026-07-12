# tech_roadmap (v5.19.0)

Professional research-ops module in the v5.2–v5.51 maturity train.

## Purpose

Offline structured note-taking / analysis helper for **tech roadmap**.

## CLI

```bash
python main.py pro tech_roadmap
python main.py pro tech_roadmap --action analyze --text "..."
python main.py pro tech_roadmap --action add --title "..." --text "..." --symbol NVDA
python main.py pro tech_roadmap --action list --symbol NVDA
```

## API

`POST /pro/tech_roadmap` with JSON body `{"action":"analyze","text":"..."}`

## Rules

- Research process only — **not investment advice**
- Prefer primary sources and dated numbers
- Always write kill / falsifiers for active theses

## Storage

Local JSONL under `data/pro/tech_roadmap.jsonl` (gitignored via data/)

---
Generated as part of the 50-version maturity train.
