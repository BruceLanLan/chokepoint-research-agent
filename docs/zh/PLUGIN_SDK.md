# 插件 SDK（数据源）

第三方数据源可注册进 Agent，无需改核心代码。

## 接口

实现 `search_company` / `recent_filings`（文件源）或 `quote`（行情源），设置 `name` 字符串。

## 注册

```python
from src.providers.base import get_registry
from plugins.example_provider import ExampleStaticProvider

get_registry().register_filings(ExampleStaticProvider())
```

## 鉴权插件

见 `src/auth/plugins.py` 与 `.env.example` 中 `API_*` / `OIDC_*`。

## 技能包

`skills/packs/*.yaml`，CLI：

```bash
python main.py skills
python main.py research "..." --skill semiconductor
```

## v4 自动发现

将 `.py` 放入项目 `./plugins/`：

```bash
python main.py plugins
python main.py plugins --load example_provider
```

完整说明见 [../PLUGIN_SDK.md](../PLUGIN_SDK.md)。
