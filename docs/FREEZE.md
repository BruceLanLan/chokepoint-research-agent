# 文档与产品封版说明（v10.0.1）

> 状态：**暂时封版** — 以「工作台 1.0」为可交付里程碑，优先稳定与文档，而非继续堆功能面。

## 封版版本

| 项 | 值 |
|----|-----|
| 产品版本 | **10.0.1** |
| 里程碑 | Research Workstation 1.0 |
| 测试基线 | 离线 pytest 全绿（约 167）；live/browser 默认跳过 |
| 主文档 | **中文** [README.md](../README.md) · 英文 [README.en.md](../README.en.md) |
| 截图 | [docs/images/](images/)（`scripts/capture_readme_screenshots.py` 可重生成） |

## 封版范围内「已就绪」

- 多专家研究（full / chokepoint_fast / risk_only / compare）  
- 离线 mock 研究 + live 费用门禁（402 / `--i-accept-live-costs`）  
- 5 个深垂直包 + 50 Pro YAML 模块  
- 覆盖簿 / 论点 / 证据 / 队列 / 周度运营  
- 研报 catalog 筛选、同 vertical 对比、对比包导出、thesis 关联  
- 黄金路径 `golden-path`、垂直覆盖看板  
- 专业 Web UI（中英切换）+ CLI + FastAPI  
- Doctor 双分（config / ops）、capabilities 快照  

## 封版期间不主动做

- 再堆一批行业 YAML / 再刷次要版本号  
- 默认开启 live LLM 或静默烧 token  
- 券商 / 组合 P&L / 交易信号  
- 把数据提供方包装成「行情保证」  

## 允许的维护窗口

- 安全修复、密钥泄露处理  
- CI 绿与依赖安全补丁  
- 文档勘误与截图更新  
- **用户真实覆盖簿驱动** 的单点 bugfix  

## 解封条件（建议）

满足任一条可开 10.x 小版本：

1. 线上真实使用反馈集中暴露 P0  
2. 需要三重门禁下的 live memo 集成测试  
3. 覆盖簿明确需要第 6 个 deep vertical（有不可套用的杀逻辑）  

## 黄金路径（封版验收）

```bash
python main.py doctor --ops-only
python main.py golden-path -V cpo_optics
python main.py compare-vertical cpo_optics --export
python main.py --server
make check   # 或 pytest -q -m "not live and not browser"
```

## 免责

本仓库仅供研究学习，不构成投资建议。详见 [DISCLAIMER.md](../DISCLAIMER.md)。
