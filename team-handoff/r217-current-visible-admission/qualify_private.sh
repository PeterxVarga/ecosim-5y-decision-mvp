#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
export R217_PRIVATE_PAGES="${R217_PRIVATE_PAGES:-$HOME/Downloads/ecosim-r217-live-readonly-20261102}"
export R217_PRIVATE_RECEIPT="${R217_PRIVATE_RECEIPT:-$HOME/Downloads/ecosim-r217-current-admission-20261102}"
test -d "$R217_PRIVATE_PAGES" && test -f "$R217_PRIVATE_RECEIPT/R217_RECEIPT.json" || { echo HOLD_PRIVATE_BROWSER_SOURCES_MISSING;exit 4; }
python3 -I -B "$HERE/test_visible_r217.py"
export R220_PRIVATE_PAGES="$R217_PRIVATE_PAGES"
export R220_R217_DIR="$R217_PRIVATE_RECEIPT"
python3 -I -B "$HERE/test_all_views_r220.py"
echo "R220_NATIVE_E2E=PASS_35_VISIBLE_CARDS_R191_R192_HOLD"
echo "R217_NATIVE_E2E=PASS_R156_PARTIAL_R191_CORRECT_HOLD"
echo "GAME_ACTION_GATE=STOP"
