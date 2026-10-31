#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
cd "$(dirname -- "${BASH_SOURCE[0]}")"
# Offline only. Does NOT open the EcoSim website, change any data, or call Codex.
python3 -I -B tools/decision_desk_r149.py "$@"
