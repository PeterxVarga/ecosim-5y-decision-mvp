#!/usr/bin/env python3
"""Reproducible, offline P2 indirect-company-effects sensitivity.

NOT a calibrated causal model; the P1->P2 secant is an observational stress scale.
No EcoSim APIs, browser, game writes, bank accounts, or network calls.
"""
from __future__ import annotations
from itertools import combinations
from pathlib import Path
from collections import Counter
import argparse,json,sys,math
from p2_joint_screen import load, conditional_delta, cost_for, direct_eligibility
from r142_proxy_reference import COEFF

ROOT=Path(__file__).resolve().parent
METRICS={'Kisvállalkozások száma':'small', 'Középvállalkozások száma':'medium'}
OBS={
    'p1_fact_small_firms':4765,'p2_plan_small_firms':5226,
    'p1_fact_medium_firms':92,'p2_plan_medium_firms':108,
    'p1_fact_large_firms':25,'p2_plan_large_firms':28,
    'p1_fact_business_factor':50.51,'p2_plan_business_factor':59.85,
}
BUDGETS=(75000,150000,300000,450000)
SCALE_GRID=(0.0,0.05,0.10,0.25,0.5,1.0,2.0,5.0,10.0,20.0)
MIX_GRID=(0.25,1.0,5.0,20.0)

def counts_effect(ids,idx):
    ms={'small':1.0,'medium':1.0}
    matched=[]
    for pid in ids:
        for e in idx[pid]['effects']:
            k=METRICS.get(e['metric'])
            if k:
                ms[k]*=1+float(e['value_percent'])/100.0
                matched.append({'project_id':pid,'metric':e['metric'],'value_percent':e['value_percent']})
    return {'small_delta':OBS['p2_plan_small_firms']*(ms['small']-1),
            'medium_delta':OBS['p2_plan_medium_firms']*(ms['medium']-1),
            'small_multiplier':ms['small'],'medium_multiplier':ms['medium'],
            'records':matched}

def combined_delta(direct, small, medium, ref, scale=1., medium_relative=1.):
    return direct+ref*scale*(small+medium_relative*medium)

def top_key(x):return (-x['modeled_delta'],x['conservative_incremental_p2_cash_requirement'],x['ids'])

def compute():
    data,idx=load();base=data['baseline']; factors=base['p2_plan_factors']
    active={p['id'] for p in idx.values() if p['status_p2']=='Fut'}
    remaining=[i for i in idx if i not in active]
    obs_delta_total=(OBS['p2_plan_small_firms']-OBS['p1_fact_small_firms']
                    +OBS['p2_plan_medium_firms']-OBS['p1_fact_medium_firms']
                    +OBS['p2_plan_large_firms']-OBS['p1_fact_large_firms'])
    factor_delta=OBS['p2_plan_business_factor']-OBS['p1_fact_business_factor']
    assert obs_delta_total==480 and abs(factor_delta-9.34)<1e-9
    secant_factor_per_firm=factor_delta/obs_delta_total
    reference_index_per_firm=secant_factor_per_firm*COEFF['Vállalkozások száma']
    eligible=[i for i in remaining if direct_eligibility([i],idx,active)]
    eligible_set=set(eligible)
    nsmall=nmedium=0
    all_indirect=[]
    for pid in idx:
        for e in idx[pid]['effects']:
            if e['metric'] in METRICS:
                all_indirect.append((pid,e['metric'],e['value_percent']))
                nsmall+=(e['metric']=='Kisvállalkozások száma')
                nmedium+=(e['metric']=='Középvállalkozások száma')
    assert (nsmall,nmedium)==(22,8)
    rows=[]
    for k in range(1,5):
        for ids in combinations(sorted(remaining),k):
            if not direct_eligibility(ids,idx,active):continue
            costs=cost_for(ids,idx)
            if costs['conservative_incremental_p2_cash_requirement']>max(BUDGETS):continue
            direct=conditional_delta(ids,idx,factors)
            ind=counts_effect(ids,idx)
            assert ind['small_delta']>=0 and ind['medium_delta']>=0
            rows.append({'ids':list(ids), 'names':[idx[i]['name'] for i in ids],
                   **costs, 'direct_delta':direct['delta'],
                   'small_added_firms_scenario':ind['small_delta'],
                   'medium_added_firms_scenario':ind['medium_delta'],
                   'unmapped_effect_records':direct['unmapped_count']})
    # Rankings via conditional sensitivity, not source-validated score
    by_budget={}
    for b in BUDGETS:
        valid=[r for r in rows if r['conservative_incremental_p2_cash_requirement']<=b]
        nominal=[]
        for mix in MIX_GRID:
            for scale in SCALE_GRID:
                shortlist=sorted(valid,key=lambda r:(
                    -combined_delta(r['direct_delta'],r['small_added_firms_scenario'],r['medium_added_firms_scenario'],reference_index_per_firm,scale,mix),
                    r['conservative_incremental_p2_cash_requirement'],r['ids']))[:6]
                arr=[{'ids':r['ids'], 'direct_delta':round(r['direct_delta'],9),
                      'indirect_proxy_delta':round(reference_index_per_firm*scale*(r['small_added_firms_scenario']+mix*r['medium_added_firms_scenario']),9),
                      'total_conditional_delta':round(combined_delta(r['direct_delta'],r['small_added_firms_scenario'],r['medium_added_firms_scenario'],reference_index_per_firm,scale,mix),9),
                      'safe_p2_cost':r['conservative_incremental_p2_cash_requirement']}
                     for r in shortlist]
                nominal.append({'medium_count_weight':mix,'secant_reference_multiple':scale,'top6':arr})
        base_case=next(t for t in nominal if t['medium_count_weight']==1 and t['secant_reference_multiple']==0)
        baseline_winner=base_case['top6'][0]['ids']
        equal_weight=[t for t in nominal if t['medium_count_weight']==1]
        winners={tuple(t['top6'][0]['ids']) for t in nominal}
        changed=min((t['secant_reference_multiple'] for t in equal_weight if t['top6'][0]['ids']!=baseline_winner), default=None)
        by_budget[str(b)]={'feasible_combinations':len(valid),
           'direct_only_leader':base_case['top6'][0],
           'reference_equal_weight_1x':next(t for t in nominal if t['medium_count_weight']==1 and t['secant_reference_multiple']==1)['top6'][0],
           'first_leader_flip_equal_firm_weight_grid':changed,
           'distinct_winners_full_grid':sorted([list(t) for t in winners]),
           'scenarios':nominal}
    # Single-project company count effects; counts not necessarily index score.
    project_indirect=[]
    for pid in sorted(idx):
        v=counts_effect([pid],idx)
        if v['records']:
            project_indirect.append({'id':pid,'name':idx[pid]['name'],'status_p2':idx[pid]['status_p2'],
              'records':v['records'],'small_firm_scenario_delta':round(v['small_delta'],8),
              'medium_firm_scenario_delta':round(v['medium_delta'],8),
              'equal_weight_1x_reference_index_delta':round(reference_index_per_firm*(v['small_delta']+v['medium_delta']),9)})
    # Compare near-tie and derive zero crossing analytically when possible.
    def comparison(idsA,idsB):
        ra=next(r for r in rows if r['ids']==idsA);rb=next(r for r in rows if r['ids']==idsB)
        dd=ra['direct_delta']-rb['direct_delta'];cs=ra['small_added_firms_scenario']-rb['small_added_firms_scenario'];cm=ra['medium_added_firms_scenario']-rb['medium_added_firms_scenario'];
        denom=reference_index_per_firm*(cs+cm)
        threshold=-dd/denom if abs(denom)>1e-15 else None
        return {'a_ids':idsA,'b_ids':idsB,'direct_A_minus_B':dd,
                'small_firm_difference_A_minus_B':cs,'medium_firm_difference_A_minus_B':cm,
                'reference_1x_indirect_A_minus_B':denom,
                'equal_weight_crossing_secant_multiple':threshold,
                'crossing_in_nonnegative_scale':threshold is not None and threshold>=0}
    focus=[]
    for a,b in [([4,8,21,33],[4,8,16,33]),([8,21,26,33],[4,8,21,33])]:
        focus.append(comparison(a,b))
    result={
        'schema':'ecosim.p2.indirect_business_sensitivity.v1',
        'status':'OFFLINE_STRESS_TEST_NOT_CAUSAL_ESTIMATE',
        'sources':{'input':'P2_joined_input.json','effect_source':'2026-10-30 TEST Z, unverified P2',
                   'company_counts_source':'2026-11-05 P2 Brave Codex subview P1 FACT P2 PLAN',
                   'index_factor_source':'2026-11-05 P2 summary P1 FACT P2 PLAN'},
        'no_game_writes':True,'data_counts':{
           'project_count':len(idx),'historical_project_effect_count':sum(len(p['effects']) for p in idx.values()),
           'indirect_total':len(all_indirect),'small_effect_count':nsmall,'medium_effect_count':nmedium,
           'projects_with_any_indirect':len(project_indirect),'eligible_non_running_project_ids':eligible,
           'scored_combo_count_once':len(rows)},
        'observation':{**OBS,'observed_company_total_change_all_sizes':obs_delta_total,
            'observed_factor_change':factor_delta,'observational_secant_factor_points_per_added_firm':secant_factor_per_firm,
            'observational_reference_index_points_per_added_firm':reference_index_per_firm,
            'business_factor_aggregate_weight':COEFF['Vállalkozások száma'],
            'warning':'P1->P2 changes cannot identify causal per-project effect, firm-size coefficients, or P2 company growth trajectory.'},
        'assumptions':{'new_project_cap':4,'project_budget_envelopes':BUDGETS,
            'startup_cost':'startup+investment+max(0,maintenance), no partner support netting',
            'indirect_mechanism':'Multiplicative card percentage on P2 displayed small/medium counts only; hypothesis, not proven EcoSim client pathway.',
            'score_proxy':'P1 FACT -> P2 PLAN *observational* secant maps sum of firm count changes to score factor; non-causal, unit exchangeability unproven.',
            'unknown_effects':'Never assumed to be truly zero; 0x scenario is a mathematical reference only.',
            'large_company_project_effects':'Not listed in 30 indirect effects; large-company macro change confounds secant.',
            'factor_saturation':'Unknown; no validated client end-to-end causal score response.'},
        'all_30_indirect_effects':[{'id':pid,'metric':m,'value_percent':v} for pid,m,v in all_indirect],
        'project_indirect':project_indirect,
        'rankings_by_budget':by_budget,
        'focused_pair_comparisons':focus,
        'model_gates':{'p2_plan_saved':'UNKNOWN','project_score_effects_p2_live':'NOT_VALIDATED',
             'company_count_to_factor_causal':'NOT_IDENTIFIABLE','p3_p5_effect':'UNKNOWN',
             'next_action':'No EcoSim write; next highest ROI is historical single-variable P1 observational discrimination or source-specific city formula if available'}
    }
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',default=str(ROOT/'P2_indirect_business_sensitivity.json'))
    args=ap.parse_args()
    result=compute()
    dst=Path(args.out);dst.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('INDIRECT_SCAN=PASS',result['data_counts'])
    print('OBSERVED_REFERENCE_INDEX_PER_COMPANY=',result['observation']['observational_reference_index_points_per_added_firm'])
    for b,d in result['rankings_by_budget'].items():
        print('BUDGET',b,'feasible',d['feasible_combinations'],'direct',d['direct_only_leader']['ids'],
              'indirect_1x',d['reference_equal_weight_1x']['ids'],
              'first_flip_grid',d['first_leader_flip_equal_firm_weight_grid'],
              'distinct_winners_full_grid',d['distinct_winners_full_grid'])
    for p in result['focused_pair_comparisons']:
        print('PAIR',p)
if __name__=='__main__':main()
