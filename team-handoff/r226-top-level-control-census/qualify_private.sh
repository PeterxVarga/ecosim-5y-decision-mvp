#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
export R226_PRIMARY="$HOME/Downloads/ecosim-r226-full-menu-visible-20261102"
export R226_R225_PAGES="$HOME/Downloads/ecosim-r225-periodic-current-20261102"
export R226_R225_RECEIPT="$HOME/Downloads/ecosim-r225-periodic-qualification-v2-20261102"
export R226_R156="$HOME/Downloads/ecosim-r223-fresh-r156-20261102"
export R226_RESULT="$HOME/Downloads/ecosim-r226-final-census-20261102"
test -f "$R226_RESULT/R226_RECEIPT.json" || { echo "HOLD_REAL_OPERATOR_SOURCE_REQUIRED";exit 4; }
python3 -I -B "$HERE/test_census_r226.py"
echo "R226_NATIVE_E2E=PASS_TEN_TOP_LEVEL_VIEWS_19_VISIBLE_INPUTS_R145_UNKNOWN"
echo "NUMERIC_CAP=UNKNOWN; ACTUAL_SPENDABLE_CASH=UNKNOWN"
echo "GAME_ACTION_GATE=STOP"
