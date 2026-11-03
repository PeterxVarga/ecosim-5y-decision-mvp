#!/usr/bin/env bash
# R198 historical CROSS-MODEL read-only qualification. Uses an existing R195 PASS receipt.
set -Eeuo pipefail
umask 077

[[ "${1:-}" == "--tradeoff" && -n "${2:-}" && "${3:-}" == "" ]] || {
  echo 'Usage: bash run_joint_historical.sh --tradeoff /absolute/path/TRADEOFF.json' >&2; exit 2;
}
TRADEOFF="$(realpath -- "$2")"
HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT="$(cd -- "$HERE/../.." && pwd -P)"
R162="$ROOT/ECOSIM_R162_INTEGRITY_REVIEW_RC"
R196="$ROOT/team-handoff/r196-city-review"
STATE="$ROOT/team-handoff/r191-live-admission/examples/historical_test_state.json"
[[ -f "$TRADEOFF" && -f "$STATE" && -f "$R162/tools/decision_desk_r149.py" && -f "$R196/tools/city_review_r196.py" ]] || { echo 'HOLD_MISSING_SOURCE'; exit 2; }

OUT="$(mktemp -d "${TMPDIR:-/tmp}/ecosim-r198-native-XXXXXXXX")"
python3 - "$R162" "$STATE" "$TRADEOFF" "$OUT" <<'PY'
import json, hashlib, sys, shutil
from pathlib import Path
r162,state,tfile,out=map(Path,sys.argv[1:])
tradeoff=json.loads(tfile.read_text(encoding='utf-8'))
if (tradeoff.get('mode')!='historical-test' or tradeoff.get('source_pin')!='9d2d17d822bb97a210151e269454a0432a1952ae'
    or tradeoff.get('gameplay_gate')!='STOP' or tradeoff.get('financing_approved') is not False):
    raise SystemExit('HOLD_NOT_PINNED_R195_HISTORICAL')
if hashlib.sha256(state.read_bytes()).hexdigest()!=tradeoff.get('input_state_sha256'):
    raise SystemExit('HOLD_ORIGINAL_STATE_SHA_MISMATCH')
shutil.copyfile(state,out/'original_state.json')
cfg=json.loads((r162/'inputs/mvp_run.r155_synthetic.json').read_text(encoding='utf-8'))
cfg['state_path']=str(out/'original_state.json')
for name in ('historical_read_only_snapshots_path','policy_tracks_path','league_observations_path',
             'paired_plan_observations_path','forecast_audit_path','tax_scenarios_path',
             'tax_revenue_scenarios_path','operating_scenarios_path'):
    if cfg.get(name): cfg[name]=str(r162/cfg[name])
(out/'r149_config.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
PY
python3 -B "$R162/tools/decision_desk_r149.py" --config "$OUT/r149_config.json" --out-dir "$OUT/r149" > "$OUT/R149.log" 2>&1
python3 -B "$R196/tools/city_review_r196.py" --tradeoff "$TRADEOFF" --out-json "$OUT/R196.json" --out-md "$OUT/R196.md" > "$OUT/R196.log" 2>&1
python3 -B "$HERE/tools/bridge_r197.py" --tradeoff "$TRADEOFF" --decision-desk "$OUT/r149/DECISION_DESK.json" --city-review "$OUT/R196.json" --out-json "$OUT/R197.json" --out-md "$OUT/R197.md" > "$OUT/R197.log" 2>&1
python3 -B "$HERE/tools/paired_decision_r198.py" --tradeoff "$TRADEOFF" --decision-desk "$OUT/r149/DECISION_DESK.json" --city-review "$OUT/R196.json" --out-json "$OUT/R198.json" --out-md "$OUT/R198.md" > "$OUT/R198.log" 2>&1
python3 - "$OUT" <<'PY'
from pathlib import Path
import json,sys,hashlib
p=Path(sys.argv[1]);a=json.loads((p/'R196.json').read_text());b=json.loads((p/'R197.json').read_text());c=json.loads((p/'R198.json').read_text())
assert a['status']=='HISTORICAL_PROJECT_MODEL_ONLY'
assert b['same_initial_state_verified'] is True and b['citywide_optimality_validated'] is False
assert c['gameplay_gate']=='STOP' and c['complete_city_optimization'] is False and c['funds_authorized'] is False
assert c['r197_source_proof']['r149_sha256']==b['r149_sha256']
manifest={str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*') if f.is_file()}
(p/'R198_MANIFEST.json').write_text(json.dumps({'sha256':manifest,'gameplay_gate':'STOP'},indent=2)+'\n')
print('R198_SAME_STATE_NATIVE=PASS_HISTORY_ONLY')
print('R198_PAIR_STATUS='+c['status'])
print('R198_MODEL_CANDIDATES='+str(c['r149_candidate_count']))
print('R198_MODEL_PAIRS='+str(c['r159_tested_pairs']))
print('R198_PATH='+str(p))
print('GAME_ACTION_GATE=STOP')
PY
