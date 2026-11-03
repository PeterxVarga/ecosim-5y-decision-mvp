#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
PROFILE="$HOME/Downloads/ecosim-r205-library-evidence"
R205="$HOME/Downloads/ecosim-r205-qualified-LeH8ZQmG/first/R205.json"
R206="$HOME/Downloads/ecosim-r206-native-result-20261102/R206.json"
for p in "$PROFILE" "$R205" "$R206"; do
  [[ -e "$p" ]] || { echo "HOLD_PRIVATE_HISTORICAL_SOURCE_MISSING";exit 4; }
done
python3 -I -B "$HERE/test_finance_stress_r211.py"
ROOT="$(mktemp -d "$HOME/Downloads/ecosim-r211-qualification-XXXXXXXX")"
for pass in first second; do
  python3 -I -B "$HERE/finance_stress_r211.py" --r205 "$R205" --r206 "$R206" \
    --r205-private-sources "$PROFILE" --out-dir "$ROOT/$pass"
done
cmp "$ROOT/first/R211.json" "$ROOT/second/R211.json"
cmp "$ROOT/first/R211_HU.md" "$ROOT/second/R211_HU.md"
python3 -I -B "$HERE/test_mock_year2_replan_r211.py" > "$ROOT/mock_replan_first.json"
python3 -I -B "$HERE/test_mock_year2_replan_r211.py" > "$ROOT/mock_replan_second.json"
cmp "$ROOT/mock_replan_first.json" "$ROOT/mock_replan_second.json"
echo "R211_REPLAN_E2E=PASS_R203_MOCK_FACT_PAIR_TO_YEAR2_ORIGINAL_R162"
echo "R211_NATIVE_E2E=PASS_REPRODUCIBLE_HISTORICAL_PARTIAL_FINANCE"
echo "R211_PRIVATE_REPORT=$ROOT/first/R211_HU.md"
echo "GAME_ACTION_GATE=STOP"
