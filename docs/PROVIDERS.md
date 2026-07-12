# Data providers — capabilities & limits

Best-effort public / educational data sources. **Not** a professional market-data terminal.

**Research only — not investment advice.**

## Registry

| Provider | Kind | Notes |
|----------|------|-------|
| `sec_edgar` | filings | US public company tickers + recent filings (needs HTTPS + User-Agent) |
| `cn_announcements` | filings | Multi-source A-share announcements (Eastmoney / Sina style) |
| `hkex_news` | filings | HK-oriented news/filings best-effort |
| `yahoo_market` | market | Quote snapshots; delays/gaps expected |
| `./plugins/*` | optional | Local third-party; remote install is hash-pinned + allowlisted |

List at runtime: `python main.py providers` · `python main.py provider-health`

## Failure modes

| Symptom | Meaning |
|---------|---------|
| Empty / error JSON | Network, rate limit, or site layout change |
| `stub: true` in quote cache | Offline/fallback row — **not** a real last price |
| Cache hit | SEC tickers etc. may be disk-cached (TTL) |

## Safety

- Never treat provider output as investment advice  
- Label stubs in UI/CLI when present  
- Live probes: `provider-health --live` (network)  

## Extension

See [PLUGIN_SDK.md](./PLUGIN_SDK.md) and [REMOTE_PLUGIN_DESIGN.md](./REMOTE_PLUGIN_DESIGN.md).
