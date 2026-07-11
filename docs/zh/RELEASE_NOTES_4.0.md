# 发布说明 — v3.1 → v4.0.0

v3.0 之后的自主迭代：**证据账本、论点图谱、结构化对比、标签集合、杀逻辑监控、覆盖热力、审计、DOCX、快照、插件加载**。

English → [../RELEASE_NOTES_4.0.md](../RELEASE_NOTES_4.0.md)

## 能力一览

- **证据账本**：从 memo 抽取 URL / 域名 / 声明行 / 代码
- **论点图谱**：论点 ↔ 卡点 ↔ 标的，支持 Mermaid
- **研报对比**：质量排序、章节覆盖、共享 scorecard 节点
- **标签与合集**：本地组织研报库
- **Kill 监控**：标出「活跃但无杀逻辑」的过程风险
- **覆盖热力**：观察名单 × 论点 × 研报密度
- **审计轨迹**：可追加的操作日志
- **DOCX 导出**：纯标准库 OOXML，无额外依赖
- **工作区快照**：zip 打包（**绝不**包含 `.env`）
- **插件加载**：扫描 `./plugins/`

## 快速命令

```bash
python main.py evidence --summary
python main.py graph --mermaid
python main.py kill-monitor
python main.py coverage
python main.py snapshot
```

UI 新增 **Ops 图谱/证据** 页签。

**仅供研究学习，不构成投资建议。**
