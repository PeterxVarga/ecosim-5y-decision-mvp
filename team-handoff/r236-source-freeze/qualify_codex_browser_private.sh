#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
python3 -I -B "$HERE/test_codex_browser_intake.py"
echo R236_NATIVE_CODEX_BROWSER=CONNECTED_ORIGIN_PERMISSION_BLOCKED
echo GAME_ACTION_GATE=STOP
