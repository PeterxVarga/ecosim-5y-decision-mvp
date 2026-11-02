#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
test "$#" -eq 2 && test "$1" = "--out-dir" || { echo "USAGE: $0 --out-dir NEW_PRIVATE_DIRECTORY" >&2; exit 2; }
test ! -e "$2" && test ! -L "$2" || { echo "HOLD_NEW_PRIVATE_DIRECTORY_REQUIRED" >&2; exit 2; }
exec python3 -I -B "$HERE/policy_bounds_r234.py" \
 --r225 "$HOME/Downloads/ecosim-r225-periodic-qualification-v2-20261102/R225_RECEIPT.json" \
 --r226 "$HOME/Downloads/ecosim-r226-final-census-20261102/R226_RECEIPT.json" \
 --r228 "$HOME/Downloads/ecosim-r228-finance-joined-20261102/R228_RECEIPT.json" \
 --tax "$HOME/Downloads/ecosim-r228-tax-active-view-readonly-20261102.json" \
 --r233 "$HOME/Downloads/ecosim-r233-source-reconciled-20261102/R233_RECEIPT.json" \
 --track "$HOME/Downloads/ecosim-r228-finance-joined-20261102/R228_POLICY_UNKNOWN_CONTRACT_TEST_ONLY.json" \
 --xlsx "$HOME/Downloads/X-Challenge 2026 Selejtező_Jutalom a nap végén_Selejtező_I.xlsx" \
 --manual-pdf "$HOME/Downloads/ecosim-r221-rulebook-readonly-20261102/rulebook_hu.pdf" \
 --manual-text "$HOME/Downloads/ecosim-r221-rulebook-readonly-20261102/rulebook_hu.txt" \
 --source-js "$HOME/Downloads/ECOSIM_R142A_CODEX_GATES/private_js/45.4ed483b5.chunk.js" \
 --out-dir "$2"
