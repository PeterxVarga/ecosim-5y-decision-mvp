#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
export R233_XLSX="$HOME/Downloads/X-Challenge 2026 Selejtező_Jutalom a nap végén_Selejtező_I.xlsx"
export R233_P1="$HOME/Downloads/ecosim-r223-fresh-r156-20261102/R217_P1_FACTORS.csv"
export R233_SUMMARY="$HOME/Downloads/ecosim-r223-fresh-readonly-pages-20261102/summary.txt"
export R233_R217="$HOME/Downloads/ecosim-r223-fresh-r156-20261102/R217_RECEIPT.json"
export R233_MANIFEST="$HOME/Downloads/ecosim-r223-fresh-r156-20261102/r156_immutable/manifest.json"
export R233_R232="$HOME/Downloads/ecosim-r232-organizer-cap4-20261102/R232_RECEIPT.json"
export R233_TRACK="$HOME/Downloads/ecosim-r228-finance-joined-20261102/R228_POLICY_UNKNOWN_CONTRACT_TEST_ONLY.json"
export R233_RESULT="$HOME/Downloads/ecosim-r233-source-reconciled-20261102"
test -f "$R233_RESULT/R233_RECEIPT.json" || { echo "HOLD_PRIVATE_R233_OUTPUT_MISSING" >&2; exit 3; }
python3 -I -B "$HERE/test_baseline_compare_r233.py"
echo "R233_ORIGINAL_P1_BASELINE_ATTRIBUTION=PASS_29_FACTORS_8_REPLAYS"
echo "GAME_ACTION_GATE=STOP"
