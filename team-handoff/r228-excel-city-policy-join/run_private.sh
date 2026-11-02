#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
OUTPUT=""
while (($#)); do
 case "$1" in
  --out-dir) OUTPUT="${2:?}";shift 2;;
  *) echo "HOLD_UNEXPECTED_ARGUMENT" >&2;exit 2;;
 esac
done
test -n "$OUTPUT" && test ! -e "$OUTPUT" && test ! -L "$OUTPUT" || {
 echo "HOLD_NEW_PRIVATE_OUTPUT_REQUIRED" >&2;exit 2; }
exec python3 -I -B "$HERE/source_join_r228.py" \
 --excel "$HOME/Downloads/X-Challenge 2026 Selejtező_Jutalom a nap végén_Selejtező_I.xlsx" \
 --r226 "$HOME/Downloads/ecosim-r226-final-census-20261102/R226_RECEIPT.json" \
 --tax "$HOME/Downloads/ecosim-r228-tax-active-view-readonly-20261102.json" \
 --r156 "$HOME/Downloads/ecosim-r223-fresh-r156-20261102" \
 --r224 "$HOME/Downloads/ecosim-r224-source-anchored-finance-20261102/R224_RECEIPT.json" \
 --out-dir "$OUTPUT"
