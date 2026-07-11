# 命令行速查（中文）

入口：`python main.py`（或安装后的 `invest-agent` / `chokepoint-agent`）。

---

## 研究

```bash
# 默认 full 模式
python main.py "研究问题"

# 指定模式
python main.py "问题" --mode full
python main.py "问题" --mode chokepoint_fast
python main.py "问题" --mode risk_only
python main.py "问题" --mode compare

# 流式打印中间过程
python main.py "问题" --stream

# 双语 + 导出 JSON/HTML
python main.py "问题" --bilingual --export

# 不落盘
python main.py "问题" --no-save
```

子命令形式：

```bash
python main.py research "问题" --mode chokepoint_fast
```

---

## 会话

```bash
python main.py new-session
# 输出：a1b2c3d4e5f6

python main.py "第一问" --session a1b2c3d4e5f6
python main.py "继续深挖刚才的 ELS" --session a1b2c3d4e5f6
```

---

## 研报

```bash
python main.py list-reports
python main.py list-reports -n 50
```

生成文件默认在 `reports/`：

- `*.md` 正文  
- 开启导出时还有 `*.json` / `*.html`  

---

## 运营命令（v0.8+）

```bash
python main.py doctor
python main.py watch add NVDA --name NVIDIA --thesis "AI GPU" --priority high
python main.py watch list
python main.py thesis add --title "CPO" --statement "..." --kills "copper wins"
python main.py templates
python main.py research --template chokepoint_map --var system="AI CPO" --var context=""
python main.py list-reports --q CPO
python main.py brief --dry-run
python main.py brief -n 3          # 会真实调用模型，注意成本
python main.py providers
python main.py analytics
python main.py job "CPO 卡点快扫" --mode chokepoint_fast
# python main.py job "..." --wait   # 轮询直到完成

# v2.0 定时任务（macOS launchd / 通用 cron 行）
python main.py schedule install --hour 9 --minute 0 --limit 3
python main.py schedule status
python main.py schedule run
python main.py schedule uninstall

# 精美 PDF
python main.py pdf --file reports/xxx.md --title "投研备忘录"

# v2.5 检索 / 图表
python main.py search-memos "卡脖子 Scorecard"
python main.py chart scorecard --report xxx.md
python main.py chart price --symbol 0700.HK --period 3mo

# v3.0 技能包 / 后处理 / 离线评测
python main.py skills
python main.py research "CPO" --skill semiconductor --min-quality 50
python main.py mock-eval
python main.py metrics
python main.py clear-cache
```

## 评测与版本

```bash
python main.py eval      # 离线结构评测
python main.py version
```

---

## 服务

```bash
python main.py --server
python main.py server --host 0.0.0.0 --port 8000
```

---

## Make 快捷方式

```bash
make install
make check     # smoke + pytest + eval
make test
make eval
make server
make clean
```

---

## 退出码

| 场景 | 码 |
|------|-----|
| 成功 | 0 |
| 缺模型 Key / 初始化失败 | 1 |
| 非法 mode | 2 |
| `eval` 有失败用例 | 1 |
