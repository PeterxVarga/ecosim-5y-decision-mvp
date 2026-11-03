#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
export R221_R217="$HOME/Downloads/ecosim-r217-current-admission-20261102/R217_RECEIPT.json"
export R221_R220="$HOME/Downloads/ecosim-r220-all-35-current-source-20261102/R220_RECEIPT.json"
export R221_RULEBOOK="$HOME/Downloads/ecosim-r221-rulebook-readonly-20261102/rulebook_hu.pdf"
export R221_R156_BUNDLE="$HOME/Downloads/ecosim-r217-current-admission-20261102/r156_immutable"
export R221_RECEIPT="$HOME/Downloads/ecosim-r221-current-source-scenarios-20261102/R221.json"
python3 -I -B "$HERE/test_conditional_r221.py"
echo "R221_NATIVE_E2E=PASS_ORIGINAL_R162_R160_24_HYPOTHETICAL_GRID"
echo "R221_ACTUAL_MARKET_CAP=UNKNOWN"
echo "R221_ACTUAL_SPENDABLE_CASH=UNKNOWN"
echo "GAME_ACTION_GATE=STOP"
