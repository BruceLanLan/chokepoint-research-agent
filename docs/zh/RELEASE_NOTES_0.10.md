# 发布说明 — v0.8 → v0.10（专业工作台迭代）

## 摘要

向**专业投研工作台**靠拢：覆盖名单、论点台账、研究模板、研报目录、多面板 UI、自选简报；坚持**研究用途 / 非投资建议**边界。

English: [../RELEASE_NOTES_0.10.md](../RELEASE_NOTES_0.10.md)

## v0.8 运营层

- `doctor` 环境体检
- 覆盖名单 `watch`
- 论点台账 `thesis`
- 研报目录检索
- 内置研究模板 `templates/research/`

## v0.9 工作台

- 多面板 Web UI
- REST：watchlist / theses / templates / doctor
- 模板渲染后一键填入研究页

## v0.10 自动化与打磨

- `brief` 自选组合批处理简报
- 打印友好 HTML（浏览器导出 PDF）
- 运营层单测
- 中英文路线图

## 升级

```bash
git pull
pip install -r requirements.txt
python main.py doctor
python main.py --server
```

本地数据在 `data/`（默认不入库）。
