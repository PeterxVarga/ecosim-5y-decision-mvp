#!/usr/bin/env bash
# R207 current-readonly only. Run inside the full canonical EcoSim repo.
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO="$(cd -- "$HERE/../.." && pwd)"
python3 -I -B "$HERE/test_first_round.py"
# All inputs are explicit, independent current-round operator source evidence.
# No default/test amounts, market names, screenshot guesses, or game actions.
python3 -I -B "$HERE/first_round.py" --repo-root "$REPO" "$@"
