#!/usr/bin/env python3
"""One consolidated qualification of R144 legacy + R145 policy integration."""
from __future__ import annotations
import copy, json, runpy, sys, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))
# R144 suite runs ONCE; no parallel tests, game connection or network.
runpy.run_path(str(ROOT/'tools/qualify_integrated.py'),run_name='r144_included')
from strategy_5y import read_json, search
from portfolio_5y import project_index
from policy_tracks import (load_tracks, policy_factor_replay, policy_money_replay,
                           cost_reservation_for_year, replay_policy_joint)
from joint_5y import evaluate_tracks,combine_counterfactual_cash,render_joint_md
from city_bridge import computed_index_from_factors

checks=[]
def check(name,ok):
    if not ok:raise AssertionError(name)
    checks.append(name)

state=read_json(ROOT/'inputs/official_state.template.json')
tracks=load_tracks(ROOT/'inputs/policy_tracks.synthetic.example.json')
check('three explicitly synthetic tracks recognized',len(tracks)==3 and all(t['mode']=='SYNTHETIC_TEST_ONLY' for t in tracks))
check('no-policy track has zero reserved cost',cost_reservation_for_year(tracks[0],1)==0)
check('synthetic policy annual cost reserved',cost_reservation_for_year(tracks[1],1)==5000)
check('synthetic persistent annual cost reserved in year5',cost_reservation_for_year(tracks[1],5)==5000)
check('unknown tax policy cannot be treated as extra project money',cost_reservation_for_year(tracks[2],1)==0 and policy_money_replay(tracks[2],1,1)['complete'] is False)
baseline=read_json(ROOT/'data/ECOSIM_R141_PROJECT_PROXY.json')['baseline_from_UI']
f,applied,missing=policy_factor_replay(baseline,tracks[1],5,1)
check('two-percent relative factor replay remains symbolic hypothesis',abs(f['Lakosság képzettsége']-baseline['Lakosság képzettsége']*1.02)<1e-10 and len(applied)==1 and not missing)
f,applied,missing=policy_factor_replay(baseline,tracks[2],5,1)
check('unknown policy factor is explicitly unresolved',len(missing)==1 and f==baseline)
f,applied,missing=policy_factor_replay(baseline,tracks[1],5,2)
check('replanning omits policy effects already contained in fresh baseline',f==baseline)
try:
    load_tracks(ROOT/'inputs/official_state.template.json')
    raise AssertionError('bad schema accepted')
except ValueError:check('wrong policy schema rejected',True)
# Fresh project search per track for all five years. No future parameter sourced
# from R94 p1 finance as available cash.
report=evaluate_tracks(state,1,tracks,[100000.]*5,4,6,15)
check('all supplied tracks evaluated with legacy engine',len(report['tracks'])==3)
check('overall gameplay STOP and score prediction null',report['gameplay_decision']=='STOP' and report['actual_five_year_game_score'] is None)
clean=report['tracks'][0];synth=report['tracks'][1];unknown=report['tracks'][2]
check('no-policy track retains full hypothetical budget',clean['project_budgets_after_policy_reservation_ecu']==[100000.]*5)
check('synthetic policy spending reduces each project envelope',synth['project_budgets_after_policy_reservation_ecu']==[95000.]*5)
check('unknown track leaves unprovided finance response unknown',unknown['joint_options'][0]['missing_policy_factor_actions']>0)
check('unknown action never implies actual predicted index',unknown['joint_options'][0]['joint_factor_counterfactual_by_year'][-1]['actual_index_forecast'] is None)
check('no track financially approved',all(not p['financial_funding_proof'] for t in report['tracks'] for p in t['joint_options']))
check('three years from now implies strict no-cash certainty',all(p['joint_cash_counterfactual']['status']=='UNKNOWN_NO_EXPLICIT_NONPROJECT_CASH_SCENARIO' for t in report['tracks'] for p in t['joint_options']))
check('markdown generated with uncertainty / no writes', 'nem validált' in render_joint_md(report) and 'Játékbeli módosítás: 0' in render_joint_md(report))
check('synthetic track has different joint factor outcome than neutral if same plan chosen',
      (abs(synth['joint_options'][0]['joint_terminal_counterfactual_delta']-synth['joint_options'][0]['project_heuristic_terminal_proxy_delta'])>.000001))
# Explicitly entered scenario cash flow path requires nonoverlap flags.
sc=copy.deepcopy(state)
sc['finance_counterfactual']={'mode':'EXPLICIT_HYPOTHETICAL_NONPROJECT_NET_ONLY',
    'initial_uncommitted_cash_ecu':100000,'annual_nonproject_net_cash_ecu':[100000.]*5,
    'assumption_note':'Synthetic-only diagnostic; NOT official EcoSim cash',
    'nonproject_flow_excludes_policy_track':True}
ledger=evaluate_tracks(sc,1,tracks,[100000.]*5,4,2,5)
check('paired hypothetical cash scenario can be evaluated', ledger['tracks'][1]['joint_options'][0]['joint_cash_counterfactual']['years'][0]['cash_if_all_declared_assumptions_hold_ecu'] is not None)
check('unknown cash action causes null cash forecast',ledger['tracks'][2]['joint_options'][0]['joint_cash_counterfactual']['years'][0]['cash_if_all_declared_assumptions_hold_ecu'] is None)
sc2=copy.deepcopy(sc);sc2['finance_counterfactual'].pop('nonproject_flow_excludes_policy_track')
blocked=evaluate_tracks(sc2,1,tracks,[100000.]*5,4,1,4)
check('missing no-overlap declaration blocks policy cash calculation',blocked['tracks'][1]['joint_options'][0]['joint_cash_counterfactual']['status']=='UNKNOWN_POSSIBLE_DOUBLE_COUNT_OF_OPERATING_POLICY')
poor=evaluate_tracks(state,1,[tracks[1]],[2000.]*5,4,2,5)
check('policy action greater than envelope explicitly infeasible',poor['tracks'][0]['status']=='INFEASIBLE_UNDER_SCENARIO_RESERVATIONS')
check('policy cash never expands known budget', all(x<=100000 for x in synth['project_budgets_after_policy_reservation_ecu']))
# An R145 synthetic scenario never claims observed coefficients, passivity is intact.
check('game independent and no web',report['game_writes']==0 and report['external_calls']==0)
# Save a reproducible example and updated coverage receipt.
from strategy_5y import write_json
write_json(ROOT/'results/R145_JOINT_SYNTHETIC_100K.json',report)
(ROOT/'results/R145_JOINT_SYNTHETIC_100K.md').write_text(render_joint_md(report),encoding='utf8')
r144=read_json(ROOT/'results/R144_INTEGRATED_QUALIFICATION.json')
check('R144 legacy qualification remains 59 PASS',r144['check_count']==59)
receipt={'release':'R145_INTEGRATED_POLICY_SCENARIO_ENGINE',
         'qualification':'PASS_OFFLINE_ONLY',
         'r144_checks':r144['check_count'],
         'r145_checks':len(checks),
         'total_checks':r144['check_count']+len(checks),
         'checks':checks,
         'test_projects':35,
         'scenario_tracks_examined':len(tracks),
         'registered_policy_categories':['tax','service_fee','institution_capacity','staffing_payroll','transport','environment','social','other'],
         'source_r144_archive_sha256':None,
         'current_market_values_verified':False,
         'full_operating_policy_response_model':False,
         'official_year5_index_forecast':None,
         'server_finance_and_credit_validated':False,
         'synthetic_example_only':True,
         'game_writes':0,
         'external_calls':0,
         'gameplay_decision':'STOP'}
write_json(ROOT/'results/R145_INTEGRATED_QUALIFICATION.json',receipt)
print('R145_INTEGRATED_QUALIFICATION=PASS; legacy='+str(r144['check_count'])+ '; new='+str(len(checks))+'; total='+str(receipt['total_checks'])+'; game=STOP')
