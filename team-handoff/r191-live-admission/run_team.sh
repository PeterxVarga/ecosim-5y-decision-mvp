#!/usr/bin/env bash
# R194: one entrypoint for historical demonstration or operator-observed current plan.
# No EcoSim browser/network access or game state mutation. The only writes are local evidence.
set -Eeuo pipefail
umask 077

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
PIN='9d2d17d822bb97a210151e269454a0432a1952ae'
usage() {
  cat <<'USAGE'
Offline EcoSim team decision runner. GAME_ACTION_GATE=STOP.

  bash team-handoff/r191-live-admission/run_team.sh historical

  bash team-handoff/r191-live-admission/run_team.sh current \
    --state /path/to/current-state.json \
    --r156-bundle /path/to/r156-immutable-bundle \
    --year1-finance /path/to/observed-finance.json \
    --current-card-catalog /path/to/observed-cards.json \
    --annual-budget 100000 --cap 4

The budget and cap must be explicit, observed/qualified inputs; the future-year
budget remains a hypothetical scenario. The historical mode uses TEST data only.
USAGE
}

MODE="${1:-}"
case "$MODE" in
  historical)
    [[ "$#" -eq 1 ]] || { usage >&2; exit 2; }
    exec bash "$HERE/run_native_r162_r193.sh"
    ;;
  current)
    shift
    ;;
  -h|--help|help)
    usage; exit 0
    ;;
  *)
    usage >&2; exit 2
    ;;
esac

STATE=''; BUNDLE=''; FINANCE=''; CARDS=''; BUDGET=''; CAP=''
while (($#)); do
  (($# >= 2)) || { echo 'HOLD=MISSING_VALUE' >&2; exit 2; }
  case "$1" in
    --state) STATE="$2";;
    --r156-bundle) BUNDLE="$2";;
    --year1-finance) FINANCE="$2";;
    --current-card-catalog) CARDS="$2";;
    --annual-budget) BUDGET="$2";;
    --cap) CAP="$2";;
    *) echo "HOLD=UNRECOGNIZED_OPTION:$1" >&2; exit 2;;
  esac
  shift 2
done
[[ -f "$STATE" && -d "$BUNDLE" && -f "$FINANCE" && -f "$CARDS" ]] || {
  echo 'HOLD=CURRENT_OBSERVATION_FILES_MISSING' >&2; exit 2;
}
[[ "$BUDGET" =~ ^[0-9]+$ && "$CAP" =~ ^[0-9]+$ ]] || {
  echo 'HOLD=EXPLICIT_INTEGER_BUDGET_AND_CAP_REQUIRED' >&2; exit 2;
}
REPO="$(git -C "$HERE" rev-parse --show-toplevel)" || {
  echo 'HOLD=TEAM_GIT_CHECKOUT_REQUIRED' >&2; exit 2;
}
[[ -f "$REPO/team-handoff/r189-r190/tools/bounded_shadow_r189.py" ]] || {
  echo 'HOLD=R189_SHARED_SOURCE_MISSING' >&2; exit 2;
}
[[ "$(git hash-object "$REPO/team-handoff/r189-r190/tools/bounded_shadow_r189.py")" == '5042d7da2d762bd393ab0e6848acee46e2bdbae8' ]] || {
  echo 'HOLD=R189_SHARED_SOURCE_DRIFT' >&2; exit 2;
}
git -C "$REPO" cat-file -e "${PIN}^{commit}" || {
  echo 'HOLD=R162_PIN_NOT_AVAILABLE_IN_LOCAL_GIT_HISTORY' >&2; exit 2;
}
OUT="$(mktemp -d "${TMPDIR:-/tmp}/ecosim-r194-current-XXXXXXXX")"
WORKTREE="$OUT/pinned-r162"
CLEAN=0
cleanup() {
  if ((CLEAN)); then
    git -C "$REPO" worktree remove --force "$WORKTREE" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT
printf 'R194_EVIDENCE_DIR=%s\nGAME_ACTION_GATE=STOP\n' "$OUT"
git -C "$REPO" worktree add --quiet --detach "$WORKTREE" "$PIN"
CLEAN=1
R162="$WORKTREE/ECOSIM_R162_INTEGRITY_REVIEW_RC"
bash "$R162/verify_release_r162.sh" >"$OUT/source_integrity.log" 2>&1
python3 -B -m unittest discover -s "$HERE/tests" -v >"$OUT/local_contract_tests.log" 2>&1
python3 -B "$HERE/tools/run_r191_shadow.py" \
  --repo-root "$R162" \
  --state "$STATE" --mode current-readonly \
  --r156-bundle "$BUNDLE" --year1-finance "$FINANCE" \
  --current-card-catalog "$CARDS" \
  --annual-budget "$BUDGET" --cap "$CAP" \
  --out "$OUT/current_readonly_decision.json" \
  >"$OUT/human_decision_hu.md" 2>"$OUT/runner_stderr.log"
bash "$R162/qualify_r162_once.sh" >"$OUT/r162_historical_qualification.log" 2>&1
printf 'R194_CURRENT_READONLY=PASS_OPERATOR_DECLARED_MODEL_ONLY\n'
printf 'HUMAN_REPORT=%s\n' "$OUT/human_decision_hu.md"
printf 'RECEIPT=%s\nGAME_ACTION_GATE=STOP\n' "$OUT/current_readonly_decision.json"
