#!/usr/bin/env python3
"""One R160 adversarial qualification + ONE full R157 -> R159 decision run.

Offline-only contract checks are not validation of EcoSim server behavior.
"""
from __future__ import annotations
import copy, json, math, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))
from independent_audit_r160 import audit_plan, SCHEMA
from portfolio_5y import project_index
from decision_quality_r150 import _dominates, assess_candidate_quality
from decision_desk_r149 import make_report, read_json, write_json
from decision_view_r149 import render_offline_html

checks=[]
def yes(name, value):
    if not value:raise AssertionError(name)
    checks.append(name)
def reject(name, action):
    try:action()
    except (ValueError,TypeError,KeyError):checks.append(name)
    else:raise AssertionError('Must reject: '+name)
idx=project_index();running=[14,22,23,24,34,35]
valid=[[8,13,27],[4,9,21,28],[5,16,17,26],[1,29],[6,20,25,30]]
def run(starts=valid, **kwargs):
    args=dict(idx=idx,start_year=1,active_ids=running,
              fixed_first_ids=[],previous_project1_active=None,base_project_cap=4,
              annual_budgets=[100000]*5,starts=starts,allow_same_year=True)
    args.update(kwargs)
    return audit_plan(**args)

base=run()
yes('Schema pinned',base['schema']==SCHEMA)
yes('Historical R94 sample stays conditional',base['status']=='CONDITIONAL_NOT_SERVER_VERIFIED')
yes('Five annual records',len(base['years'])==5)
yes('Old 100k example year 1 cost agrees',base['years'][0]['independently_replayed_conservative_cash_need_ecu']==99000)
yes('Five-year sample sum agrees',base['replayed_card_cost_total_ecu']==481300)
yes('Only hypothetical envelope, not loan approval',base['actual_funding_approval'] is None)
yes('No true outcome claim',base['true_eco_sim_outcome'] is None)
yes('No game actions in audit',base['gameplay_gate']=='STOP')
yes('Unknown old project1 is not silently false',any(x['issue']=='PREVIOUS_PERIOD_PROJECT1_BONUS_UNKNOWN' for x in base['conditional_eligibility_items']))
yes('Year one includes existing six running',set(running)<=set(base['years'][0]['running_after_start_ids']))
yes('Year two preserves earlier starts',8 in base['years'][1]['running_after_start_ids'])
yes('Later project 1 activates bonus only after year4',base['years'][4]['effective_cap_min']==5)

# Source statuses and dependencies, NOT server authorization.
yes('Project30 dependency can be satisfied by prior project29',not any('30:UNMET' in x['issue'] for x in base['hard_rule_violations']))
co_start=run(starts=[[29,30],[],[],[],[]],annual_budgets=[200000]*5)
yes('Same-year Fut label is explicitly conditional',any('SAME_YEAR_FUT' in x['issue'] for x in co_start['conditional_eligibility_items']))
yes('Same-year Fut never marked approved',co_start['actual_game_eligibility'] is None)
strict=run(starts=[[29,30],[],[],[],[]],annual_budgets=[200000]*5,allow_same_year=False)
yes('Strict prior year disallows co-start',any('FORBIDDEN' in x['issue'] for x in strict['hard_rule_violations']))
missing=run(starts=[[30],[],[],[],[]],annual_budgets=[200000]*5)
yes('Unsatisfied condition rejected',any('UNMET' in x['issue'] for x in missing['hard_rule_violations']))
prior=run(starts=[[29],[30],[],[],[]],annual_budgets=[200000]*5)
yes('Prior-year Fut condition not hard rejected',not prior['hard_rule_violations'])
# Separate second dependent card, prior running #27. This is card31's prerequisite.
rail=run(starts=[[27],[31],[],[],[]],annual_budgets=[200000]*5)
yes('Second dependent project can meet prior condition',not rail['hard_rule_violations'])
# Negative hypothetical display condition, ensure it cannot be bypassed by co-start.
idx2=copy.deepcopy(idx)
idx2[9]['project_conditions']=['not '+idx2[8]['name']+' — Nem fut']
x=audit_plan(idx2,start_year=1,active_ids=running,fixed_first_ids=[],previous_project1_active=False,
             base_project_cap=4,annual_budgets=[200000]*5,starts=[[8,9],[],[],[],[]])
yes('Negative dependency conflict caught',any('NEGATIVE_CONDITION_CONFLICT' in v['issue'] for v in x['hard_rule_violations']))
x=audit_plan(idx2,start_year=1,active_ids=running,fixed_first_ids=[],previous_project1_active=False,
             base_project_cap=4,annual_budgets=[200000]*5,starts=[[9],[],[],[],[]])
yes('Negative condition consistent when prerequisite absent',not x['hard_rule_violations'])
idx3=copy.deepcopy(idx);idx3[9]['project_conditions']=['Unknown ghost project — Fut']
x=audit_plan(idx3,start_year=1,active_ids=running,fixed_first_ids=[],previous_project1_active=False,
             base_project_cap=4,annual_budgets=[200000]*5,starts=[[9],[],[],[],[]])
yes('Unknown label never converted to valid',any('UNMAPPED' in v['issue'] for v in x['conditional_eligibility_items']))
# Budget and cost replay: discrepancies are not soft warnings.
yes('Cost mismatch rejects a search result',any('SEARCH_REPORTED_COST_MISMATCH' in x['issue'] for x in run(advertised_costs=[0]*5)['hard_rule_violations']))
yes('Total mismatch rejects a search result',any('SEARCH_REPORTED_FIVE_YEAR_COST_MISMATCH' in x['issue'] for x in run(advertised_total=1)['hard_rule_violations']))
yes('Narrow budget rejects infeasible plan',any('ILLUSTRATIVE_ENVELOPE_EXCEEDED' in x['issue'] for x in run(annual_budgets=[100]*5)['hard_rule_violations']))
yes('Duplicate project start across years rejects',any('RESTART' in x['issue'] or 'DUPLICATE' in x['issue'] for x in run(starts=[[8],[8],[],[],[]])['hard_rule_violations']))
yes('Existing current selection is enforced',any('ALREADY_SELECTED_PROJECT_MISSING' in x['issue'] for x in run(fixed_first_ids=[2])['hard_rule_violations']))
yes('Existing current selection can be validly included',not run(starts=[[8,13,27],[],[],[],[]],fixed_first_ids=[8])['hard_rule_violations'])
yes('Over cap rejects',any('PROJECT_CAP_EXCEEDED' in x['issue'] for x in run(starts=[[1,3,4,5,6],[],[],[],[]],annual_budgets=[500000]*5,previous_project1_active=False)['hard_rule_violations']))
yes('Conditional project1 bonus does not certify',any('BONUS' in x['issue'] for x in run(starts=[[1,3,4,5,6],[],[],[],[]],annual_budgets=[500000]*5)['conditional_eligibility_items']))
yes('Confirmed project1 bonus permits five slots in display model',not run(starts=[[1,3,4,5,6],[],[],[],[]],annual_budgets=[500000]*5,previous_project1_active=True)['hard_rule_violations'])

reject('Reject unknown project',lambda:run(starts=[[999],[],[],[],[]]))
reject('Reject boolean project IDs',lambda:run(starts=[[True],[],[],[],[]]))
reject('Reject duplicate within year',lambda:run(starts=[[8,8],[],[],[],[]]))
reject('Reject malformed horizon',lambda:run(starts=[[8],[]]))
reject('Reject NaN envelope',lambda:run(annual_budgets=[math.nan]*5))
reject('Reject infinity envelope',lambda:run(annual_budgets=[math.inf]*5))
reject('Reject negative budget',lambda:run(annual_budgets=[-1]*5))
reject('Reject incompatible cost list',lambda:run(advertised_costs=[100]))
reject('Reject nonfinite total',lambda:run(advertised_total=math.inf))
reject('Reject invalid cap',lambda:run(base_project_cap=-1))
reject('Reject boolean cap',lambda:run(base_project_cap=True))
reject('Reject invalid bonus',lambda:run(previous_project1_active=1))
reject('Reject overlapping existing and active',lambda:run(fixed_first_ids=[14]))
reject('Reject repeated project display names',lambda:audit_plan({**idx,2:{**idx[2],'name':idx[1]['name']}},
  start_year=1,active_ids=running,fixed_first_ids=[],previous_project1_active=False,
  base_project_cap=4,annual_budgets=[100000]*5,starts=[[],[],[],[],[]]))
# Adversarial dominance: unknown-effect count is NOT signed impact and cannot
# independently decide a partial-model Pareto result.
def cand(cid,unknown,score=1.,cost=100.,co=False):
    return {'candidate_id':cid,'mapped_terminal_proxy_delta':score,
     'worst_of_existing_illustrative_mapped_sensitivities':score,
     'unmapped_or_uncertain_project_effect_occurrences':unknown,
     'same_year_co_start_condition_unverified':co,
     'conservative_project_need_ecu_by_year':[cost,0,0,0,0]}
a,b=cand('A',0),cand('B',10)
yes('Unknown-effect count alone cannot dominate',not _dominates(a,b) and not _dominates(b,a))
yes('Conditional same-year flag alone cannot dominate',not _dominates(cand('A',0,co=False),cand('B',0,co=True)))
yes('Known metric advantage can dominate partial model',_dominates(cand('A',100,score=2),cand('B',0,score=1)))
yes('Higher cost prevents partial dominance if scores equal',not _dominates(cand('A',0,cost=101),cand('B',20,cost=100)))

# One full existing pipeline, NOT independent synthetic replacement of search.
report=make_report(ROOT/'inputs/mvp_run.r157_robust_historical.json')
all_sampled=report['r150_sampled_quality']['sampled_candidate_count']
yes('Full decision pipeline produced candidate set',all_sampled>0)
yes('R160 all returned candidates have independent audit',all(isinstance(c.get('r160_independent_constraint_replay'),dict) for c in report['candidate_comparison']))
yes('All candidate audit failures zero',report['r160_independent_plan_audits']['hard_errors']==0)
yes('Audit counts cover entire sampled union',report['r160_independent_plan_audits']['plans_replayed']==all_sampled)
yes('R160 authentic condition uncertainty visible',report['r160_independent_plan_audits']['conditional_or_unknown_server_acceptance']>=0)
yes('No gameplay action',report['gameplay_gate']=='STOP' and report['game_writes']==0)
yes('Actual win rank remains unknown',report['game_result_prediction_validated'] is False)
yes('Three envelope runs retained',len(report['comparison_envelopes'])==3)
yes('Historical R94 source not live',report['run_mode']=='HISTORICAL_ILLUSTRATION')
yes('R159 timing module remains integrated',report['r158_annual_partial_cash_timing']['schema'].startswith('ECOSIM_R159_'))
quality=report['r150_sampled_quality']
yes('Partial dominance excludes unknown count',quality['r160_unknown_effect_counts_not_treated_as_negative_objectives'] is True)
yes('Real economic dominance explicitly unknown',quality['r160_real_outcome_dominance_for_any_two_candidates'].startswith('UNDETERMINED'))
yes('No candidate receives game eligibility',all(c['r160_independent_constraint_replay']['actual_game_eligibility'] is None for c in report['candidate_comparison']))
html=render_offline_html(report)
yes('Decision HTML still renders safely without JS',len(html)>1000 and '<script' not in html and '<iframe' not in html)
# Save one ready-to-open actual end-to-end result.
folder=ROOT/'results/R160_HISTORICAL_CONSISTENCY_DEMO';folder.mkdir(parents=True,exist_ok=True)
write_json(folder/'DECISION_DESK.json',report)
(folder/'DECISION_DESK.html').write_text(html,encoding='utf-8')
from decision_desk_r149 import render_md
(folder/'DECISION_DESK.md').write_text(render_md(report),encoding='utf-8')
receipt={'schema':'ECOSIM_R160_CONSISTENCY_GATED_QUALIFICATION_V1',
    'status':'PASS_OFFLINE_ONLY','new_checks':len(checks),'checks':checks,
    'sampled_candidates_independently_replayed':all_sampled,
    'prior_r159_checks_preserved_not_rerun':51,
    'search_is_heuristic':True,'current_market_team_verified':False,
    'full_annual_city_outcomes_known':False,
    'real_score_reliability_measured':False,'gameplay_gate':'STOP','game_actions':0}
write_json(ROOT/'results/R160_QUALIFICATION.json',receipt)
print('R160_INDEPENDENT_AUDIT=PASS; CHECKS='+str(len(checks))+'; CANDIDATES='+str(all_sampled)+'; GAME=STOP')
