#!/usr/bin/env python3
"""EcoSim R3 offline empirical 'company count' indicator hypothesis, no network/game access.

Run from folder containing the R2 p2_joint_screen.py, effect_replay_r147.py,
r142_proxy_reference.py, and P2_joined_input.json, with observation JSON passed in.
No console secrets, cookies, browser access, game modifications, or writes except output JSON.
"""
import argparse, sys, json, math
from pathlib import Path
from itertools import combinations

ROOT=Path(__file__).resolve().parent
# Support placement alongside R2 source in the checked-in ZIP or in /mnt/data.
if not (ROOT/'p2_joint_screen.py').exists():sys.path.insert(0,str(ROOT/'ecosim_p2_joint_work'))
from p2_joint_screen import load, conditional_delta, cost_for, direct_eligibility
from r142_proxy_reference import COEFF

BUDGETS=(75000,150000,300000,450000)
INDIRECT_METRICS={'Kisvállalkozások száma':'small','Középvállalkozások száma':'medium'}

def total(d):return sum(d[k] for k in ('small','medium','large'))
def f_yoy(curr,prev):return 50+100*(curr/prev-1)
def f_old_50_ratio(curr,prev):return 50*curr/prev

def from_counts(counts):return {'small':int(counts['small']),'medium':int(counts['medium']),'large':int(counts['large'])}

def round2_compatible(predict,observed):return round(predict,2)==round(observed,2)

def rounding_range(n_now,n_prev,classes=3):
    d=classes/2 # displayed integer amount for each of three classes; hidden rounding +/-0.5
    return [f_yoy(n_now-d,n_prev+d),f_yoy(n_now+d,n_prev-d)]

def contribution(ids, projects, live):
    mult={'small':1.,'medium':1.};matched=[]
    for i in ids:
        for e in projects[i]['effects']:
            kind=INDIRECT_METRICS.get(e['metric'])
            if kind:
                mult[kind]*=(1+float(e['value_percent'])/100.)
                matched.append({'project_id':i,'size':kind,'shown_percent':e['value_percent']})
    added={kind:live[kind]*(mult[kind]-1) for kind in mult}
    return added,matched

def sample(label,prev,now,factor,source):
    p=f_yoy(now,prev)
    return {'label':label,'source':source,'previous_total_displayed':prev,
            'current_total_displayed':now,'observed_factor':factor,
            'hypothesis_yoy_prediction':round(p,9),
            'difference_observed_minus_prediction':round(factor-p,9),
            'exact_to_displayed_2_decimals':round2_compatible(p,factor),
            'compatible_with_integer_rounding':rounding_range(now,prev)[0]-.005 <= factor <= rounding_range(now,prev)[1]+.005,
            'alternative_50_times_growth':round(f_old_50_ratio(now,prev),9)}

def compute(inp):
    facts=json.loads(Path(inp).read_text(encoding='utf8'))
    p0=facts['p0_base'];n0=total(p0)
    records=[]
    for row in facts['p1_all_teams']:
        n=sum(int(row['p1_'+k]) for k in ('small','medium','large'))
        records.append(sample('I P1 FACT: '+row['team'],n0,n,float(row['p1_business_factor']),facts['p1_xlsx_source']))
    zrecords=[]
    for z in facts['p1_z_historical_samples']:
        zrecords.append(sample('Z TEST P1: '+z['source'],z['previous_company_total'],z['plan_company_total'],z['plan_factor'],z['summary_path']))

    p2=facts['p2_current'];prev=from_counts(p2['p1_fact_company_sizes']); now=from_counts(p2['p2_plan_company_sizes'])
    n1=total(prev);n2=total(now)
    p2_sample=sample('I P2 PLAN',n1,n2,float(p2['p2_plan_factor']),'+'.join(p2['source_files']))
    delta_range=rounding_range(n2,n1)
    assert n0==4857 and n1==4882 and n2==5362
    assert p2_sample['compatible_with_integer_rounding']
    assert sum(r['exact_to_displayed_2_decimals'] for r in records)==6
    assert all(r['compatible_with_integer_rounding'] for r in records+zrecords)
    assert all(r['exact_to_displayed_2_decimals'] for r in zrecords)

    source,idx=load();assert len(idx)==35
    pB=facts['p1_project_B_historical_control'];ids=pB['projects'];assert ids==[4,13,21,27]
    zbase=facts['p1_z_historical_samples'][1]['raw_by_size']
    zcurr={k:zbase[k][1] for k in ('small','medium','large')}
    addedB, effectsB=contribution(ids,idx,zcurr)
    predicted_B_delta=100*(addedB['small']+addedB['medium'])/n0
    observed_B_delta=pB['trial_factor']-pB['prior_factor']
    assert pB['rollback_factor']==pB['prior_factor'] and pB['save_count']==0
    assert abs(observed_B_delta-predicted_B_delta)<.012  # display rounding + percent rounding

    c=COEFF['Vállalkozások száma']
    r2_secant=(p2['p2_plan_factor']-p2['p1_fact_factor'])/(n2-n1)
    r3_per_company_factor=100/n1
    r3_per_company_index=c*r3_per_company_factor
    r2_per_company_index=c*r2_secant
    active={i for i,p in idx.items() if p['status_p2']=='Fut'}
    remaining=sorted(set(idx)-active); assert len(active)==10 and len(remaining)==25
    eligible=[i for i in remaining if direct_eligibility([i],idx,active)]
    baselines=source['baseline']['p2_plan_factors']
    combos=[]
    for k in range(1,5):
        for ids0 in combinations(remaining,k):
            ids=list(ids0)
            if not direct_eligibility(ids,idx,active):continue
            cost=cost_for(ids,idx)['conservative_incremental_p2_cash_requirement']
            if cost>max(BUDGETS):continue
            direct=conditional_delta(ids,idx,baselines)['delta']
            added,_=contribution(ids,idx,now)
            combos.append({'ids':ids,'cost':cost,'direct':direct,'added_small':added['small'],'added_medium':added['medium']})
    assert len(combos)==12386
    def score(row, coefficient,medium_weight=1):
        return row['direct']+coefficient*(row['added_small']+medium_weight*row['added_medium'])
    standings={}
    for b in BUDGETS:
        valid=[r for r in combos if r['cost']<=b]
        models={'direct':0.,'old_P1_P2_secant':r2_per_company_index,'year_on_year_hypothesis':r3_per_company_index}
        leaders={}
        for key,coeff in models.items():
            top=sorted(valid,key=lambda r:(-score(r,coeff),r['cost'],r['ids']))[:4]
            leaders[key]=[{'ids':r['ids'],'cost':r['cost'],
                           'conditional_index_delta':round(score(r,coeff),9),
                           'direct_delta':round(r['direct'],9),
                           'small_extra':round(r['added_small'],6),
                           'medium_extra':round(r['added_medium'],6)} for r in top]
        standings[str(b)]={'feasible_combinations':len(valid),'leaders':leaders}
    key=(4,8,16,33),(4,8,21,33)
    x=next(r for r in combos if tuple(r['ids'])==key[0]);y=next(r for r in combos if tuple(r['ids'])==key[1]);
    old_pair=score(x,r2_per_company_index)-score(y,r2_per_company_index)
    new_pair=score(x,r3_per_company_index)-score(y,r3_per_company_index)
    denom=r3_per_company_index*((x['added_small']+x['added_medium'])-(y['added_small']+y['added_medium']))
    threshold=-(x['direct']-y['direct'])/denom if denom else None
    assert threshold is not None and threshold>0
    return {
      'schema':'ecosim.business-factor.empirical-reconstruction.r3',
      'status':'STRONGLY_SUPPORTED_HYPOTHESIS_NOT_SERVER_SOURCE',
      'no_game_writes':True,
      'formula_hypothesis':'50 + 100*(current_period_company_count/previous_period_company_count - 1)',
      'p0_company_total':n0,
      'samples':{'p1_teams':records,'test_round_z_p1':zrecords,'p2_plan':p2_sample},
      'fit':{
        'p1_fact_displayed_2_decimal_exact':sum(r['exact_to_displayed_2_decimals'] for r in records),
        'p1_fact_samples_total':len(records),
        'p1_fact_rounding_compatible':sum(r['compatible_with_integer_rounding'] for r in records),
        'historical_test_z_two_dec_exact':sum(r['exact_to_displayed_2_decimals'] for r in zrecords),
        'p2_yoy_prediction_using_rounded_counts':p2_sample['hypothesis_yoy_prediction'],
        'p2_actual_factor':p2_sample['observed_factor'],
        'p2_yoy_bounds_if_count_rounded_to_integer':delta_range,
        'p2_cumulative_since_p0_prediction':f_yoy(n2,n0),
        'p2_wrong_50_times_yoy_growth_prediction':f_old_50_ratio(n2,n1),
        'implied_previous_company_total_if_p2_total_exact':n2/(1+(p2['p2_plan_factor']-50)/100)
      },
      'controlled_historical_preview':{
         'projects':pB['projects'],'before_factor':pB['prior_factor'],'after_factor':pB['trial_factor'],
         'rollback_factor':pB['rollback_factor'],'observed_factor_delta':round(observed_B_delta,9),
         'project_card_additional_company_estimate':addedB,
         'project_card_effects':effectsB,'predicted_factor_delta_under_hypothesis':round(predicted_B_delta,9),
         'source':pB['source_zip']+'!'+pB['source_inside_zip'],
         'caveat':'Four projects toggled together, after-project company-count table missing; supports order of magnitude but does not isolate individual project contributions.'
      },
      'p2_model_coefficients':{
         'reference_period_displayed_company_total':n1,
         'company_factor_weight_within_29_factor_proxy':c,
         'r2_observational_secant_factor_per_firm':r2_secant,
         'r3_yoy_factor_per_firm_at_displayed_previous_count':r3_per_company_factor,
         'r2_observational_index_per_firm':r2_per_company_index,
         'r3_yoy_hypothetical_index_per_firm':r3_per_company_index,
         'r3_to_r2_ratio':r3_per_company_index/r2_per_company_index,
         'interpretation':'R3 maps project-conditional extra firms to index proxy; source formula, per-project dynamics, rounding, fiscal carryover still unknown.'
      },
      'p2_portfolio_screen':{
         'scenario_note':'Historical card effects, hypothetical cash budgets, max 4 starts; no P2 live project preview.',
         'evaluated_unique_feasible_within_450000':len(combos),
         'by_budget':standings,
         'focus_450k_16_vs_21':{
           'ids_A':list(key[0]),'ids_B':list(key[1]),
           'old_R2_A_minus_B_conditional_index':old_pair,
           'new_R3_A_minus_B_conditional_index':new_pair,
           'r3_yoy_hypothesis_zero_crossing_scale':threshold,
           'warning':'Forecast difference within model only, not proven performance.'}
      },
      'limitations':[
         'No authoritative EcoSim server formula/source was located.',
         'Displayed integer business counts may hide fractional values, which prevents exact two-decimal reconstruction in every observation.',
         'Cross-sectional association and joint four-project preview do not identify causal weights for small vs medium businesses.',
         'P2 is a plan, not realized fact; save state unknown.',
         'Project effect percentages date from an earlier TEST-Z project catalog, though P2 card costs/statuses were rechecked.',
         'Large-company dynamics, delayed effects, saturation and P3-P5 evolution remain unknown.'
      ]
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',default=str(ROOT/'EcoSim_P2_vallalkozasszam_forrasmegfigyelesek_20261105.json'))
    ap.add_argument('--output',default=str(ROOT/'EcoSim_P2_vallalkozasszam_empirikus_R3_20261105.json'))
    args=ap.parse_args()
    result=compute(args.input)
    Path(args.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('EMPIRICAL_YOY=SUPPORTED_NOT_PROVEN; P1_FACT_ROUND_COMPATIBLE=',result['fit']['p1_fact_rounding_compatible'],'of',result['fit']['p1_fact_samples_total'])
    print('OLD_NEW_RATIO=',result['p2_model_coefficients']['r3_to_r2_ratio'])
    for b,d in result['p2_portfolio_screen']['by_budget'].items():
        print(b, d['feasible_combinations'], 'DIRECT',d['leaders']['direct'][0]['ids'],'R2',d['leaders']['old_P1_P2_secant'][0]['ids'],'R3',d['leaders']['year_on_year_hypothesis'][0]['ids'])
    print('RECEIPT=',args.output)
if __name__=='__main__':main()
