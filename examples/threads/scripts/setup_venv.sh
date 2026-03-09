#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLI_DIR="$SKILL_DIR/cli"

python3 -m venv "$SKILL_DIR/.venv"
# shellcheck disable=SC1090
source "$SKILL_DIR/.venv/bin/activate"

python3 -m pip install -U pip
python3 -m pip install -r "$CLI_DIR/requirements.txt"

echo "OK: venv created at $SKILL_DIR/.venv"
echo "Next: source $SKILL_DIR/.venv/bin/activate"
