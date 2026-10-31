#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
cd "$(dirname -- "${BASH_SOURCE[0]}")"
python3 -I -B tools/decision_desk_r149.py --config inputs/mvp_run.r157_robust_historical.json --out-dir results/R159_HISTORICAL_FALSIFICATION_DEMO
