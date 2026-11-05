#!/usr/bin/env python3
"""EcoSim P2 source-bounded project-only score/cash screening.

Offline/no game/network/browser writes. It bridges *live displayed* P2 factor, finance,
project status and cost with *historical test round* project effect labels.
The mapped direct-effect response is only conditional, never a server forecast.
"""
from __future__ import annotations
import argparse
from itertools import combinations
from collections import Counter
from pathlib import Path
import json,sys,math
from r142_proxy_reference import COEFF,proxy_value
from effect_replay_r147 import replay_effects, normalize_metric

ROOT=Path(__file__).resolve().parent

def load():
 data=json.loads((ROOT/'P2_joined_input.json').read_text(encoding='utf-8'))
 assert data['game_mutations']==0
 idx={p['id']:p for p in data['projects']}
 assert set(idx)==set(range(1,36))
 assert len({p['name'] for p in idx.values()})==35
 return data,idx

def effects_for(ids,idx):
 return [(i,e) for i in ids for e in idx[i]['effects']]

def conditional_delta(ids,idx,baseline,scale=1.0):
 factors=dict(baseline)
 pairs=effects_for(ids,idx)
 records=replay_effects(factors,pairs,COEFF,scale=scale)
 mapped=[r for r in records if r.get('mapped')]
 unknown=[r for r in records if not r.get('mapped')]
 cap_edge=[r for r in records if r.get('uncertain_due_to_saturation')]
 zero_baseline=[{'project_id':pid,'metric':e['metric']} for pid,e in pairs if normalize_metric(e['metric']) in COEFF and abs(baseline[normalize_metric(e['metric'])])<1e-9 and abs(e['value_percent'])>1e-12]
 return {'delta':proxy_value(factors)-proxy_value(baseline),'unmapped_count':len(unknown),'unmapped_metrics':sorted({r['project_metric'] for r in unknown}), 'cap_edge_count':len(cap_edge), 'zero_baseline_count':len(zero_baseline)}

def cost_for(ids,idx):
 upfront=sum(idx[i]['startup_cost']+idx[i]['investment'] for i in ids)
 positive=sum(max(0,idx[i]['maintenance_cost']) for i in ids)
 signed=sum(idx[i]['maintenance_cost'] for i in ids)
 support=sum(idx[i]['partner_support'] for i in ids)
 return {'upfront':upfront,'positive_annual_maintenance':positive,'signed_annual_maintenance':signed,'four_year_conservative_p2_p5_cost':upfront+4*positive,'four_year_signed_p2_p5_project_line':upfront+4*signed,'support_displayed_not_cash':support,'conservative_incremental_p2_cash_requirement':upfront+positive,'signed_p2_project_line_increment':upfront+signed}

def direct_eligibility(ids,idx,already_running,strict=True):
 names={p['name']:i for i,p in idx.items()}
 for i in ids:
  for raw in idx[i].get('project_conditions',[]):
   field=raw.split(' — ',1)[0].strip();neg=field.startswith('not ')
   if neg:field=field[4:]
   prereq=names.get(field)
   if prereq is None:return False
   if neg and (prereq in already_running or prereq in ids):return False
   if not neg and prereq not in already_running:
    # Same-year preconditions have not been proven acceptable. Block in strict mode.
    if strict or prereq not in ids:return False
 return True

def compute(budgets=(75000,150000,300000,450000),max_start=4):
 source,idx=load()
 base=source['baseline']
 baseline=base['p2_plan_factors'];raw=base['p2_reconstructed_index']
 assert abs(proxy_value(baseline)-raw)<1e-8
 active={i for i,p in idx.items() if p['status_p2']=='Fut'}
 assert len(active)==10 and sum(idx[i]['maintenance_cost'] for i in active)==-65800
 assert abs(raw-base['p2_plan_index'])<=0.005
 candidates=[i for i in sorted(idx) if i not in active]
 assert len(candidates)==25
 candidate_details=[]
 for i in candidates:
  if not direct_eligibility([i],idx,active):continue
  costs=cost_for([i],idx)
  score=conditional_delta([i],idx,baseline)
  candidate_details.append({'ids':[i],'names':[idx[i]['name']],**costs,**score})
 ranked={str(b):[] for b in budgets}
 total_feasible={str(b):0 for b in budgets}
 num_explored=0
 for k in range(1,min(max_start,len(candidates))+1):
  for ids in combinations(candidates,k):
   num_explored+=1
   if not direct_eligibility(ids,idx,active):continue
   costs=cost_for(ids,idx)
   valid=[b for b in budgets if costs['conservative_incremental_p2_cash_requirement']<=b]
   if not valid:continue
   nom=conditional_delta(ids,idx,baseline,1)
   half=conditional_delta(ids,idx,baseline,.5)
   more=conditional_delta(ids,idx,baseline,1.5)
   row={'ids':list(ids),'names':[idx[i]['name'] for i in ids],**costs,
      'mapped_proxy_delta_p2':round(nom['delta'],6),
      'mapped_proxy_delta_half_effect':round(half['delta'],6),
      'mapped_proxy_delta_onehalf_effect':round(more['delta'],6),
      'scenario_min_mapped_proxy_delta':round(min(half['delta'],nom['delta'],more['delta']),6),
      'mapped_proxy_index_if_direct_effects_only':round(raw+nom['delta'],6),
      'scenario_no_grant_reserve_after_conservative_increment':round(base['p2_plan_reserve_ecu']-costs['conservative_incremental_p2_cash_requirement'],2),
      'unknown_effect_records':nom['unmapped_count'],'unknown_effect_labels':nom['unmapped_metrics'],
      'zero_baseline_effect_records':nom['zero_baseline_count'],
      'ambiguous_clamp_records':nom['cap_edge_count'],
      'cost_data':'P2_VERIFIED','effects':'HISTORICAL_TEST_ONLY_UNVALIDATED_P2',
      'status':'HYPOTHETICAL_NO_GAME_MUTATION'}
   for b in valid:
    key=str(b);total_feasible[key]+=1
    ranked[key].append(row)
 # choose both nominal and robust ranked shortlists based on finite enumeration
 output={}
 for budget,records in ranked.items():
  def keynom(x):return (-x['mapped_proxy_delta_p2'],x['unknown_effect_records'],-x['scenario_min_mapped_proxy_delta'],x['conservative_incremental_p2_cash_requirement'],x['ids'])
  def keyrob(x):return (-x['scenario_min_mapped_proxy_delta'],x['unknown_effect_records'],-x['mapped_proxy_delta_p2'],x['conservative_incremental_p2_cash_requirement'],x['ids'])
  nominal=sorted(records,key=keynom)[:10]
  robust=sorted(records,key=keyrob)[:10]
  output[budget]={'feasible_combo_count':total_feasible[budget], 'top_nominal':nominal,'top_sensitivity_min':robust}
 single=sorted(candidate_details,key=lambda x:(-x['delta'],x['conservative_incremental_p2_cash_requirement'],x['ids']))
 result={
 'schema':'ecosim.p2.joint_project_finance.screen.v1','source':'P2_joined_input.json','run_scope':'OFFLINE_NO_GAME_WRITES',
 'model_gate':'CONDITIONAL_PROJECT_ONLY_PROXY_NOT_ECOSIM_PREVIEW_OR_SERVER_FORECAST',
 'baseline':{k:v for k,v in base.items() if k not in ('p1_fact_factors','p2_plan_factors')},
 'data_quality':source['quality'],
 'restrictions':{'new_project_limit':max_start,'limit_status':'REPORTED_ORGANIZER_FOUR_PER_YEAR_NOT_LIVE_VERIFIED',
   'cash_envelopes_ecu':list(budgets),'cash_envelopes_are_hypothetical':True,
   'cash_baseline_reserve_includes_p1_opening':True,'initial_running_count':len(active),
   'cash_conservative':'incremental startup+investment+positive new maintenance, without grants or negative maintenance funding',
   'existing_running_maintenance_included_in_baseline':True,
   'project_effects_source':'2026-10-30 test round Z historical effects (unverified live I P2)',
   'project_effects_applied_once':'HYPOTHETICAL immediate direct multiplier only; no indirect effects / future transitions',
   'project_effects_unmapped_never_treated_as_zero':True,
   'same_year_dependency':'BLOCKED_IF_PREREQ_NOT_ALREADY_RUNNING',
   'gameplay_decision':'STOP',
   'future_cash_p3_p5':'UNKNOWN',
   'P2_game_plan_saved':'UNKNOWN'},
 'candidate_pool_count':len(candidates),'eligible_direct_single_count':len(single),
 'combinations_pre_eligibility_explored':num_explored,'single_candidates':single,
 'by_hypothetical_p2_budget':output}
 return result


def main():
 p=argparse.ArgumentParser();p.add_argument('--out',default=str(ROOT/'P2_joint_scenarios.json'))
 p.add_argument('--budgets',default='75000,150000,300000,450000')
 args=p.parse_args()
 budgets=tuple(int(i) for i in args.budgets.split(','))
 if any(b<0 for b in budgets) or len(set(budgets))!=len(budgets):raise ValueError('invalid budgets')
 d=compute(budgets)
 Path(args.out).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('SCENARIO_MODEL=PASS')
 print('BASELINE_P2_INDEX=',d['baseline']['p2_reconstructed_index'],'LOADED=',d['data_quality']['p2_live_project_cost_status_count'])
 for b,s in d['by_hypothetical_p2_budget'].items():
  a=s['top_nominal'][0]
  print('SCENARIO',b,'feasible',s['feasible_combo_count'],'nominal_ids',a['ids'],'delta',a['mapped_proxy_delta_p2'],'safe_cash',a['conservative_incremental_p2_cash_requirement'],'unknown',a['unknown_effect_records'])

if __name__=='__main__':main()
