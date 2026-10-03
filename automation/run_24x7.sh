#!/data/data/com.termux/files/usr/bin/bash
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
LOG_DIR="$ROOT/automation/logs"
LOG="$LOG_DIR/auto_generator.log"
LOCK="$ROOT/automation/.service.lock"
mkdir -p "$LOG_DIR"
mkdir "$LOCK" 2>/dev/null || { echo "service already running"; exit 1; }
cleanup() { rmdir "$LOCK" 2>/dev/null || true; }
trap cleanup EXIT INT TERM
command -v termux-wake-lock >/dev/null 2>&1 && termux-wake-lock || true
echo "[$(date -Is)] v2 service started" >> "$LOG"
while true; do
 echo "[$(date -Is)] research/generation cycle" >> "$LOG"
 python "$ROOT/automation/auto_generator.py" >> "$LOG" 2>&1 || echo "[$(date -Is)] generation failed" >> "$LOG"
 latest="$(ls -t "$ROOT/automation/generated/"*.html 2>/dev/null | head -1 || true)"
 if [ -n "$latest" ] && python "$ROOT/automation/quality_gate.py" "$latest" >> "$LOG" 2>&1; then
  if env | grep -q "^PUBLISH_ENABLED=true$" && env | grep -q "^GOOGLE_REFRESH_TOKEN=."; then
   title="$(basename "$latest" .html | sed 's/^[0-9TZ-]*-//' | tr '-' ' ')"
   python "$ROOT/automation/publish_blogger.py" "$latest" "$title" >> "$LOG" 2>&1 || echo "[$(date -Is)] Blogger publish failed" >> "$LOG"
  else
   echo "[$(date -Is)] publishing disabled; quality-approved article kept locally" >> "$LOG"
  fi
 else
  echo "[$(date -Is)] quality gate failed or no article; publishing skipped" >> "$LOG"
 fi
 HOURS="$(python -c 'import json; print(float(json.load(open("automation/auto_config.json"))["cadence_hours"]))')"
 SLEEP_SECONDS="$(python -c 'print(max(3600,int(float("'$HOURS'")*3600)))')"
 echo "[$(date -Is)] next cycle in $SLEEP_SECONDS seconds" >> "$LOG"
 sleep "$SLEEP_SECONDS"
done
