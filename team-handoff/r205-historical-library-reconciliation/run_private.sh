#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
SOURCE="$HOME/Downloads/ecosim-r205-library-evidence"
PROFILE="$REPO/team-handoff/r200-historical-plugplay/profiles/historical_R94_R200.json"
R202="$HOME/Downloads/ecosim-r202-historical-v6w3euqA/R202.json"
R204="$HOME/Downloads/ecosim-r204-unified-SeqAg0cs/first/DECISION_PACKET.json"
for source in "$SOURCE/income.csv" "$SOURCE/loans.csv" "$SOURCE/rules.csv" \
  "$SOURCE/observations.csv" "$SOURCE/source_index.csv" "$SOURCE/LIBRARY_SOURCE_MANIFEST.json" \
  "$PROFILE" "$R202" "$R204"; do
  [[ -s "$source" ]] || { echo "HOLD_MISSING_PREVIOUSLY_UPLOADED_EVIDENCE"; exit 4; }
done
ROOT="$(mktemp -d "$HOME/Downloads/ecosim-r205-qualified-XXXXXXXX")"
for iteration in first second; do
  python3 -I -B "$HERE/reconcile.py" \
    --source-dir "$SOURCE" \
    --manifest "$SOURCE/LIBRARY_SOURCE_MANIFEST.json" \
    --profile "$PROFILE" --r202 "$R202" --r204 "$R204" \
    --out-dir "$ROOT/$iteration"
done
cmp "$ROOT/first/R205.json" "$ROOT/second/R205.json"
cmp "$ROOT/first/R205_HU.md" "$ROOT/second/R205_HU.md"
for old in r196-city-review r197-r198-city-join r200-historical-plugplay \
 r201-robust-test-replay r202-calibration-gate r203-transition-evidence; do
  python3 -I -B -m unittest discover -s "$REPO/team-handoff/$old/tests" -p 'test_*.py' -q
done
python3 -I -B "$REPO/team-handoff/ecosim-decision-engine-v1/test_decision_engine.py"
python3 -I -B "$REPO/team-handoff/ecosim-decision-engine-v1/test_decision_brief.py"
python3 -I -B "$HERE/test_reconcile.py"
echo "R205_NATIVE_E2E=PASS_REPRODUCIBLE_HISTORICAL_ONLY"
echo "R205_FULL_TARGETED_REGRESSIONS=203/203_PASS"
echo "R205_REPORT=$ROOT/first/R205_HU.md"
echo "R205_RESULT=$ROOT/first/R205.json"
echo "GAME_ACTION_GATE=STOP"
