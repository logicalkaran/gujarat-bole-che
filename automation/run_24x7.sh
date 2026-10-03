#!/data/data/com.termux/files/usr/bin/bash
set -u
cd "$(dirname "$0")/.."
LOG="growth/auto_generator.log"
LOCK="growth/.service.lock"
mkdir "$LOCK" 2>/dev/null || { echo "service already running"; exit 1; }
cleanup() { rmdir "$LOCK" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

command -v termux-wake-lock >/dev/null 2>&1 && termux-wake-lock || true
echo "[$(date -Is)] 24/7 service started" >> "$LOG"

while true; do
  echo "[$(date -Is)] research/generation cycle" >> "$LOG"
  python growth/auto_generator.py >> "$LOG" 2>&1 || echo "[$(date -Is)] generation failed: $?" >> "$LOG"

  if [ "$PUBLISH_ENABLED" = "true" ] && [ -n "$GOOGLE_REFRESH_TOKEN" ]; then
    latest="$(ls -t growth/generated/*.html 2>/dev/null | head -1 || true)"
    if [ -n "$latest" ]; then
      title="$(basename "$latest" .html | sed 's/^[0-9TZ-]*-//' | tr '-' ' ')"
      python growth/publish_blogger.py "$latest" "$title" >> "$LOG" 2>&1 ||         echo "[$(date -Is)] Blogger publish failed: $?" >> "$LOG"
    fi
  else
    echo "[$(date -Is)] publishing disabled; generated article kept locally" >> "$LOG"
  fi

  HOURS="$(python - <<'PY'
import json
print(float(json.load(open("growth/auto_config.json", encoding="utf-8"))["cadence_hours"]))
PY
)"
  SLEEP_SECONDS="$(python - <<PY
print(max(3600, int(float("$HOURS") * 3600)))
PY
)"
  echo "[$(date -Is)] next cycle in $SLEEP_SECONDS seconds" >> "$LOG"
  sleep "$SLEEP_SECONDS"
done
