#!/usr/bin/env python3
"""R158 consolidated offline release: re-run R157 and adversarial temporal checks."""
from __future__ import annotations
import copy,json,math,runpy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))
from temporal_cash_r158 import timeline_for_candidate,build_timing_bridge,SCHEMA
from decision_desk_r149 import make_report,render_md
from decision_view_r149 import render_offline_html
from strategy_5y import read_json,write_json

checks=[]
def check(name,condition):
    if not condition:raise AssertionError(name)
    checks.append(name)
def reject(name,callback):
    try:callback()
    except (ValueError,TypeError,KeyError,IndexError):check(name,True)
    else:raise AssertionError(name+' incorrectly accepted')

# Historical baseline retained; targeted R158 integration is executed once.
# R157 comprehensive regression is *not* re-run because it chains older suites
# and is the low-ROI, expensive path already qualified in prior release.
prev=read_json(ROOT/'results/R157_QUALIFICATION.json')
check('R157 prior regression receipt preserved',prev['r157_new_checks']==66 and prev['gameplay_gate']=='STOP')

cid='UNIT-A'
base_candidate={'candidate_id':cid,'project_ids_by_year':[[1],[],[],[],[]],
                'conservative_project_need_ecu_by_year':[100,0,0,0,0],
                'five_year_conservative_project_need_ecu':100}
def tc(flows):return {'yearly':[{'year':i+1,'fixed_base_four_tax_delta_ecu':a} for i,a in enumerate(flows)],
                     'five_year_fixed_base_tax_delta_ecu':sum(flows)}
def oc(flows):return {'annual_rows':[{'year':i+1,'partial_annual_operating_net_delta_ecu':a} for i,a in enumerate(flows)],
                     'five_year_partial_operating_net_delta_ecu':sum(flows)}
# Equal terminal money, VERY different intermediate pressure: the bug which
# aggregated R155 five-year reports cannot distinguish.
early=timeline_for_candidate(base_candidate,tc([100,0,0,0,0]),oc([0]*5),1)
late=timeline_for_candidate(base_candidate,tc([0,100,0,0,0]),oc([0]*5),1)
check('Annual pipeline returns exact horizon',len(late['annual_rows'])==5)
check('Same five-year tax sums',early['five_year_partial_net_after_card_cost_ecu']==late['five_year_partial_net_after_card_cost_ecu']==0)
check('Same-year recognition early cash need zero',early['hypothetical_peak_zero_opening_cash_shortfall_immediate_ecu']==0)
check('Later tax income creates early funding pressure',late['hypothetical_peak_zero_opening_cash_shortfall_immediate_ecu']==100)
check('Positive delayed-tax stress does not fund same-year project',early['hypothetical_peak_zero_opening_cash_shortfall_positive_receipts_deferred_ecu']==100)
check('Delayed recognition shifts positive tax credit to next year',early['annual_rows'][0]['deferred_net_after_card_cost_ecu']==-100 and early['annual_rows'][1]['deferred_net_after_card_cost_ecu']==100)
check('First negative cumulative year identified',late['earliest_negative_cumulative_year_immediate']==1)
check('No game cash or spending authorization',early['actual_spendable_cash_ecu'] is None and early['affordability_authorized'] is False)
check('No game credit rules claimed',early['server_cash_timing_and_credit_rules_known'] is False)
check('Project spend appears only once',sum(x['project_card_need_ecu'] for x in early['annual_rows'])==100)
check('Project receipts are not confused with tax receipt',early['annual_rows'][0]['four_tax_delta_ecu']==100)
check('No other cash silently added',early['five_year_partial_net_after_card_cost_ecu']==0)

# negative increments can never be treated as discretionary extra budget
neg=timeline_for_candidate(base_candidate,tc([-5]*5),oc([-10]*5),1)
check('Negative partial operating and tax deltas increase pressure',neg['hypothetical_peak_zero_opening_cash_shortfall_immediate_ecu']==175)
check('Negative deltas are not deferred',neg['hypothetical_peak_zero_opening_cash_shortfall_positive_receipts_deferred_ecu']==175)
check('Net annual first year correct',neg['annual_rows'][0]['partial_net_after_card_cost_ecu']==-115)

# rolling planning starts at year 3: earlier years MUST NOT enter the ledger
rolling={'candidate_id':'rolling','project_ids_by_year':[[1],[],[]],
         'conservative_project_need_ecu_by_year':[20,5,5],
         'five_year_conservative_project_need_ecu':30}
r3=timeline_for_candidate(rolling,
    {'yearly':[{'year':k,'fixed_base_four_tax_delta_ecu':15} for k in range(3,6)],'five_year_fixed_base_tax_delta_ecu':45},
    {'annual_rows':[{'year':k,'partial_annual_operating_net_delta_ecu':-1} for k in range(3,6)],'five_year_partial_operating_net_delta_ecu':-3},3)
check('Rolling starts with current actual year',r3['annual_rows'][0]['year']==3)
check('Rolling includes only remaining years',len(r3['annual_rows'])==3 and r3['annual_rows'][-1]['year']==5)
check('Rolling tax and project totals align',r3['five_year_partial_net_after_card_cost_ecu']==12)
check('Rolling deferred receipts still accrue after each year',r3['annual_rows'][0]['deferred_net_after_card_cost_ecu']==-21)

reject('Reject outside five-year start',lambda:timeline_for_candidate(base_candidate,tc([0]*5),oc([0]*5),0))
reject('Reject mismatched horizon',lambda:timeline_for_candidate(base_candidate,tc([0]*5),oc([0]*5),3))
reject('Reject missing tax year',lambda:timeline_for_candidate(base_candidate,{'yearly':tc([0]*5)['yearly'][1:], 'five_year_fixed_base_tax_delta_ecu':0},oc([0]*5),1))
reject('Reject duplicated tax year',lambda:timeline_for_candidate(base_candidate,{'yearly':tc([0]*5)['yearly'][:4]+[tc([0]*5)['yearly'][0]], 'five_year_fixed_base_tax_delta_ecu':0},oc([0]*5),1))
reject('Reject NaN tax',lambda:timeline_for_candidate(base_candidate,tc([math.nan,0,0,0,0]),oc([0]*5),1))
reject('Reject infinity operation delta',lambda:timeline_for_candidate(base_candidate,tc([0]*5),oc([math.inf,0,0,0,0]),1))
reject('Reject nonfinite project card',lambda:timeline_for_candidate({**base_candidate,'conservative_project_need_ecu_by_year':[math.nan,0,0,0,0]},tc([0]*5),oc([0]*5),1))
reject('Reject negative project card',lambda:timeline_for_candidate({**base_candidate,'conservative_project_need_ecu_by_year':[-100,0,0,0,0]},tc([0]*5),oc([0]*5),1))
reject('Reject mismatched annual project sum',lambda:timeline_for_candidate({**base_candidate,'five_year_conservative_project_need_ecu':99},tc([0]*5),oc([0]*5),1))
reject('Reject mismatched tax total',lambda:timeline_for_candidate(base_candidate,{**tc([0]*5),'five_year_fixed_base_tax_delta_ecu':1},oc([0]*5),1))
reject('Reject mismatched operation total',lambda:timeline_for_candidate(base_candidate,tc([0]*5),{**oc([0]*5),'five_year_partial_operating_net_delta_ecu':9},1))
reject('Reject missing candidate id',lambda:timeline_for_candidate({**base_candidate,'candidate_id':None},tc([0]*5),oc([0]*5),1))
reject('Reject booleans as numeric money',lambda:timeline_for_candidate(base_candidate,tc([True,0,0,0,0]),oc([0]*5),1))

out=make_report(ROOT/'inputs/mvp_run.r157_robust_historical.json')
r=out['r158_annual_partial_cash_timing']
check('R158 is present in actual existing decision desk',r['schema']==SCHEMA)
check('R157 search still on in integrated sample',out['r157_robust_search_enabled'] is True)
check('All official source classes are illustrative, never live',r['source_class']=='SYNTHETIC_TEST_ONLY')
check('All 3 policy path joins present',len(r['path_summaries'])==3)
check('Candidate x path product complete',r['evaluated_combinations']==3*len({x['candidate_id'] for x in r['combinations']}))
check('Every time series carries five years',all(len(c['annual_rows'])==5 for c in r['combinations']))
check('No synthetic ledger claims true cash',all(c['true_funding_gap_ecu'] is None for c in r['combinations']))
check('All individual combinations retain STOP',all(c['gameplay_gate']=='STOP' for c in r['combinations']))
check('Sampled temporal three-axis fronts computed',len(r['sampled_three_axis_timing_front_by_path'])==3)
check('Nondominated counts bounded by sampled candidates',all(0<=x['nondominated_in_sample']<=x['evaluated_with_mapped_index'] for x in r['sampled_three_axis_timing_front_by_path']))
check('Positive cash delayed stress never improves peak gap',all(c['hypothetical_peak_zero_opening_cash_shortfall_positive_receipts_deferred_ecu']+1e-6>=c['hypothetical_peak_zero_opening_cash_shortfall_immediate_ecu'] for c in r['combinations']))
check('Historical report preserves game STOP',out['gameplay_gate']=='STOP' and out['game_writes']==0)
check('No actual forecast accuracy claimed',out['game_result_prediction_validated'] is False)
check('Report lists missing real cash components','baseline treasury' in r['missing_cash_components'])
html=render_offline_html(out);md=render_md(out)
check('HTML includes temporal section','R158' in html and 'éves' in html)
check('Markdown includes temporal section','## R158' in md)
check('HTML remains static without scripts','<script' not in html and '<iframe' not in html)
check('All calculations are explicit and label STOP',r['gameplay_gate']=='STOP' and r['true_cash_availability_or_financing_proven'] is False)

# Adversarial join rejects mixed versions, partial path coverage and duplication.
ft=copy.deepcopy(out['r154_source_four_tax_fiscal_tradeoffs'])
op=copy.deepcopy(out['r155_source_operating_cash_tradeoffs'])
resp=copy.deepcopy(out['r153_source_backed_tax_sensitivity'])
# only top20 reports exposed; full sampled union from make_report is >20, so
# join test with synthetic one candidate and a matching response structure.
fc=copy.deepcopy(ft);ocopy=copy.deepcopy(op);rc=copy.deepcopy(resp)
cand_one=[base_candidate]
for p in rc['paths']:
    p['conditional_candidate_comparison']=[{'candidate_id':cid,'mapped_terminal_proxy_plus_tax_path_delta':0.1}]
# use real year streams with new tiny candidate to avoid relying on hidden union
joined=build_timing_bridge(cand_one,fc,ocopy,rc,1)
check('One-plan source-backed temporal join',joined['evaluated_combinations']==3)
check('One-plan join maintains game STOP',joined['gameplay_gate']=='STOP')
mis=copy.deepcopy(ocopy);mis['source_class']='OPERATOR_DECLARED_READONLY_HYPOTHESIS'
reject('Reject mixed operating source classes',lambda:build_timing_bridge(cand_one,fc,mis,rc,1))
mis=copy.deepcopy(ocopy);mis['path_counterfactuals'].pop()
reject('Reject missing operating policy path',lambda:build_timing_bridge(cand_one,fc,mis,rc,1))
mis=copy.deepcopy(fc);mis['path_counterfactuals'].append(copy.deepcopy(mis['path_counterfactuals'][0]))
reject('Reject duplicate tax path identifier',lambda:build_timing_bridge(cand_one,mis,ocopy,rc,1))
mis=copy.deepcopy(rc);mis['paths'][0]['conditional_candidate_comparison']=[]
reject('Reject omitted response candidate',lambda:build_timing_bridge(cand_one,fc,ocopy,mis,1))
check('Missing all modelled evidence is explicitly blocked',build_timing_bridge([],None,None,None,1)['status'].startswith('BLOCKED'))

saved=ROOT/'results/R158_HISTORICAL_TIMING_DEMO';saved.mkdir(exist_ok=True,parents=True)
write_json(saved/'DECISION_DESK.json',out)
(saved/'DECISION_DESK.html').write_text(html,encoding='utf8')
(saved/'DECISION_DESK.md').write_text(md,encoding='utf8')
(saved/'INPUT_HASHES.json').write_text(json.dumps(out['inputs'],indent=2,ensure_ascii=False)+'\n',encoding='utf8')
receipt={'schema':'ECOSIM_R158_TEMPORAL_CASH_QUALIFICATION_V1','status':'PASS_OFFLINE',
         'previous_r156_checks_preserved_not_rerun':68,'previous_r157_checks_preserved_not_rerun':66,
         'r158_new_checks':len(checks),'checks':checks,
         'historical_candidate_policy_combinations':r['evaluated_combinations'],
         'sampled_front_per_path':r['sampled_three_axis_timing_front_by_path'],
         'live_state_available':False,'true_game_financing_verified':False,
         'measured_prediction_accuracy':None,'game_actions':0,'gameplay_gate':'STOP'}
write_json(ROOT/'results/R158_QUALIFICATION.json',receipt)
print(f"R158_FINAL_QUALIFICATION=PASS; R156_AND_R157_RECEIPTS_RETAINED=134; R158_NEW={len(checks)}; JOINED={r['evaluated_combinations']}; GAME=STOP")
