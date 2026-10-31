#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
cd "$(dirname -- "${BASH_SOURCE[0]}")"
python3 -I -B tools/readonly_intake_r156.py \
  --export capture/R156_HISTORICAL_TEST_EXPORT.json \
  --out-dir results/R156_HISTORICAL_FULL_DEMO \
  --decision-config inputs/mvp_run.r155_synthetic.json
