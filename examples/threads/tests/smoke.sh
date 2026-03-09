#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT/.env"

cd "$ROOT/cli"

python3 -m threads_cli --env-file "$ENV_FILE" me > /dev/null

echo "me: OK"

# Dashboard generation (no send)
python3 "$ROOT/scripts/dashboard.py" --env-file "$ENV_FILE" --days 7 --top-days 30 --top-n 3 > /dev/null

echo "dashboard: OK"

# Inbox digest (may contain API 500 for mentions; should still output JSON)
python3 "$ROOT/scripts/inbox.py" --env-file "$ENV_FILE" --limit 3 > /dev/null

echo "inbox: OK"

# Posting workflow: draft/approve/status only (no publish)
python3 "$ROOT/scripts/posting.py" cancel > /dev/null || true
python3 "$ROOT/scripts/posting.py" draft --text "smoke test draft" > /dev/null
python3 "$ROOT/scripts/posting.py" approve > /dev/null
python3 "$ROOT/scripts/posting.py" status > /dev/null

echo "posting: OK"

echo "SMOKE: OK"
