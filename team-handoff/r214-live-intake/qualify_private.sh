#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO="$(cd -- "$HERE/../.." && pwd)"
export R214_BASELINE_PRIVATE="$HOME/Downloads/X-Challenge 2026 Tesztforduló_Jutalom a nap végén_Tesztforduló_Z (1).xlsx"
export R214_BINARY_DIFFERENT_SAME_VALUES="$HOME/Downloads/X-Challenge 2026 Tesztforduló_Jutalom a nap végén_Tesztforduló_Z.xlsx"
test -f "$R214_BASELINE_PRIVATE" && test -f "$R214_BINARY_DIFFERENT_SAME_VALUES" || { echo HOLD_R214_PRIVATE_EXCEL_MISSING;exit 4; }
printf '%s  %s\n' 'c6cd0681a28872beb556652b584674f442c5105c379f365027ee9dbd3efe69bc' "$R214_BASELINE_PRIVATE" '4db0e1b415d5670af1427985eaccb8f9fe0b096c6402a67e1fb41fca21e76667' "$R214_BINARY_DIFFERENT_SAME_VALUES" | sha256sum -c -
python3 -I -B "$HERE/test_r214.py"
python3 -I -B -m unittest discover -s "$REPO/team-handoff/r207-first-round" -p 'test_first_round.py' -q
python3 -I -B "$REPO/team-handoff/r212-current-catalog/test_source_adapted_catalog_r212.py"
echo "R214_NATIVE_E2E=PASS_R156_TO_R207_ORIGINAL_MODULE_CHAIN_MOCK_ONLY"
echo "GAME_ACTION_GATE=STOP"
