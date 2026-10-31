#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
cd "$(dirname -- "${BASH_SOURCE[0]}")"
python3 -I -B tools/run_evidence_pipeline_r152.py \
 --bundle examples/R152_HISTORICAL_R94_READONLY_PACKET/manifest.json \
 --decision-config inputs/mvp_run.r155_synthetic.json \
 --out-dir results/R155_EVIDENCE_TO_OPERATING_DECISION
