# 发布说明 — v4.4.0

队列 worker（mock / live）、导出包、自动标签、论点过程健康、脱敏配置、Notion 友好导出、插件目录、批量观察名单、质量排行榜。

```bash
python main.py queue --from-map cpo_ai_interconnect
python main.py queue --run 2          # mock，不烧 token
# python main.py queue --run 1 --live  # 真 LLM
python main.py export-pack xxx.md
python main.py thesis-health
python main.py watch bulk NVDA,AVGO
```

**仅供研究学习，不构成投资建议。**
