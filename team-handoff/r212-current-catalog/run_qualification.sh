#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO="$(cd -- "$HERE/../.." && pwd)"
python3 -I -B -m unittest discover -s "$REPO/team-handoff/r207-first-round" -p 'test_first_round.py' -q
python3 -I -B "$REPO/team-handoff/r207-first-round/test_r210_current_synthetic_e2e.py"
python3 -I -B "$HERE/test_source_adapted_catalog_r212.py"
echo "R212_NATIVE_E2E=PASS_ADAPTED_CATALOG_PERIOD1_AND_PERIOD2_MOCK"
echo "R212_QUALIFICATION_MODE=OFFLINE_MOCK_NOT_LIVE"
echo "GAME_ACTION_GATE=STOP"
