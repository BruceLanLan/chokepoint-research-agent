# Remote plugin install — design note (not implemented)

Status: **design only** (v6.2+). Local marketplace remains the supported path.

## Goals

- Allow third-party data providers without forking core
- Keep secrets out of the agent process by default
- Fail closed: unsigned / unknown sources never auto-load

## Non-goals

- App-store style remote code execution without review
- Guaranteed market data quality
- Investment advice plugins

## Proposed flow

1. Operator places a **manifest URL** (HTTPS only) pointing to JSON:
   ```json
   {
     "id": "vendor.x",
     "version": "1.0.0",
     "sha256": "...",
     "entry": "provider.py",
     "permissions": ["filings.read", "market.quote"]
   }
   ```
2. Agent downloads to `plugins/cache/<id>/` after hash verify
3. Load via existing `src.plugins.loader` in **sandbox** (no network for untrusted code except declared hosts)
4. Register into `get_registry()` only if permissions match config allowlist

## Safety controls

| Control | Rule |
|---------|------|
| Hash pin | Required `sha256` |
| Allowlist | `PLUGIN_ALLOW_HOSTS` / signed publisher keys |
| Network | Default deny; opt-in hosts |
| Secrets | Passed as env names only, never logged |
| Audit | Every install/load → `audit.jsonl` |

## Interim (today)

```bash
python main.py marketplace
# drop .py into ./plugins/ and:
python main.py plugins --load example_provider
```

**Research only — not investment advice.**
