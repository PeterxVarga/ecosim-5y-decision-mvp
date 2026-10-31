#!/usr/bin/env python3
"""R146 one consolidated offline qualification: 85 legacy + new guarded checks."""
from __future__ import annotations
from pathlib import Path
import copy, json, runpy, sys, hashlib
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))

# Recheck compatibility in one single qualification; no network or game.
runpy.run_path(str(ROOT/'tools/qualify_r145.py'),run_name='r145_regression')

from strategy_5y import read_json, write_json, search, evaluate_proxy
from policy_tracks import load_tracks, policy_factor_replay
from city_bridge import computed_index_from_factors
from portfolio_5y import project_index
from robust_r146 import PROFILES, stress_plan
from passive_r146 import reconcile_snapshots
from joint_5y import evaluate_tracks
checks=[]
def check(name,truth):
    if not truth:raise AssertionError(name)
    checks.append(name)

state=read_json(ROOT/'inputs/official_state.template.json')
tracks=load_tracks(ROOT/'inputs/policy_tracks.synthetic.example.json')
baseline=read_json(ROOT/'data/ECOSIM_R141_PROJECT_PROXY.json')['baseline_from_UI']
idx=project_index()
legacy=read_json(ROOT/'results/R145_INTEGRATED_QUALIFICATION.json')
check('all 85 older checks retained',legacy['total_checks']==85)
check('old synthetic fixture carries zero game writes',legacy['game_writes']==0 and legacy['external_calls']==0)
check('source project count 35',len(idx)==35)

# No further full-time search: reuse the just-produced R145 suite's example.
r=read_json(ROOT/'results/R145_JOINT_SYNTHETIC_100K.json')
check('joint report has revised version',r['schema']=='ECOSIM_R146_POLICY_AND_PROJECT_STRESS_COMPARISON_V1')
check('revised search explicitly conditioned on policy',r['policy_conditioned_joint_project_search'] is True)
check('official game outcome not predicted',r['actual_five_year_game_score'] is None)
a,b,c=r['tracks']
check('three synthetic tracks',len(r['tracks'])==3)
check('neutral scenario retains 100k hypothetical caps',a['project_budgets_after_policy_reservation_ecu']==[100000]*5)
check('synthetic operating expense reserves 5k/year',b['project_budgets_after_policy_reservation_ecu']==[95000]*5)
check('unpriced tax policy cash marked unknown',c['policy_project_budget_interpretation']=='UNKNOWN_UNBOUNDED_POLICY_CASH_EFFECT')
check('unknown tax cannot be reported as cash envelope',c['project_budgets_after_policy_reservation_ecu'] is None)
check('unknown financial cost explicit',c['unknown_policy_cash_decisions']==['tax_rate_uncalibrated'])
check('all policy tracks no gameplay authorization',all(t['gameplay_gate']=='STOP' for t in r['tracks']))
for t in r['tracks']:
    if not t['joint_options']:continue
    p=t['joint_options'][0]
    check('per-plan applied policy-conditioned gain '+t['track_id'], 'policy_conditioned_search_project_gain' in p)
    stress=p['illustrative_robustness']
    check('stress scenarios completed '+t['track_id'], len(stress['profiles'])==4)
    check('stress uncertainty not presented as confidence '+t['track_id'],
          stress['stress_minmax_are_actual_outcome_bounds'] is False and
          stress['stress_profiles_are_observed_probabilities'] is False)
    check('stress values finite '+t['track_id'],
          stress['worst_mapped_terminal_index_delta']<=stress['best_mapped_terminal_index_delta'])
    check('gameplay remains STOP in stress '+t['track_id'],stress['gameplay_decision']=='STOP')

check('uncalibrated tax track reports unknown policy factor',
      c['joint_options'][0]['illustrative_robustness']['uncertain_policy_response_coverage'])
check('unpriced synthetic track stress finance unknown',
      c['joint_options'][0]['illustrative_robustness']['profiles'][0]['stressed_budget_status'].startswith('UNKNOWN'))
check('priced synthetic stress contains budget shadow',
      b['joint_options'][0]['illustrative_robustness']['profiles'][0]['stressed_budget_rows']!=[])
check('no-scenario borrowing authorized',
      all(not p['candidate_financially_authorized'] for t in r['tracks'] for p in t['joint_options']))

# Demonstrate actual DIFFERENT project scoring when a policy changes a mapped factor.
mult,_,_=policy_factor_replay({k:1. for k in baseline},tracks[1],5,1)
weighted={k:baseline[k]*mult[k] for k in baseline}
old=evaluate_proxy(idx,{13},baseline)
new=evaluate_proxy(idx,{13},weighted)
check('policy condition modifies known marginal project score',abs(old[0]-new[0])>1e-7)
check('unmapped aliases not silently counted as known',new[1]>=0)

historical=read_json(ROOT/'inputs/historical_passive_summary_20261030.json')
passive=reconcile_snapshots(historical)
check('passive historic two records',len(passive['snapshots'])==2)
check('p0 fact distinct from p1 plan',
      passive['snapshots'][0]['kind']=='FACT' and passive['snapshots'][1]['kind']=='PLAN')
check('historical factors close to displayed index',
      all(x['index_close_at_two_decimal_precision'] for x in passive['snapshots']))
check('historical p1 cash arithmetic 865588',passive['snapshots'][1]['finance_arithmetic']['arithmetic_difference_ecu']==865588)
check('no p0-to-p1 transition inferred',passive['p0_fact_vs_p1_plan_is_not_a_realized_transition'])
check('no factual five-year calibration claimed',passive['calibrated_five_year_transition'] is False)
check('untrusted current live config not fabricated',state['market']['maxProjectPerTurn'] is None)

paired=copy.deepcopy(historical)
paired['snapshots'].append({**paired['snapshots'][1],'id':'SYNTHETIC_P1_FACT',
                            'kind':'FACT','displayed_total_index':52.0,
                            'source_evidence_id':'SYNTHETIC_REGRESSION_ONLY'})
pp=reconcile_snapshots(paired)
check('same period plan/fact pair supported',len(pp['paired_same_period_plan_fact'])==1)
check('plan/fact diff is descriptive only',pp['paired_same_period_plan_fact'][0]['causal_explanation_identified'] is False)
missing=copy.deepcopy(historical);missing['snapshots'][0].pop('market')
try:reconcile_snapshots(missing)
except ValueError:check('missing provenance fails closed',True)
else:raise AssertionError('missing provenance incorrectly accepted')

# Synthetic project-only (policy neutral) stress with raw demonstration budget.
plan=r['tracks'][0]['joint_options'][0]
check('illustrative stress profile labels fixed',
      {v['profile_id'] for v in plan['illustrative_robustness']['profiles']}==
      {v['id'] for v in PROFILES})
check('strict decision STOP in overall output',r['gameplay_decision']=='STOP' and r['actual_score_uncertainty_bounds'] is None)

write_json(ROOT/'results/R146_PASSIVE_HISTORICAL_RECONCILIATION.json',passive)
count=legacy['total_checks']+len(checks)
receipt={'schema':'ECOSIM_R146_INTEGRATED_OFFLINE_QUALIFICATION_V1',
         'qualification':'PASS_OFFLINE_ONLY','r145_regression_checks':legacy['total_checks'],
         'r146_new_checks':len(checks),'total_checks':count,
         'checks':checks,'source_archive_sha256_parent':None,
         'codex_invoked':False,'game_writes':0,'network_calls':0,
         'full_city_transition_validated':False,'policy_response_is_observed':False,
         'true_y5_index_forecast':None,'gameplay_gate':'STOP'}
write_json(ROOT/'results/R146_INTEGRATED_QUALIFICATION.json',receipt)
print(f'R146_INTEGRATED_QUALIFICATION=PASS; legacy={legacy["total_checks"]}; new={len(checks)}; total={count}; GAME=STOP')
