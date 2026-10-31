#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
cd "$(dirname -- "${BASH_SOURCE[0]}")"
python3 -I -B tools/run_evidence_pipeline_r152.py \
  --bundle examples/R152_HISTORICAL_R94_READONLY_PACKET/manifest.json \
  --decision-config inputs/mvp_run.r154_synthetic.json \
  --out-dir results/R154_EVIDENCE_TO_FOUR_TAX_DECISION
