# 发布说明 — v2.6 → v3.0.0

自主优化波次：**缓存、研报后处理、垂直技能包、指标、插件 SDK、CI 加固**。

English → [../RELEASE_NOTES_3.0.md](../RELEASE_NOTES_3.0.md)

---

## 版本摘要

| 版本 | 内容 |
|------|------|
| **2.6** | HTTP 磁盘缓存（SEC tickers 等） |
| **2.7** | 研报后处理：图表/质检/metrics/`--min-quality` |
| **2.8** | 技能包 semiconductor / robotics / energy_power |
| **2.9** | `mock-eval` 离线流水线 + CI |
| **3.0.0** | 插件文档与示例、版本收口 |

---

## 升级

```bash
git pull
pip install -r requirements.txt
python main.py mock-eval
python main.py skills
python main.py research "..." --skill semiconductor
```

**仅供研究学习，不构成投资建议。**
