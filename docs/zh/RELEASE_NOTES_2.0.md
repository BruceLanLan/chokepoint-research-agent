# 发布说明 — v2.0.0

## 主题

**成熟投研 Agent v2**：真·系统定时任务、精美 PDF 研报、多源 A 股公告。

English → [../RELEASE_NOTES_2.0.md](../RELEASE_NOTES_2.0.md)

---

## 1. 真·定时任务

| 命令 | 作用 |
|------|------|
| `schedule install --hour 9 --minute 0` | macOS **launchd** 每日任务，并打印 **cron** 行 |
| `schedule status` | 查看配置 / launchctl |
| `schedule uninstall` | 卸载 |
| `schedule run` | 立刻跑一轮（会调模型） |
| `scripts/run_scheduled_brief.py` | cron/launchd 入口 |

默认任务：对 **watchlist** 做 `chokepoint_fast` 简报。  
日志：`data/logs/`。

---

## 2. 更漂亮的 PDF

- `fpdf2` + 系统中文字体（苹方 / Noto / 微软雅黑等）
- `python main.py pdf --file reports/xxx.md`
- 导出套件自动附带 PDF
- `POST /export/pdf`
- 页眉免责声明 + 标题层级 + 页脚

---

## 3. 更多 A 股公告源

`cn_announcements` 多源聚合：

1. 东方财富个股公告（6 位代码）
2. 东财搜索 / CMS
3. 东财资讯栏目
4. 新浪财经滚动

工具：`cn_search_announcements`、`cn_company_suggest`

---

## 升级

```bash
git pull
pip install -r requirements.txt
python main.py doctor
python main.py schedule install --hour 9 --minute 0
```

**仅供研究学习，不构成投资建议。**
