#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
cd "$(dirname "${BASH_SOURCE[0]}")"
if [[ "${R143_ENABLE_CODEX:-NO}" != "YES" ]]; then
  echo "R143_REFINED_NO_EXECUTION: this release is for review, not a Codex run. Explicit enablement is required for future use."
  exit 0
fi
command -v python3 >/dev/null || { echo "R143_BLOCKED=PYTHON_MISSING"; exit 2; }
command -v codex >/dev/null || { echo "R143_BLOCKED=CODEX_CLI_MISSING"; exit 2; }
python3 -I -B tools/prepare_inputs.py
python3 -I -B tools/portfolio_5y.py   --plan examples/illustrative_plan.json   --state inputs/official_state.template.json   --out results/R143_PROJECT_CASH_CALENDAR.json
python3 -I -B tools/readiness.py
codex exec -C "$PWD"  --sandbox workspace-write  --skip-git-repo-check  -c 'model_reasoning_effort="high"'  -c 'sandbox_workspace_write.network_access=false'  --output-last-message "$PWD/results/CODEX_LAST.md"  - < CODEX_TASK.md
python3 -I -B tools/pack_review.py
