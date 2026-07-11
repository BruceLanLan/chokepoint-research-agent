# Release notes — v3.1 → v4.0.0

Autonomous wave after v3.0: **evidence, graph, compare, tags, kill monitor, coverage, audit, DOCX, snapshot, plugin loader**.

中文 → [zh/RELEASE_NOTES_4.0.md](./zh/RELEASE_NOTES_4.0.md)

---

## Highlights

| Area | What you get |
|------|----------------|
| Evidence ledger | Structured URLs / domains / claim lines from memos |
| Thesis graph | Nodes + edges + Mermaid for theses / chokepoints / symbols |
| Compare memos | Quality rank, heading coverage, shared scorecard nodes |
| Tags & collections | Organize reports without a DMS |
| Kill monitor | Flags active theses missing kill criteria (process risk) |
| Coverage heat | Watchlist density vs theses & reports |
| Audit trail | Append-only provenance for workstation actions |
| DOCX | Stdlib OOXML export (no extra deps) |
| Snapshot | Zip of data + recent reports — **never** `.env` |
| Plugins | Auto-list/load modules under `./plugins/` |

---

## CLI quick ref

```bash
python main.py evidence --summary
python main.py evidence --report some_memo.md
python main.py graph --mermaid
python main.py compare-memos a.md b.md
python main.py tag some.md --tags cpo,optics
python main.py collections --create "Q3 optics"
python main.py kill-monitor
python main.py coverage
python main.py audit --summary
python main.py snapshot
python main.py docx some_memo.md
python main.py plugins
```

## API

- `GET /evidence`, `POST /evidence/extract`
- `GET /graph?mermaid=true`
- `POST /compare-memos` `{"names":["a.md","b.md"]}`
- `GET|POST /tags`, `GET|POST /collections`
- `GET /kill-monitor`, `GET /coverage`, `GET /audit`
- `POST /snapshot`, `POST /export/docx`, `GET /plugins`

UI: new **Ops** tab.

---

## Upgrade

```bash
git pull
pip install -r requirements.txt
python main.py doctor
python main.py mock-eval
python main.py graph --mermaid
```

**Research only — not investment advice.**
