# Plugin SDK (providers)

Third-party data sources can register into the agent without forking core code.

## Interface

```python
class MyFilingsProvider:
    name = "my_vendor"

    def search_company(self, query: str) -> list[dict]:
        ...

    def recent_filings(self, cik: str, form: str | None = None, limit: int = 10) -> list[dict]:
        ...
```

Market quotes:

```python
class MyMarketProvider:
    name = "my_market"
    def quote(self, symbol: str) -> dict:
        ...
```

## Register

```python
from src.providers.base import get_registry
from plugins.example_provider import ExampleStaticProvider

reg = get_registry()
reg.register_filings(ExampleStaticProvider())
print(reg.list_providers())
```

## Auth plugins

See `src/auth/plugins.py`:

- `API_ACCESS_KEY`
- `API_BEARER_TOKEN`
- `OIDC_ISSUER` + `OIDC_AUDIENCE` (+ optional JWKS)

## Skill packs

YAML under `skills/packs/*.yaml` — load with:

```bash
python main.py skills
python main.py research "..." --skill semiconductor
```

中文简版见 [zh/PLUGIN_SDK.md](./zh/PLUGIN_SDK.md)。
