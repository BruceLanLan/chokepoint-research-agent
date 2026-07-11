# Local extension marketplace

There is **no remote package install** yet. The “marketplace” is a **local discovery index**.

```bash
python main.py marketplace
python main.py marketplace --q cpo
python main.py plugin-catalog
```

API: `GET /marketplace`, `GET /marketplace?q=cpo`

## What is listed

| Kind | Location |
|------|----------|
| Plugins | `./plugins/*.py` |
| Skill packs | `skills/packs/*.yaml` |
| Templates | `templates/research/*.yaml` |
| Knowledge maps | `knowledge/maps/*.yaml` |

## Adding a third-party plugin

1. Implement `search_company` / `recent_filings` or `quote` (see [PLUGIN_SDK.md](./PLUGIN_SDK.md))
2. Copy into `./plugins/my_vendor.py`
3. `python main.py plugins --load my_vendor` or register via `get_registry()`

中文：本地索引，无远程安装；`python main.py marketplace`。

**Research only — not investment advice.**
