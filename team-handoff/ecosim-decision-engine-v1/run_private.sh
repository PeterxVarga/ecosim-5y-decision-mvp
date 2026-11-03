#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
ROOT="$(mktemp -d "$HOME/Downloads/ecosim-r204-unified-XXXXXXXX")"
R201="$HOME/Downloads/ecosim-r201-historical-tgwUX7NS/R201.json"
R202="$HOME/Downloads/ecosim-r202-historical-v6w3euqA/R202.json"
R203="$HOME/Downloads/ecosim-r203-historical-4ngMHvHh/R203.json"
for required in "$R201" "$R202" "$R203"; do
  test -s "$required" || { echo "HOLD_MISSING_PRIVATE_HISTORICAL_REPORT"; exit 4; }
done
for run in first second; do
  OUT="$ROOT/$run"
  python3 -I -B "$HERE/decision_engine.py" \
    --r201 "$R201" --r202 "$R202" --r203 "$R203" --out-dir "$OUT"
  python3 -I -B "$HERE/decision_brief.py" \
    --packet "$OUT/DECISION_PACKET.json" --out-dir "$OUT"
done
for report in DECISION_PACKET.json DECISION_PACKET_HU.md DECISION_COMPARISON.json DECISION_COMPARISON.csv DECISION_COMPARISON_HU.md; do
  cmp "$ROOT/first/$report" "$ROOT/second/$report"
done
python3 -I -B "$HERE/test_decision_engine.py"
python3 -I -B "$HERE/test_decision_brief.py"
echo "R204_NATIVE_E2E=PASS_REPRODUCIBLE_HISTORICAL_ONLY"
echo "R204_REPORT=$ROOT/first/DECISION_COMPARISON_HU.md"
echo "R204_RESULT=$ROOT/first/DECISION_COMPARISON.json"
echo "GAME_ACTION_GATE=STOP"
