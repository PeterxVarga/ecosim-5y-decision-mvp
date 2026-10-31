#!/usr/bin/env python3
"""One consolidated R159 adversarial audit: component timing + real pipeline.

This is an OFFLINE software check, not EcoSim outcome validation.
"""
from __future__ import annotations
import copy, json, math, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))
from temporal_cash_r158 import timeline_for_candidate,SCHEMA
from decision_desk_r149 import make_report,read_json,write_json,_build_candidate_union
from decision_view_r149 import render_offline_html
from operating_cash_r155 import FEES
from tax_revenue_r154 import REVENUE_CHANNELS

checks=[]
def yes(name,x):
    if not x:raise AssertionError(name)
    checks.append(name)
def reject(name,func):
    try:func()
    except (ValueError,TypeError,KeyError,IndexError):yes(name,True)
    else:raise AssertionError(name+' must reject')

def taxable(values):
    return {k:values.get(k,0) for k in REVENUE_CHANNELS}
def fees(values):
    return {k:values.get(k,0) for k in FEES}
def taxrows(flow):
    return {'yearly':[{'year':i+1,'four_tax_channel_deltas_ecu':taxable(v),
                       'fixed_base_four_tax_delta_ecu':sum(v.values())} for i,v in enumerate(flow)],
            'five_year_fixed_base_tax_delta_ecu':sum(sum(x.values()) for x in flow)}
def opros(fee_flow,cost_flow):
    return {'annual_rows':[{'year':i+1,'six_fee_channel_deltas_ecu':fees(v),
          'six_fee_delta_ecu':sum(v.values()),
          'covered_institution_cost_delta_ecu':cost_flow[i],
          'partial_annual_operating_net_delta_ecu':sum(v.values())-cost_flow[i]}
          for i,v in enumerate(fee_flow)],
         'five_year_partial_operating_net_delta_ecu':sum(sum(v.values())-c for v,c in zip(fee_flow,cost_flow))}
candidate={'candidate_id':'FALSIFY-A','project_ids_by_year':[[1],[],[],[],[]],
           'conservative_project_need_ecu_by_year':[100,0,0,0,0],
           'five_year_conservative_project_need_ecu':100}
empty=[{} for _ in range(5)]
def run(tax,feelist=empty,costs=(0,0,0,0,0),cand=candidate):
    return timeline_for_candidate(cand,taxrows(tax),opros(feelist,costs),1)

# Counterexample 1: income 100 and staff cost 100 in the SAME year: net zero.
# R158 erroneously deferred the net (0), making the 100 staff cost vanish.
a=run(empty,[{'burial':100},{},{},{},{}],[100,0,0,0,0])
y1,y2=a['annual_rows'][:2]
yes('R159 net-neutral fee + staff still needs 100 immediately',y1['deferred_net_after_card_cost_ecu']==-200)
yes('R159 first-year immediate net remains -100 card',y1['partial_net_after_card_cost_ecu']==-100)
yes('R159 following year collects deferred 100',y2['deferred_net_after_card_cost_ecu']==100)
yes('R159 5-year total cash remains -100',a['five_year_partial_net_after_card_cost_ecu']==-100)
yes('R159 peak deferred shortfall is 200',a['hypothetical_peak_zero_opening_cash_shortfall_positive_receipts_deferred_ecu']==200)

# Counterexample 2: opposing taxes must not cancel BEFORE timing.
b=run([{'business':120,'vehicle':-120},{},{},{},{}])
yes('Tax channel net-zero immediate first-year delta',b['annual_rows'][0]['four_tax_delta_ecu']==0)
yes('Tax +120 cannot cover -120 immediately under delay',b['annual_rows'][0]['deferred_net_after_card_cost_ecu']==-220)
yes('120 positive tax deferred into year2',b['annual_rows'][1]['deferred_net_after_card_cost_ecu']==120)

# Counterexample 3: opposing fee channels independent of staff.
c=run(empty,[{'burial':90,'parking':-90},{},{},{},{}])
yes('Fee aggregate zero',c['annual_rows'][0]['direct_six_fee_delta_ecu']==0)
yes('Fee positive delayed, negative immediate',c['annual_rows'][0]['deferred_net_after_card_cost_ecu']==-190)
yes('Fee positive arrives next year',c['annual_rows'][1]['deferred_net_after_card_cost_ecu']==90)

# Counterexample 4: decreased wages are saved now, not a postponed receipt.
d=run(empty,empty,[-50,0,0,0,0])
yes('Expense savings offset current project cash',d['annual_rows'][0]['deferred_net_after_card_cost_ecu']==-50)
yes('Expense savings never create deferred income',d['annual_rows'][1]['deferred_net_after_card_cost_ecu']==0)

# Original R158 simple cash baseline preserved with source-complete channels.
e=run([{'business':100},{},{},{},{}])
yes('Original equal-year immediate cash equals zero',e['hypothetical_peak_zero_opening_cash_shortfall_immediate_ecu']==0)
yes('Original delayed positive receipt requires 100',e['hypothetical_peak_zero_opening_cash_shortfall_positive_receipts_deferred_ecu']==100)
yes('Known unit is income channels',e['delayed_income_unit']=='PER_TAX_AND_FEE_CHANNEL_NOT_NET_OF_INSTITUTIONAL_COSTS')
yes('Zero opening remains assumption not actual',e['actual_opening_cash_ecu'] is None and not e['affordability_authorized'])
yes('Gameplay stop preserved',e['gameplay_gate']=='STOP')

# Source-exact provenance and cash component reconciliation, fail closed.
t=taxrows(empty);o=opros(empty,[0]*5)
invalid=copy.deepcopy(t);del invalid['yearly'][0]['four_tax_channel_deltas_ecu']
reject('Fail on absent tax channel decomposition',lambda:timeline_for_candidate(candidate,invalid,o,1))
invalid=copy.deepcopy(t);invalid['yearly'][0]['four_tax_channel_deltas_ecu'].pop('vehicle')
reject('Fail on incomplete tax channel set',lambda:timeline_for_candidate(candidate,invalid,o,1))
invalid=copy.deepcopy(t);invalid['yearly'][0]['four_tax_channel_deltas_ecu']['bonus']=0
reject('Fail on invented tax channel',lambda:timeline_for_candidate(candidate,invalid,o,1))
invalid=copy.deepcopy(t);invalid['yearly'][0]['four_tax_channel_deltas_ecu']['business']=10
reject('Fail on tax total mismatch',lambda:timeline_for_candidate(candidate,invalid,o,1))
invalid=copy.deepcopy(o);del invalid['annual_rows'][0]['six_fee_channel_deltas_ecu']
reject('Fail on absent fee channel decomposition',lambda:timeline_for_candidate(candidate,t,invalid,1))
invalid=copy.deepcopy(o);invalid['annual_rows'][0]['six_fee_channel_deltas_ecu']['burial']=10
reject('Fail on fee/net cost mismatch',lambda:timeline_for_candidate(candidate,t,invalid,1))
invalid=copy.deepcopy(o);invalid['annual_rows'][0]['covered_institution_cost_delta_ecu']=1
reject('Fail on extra unexplained expense component',lambda:timeline_for_candidate(candidate,t,invalid,1))
invalid=copy.deepcopy(o);invalid['annual_rows'][0]['six_fee_channel_deltas_ecu']['burial']=math.inf
reject('Fail on nonfinite channel',lambda:timeline_for_candidate(candidate,t,invalid,1))
invalid=copy.deepcopy(candidate);invalid['project_ids_by_year'][1]=[1]
reject('Fail on repeated project start in later year',lambda:timeline_for_candidate(invalid,t,o,1))
invalid=copy.deepcopy(candidate);invalid['project_ids_by_year'][1]=[True]
reject('Fail on boolean project ID',lambda:timeline_for_candidate(invalid,t,o,1))
invalid=copy.deepcopy(candidate);invalid['candidate_id']=' '
reject('Fail on blank candidate ID',lambda:timeline_for_candidate(invalid,t,o,1))

# Rolling plans are a conditional zero carry scenario, not a verified amount.
rolling={'candidate_id':'ROLL','project_ids_by_year':[[],[],[]],
        'conservative_project_need_ecu_by_year':[0,0,0],
        'five_year_conservative_project_need_ecu':0}
r3=timeline_for_candidate(rolling,
  {'yearly':[{'year':y,'four_tax_channel_deltas_ecu':taxable({}),
             'fixed_base_four_tax_delta_ecu':0} for y in range(3,6)],
   'five_year_fixed_base_tax_delta_ecu':0},
  {'annual_rows':[{'year':y,'six_fee_channel_deltas_ecu':fees({}),
                   'covered_institution_cost_delta_ecu':0,
                   'partial_annual_operating_net_delta_ecu':0} for y in range(3,6)],
   'five_year_partial_operating_net_delta_ecu':0},3)
yes('Rolling starts year3 and has 3 rows',len(r3['annual_rows'])==3 and r3['annual_rows'][0]['year']==3)
yes('Rolling year3 prior deferred receipts explicitly unknown',r3['pre_horizon_carry_in_assumed_zero_not_verified'] is True)
yes('Year1 has no prior carry ambiguity',e['pre_horizon_delayed_positive_receipts_known'] is True)

# Full existing R152–R157 decision path AND R155 source bridge used, not mock search.
out=make_report(ROOT/'inputs/mvp_run.r157_robust_historical.json')
bridge=out['r158_annual_partial_cash_timing']
yes('R159 inserted into real R157 decision pipeline',bridge['schema']==SCHEMA)
yes('R157 same search flag preserved',out['r157_robust_search_enabled'] is True)
yes('Historical mode not promoted to live',out['run_mode']=='HISTORICAL_ILLUSTRATION')
yes('Synthetic source explicitly preserved',bridge['source_class']=='SYNTHETIC_TEST_ONLY')
yes('Three policy paths joined',len(bridge['path_summaries'])==3)
yes('All plan-path combinations covered',bridge['evaluated_combinations']==3*len({x['candidate_id'] for x in bridge['combinations']}))
yes('Every plan has five periods',all(len(x['annual_rows'])==5 for x in bridge['combinations']))
yes('Every sampled cash row source-resolved',all(x['delayed_income_unit']=='PER_TAX_AND_FEE_CHANNEL_NOT_NET_OF_INSTITUTIONAL_COSTS' for x in bridge['combinations']))
yes('Deferred income never improves peak pressure',all(x['hypothetical_peak_zero_opening_cash_shortfall_positive_receipts_deferred_ecu']+1e-5>=x['hypothetical_peak_zero_opening_cash_shortfall_immediate_ecu'] for x in bridge['combinations']))
yes('All sampled decisions STOP',out['gameplay_gate']=='STOP' and all(x['gameplay_gate']=='STOP' for x in bridge['combinations']))
yes('No actual credit or opening cash manufactured',all(x['actual_spendable_cash_ecu'] is None and x['true_funding_gap_ecu'] is None for x in bridge['combinations']))
yes('No validated game score fabricated',out['game_result_prediction_validated'] is False)

# Cross-check unchanged candidate selection vs the prior R158 qualified release.
old=read_json(ROOT/'results/R158_HISTORICAL_TIMING_DEMO/DECISION_DESK.json')
yes('Search candidates unchanged by cash accounting correction',
    {v['candidate_id']:v['project_ids_by_year'] for v in out['candidate_comparison']} ==
    {v['candidate_id']:v['project_ids_by_year'] for v in old['candidate_comparison']})
yes('No financial envelope inflated by positive fees',out['comparison_envelopes']==old['comparison_envelopes'])

# Standalone static report, same exact outputs as JSON, not hidden model.
html=render_offline_html(out)
yes('R159 corrected timing is reported to operator','R159' in html and 'bér/anyagköltség' in html)
yes('HTML has no executable scripts or iframe','<script' not in html and '<iframe' not in html)
yes('Cash source remains untrusted for spend authorization',bridge['true_cash_availability_or_financing_proven'] is False)
yes('R159 is still an illustrative not realized frontier',all(f['not_game_or_global_pareto'] for f in bridge['sampled_three_axis_timing_front_by_path']))

# Original receipt is retained as legacy evidence, not claimed as current test.
prior=read_json(ROOT/'results/R158_QUALIFICATION.json')
yes('R158 prior qualification retained and properly separate',prior['r158_new_checks']==58 and prior['gameplay_gate']=='STOP')

save=ROOT/'results/R159_HISTORICAL_FALSIFICATION_DEMO';save.mkdir(parents=True,exist_ok=True)
write_json(save/'DECISION_DESK.json',out)
(save/'DECISION_DESK.html').write_text(html,encoding='utf8')
from decision_desk_r149 import render_md
(save/'DECISION_DESK.md').write_text(render_md(out),encoding='utf8')
receipt={'schema':'ECOSIM_R159_FALSIFICATION_HARDENED_QUALIFICATION_V1',
         'status':'PASS_OFFLINE_ONLY','new_checks':len(checks),'checks':checks,
         'r158_prior_checks_preserved_not_rerun':58,
         'historical_plan_policy_combinations':bridge['evaluated_combinations'],
         'legacy_r158_algorithm_bug_verified_by_adversarial_counterexamples':True,
         'gameplay_gate':'STOP','game_actions':0,'server_score_accuracy_measured':False,
         'current_market_team_available':False}
write_json(ROOT/'results/R159_QUALIFICATION.json',receipt)
print(f"R159_CONSOLIDATED=PASS; CHECKS={len(checks)}; JOINED={bridge['evaluated_combinations']}; GAME=STOP")
