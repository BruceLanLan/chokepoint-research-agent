#!/usr/bin/env bash
# Overnight / unattended Grok Build runner for chokepoint-research-agent.
#
# What it does:
#   1) Verifies repo + grok CLI
#   2) Runs a YOLO headless session that continues autonomous work
#   3) Optionally loops N more continuation turns with -c
#   4) Logs everything under data/logs/autonomous/
#
# Usage:
#   ./scripts/autonomous_overnight.sh
#   TURNS=5 INTERVAL_MIN=0 ./scripts/autonomous_overnight.sh
#   DRY_RUN=1 ./scripts/autonomous_overnight.sh    # print plan only
#
# Requirements:
#   - `grok` on PATH (or set GROK_BIN)
#   - Logged in / XAI_API_KEY for headless
#   - Network for push/release if the agent ships
#
# Safety:
#   - Prompt forbids live research burns and secret commits
#   - Still uses --yolo: only run on a machine you trust

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

GROK_BIN="${GROK_BIN:-$(command -v grok || true)}"
TURNS="${TURNS:-3}"                 # total headless turns (1 initial + TURNS-1 continues)
INTERVAL_MIN="${INTERVAL_MIN:-0}"   # sleep between turns (minutes)
MODEL="${MODEL:-}"                  # e.g. grok-build; empty = CLI default
DRY_RUN="${DRY_RUN:-0}"
LOG_DIR="${LOG_DIR:-$ROOT/data/logs/autonomous}"
STAMP="$(date +%Y%m%d_%H%M%S)"
LOG_FILE="$LOG_DIR/overnight_${STAMP}.log"
SESSION_FILE="$LOG_DIR/last_session_id.txt"

mkdir -p "$LOG_DIR"

if [[ -z "$GROK_BIN" || ! -x "$GROK_BIN" ]]; then
  echo "error: grok CLI not found. Install Grok Build CLI or set GROK_BIN." >&2
  exit 1
fi

if [[ ! -f "$ROOT/AGENTS.md" ]]; then
  echo "error: AGENTS.md missing — refuse to run without durable rules." >&2
  exit 1
fi

PROMPT_INITIAL="$(cat <<'EOF'
You are in unattended overnight mode for the Chokepoint Research Agent repo.

MANDATORY first steps:
1. Read AGENTS.md, docs/AUTONOMOUS_LOG.md, docs/ROADMAP.md
2. git status + git log -5; run .venv/bin/python -m pytest tests/ -q (create/fix venv only if needed)
3. Resume from AUTONOMOUS_LOG "Next up"; do not wait for the user

Then autonomously implement the highest-value offline items (prefer v4.7-class ops):
- ship only if tests are green
- update docs/AUTONOMOUS_LOG.md every batch
- follow AGENTS.md allow/deny lists exactly

Hard rules:
- Never commit or print .env / API keys
- No live research / queue --run --live / heavy Tavily unless AUTONOMOUS_LOG explicitly says user requested it
- No brokerage or investment-advice product features
- Push/tag/release allowed for this public repo when a version is ready

When done with a batch, leave clear "Next up" bullets in docs/AUTONOMOUS_LOG.md so the next turn can continue.
EOF
)"

PROMPT_CONTINUE="$(cat <<'EOF'
Continue unattended overnight work for this repo.

Read docs/AUTONOMOUS_LOG.md and AGENTS.md. Pick up "Next up".
Run tests after changes. Ship (tag/push/release) only if green and meaningful.
Update docs/AUTONOMOUS_LOG.md. Do not wait for the user. Obey AGENTS.md hard rules (no secrets, no live research burns).
EOF
)"

echo "== autonomous overnight =="
echo "root:     $ROOT"
echo "grok:     $GROK_BIN"
echo "turns:    $TURNS"
echo "interval: ${INTERVAL_MIN}m"
echo "log:      $LOG_FILE"
echo "model:    ${MODEL:-<default>}"
echo

if [[ "$DRY_RUN" == "1" ]]; then
  echo "[DRY_RUN] would run $TURNS headless YOLO turn(s)"
  echo "--- initial prompt ---"
  echo "$PROMPT_INITIAL"
  exit 0
fi

{
  echo "===== start $(date -Iseconds) ====="
  echo "host=$(hostname) user=$(whoami) pwd=$ROOT"
} | tee -a "$LOG_FILE"

run_turn() {
  local n="$1"
  local prompt="$2"
  local extra=()
  if [[ -n "$MODEL" ]]; then
    extra+=(-m "$MODEL")
  fi

  echo "" | tee -a "$LOG_FILE"
  echo "===== turn $n / $TURNS $(date -Iseconds) =====" | tee -a "$LOG_FILE"

  # First turn: fresh session with JSON so we can capture sessionId.
  # Later turns: -c continues most recent session in this cwd.
  if [[ "$n" -eq 1 ]]; then
    set +e
    "$GROK_BIN" -p "$prompt" \
      --cwd "$ROOT" \
      --yolo \
      --output-format json \
      --no-auto-update \
      "${extra[@]}" \
      2>>"$LOG_FILE" | tee -a "$LOG_FILE" | tee /tmp/grok_overnight_last.json >/dev/null
    local rc=${PIPESTATUS[0]}
    set -e
    if command -v jq >/dev/null 2>&1 && [[ -f /tmp/grok_overnight_last.json ]]; then
      sid=$(jq -r '.sessionId // empty' /tmp/grok_overnight_last.json 2>/dev/null || true)
      if [[ -n "$sid" ]]; then
        echo "$sid" >"$SESSION_FILE"
        echo "sessionId=$sid" | tee -a "$LOG_FILE"
      fi
    fi
    return "$rc"
  else
    set +e
    "$GROK_BIN" -p "$prompt" \
      --cwd "$ROOT" \
      --yolo \
      -c \
      --output-format json \
      --no-auto-update \
      "${extra[@]}" \
      2>>"$LOG_FILE" | tee -a "$LOG_FILE" >/dev/null
    local rc=${PIPESTATUS[0]}
    set -e
    return "$rc"
  fi
}

fail=0
for ((i=1; i<=TURNS; i++)); do
  if [[ "$i" -eq 1 ]]; then
    prompt="$PROMPT_INITIAL"
  else
    prompt="$PROMPT_CONTINUE"
  fi

  if ! run_turn "$i" "$prompt"; then
    echo "turn $i failed (exit non-zero) — will try remaining turns" | tee -a "$LOG_FILE"
    fail=1
  fi

  if [[ "$i" -lt "$TURNS" && "$INTERVAL_MIN" -gt 0 ]]; then
    echo "sleep ${INTERVAL_MIN}m before next turn…" | tee -a "$LOG_FILE"
    sleep $((INTERVAL_MIN * 60))
  fi
done

{
  echo "===== end $(date -Iseconds) fail=$fail ====="
  echo "See docs/AUTONOMOUS_LOG.md for agent-written progress."
  if [[ -f "$SESSION_FILE" ]]; then
    echo "Last session id: $(cat "$SESSION_FILE")"
    echo "Resume manually: grok -p 'continue' --resume \"$(cat "$SESSION_FILE")\" --yolo --cwd \"$ROOT\""
  fi
} | tee -a "$LOG_FILE"

exit "$fail"
