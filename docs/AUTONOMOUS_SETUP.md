# Autonomous / overnight setup

How to let Grok advance this repo for long stretches without babysitting.

中文简版见文末。

## 1. Durable rules

- **`AGENTS.md`** (repo root) — always loaded; allow/deny, ship ritual, product constraints
- **`docs/AUTONOMOUS_LOG.md`** — progress + “Next up” for session resume
- Optional: **`docs/BLOCKERS.md`** when stuck

Check rules load:

```bash
grok inspect
```

## 2. Interactive TUI (you leave the laptop open)

```text
cd investment-research-agent
grok
```

Then:

```text
/always-approve
```

Prompt:

```text
按 AGENTS.md 自主推进。读 docs/AUTONOMOUS_LOG.md，实现 Next up，
测试绿就 ship，更新 AUTONOMOUS_LOG。不要 live research，不要等我确认。
```

Optional periodic kick:

```text
/loop 2h 读 AUTONOMOUS_LOG 与 AGENTS.md，继续 Next up；pytest 绿可 ship；禁止 live research 与密钥
```

## 3. One-command overnight script

```bash
cd /Users/bruce/investment-research-agent
chmod +x scripts/autonomous_overnight.sh

# dry run (print plan)
DRY_RUN=1 ./scripts/autonomous_overnight.sh

# 3 headless YOLO turns, no sleep between
./scripts/autonomous_overnight.sh

# 5 turns, 30 minutes apart
TURNS=5 INTERVAL_MIN=30 ./scripts/autonomous_overnight.sh
```

Logs: `data/logs/autonomous/overnight_*.log`  
Session id: `data/logs/autonomous/last_session_id.txt`

Resume later:

```bash
grok -p "继续 AUTONOMOUS_LOG 的 Next up" -c --yolo --cwd /Users/bruce/investment-research-agent
```

## 4. Requirements

| Need | Notes |
|------|--------|
| `grok` CLI | `~/.local/bin/grok` or `GROK_BIN=…` |
| Auth | Browser login cache or `XAI_API_KEY` for headless |
| SuperGrok / quota | Headless burns **your** Grok quota, not MiniMax |
| `gh` + git remote | Only if the agent ships releases |
| Network | For push/release |

## 5. Safety

- Script always uses `--yolo` → only on a trusted machine
- Prompt + `AGENTS.md` forbid secret commits and live research burns
- Still review `git log` / GitHub Releases after overnight runs

## 6. 中文摘要

1. 仓库根目录 `AGENTS.md` = 永久授权与红线  
2. `docs/AUTONOMOUS_LOG.md` = 进度与「下一步」  
3. TUI：`/always-approve` + 一条长目标；或 `/loop`  
4. 睡觉前：`./scripts/autonomous_overnight.sh`  
5. 第二天看 `AUTONOMOUS_LOG` 与 `data/logs/autonomous/`  

**Research only — not investment advice.**
