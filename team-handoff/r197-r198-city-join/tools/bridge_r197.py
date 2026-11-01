#!/usr/bin/env python3
"""R197 read-only, provenance-locked cross-tab report. No optimization or game writes."""
import argparse, hashlib, json, math
from pathlib import Path

SCHEMA='ECOSIM_R197_SHARED_STATE_CITY_DECISION_V1'
HOLD='HOLD_UNVERIFIED_CITYWIDE_DECISION'
KEYS=('r153_source_backed_tax_sensitivity','r154_source_four_tax_fiscal_tradeoffs','r155_source_operating_cash_tradeoffs','r158_annual_partial_cash_timing')

def load(path):
    data=Path(path).read_bytes()
    if len(data)>10_000_000: raise ValueError('OVERSIZED_JSON')
    def pairs(xs):
        d={}
        for k,v in xs:
            if k in d: raise ValueError('DUPLICATE_JSON_KEY')
            d[k]=v
        return d
    def real(v):
        x=float(v)
        if not math.isfinite(x):raise ValueError('NONFINITE_JSON')
        return x
    return json.loads(data.decode('utf-8'),object_pairs_hook=pairs,parse_float=real,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('NONFINITE_JSON'))), hashlib.sha256(data).hexdigest()

def assemble(tradeoff,tradeoff_sha,policy,policy_sha,city=None,city_sha=None):
    if tradeoff.get('schema')!='ECOSIM_R195_TWO_ENVELOPE_TRADEOFF_V1' or tradeoff.get('gameplay_gate')!='STOP' or tradeoff.get('financing_approved') is not False:raise ValueError('R195_PROOF_GATE_FAILED')
    if policy.get('schema')!='ECOSIM_R149_OFFLINE_DECISION_DESK_RESULT_V1' or policy.get('gameplay_gate')!='STOP' or policy.get('game_writes')!=0:raise ValueError('R149_PROOF_GATE_FAILED')
    pinputs=policy.get('inputs') or {}
    inp=pinputs.get('state') or pinputs.get('read_only_capture') or {}
    if inp.get('sha256')!=tradeoff.get('input_state_sha256'):raise ValueError('STATE_HASH_MISMATCH')
    if tradeoff.get('mode')=='historical-test':
        if policy.get('run_mode')!='HISTORICAL_ILLUSTRATION':raise ValueError('HISTORICAL_MODE_MISMATCH')
    elif tradeoff.get('mode')=='current-readonly':
        if policy.get('run_mode')!='CURRENT_SNAPSHOT_REVIEW':raise ValueError('CURRENT_MODE_MISMATCH')
    else:raise ValueError('UNKNOWN_R195_MODE')
    if city is None:
        city_status='NOT_PROVIDED'
    else:
        if city.get('schema')!='ECOSIM_R196_CITY_CROSS_TAB_REVIEW_V1' or city.get('r195_result_sha256')!=tradeoff_sha or city.get('r195_input_state_sha256')!=tradeoff.get('input_state_sha256') or city.get('gameplay_gate')!='STOP':raise ValueError('R196_PROOF_GATE_FAILED')
        city_status=city.get('status')
    model_rows=[]
    for key in KEYS:
        mod=policy.get(key)
        if not isinstance(mod,dict) or mod.get('gameplay_gate')!='STOP':raise ValueError('MISSING_OR_UNSAFE_MODEL_'+key)
        source=mod.get('source_class')
        model_rows.append({'model':key,'source_class':source,'status':mod.get('status','CONDITIONAL_COMPONENT_ONLY'), 'sha256':hashlib.sha256(json.dumps(mod,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()})
    tax=policy[KEYS[0]]; fiscal=policy[KEYS[1]]; operating=policy[KEYS[2]]; timing=policy[KEYS[3]]
    source_classes={x['source_class'] for x in model_rows}
    if len(source_classes)!=1 or None in source_classes:raise ValueError('PARTIAL_MODEL_SOURCE_MODE_MISMATCH')
    if tradeoff.get('mode')=='current-readonly' and ('SYNTHETIC_TEST_ONLY' in source_classes):raise ValueError('SYNTHETIC_MODE_FORBIDDEN_IN_CURRENT')
    if policy.get('start_year')!=tradeoff['annual_comparison'][0]['year']:raise ValueError('START_YEAR_MISMATCH')
    # Never merge tax-policy scenario scores into R195 project scores: distinct candidate pools.
    return {'schema':SCHEMA,'status':HOLD,'mode':tradeoff['mode'],'source_state_sha256':inp['sha256'],'r195_sha256':tradeoff_sha,'r149_sha256':policy_sha,'r196_sha256':city_sha,'r196_status':city_status,'model_components':model_rows,'source_class':next(iter(source_classes)),'r195_project_scores':{'max':tradeoff['max_model_score'],'reserve':tradeoff['reserve_model_score']},'cross_model_score_comparable':False,'cross_model_cash_additive_to_budget':False,'same_initial_state_verified':True,'same_policy_scenario_or_candidate_verified':False,'citywide_optimality_validated':False,'actual_finance_approved':False,'gameplay_gate':'STOP','next_steps':['Current same-period operator export across ten tabs','Verify year-one financial residual and financing conditions','Produce a policy-track and project identity join before citywide candidate ranking','Run paired PLAN-to-FACT calibration and independent review']}

def render(o):
    lines=['# EcoSim R197 – közös városi döntési dosszié','',f'**Státusz:** `{o["status"]}` · **Játékbeli kapu:** `STOP`','', '## Kiinduló állapot',f'Azonos R195 és R149 állapothash: `{o["source_state_sha256"]}`.',f'R196 tízfüles ellenőrzés: `{o["r196_status"]}`.','', '## Meglévő, azonos kiindulású részmodellek', '| Modul | Forrásosztály | Állapot |','|---|---|---|']
    for x in o['model_components']:lines.append(f'| `{x["model"]}` | `{x["source_class"]}` | `{x["status"]}` |')
    lines+=['','## Amit az összevetés NEM jelent','A projekttervek és a külön adó-/díj-/intézményi modellfuttatás **eltérő jelölt- és policy-pályákat** használhat. Ezért a pontszámok, részleges bevételek és cash-flow értékek nem összeadhatók, és a rangsor nem teljes városoptimális döntés.','A hitel, támogatás, teljes pénzügyi egyenleg, lakossági és vállalati visszacsatolás továbbra sem igazolt.', '', '**A következő lépés az azonos projektjelölt + adópálya + működési pálya összerendelése, ellenőrzött aktuális állapoton. Játékbeli művelet nincs.**','']
    return '\n'.join(lines)

def main():
    p=argparse.ArgumentParser();p.add_argument('--tradeoff',required=True);p.add_argument('--decision-desk',required=True);p.add_argument('--city-review');p.add_argument('--out-json',required=True);p.add_argument('--out-md',required=True);a=p.parse_args()
    paths=[Path(v).resolve() for v in (a.tradeoff,a.decision_desk,a.out_json,a.out_md,*([a.city_review] if a.city_review else []))]
    if len(set(paths))!=len(paths) or Path(a.out_md).exists() or Path(a.out_json).exists():p.error('HOLD_OUTPUT_COLLISION')
    try:
        t,ts=load(a.tradeoff);d,ds=load(a.decision_desk);c,cs=load(a.city_review) if a.city_review else (None,None);o=assemble(t,ts,d,ds,c,cs)
    except (ValueError,TypeError,KeyError,OSError) as e:p.error('HOLD_'+str(e))
    Path(a.out_json).parent.mkdir(parents=True,exist_ok=True);Path(a.out_md).parent.mkdir(parents=True,exist_ok=True)
    with open(a.out_json,'x',encoding='utf-8') as f:json.dump(o,f,ensure_ascii=False,indent=2,allow_nan=False)
    with open(a.out_md,'x',encoding='utf-8') as f:f.write(render(o))
    print('R197_SHARED_STATE=PASS_OFFLINE_LINKAGE_ONLY CITYWIDE=HOLD GAME_ACTION_GATE=STOP')
if __name__=='__main__':main()
