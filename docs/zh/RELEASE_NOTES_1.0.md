# 发布说明 — v0.11 → v1.0.0-rc1

## 定位

迈向**成熟投研 Agent**：可插拔数据源、美股 SEC 文件工具、异步任务、工作台统计——仍坚持**研究用途，非投资建议**。

English → [../RELEASE_NOTES_1.0.md](../RELEASE_NOTES_1.0.md)

---

## v0.11 数据纵深

- Provider 注册表（行情 / 监管文件插件位）
- SEC EDGAR：`sec_search_company` / `sec_recent_filings`
- `validate_citations` 引用启发式检查
- 接入 Agent 工具与 full 模式提示

## v0.12 运营成熟度

- 异步任务：`/jobs` + CLI `job`
- 工作台统计：`/analytics` + CLI `analytics`
- UI：Analytics / Jobs 面板
- `GET /providers`

## v1.0.0-rc1 硬化

- 版本对齐、双语 README/路线图
- 测试扩展
- 通向正式 1.0 的说明（鉴权插件、更多交易所文件源）

---

## 升级

```bash
git pull
pip install -r requirements.txt
python main.py doctor
python main.py providers
python main.py --server
```

SEC 工具需要能访问 `sec.gov` / `data.sec.gov`。
