#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
export R225_PRIVATE_PAGES="$HOME/Downloads/ecosim-r225-periodic-current-20261102"
export R225_PRIVATE_R156="$HOME/Downloads/ecosim-r223-fresh-r156-20261102"
export R225_PRIVATE_RECEIPT="$HOME/Downloads/ecosim-r225-periodic-qualification-v2-20261102"
test -d "$R225_PRIVATE_PAGES" && test -f "$R225_PRIVATE_R156/R217_RECEIPT.json" &&
test -f "$R225_PRIVATE_RECEIPT/R225_RECEIPT.json" || {
  echo "HOLD_PRIVATE_OBSERVED_SOURCE_REQUIRED";exit 4; }
python3 -I -B "$HERE/test_intake_r225.py"
echo "R225_NATIVE_INTEGRATION=PASS_18_EDITABLE_FIELDS_R145_UNKNOWN_PROPAGATED"
echo "P1_DECISION_VALUES=UNKNOWN; R191_CAP=UNKNOWN; CASH=UNKNOWN"
echo "GAME_ACTION_GATE=STOP"
