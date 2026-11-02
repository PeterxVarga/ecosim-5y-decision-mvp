#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
python3 -I -B "$HERE/test_build_r238.py"
echo "R238_SOURCE_UNIFICATION=PASS_PRIVATE_OBSERVED_SNAPSHOT"
echo "FINAL_STRATEGY_DATA_READINESS=HOLD_GAME_WRITES=0"
