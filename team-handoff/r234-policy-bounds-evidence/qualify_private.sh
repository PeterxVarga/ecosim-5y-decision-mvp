#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
export R234_R225="$HOME/Downloads/ecosim-r225-periodic-qualification-v2-20261102/R225_RECEIPT.json"
export R234_R226="$HOME/Downloads/ecosim-r226-final-census-20261102/R226_RECEIPT.json"
export R234_R228="$HOME/Downloads/ecosim-r228-finance-joined-20261102/R228_RECEIPT.json"
export R234_TAX="$HOME/Downloads/ecosim-r228-tax-active-view-readonly-20261102.json"
export R234_R233="$HOME/Downloads/ecosim-r233-source-reconciled-20261102/R233_RECEIPT.json"
export R234_TRACK="$HOME/Downloads/ecosim-r228-finance-joined-20261102/R228_POLICY_UNKNOWN_CONTRACT_TEST_ONLY.json"
export R234_XLSX="$HOME/Downloads/X-Challenge 2026 Selejtező_Jutalom a nap végén_Selejtező_I.xlsx"
export R234_MANUAL_PDF="$HOME/Downloads/ecosim-r221-rulebook-readonly-20261102/rulebook_hu.pdf"
export R234_MANUAL_TEXT="$HOME/Downloads/ecosim-r221-rulebook-readonly-20261102/rulebook_hu.txt"
export R234_SOURCE_JS="$HOME/Downloads/ECOSIM_R142A_CODEX_GATES/private_js/45.4ed483b5.chunk.js"
export R234_OUT="$HOME/Downloads/ecosim-r234-p1-bounds-evidence-20261102"
test -f "$R234_OUT/R234_RECEIPT.json" || { echo "HOLD_PRIVATE_R234_SOURCE_REQUIRED" >&2; exit 3; }
python3 -I -B "$HERE/test_policy_bounds_r234.py"
echo "R234_ORIGINAL_SOURCE_POLICY_LIMIT_COVERAGE=PASS_23_ZERO_ADMITTED"
echo "R191_R192_R214_AND_POLICY_JOINT_OPTIMIZATION=HOLD"
echo "GAME_ACTION_GATE=STOP"
