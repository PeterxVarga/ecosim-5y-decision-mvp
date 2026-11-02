#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
export R230_R228="$HOME/Downloads/ecosim-r228-finance-joined-20261102/R228_RECEIPT.json"
export R230_R224="$HOME/Downloads/ecosim-r224-source-anchored-finance-20261102/R224_RECEIPT.json"
export R230_R222="$HOME/Downloads/ecosim-r222-current-conditions-20261102/R222_RECEIPT.json"
export R230_MANIFEST="$HOME/Downloads/ecosim-r223-fresh-r156-20261102/r156_immutable/manifest.json"
export R230_RESULT="$HOME/Downloads/ecosim-r230-first-year-readiness-20261102"
test -f "$R230_RESULT/R230_READINESS_PRIVATE.json" || { echo "HOLD_R230_SOURCE_NOT_COLLECTED"; exit 3; }
python3 -I -B "$HERE/test_readiness_r230.py"
printf '%s\n' 'R230_SOURCE_GATED_FIRST_YEAR=PASS_24_SCENARIOS_13_VARIANTS' \
 'R191_CAP_AND_R192_TIME=HOLD_ACTUAL_EVIDENCE_MISSING' 'GAME_ACTION_GATE=STOP'
