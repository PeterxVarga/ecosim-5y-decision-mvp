#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
PROFILE="$REPO/team-handoff/r200-historical-plugplay/profiles/historical_R94_R200.json"
test -s "$PROFILE" || { echo HOLD_MISSING_PRIVATE_R200_PROFILE; exit 4; }
git -C "$REPO" check-ignore -q "$PROFILE" || { echo HOLD_UNSAFE_PUBLIC_SOURCE; exit 9; }
DEST="$(mktemp -d "$HOME/Downloads/ecosim-r202-historical-XXXXXXXX")"
rmdir -- "$DEST"
python3 -I -B "$HERE/tools/calibrate_r202.py" --profile "$PROFILE" --out-dir "$DEST"
python3 -I -B -m unittest discover -s "$HERE/tests" -v
echo "R202_PRIVATE_RESULT=$DEST/R202.json"
echo "R202_PRIVATE_REPORT=$DEST/R202_HU.md"
echo GAME_ACTION_GATE=STOP
