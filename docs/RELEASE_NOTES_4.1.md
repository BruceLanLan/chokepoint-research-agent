# Release notes — v4.1.0

Citation network, report lineage, offline plans, provider health, coverage SVG, WebSocket quotes.

中文 → [zh/RELEASE_NOTES_4.1.md](./zh/RELEASE_NOTES_4.1.md)

## CLI

```bash
python main.py citations --mermaid
python main.py lineage --chain "CPO Q3" --reports a.md,b.md
python main.py lineage --parent a.md --child b.md
python main.py plan "B200 CPO racks" --skill semiconductor
python main.py provider-health
# python main.py provider-health --live   # network probes
```

## API / realtime

- `GET /citations`, `GET|POST /lineage`, `POST /plan`
- `GET /providers/health?live=false`
- `GET /charts/coverage` (SVG)
- `WS /ws/quotes` — send `{"symbol":"AAPL","interval":5}`

**Research only — not investment advice.**
