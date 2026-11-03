#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
BASE="$HOME/Downloads"
test "$#" -eq 2 && test "$1" = --out-dir || {
  echo "USAGE: $0 --out-dir NEW_PRIVATE_DIRECTORY" >&2; exit 2;
}
test ! -e "$2" && test ! -L "$2" || { echo "HOLD_NO_OVERWRITE" >&2; exit 2; }
exec python3 -I -B "$DIR/source_freeze_r236.py" \
 --r217 "$BASE/ecosim-r223-fresh-r156-20261102/R217_RECEIPT.json" \
 --r222 "$BASE/ecosim-r222-current-conditions-20261102/R222_RECEIPT.json" \
 --r224 "$BASE/ecosim-r224-source-anchored-finance-20261102/R224_RECEIPT.json" \
 --r226 "$BASE/ecosim-r226-final-census-20261102/R226_RECEIPT.json" \
 --r228 "$BASE/ecosim-r228-finance-joined-20261102/R228_RECEIPT.json" \
 --r232 "$BASE/ecosim-r232-organizer-cap4-20261102/R232_RECEIPT.json" \
 --r233 "$BASE/ecosim-r233-source-reconciled-20261102/R233_RECEIPT.json" \
 --r234 "$BASE/ecosim-r234-p1-bounds-evidence-20261102/R234_RECEIPT.json" \
 --r235 "$BASE/ecosim-r235-static-formulas-20261102/R235_RECEIPT.json" \
 --income-browser "$BASE/ecosim-r236-source-freeze-20261102/20261102_income_taxes_readonly_browser.txt" \
 --out-dir "$2"
