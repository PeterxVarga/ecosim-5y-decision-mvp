#!/usr/bin/env bash
# R195 historical/current model-budget tradeoff, reuse EXACT R194 engine twice.
# No game writes, no network, no auto-authorization, never claim global optimum.
set -Eeuo pipefail
umask 077

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
PIN='9d2d17d822bb97a210151e269454a0432a1952ae'
R189_PIN='5042d7da2d762bd393ab0e6848acee46e2bdbae8'

usage() {
cat <<'TEXT'
EcoSim R195 - compare two R194 audited five-year scenarios on identical input.

  bash team-handoff/r191-live-admission/run_tradeoff.sh historical
  bash team-handoff/r191-live-admission/run_tradeoff.sh historical --base-budget 100000 --reserve-budget 90000

  bash team-handoff/r191-live-admission/run_tradeoff.sh current \
    --state /path/to/current_state.json \
    --r156-bundle /path/to/r156_immutable_bundle \
    --year1-finance /path/to/observed_finance.json \
    --current-card-catalog /path/to/observed_35_cards.json \
    --base-budget 100000 --reserve-budget 90000 --cap 4

All financial inputs are explicitly user-declared. This is a model comparison,
not an actual game action. GAME_ACTION_GATE=STOP.
TEXT
}
MODE="${1:-}"
case "$MODE" in
  historical|current) shift;;
  -h|--help|help) usage; exit 0;;
  *) usage >&2; exit 2;;
esac

BASE='';RESERVE='';CAP='';STATE='';BUNDLE='';FINANCE='';CARDS=''
while (($#)); do
  (($#>=2)) || { echo 'HOLD=OPTION_WITHOUT_VALUE' >&2; exit 2; }
  case "$1" in
    --base-budget) BASE="$2";;
    --reserve-budget) RESERVE="$2";;
    --cap) CAP="$2";;
    --state) STATE="$2";;
    --r156-bundle) BUNDLE="$2";;
    --year1-finance) FINANCE="$2";;
    --current-card-catalog) CARDS="$2";;
    *) echo "HOLD=UNKNOWN_OPTION:$1" >&2; exit 2;;
  esac
  shift 2
done

if [[ "$MODE" == 'historical' ]]; then
  [[ -z "$STATE" && -z "$BUNDLE" && -z "$FINANCE" && -z "$CARDS" ]] || { echo 'HOLD=HISTORICAL_LIVE_INPUT_FORBIDDEN' >&2; exit 2; }
  BASE="${BASE:-100000}"; RESERVE="${RESERVE:-90000}"; CAP="${CAP:-4}"
  STATE="$HERE/examples/historical_test_state.json"
  MODE_ARG='historical-test'
else
  [[ -n "$BASE" && -n "$RESERVE" && -n "$CAP" ]] || { echo 'HOLD=EXPLICIT_CURRENT_CAP_BUDGET_REQUIRED' >&2; exit 2; }
  [[ -f "$STATE" && -d "$BUNDLE" && -f "$FINANCE" && -f "$CARDS" ]] || { echo 'HOLD=CURRENT_EVIDENCE_NOT_PRESENT' >&2; exit 2; }
  MODE_ARG='current-readonly'
fi
[[ "$BASE" =~ ^[0-9]{1,12}$ && "$RESERVE" =~ ^[0-9]{1,12}$ && "$CAP" =~ ^[0-9]{1,2}$ ]] || { echo 'HOLD=NONINTEGER_BUDGET_OR_CAP' >&2; exit 2; }
((10#$BASE > 10#$RESERVE && 10#$BASE > 0 && 10#$CAP <= 20)) || { echo 'HOLD=RESERVE_MUST_BE_LOWER_THAN_BASE' >&2; exit 2; }

REPO="$(git -C "$HERE" rev-parse --show-toplevel)" || { echo 'HOLD=GIT_REPOSITORY_REQUIRED' >&2; exit 2; }
[[ "$HERE" == "$REPO/team-handoff/r191-live-admission" ]] || { echo 'HOLD=NOT_COMMITTED_TEAM_PATH' >&2; exit 2; }
[[ -f "$REPO/team-handoff/r189-r190/tools/bounded_shadow_r189.py" ]] || { echo 'HOLD=MISSING_SHARED_R189' >&2; exit 2; }
[[ "$(git hash-object "$REPO/team-handoff/r189-r190/tools/bounded_shadow_r189.py")" == "$R189_PIN" ]] || { echo 'HOLD=R189_HASH_DRIFT' >&2; exit 2; }
git -C "$REPO" cat-file -e "${PIN}^{commit}" || { echo 'HOLD=PINNED_R162_HISTORY_NOT_AVAILABLE' >&2; exit 2; }

OUT="$(mktemp -d "${TMPDIR:-/tmp}/ecosim-r195-tradeoff-XXXXXXXX")"
WORKTREE="$OUT/pinned-r162"
CLEAN=0
cleanup() { if ((CLEAN)); then git -C "$REPO" worktree remove --force "$WORKTREE" >/dev/null 2>&1 || true; fi; }
trap cleanup EXIT
printf 'R195_EVIDENCE_DIR=%s\nR162_PIN=%s\nGAME_ACTION_GATE=STOP\n' "$OUT" "$PIN"
git -C "$REPO" worktree add --quiet --detach "$WORKTREE" "$PIN"
CLEAN=1
R162="$WORKTREE/ECOSIM_R162_INTEGRITY_REVIEW_RC"
bash "$R162/verify_release_r162.sh" >"$OUT/r162_source_integrity.log" 2>&1
python3 -B -m unittest discover -s "$HERE/tests" -v >"$OUT/team_tests.log" 2>&1

ARG=(--repo-root "$R162" --state "$STATE" --mode "$MODE_ARG" --cap "$CAP")
if [[ "$MODE" == 'current' ]]; then
  ARG+=(--r156-bundle "$BUNDLE" --year1-finance "$FINANCE" --current-card-catalog "$CARDS")
fi
python3 -B "$HERE/tools/run_r191_shadow.py" "${ARG[@]}" \
  --annual-budget "$BASE" --out "$OUT/max_receipt.json" \
  >"$OUT/max_hungarian_hu.md" 2>"$OUT/max_stderr.log"
python3 -B "$HERE/tools/run_r191_shadow.py" "${ARG[@]}" \
  --annual-budget "$RESERVE" --out "$OUT/reserve_receipt.json" \
  >"$OUT/reserve_hungarian_hu.md" 2>"$OUT/reserve_stderr.log"
python3 -B "$HERE/tools/compare_r195.py" \
  --max-receipt "$OUT/max_receipt.json" --reserve-receipt "$OUT/reserve_receipt.json" \
  --out-json "$OUT/TRADEOFF.json" --out-md "$OUT/TRADEOFF_HU.md" \
  >"$OUT/compare_stdout.log" 2>"$OUT/compare_stderr.log"
# Run original full native historical qualification AFTER both R194 runs.
bash "$R162/qualify_r162_once.sh" >"$OUT/r162_native_qualification.log" 2>&1
printf 'R195_TWO_SCENARIOS=PASS_PINNED_R162_NATIVE_OFFLINE_ONLY\nGAME_ACTION_GATE=STOP\nREPORT=%s\nRESULT=%s\n' "$OUT/TRADEOFF_HU.md" "$OUT/TRADEOFF.json"
