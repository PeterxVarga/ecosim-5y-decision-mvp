#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
export R228_EXCEL="$HOME/Downloads/X-Challenge 2026 Selejtező_Jutalom a nap végén_Selejtező_I.xlsx"
export R228_R226="$HOME/Downloads/ecosim-r226-final-census-20261102/R226_RECEIPT.json"
export R228_TAX="$HOME/Downloads/ecosim-r228-tax-active-view-readonly-20261102.json"
export R228_R156="$HOME/Downloads/ecosim-r223-fresh-r156-20261102"
export R228_R224="$HOME/Downloads/ecosim-r224-source-anchored-finance-20261102/R224_RECEIPT.json"
export R228_RESULT="$HOME/Downloads/ecosim-r228-source-joined-20261102"
test -f "$R228_EXCEL" && test -f "$R228_RESULT/R228_RECEIPT.json" || {
 echo "HOLD_REAL_PRIVATE_SOURCE_REQUIRED";exit 3; }
python3 -I -B "$HERE/test_source_join_r228.py"
echo "R228_ORIGINAL_R145_R148_E2E=PASS_24_SCENARIOS_120_YEARS"
echo "R153_R154_ACTUAL_TAX_CALIBRATION=HOLD_MISSING_UNITS_AND_MARKET_PARAMETERS"
echo "GAME_ACTION_GATE=STOP"
