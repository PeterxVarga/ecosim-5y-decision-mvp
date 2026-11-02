#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
PROFILE="$REPO/team-handoff/r200-historical-plugplay/profiles/historical_R94_R200.json"
R201="$HOME/Downloads/ecosim-r201-historical-tgwUX7NS/R201.json"
R202="$HOME/Downloads/ecosim-r202-historical-v6w3euqA/R202.json"
for file in "$PROFILE" "$R201" "$R202"; do
  test -s "$file" || { echo "HOLD_REQUIRED_PRIVATE_EVIDENCE_MISSING"; exit 4; }
done
git -C "$REPO" check-ignore -q "$PROFILE" || { echo "HOLD_UNSAFE_PUBLIC_PROFILE"; exit 9; }
OUT="$(mktemp -d "$HOME/Downloads/ecosim-r203-historical-XXXXXXXX")"
rmdir -- "$OUT"
python3 -I -B "$HERE/tools/transition_r203.py" \
  --profile "$PROFILE" --r201 "$R201" --r202 "$R202" --out-dir "$OUT"
python3 -I -B -m unittest discover -s "$HERE/tests" -v
echo "R203_PRIVATE_RESULT=$OUT/R203.json"
echo "R203_PRIVATE_REPORT=$OUT/R203_HU.md"
echo "GAME_ACTION_GATE=STOP"
