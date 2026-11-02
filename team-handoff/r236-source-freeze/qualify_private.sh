#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
B="$HOME/Downloads"
export R236_R217="$B/ecosim-r223-fresh-r156-20261102/R217_RECEIPT.json"
export R236_R222="$B/ecosim-r222-current-conditions-20261102/R222_RECEIPT.json"
export R236_R224="$B/ecosim-r224-source-anchored-finance-20261102/R224_RECEIPT.json"
export R236_R226="$B/ecosim-r226-final-census-20261102/R226_RECEIPT.json"
export R236_R228="$B/ecosim-r228-finance-joined-20261102/R228_RECEIPT.json"
export R236_R232="$B/ecosim-r232-organizer-cap4-20261102/R232_RECEIPT.json"
export R236_R233="$B/ecosim-r233-source-reconciled-20261102/R233_RECEIPT.json"
export R236_R234="$B/ecosim-r234-p1-bounds-evidence-20261102/R234_RECEIPT.json"
export R236_R235="$B/ecosim-r235-static-formulas-20261102/R235_RECEIPT.json"
export R236_INCOME_BROWSER="$B/ecosim-r236-source-freeze-20261102/20261102_income_taxes_readonly_browser.txt"
export R236_RESULT="$B/ecosim-r236-source-freeze-20261102/result"
test -f "$R236_RESULT/R236_PRIVATE_LEDGER.json" || {
  echo "HOLD_PRIVATE_R236_RESULT_NOT_COLLECTED" >&2;exit 3;
}
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
python3 -I -B "$HERE/test_source_freeze_r236.py"
echo "R236_PERIOD_DATA_INTAKE=PARTIAL_NOT_READY_FOR_FINAL_STRATEGY"
echo "R236_GAME_WRITE_COUNT=0"
