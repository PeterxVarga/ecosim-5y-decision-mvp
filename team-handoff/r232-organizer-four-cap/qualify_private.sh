#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
export R232_MANIFEST="$HOME/Downloads/ecosim-r223-fresh-r156-20261102/r156_immutable/manifest.json"
export R232_R224="$HOME/Downloads/ecosim-r224-source-anchored-finance-20261102/R224_RECEIPT.json"
export R232_R228="$HOME/Downloads/ecosim-r228-finance-joined-20261102/R228_RECEIPT.json"
export R232_R231="$HOME/Downloads/ecosim-r231-finance-semantics-20261102/R230_READINESS_PRIVATE.json"
export R232_TRACK="$HOME/Downloads/ecosim-r228-finance-joined-20261102/R228_POLICY_UNKNOWN_CONTRACT_TEST_ONLY.json"
export R232_OUTPUT="$HOME/Downloads/ecosim-r232-organizer-cap4-20261102"
test -f "$R232_OUTPUT/R232_RECEIPT.json" || { echo "HOLD_R232_FRESH_PRIVATE_OUTPUT_REQUIRED"; exit 3; }
python3 -I -B "$HERE/test_organizer_cap_r232.py"
echo R232_ORGANIZER_FOUR_HARD_CAP_8_X_5=PASS
echo R191_R192_R214=HOLD_ACTUAL_AUTHORITY
echo GAME_ACTION_GATE=STOP
