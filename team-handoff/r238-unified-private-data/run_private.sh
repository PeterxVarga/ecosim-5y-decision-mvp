#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
B="$HOME/Downloads"
test "$#" -eq 2 && test "$1" = --out-dir || { echo "USAGE --out-dir NEW_PRIVATE_DIRECTORY" >&2;exit 2; }
test ! -e "$2" && test ! -L "$2" || { echo "HOLD_OUT_DIR_ALREADY_EXISTS" >&2;exit 3; }
exec python3 -I -B "$HERE/build_r238.py" \
 --r236 "$B/ecosim-r236-source-freeze-20261102/result/R236_PRIVATE_LEDGER.json" \
 --r226 "$B/ecosim-r226-final-census-20261102/R226_RECEIPT.json" \
 --r222 "$B/ecosim-r222-current-conditions-20261102/R222_RECEIPT.json" \
 --r228 "$B/ecosim-r228-finance-joined-20261102/R228_RECEIPT.json" \
 --r234 "$B/ecosim-r234-p1-bounds-evidence-20261102/R234_RECEIPT.json" \
 --r233 "$B/ecosim-r233-source-reconciled-20261102/R233_RECEIPT.json" \
 --r217 "$B/ecosim-r223-fresh-r156-20261102/R217_RECEIPT.json" \
 --r224 "$B/ecosim-r224-source-anchored-finance-20261102/R224_RECEIPT.json" \
 --r235 "$B/ecosim-r235-static-formulas-20261102/R235_RECEIPT.json" \
 --income-browser "$B/ecosim-r236-source-freeze-20261102/20261102_income_taxes_readonly_browser.txt" \
 --xlsx "$B/X-Challenge 2026 Selejtező_Jutalom a nap végén_Selejtező_I.xlsx" \
 --projects "$HERE/../../ECOSIM_R162_INTEGRITY_REVIEW_RC/data/ecosim_projects_20261030.json" \
 --p1-factors "$B/ecosim-r223-fresh-r156-20261102/r156_immutable/factors.csv" \
 --p1-project-states "$B/ecosim-r223-fresh-r156-20261102/r156_immutable/projects.csv" \
 --base "$B" \
 --out-dir "$2"
