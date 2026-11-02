#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
PROFILE="$REPO/team-handoff/r200-historical-plugplay/profiles/historical_R94_R200.json"
test -s "$PROFILE" || { echo "HOLD_PRIVATE_R200_PROFILE_MISSING"; exit 4; }
git -C "$REPO" check-ignore -q "$PROFILE" || { echo "HOLD_UNSAFE_PUBLIC_PROFILE"; exit 9; }
DEST="$(mktemp -d "$HOME/Downloads/ecosim-r201-historical-XXXXXXXX")"
rmdir -- "$DEST"
python3 -I -B "$HERE/tools/robust_r201.py" --profile "$PROFILE" --out-dir "$DEST"
python3 -I -B -m unittest discover -s "$HERE/tests" -v
echo "R201_PRIVATE_REPORT=$DEST/R201_HU.md"
echo "R201_PRIVATE_RESULT=$DEST/R201.json"
echo "GAME_ACTION_GATE=STOP"
