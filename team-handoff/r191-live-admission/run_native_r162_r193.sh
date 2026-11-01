#!/usr/bin/env bash
# EcoSim R193 native smoke gate: isolated historical-only, NO GAME WRITES.
set -Eeuo pipefail
umask 077

PIN='9d2d17d822bb97a210151e269454a0432a1952ae'
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
if [[ "$HERE" == *'/team-handoff/r191-live-admission' ]]; then
  REPO="$(git -C "$HERE" rev-parse --show-toplevel)"
else
  echo 'HOLD=RUN_SCRIPT_FROM_COMMITTED_TEAM_HANDOFF_PATH' >&2
  exit 2
fi
[[ -f "$HERE/tools/run_r191_shadow.py" ]] || { echo 'HOLD=R193_RUNNER_MISSING' >&2; exit 2; }
[[ -f "$HERE/tools/hungarian_decision_r193.py" ]] || { echo 'HOLD=R193_REPORTER_MISSING' >&2; exit 2; }
[[ -f "$HERE/examples/historical_test_state.json" ]] || { echo 'HOLD=HISTORICAL_FIXTURE_MISSING' >&2; exit 2; }

OUT="$(mktemp -d "${TMPDIR:-/tmp}/ecosim-r193-native-XXXXXXXX")"
WORKTREE="$OUT/pinned-r162"
CLEAN=0
cleanup() {
  if (( CLEAN )); then
    git -C "$REPO" worktree remove --force "$WORKTREE" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

printf 'R193_EVIDENCE_DIR=%s\n' "$OUT"
printf 'SOURCE_PIN=%s\n' "$PIN"
printf 'GAME_ACTION_GATE=STOP\n'

# Must be a genuine Git checkout at the immutable R162 commit; no ad-hoc copy.
git -C "$REPO" cat-file -e "${PIN}^{commit}" || { echo 'HOLD=R162_PIN_NOT_IN_LOCAL_GIT_OBJECT_DATABASE' >&2; exit 2; }
git -C "$REPO" worktree add --quiet --detach "$WORKTREE" "$PIN"
CLEAN=1
ROOT="$WORKTREE/ECOSIM_R162_INTEGRITY_REVIEW_RC"
[[ -f "$ROOT/qualify_r162_once.sh" ]] || { echo 'HOLD=R162_RELEASE_ROOT_MISSING' >&2; exit 2; }

# Perform read-only source integrity first, while the pinned worktree is clean.
bash "$ROOT/verify_release_r162.sh" > "$OUT/r162_release_guard.log" 2>&1

# R189+R191+R192+R193 local contract regression.
python3 -B -m unittest discover -s "$HERE/tests" -v > "$OUT/r193_tests.log" 2>&1

# Explicit historical-only illustration: 100000 is NOT spendable live budget.
python3 -B "$HERE/tools/run_r191_shadow.py" \
  --repo-root "$ROOT" \
  --state "$HERE/examples/historical_test_state.json" \
  --mode historical-test \
  --annual-budget 100000 \
  --cap 4 \
  --out "$OUT/historical_r193_receipt.json" \
  > "$OUT/r193_human_report_hu.txt" 2> "$OUT/r193_stderr.log"

# Verify the produced recommendation + STOP contract independently of runner.
python3 -I -B - "$OUT/historical_r193_receipt.json" <<'PY' > "$OUT/r193_assertion.log"
import json,sys
from pathlib import Path
p=Path(sys.argv[1]);r=json.loads(p.read_text(encoding='utf-8'))
assert r['gameplay_gate']=='STOP'
assert r['mode']=='historical-test'
assert r['r162_source_pin']=='9d2d17d822bb97a210151e269454a0432a1952ae'
assert r['r162_result_game_action']=='STOP'
assert r['actual_gameplay_approved'] is False
assert r['human_explanation_hu']['schema']=='ECOSIM_R193_HUMAN_DECISION_EXPLANATION_V1'
assert 'Mit válasszunk most' in r['human_explanation_hu']['markdown']
assert r['human_explanation_hu']['markdown'].startswith('# Ötéves projektjavaslat – TÖRTÉNETI TESZT')
assert not r['independent_replay']['hard_violations']
print('R193_NATIVE_SMOKE_ASSERTIONS=PASS GAME_ACTION_GATE=STOP')
PY

# Qualification can write its historical evidence into the pinned worktree.
# Run AFTER the read-only pinned R193 smoke; capture logs outside the worktree.
bash "$ROOT/qualify_r162_once.sh" > "$OUT/r162_native_qualification.log" 2>&1

printf 'R193_NATIVE_E2E=PASS_OFFLINE_HISTORICAL_ONLY\n'
printf 'GAME_ACTION_GATE=STOP\n'
printf 'LOGS=%s\n' "$OUT"
