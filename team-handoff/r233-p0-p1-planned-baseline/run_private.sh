#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
test "$#" -eq 2 && test "$1" = "--out-dir" || { echo "USAGE: $0 --out-dir NEW_PRIVATE_DIRECTORY" >&2; exit 2; }
test ! -e "$2" && test ! -L "$2" || { echo "HOLD_NEW_PRIVATE_DIRECTORY" >&2; exit 2; }
exec python3 -I -B "$HERE/baseline_compare_r233.py" \
 --xlsx "$HOME/Downloads/X-Challenge 2026 Selejtező_Jutalom a nap végén_Selejtező_I.xlsx" \
 --p1-csv "$HOME/Downloads/ecosim-r223-fresh-r156-20261102/R217_P1_FACTORS.csv" \
 --summary "$HOME/Downloads/ecosim-r223-fresh-readonly-pages-20261102/summary.txt" \
 --r217 "$HOME/Downloads/ecosim-r223-fresh-r156-20261102/R217_RECEIPT.json" \
 --manifest "$HOME/Downloads/ecosim-r223-fresh-r156-20261102/r156_immutable/manifest.json" \
 --r232 "$HOME/Downloads/ecosim-r232-organizer-cap4-20261102/R232_RECEIPT.json" \
 --track "$HOME/Downloads/ecosim-r228-finance-joined-20261102/R228_POLICY_UNKNOWN_CONTRACT_TEST_ONLY.json" \
 --out-dir "$2"
