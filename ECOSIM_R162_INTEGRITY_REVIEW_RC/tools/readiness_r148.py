#!/usr/bin/env python3
"""Decision provenance/readiness (does not make a decision or fetch game data)."""
from __future__ import annotations
from json_integrity_r162 import read_json
import json,math
from pathlib import Path
from r142_proxy_reference import COEFF,WEIGHTS
from portfolio_5y import project_index
from city_bridge import computed_index_from_factors


def check_state(state):
    if not isinstance(state,dict):raise ValueError('JSON object state required')
    p=state.get('provenance') or {}; t=state.get('team') or {};m=state.get('market') or {}
    req={'source_evidence_id':p.get('source_evidence_id'),
         'timestamp':p.get('captured_at_local'),
         'team':p.get('team'),'market':p.get('market'),'period':p.get('current_period'),
         'project_cap':m.get('maxProjectPerTurn'),
         'prior_project1':t.get('project1_active_previous_period'),
         'active_projects':t.get('initially_active_project_ids'),
         'current_selections':t.get('already_selected_new_project_ids_current_period'),
         'baseline_index_factors':t.get('baseline_smartcity_factors'),
         'current_index_weights':m.get('smartcity_total_weights'),
         'loan_rates':[m.get('loan_rate_short'),m.get('loan_rate_long'),m.get('loan_rate_variable')],
         'confirmed_spendable_cash':t.get('confirmed_spendable_cash_ecu_by_year'),
         'committed_costs':t.get('committed_costs_ecu_by_year'),
         'official_preview':(state.get('verification') or {}).get('game_preview_index')}
    problems=[]; completed=[]
    def add(k,msg):problems.append({'field':k,'issue':msg})
    for k in ('source_evidence_id','timestamp','team','market','period'):
        if not req[k]:add(k,'MISSING_PROVENANCE')
        else:completed.append(k)
    if type(req['period']) is not int or not 1<=req['period']<=5:add('period','NOT_INTEGER_1_TO_5')
    if type(req['project_cap']) is not int or not 0<=req['project_cap']<=20:add('project_cap','UNKNOWN_OR_INVALID')
    if type(req['prior_project1']) is not bool:add('prior_project1','MUST_EXPLICITLY_BE_BOOLEAN')
    idx=project_index();ids=set(idx)
    for key in ('active_projects','current_selections'):
        arr=req[key]
        if not isinstance(arr,list) or any(type(x) is not int or x not in ids for x in arr) or len(set(arr))!=len(arr):
            add(key,'UNAVAILABLE_OR_INVALID_ID_LIST')
    if isinstance(req['active_projects'],list) and isinstance(req['current_selections'],list) and set(req['active_projects']) & set(req['current_selections']):
        add('current_selections','OVERLAP_WITH_PREVIOUSLY_ACTIVE')
    fac=req['baseline_index_factors']
    if not isinstance(fac,dict) or set(COEFF)-set(fac) or any(type(fac.get(k)) not in (int,float) or not math.isfinite(fac[k]) for k in COEFF):
        add('baseline_index_factors','ALL_FACTOR_VALUES_REQUIRED')
    weights=req['current_index_weights']
    if not isinstance(weights,dict) or set(weights)!=set(WEIGHTS) or any(type(v) not in (int,float) or not math.isfinite(v) or v<0 for v in weights.values()) or abs(sum(weights.values())-1)>1e-9:
        add('current_index_weights','SIX_NONNEGATIVE_WEIGHTS_SUM_TO_ONE')
    rates=req['loan_rates']
    if any(type(v) not in (int,float) or not math.isfinite(v) or v<0 for v in rates):add('loan_rates','ALL_THREE_NONNEGATIVE_RATES_REQUIRED_FOR_LOAN_MODEL')
    # Future years cannot normally be verified from the current period.
    for key in ('confirmed_spendable_cash','committed_costs'):
        vals=req[key]
        if not isinstance(vals,list) or len(vals)!=5 or any(type(x) not in (int,float) or not math.isfinite(x) or x<0 for x in vals):
            add(key,'FIVE_YEAR_CONFIRMED_ENVELOPES_UNAVAILABLE; scenario-only financing remains')
    if req['official_preview'] is None:add('official_preview','NO_SAME_PERIOD_CONTROLLED_PREVIEW')
    derived={}
    if isinstance(fac,dict) and set(COEFF)<=set(fac) and isinstance(weights,dict) and set(WEIGHTS)==set(weights):
        try:derived['observed_factor_index_aggregation']=computed_index_from_factors(fac,weights)['total_index_from_displayed_factors']
        except ValueError:pass
    if type(req['project_cap']) is int and type(req['prior_project1']) is bool and isinstance(req['current_selections'],list):
        derived['nominal_available_new_slots']=max(0,req['project_cap']+int(req['prior_project1'])-len(req['current_selections']))
        derived['server_project_acceptance_confirmed']=False
    return {'schema':'ECOSIM_R148_INPUT_READINESS_V1','fields_observed':completed,
            'specific_missing_or_invalid_evidence':problems,'derived_if_valid':derived,
            'official_state_complete_for_all_future_years':len(problems)==0,
            'actual_game_score_forecast_verified':False,'gameplay_decision':'STOP',
            'does_not_treat_historical_test_as_live':True}


def main():
    import argparse
    from strategy_5y import write_json
    root=Path(__file__).resolve().parent.parent
    p=argparse.ArgumentParser();p.add_argument('--state',default=str(root/'inputs/official_state.template.json'));p.add_argument('--out',default=str(root/'results/R148_OFFICIAL_INPUT_GATE.json'));a=p.parse_args()
    write_json(a.out,check_state(read_json(a.state)))
    print('R148_PROVENANCE_GATE=STOP_UNTIL_VERIFIED; NO_GAME_ACTIONS')
if __name__=='__main__':main()
