#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
cd "$(dirname -- "${BASH_SOURCE[0]}")"
# Only local, stdlib Python; no Codex, browser or EcoSim state changes.
python3 -I -B tools/strategy_5y.py "$@"
