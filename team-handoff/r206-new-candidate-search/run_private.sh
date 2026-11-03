#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO="$(cd -- "$HERE/../.." && pwd)"
PROFILE="$REPO/team-handoff/r200-historical-plugplay/profiles/historical_R94_R200.json"
R204="${ECOSIM_R204_PACKET:-$HOME/Downloads/ecosim-r204-unified-SeqAg0cs/first/DECISION_PACKET.json}"
R205="${ECOSIM_R205_REPORT:-$HOME/Downloads/ecosim-r205-qualified-LeH8ZQmG/first/R205.json}"
for required in "$PROFILE" "$R204" "$R205"; do
  [[ -s "$required" ]] || { echo "HOLD_MISSING_PRIVATE_R200_R204_R205_INPUT"; exit 4; }
done
python3 -I -B "$HERE/test_new_candidates.py"
OUTPUT="$(mktemp -d "$HOME/Downloads/ecosim-r206-results-XXXXXXXX")"
rmdir -- "$OUTPUT"
python3 -I -B "$HERE/new_candidates.py" \
  --profile "$PROFILE" --r204 "$R204" --r205 "$R205" \
  --out-dir "$OUTPUT" --beam 3 --shortlist 10
[[ -s "$OUTPUT/R206.json" && -s "$OUTPUT/R206_HU.md" ]]
echo "R206_HISTORICAL_OFFLINE_E2E=PASS"
echo "R206_RESULT=$OUTPUT/R206.json"
echo "R206_REPORT=$OUTPUT/R206_HU.md"
echo "GAME_ACTION_GATE=STOP"
