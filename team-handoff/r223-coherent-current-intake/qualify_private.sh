#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
export R223_FRESH_PAGES="$HOME/Downloads/ecosim-r223-fresh-readonly-pages-20261102"
export R223_FRESH_R156="$HOME/Downloads/ecosim-r223-fresh-r156-20261102"
export R223_PREVIOUS_PAGES="$HOME/Downloads/ecosim-r217-live-readonly-20261102"
test -d "$R223_FRESH_PAGES" && test -f "$R223_FRESH_R156/R217_RECEIPT.json" || {
  echo "HOLD_REAL_SOURCE_FIXTURES_MISSING";exit 4; }
python3 -I -B "$HERE/test_coherent_r223.py"
echo "R223_REAL_INTAKE=HOLD_THREE_CURRENT_CATEGORY_VIEWS"
echo "R223_SYNTHETIC_SAME_HOUR_R192=PASS_TEST_ONLY"
echo "GAME_ACTION_GATE=STOP"
