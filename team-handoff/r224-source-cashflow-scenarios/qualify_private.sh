#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
export R224_CURRENT_FINANCE="$HOME/Downloads/ecosim-r223-fresh-readonly-pages-20261102/finance.txt"
export R224_CURRENT_R156="$HOME/Downloads/ecosim-r223-fresh-r156-20261102"
export R224_RESULT="$HOME/Downloads/ecosim-r224-source-anchored-finance-20261102"
test -f "$R224_CURRENT_FINANCE" && test -f "$R224_CURRENT_R156/R217_RECEIPT.json" &&
test -f "$R224_RESULT/R224_RECEIPT.json" || {
 echo "HOLD_PRIVATE_CURRENT_SOURCE_MISSING";exit 4; }
python3 -I -B "$HERE/test_finance_r224.py"
echo "R224_PRIVATE_E2E=PASS_24_SOURCE_FINANCE_HYPOTHESES_ORIGINAL_R162_R160"
echo "ACTUAL_SPENDABLE=UNKNOWN; MARKET_CAP=UNKNOWN"
echo "GAME_ACTION_GATE=STOP"
