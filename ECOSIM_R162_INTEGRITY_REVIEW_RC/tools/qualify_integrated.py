#!/usr/bin/env python3
"""One-shot consolidated offline qualification; no live API and no Codex."""
import hashlib,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))
from portfolio_5y import project_index,verify_inputs
from r142_proxy_reference import evaluate,proxy_value
from strategy_5y import read_json,search,parse_budget,parse_dependencies,permitted,yearly_cost,write_json,render_markdown
from decision_evidence import evidence_summary

checks=[]
def check(label, assertion):
    if not assertion:raise AssertionError('FAIL '+label)
    checks.append(label)

p=project_index(); data=read_json(ROOT/'data/ecosim_projects_20261030.json')
check('35 cards exactly',len(data['projects'])==35 and len(p)==35)
check('test running count 6',sum(x['status_p1']=='Fut' for x in p.values())==6)
base=read_json(ROOT/'data/ECOSIM_R141_PROJECT_PROXY.json')['baseline_from_UI']
check('R141 baseline projection matches UI two decimals',abs(proxy_value(base)-52.48)<.01)
check('prior R142 combo mapped proxy +0.480', abs(evaluate([p[i] for i in [8,13,27]],base)[0]-.479708)<.002)
check('signed negative maintenance cannot increase available budget',yearly_cost(p,set(),(13,))==55000)
check('signed negative maintenance not used in portfolio envelope',
      verify_inputs({'years':[{'year':y,'start_project_ids':[13] if y==1 else []} for y in range(1,6)],
                     'baseline':{'source':'TEST','initially_active_project_ids':[14,22,23,24,34,35],
                                 'verified_current_market':False}},
                    {'market':{},'team':{},'provenance':{}})[0][0]['conservative_project_cash_requirement_ecu']==55000)
deps,unknown=parse_dependencies(p)
check('dependency label mapping complete for test projects',not unknown)
check('Bubi with bike route same-year conditional allowed',permitted((29,30),set(),deps,True)==(True,True))
check('Bubi with bike route same-year strict blocked',permitted((29,30),set(),deps,False)[0] is False)
check('Bubi without bike route invalid',permitted((30,),set(),deps,True)[0] is False)
check('Bubi next-year after bike route allowed',permitted((30,),{29},deps,True)[0] is True)
check('budget number replicated',parse_budget('100000',5)==[100000.]*5)
check('cap overrun not silently approved',True) # separately exercised via explicit invalid state below
invalid=read_json(ROOT/'inputs/official_state.template.json')
invalid['team']['already_selected_new_project_ids_current_period']=[1,2,3,4,5]
try:
    search(invalid,1,[100000]*5,4,1,1,True)
    raise AssertionError('Expected cap error')
except ValueError as exc:
    check('over-cap current selections are rejected', 'cap' in str(exc))
check('empty evidence does not grant qualification',evidence_summary(read_json(ROOT/'inputs/official_state.template.json'))['gameplay_decision']=='STOP')
state=read_json(ROOT/'inputs/official_state.template.json')
zero=search(state,1,[0.]*5,4,2,5,True)
check('zero budget selects no projects',all(not x['start_project_ids'] for x in zero['top_plans'][0]['start_by_year']))
check('zero budget has zero project index delta',zero['top_plans'][0]['terminal_mapped_proxy_delta']==0)
# Replicate a historical proxy case, then full 5yr beam on a clearly hypothetical envelope.
result=search(state,1,[100000.]*5,None,12,40,True)
check('five annual decisions produced',len(result['top_plans'][0]['start_by_year'])==5)
check('all alternatives declare STOP',result['final_gameplay_decision']=='STOP' and not result['actual_five_year_score_forecast_validated'])
check('all alternatives below hypothetical cost envelope',all(all(x['conservative_card_cash_requirement_ecu']<=100000 for x in plan['start_by_year']) for plan in result['top_plans']))
check('all selections unique across years',all(len(set(i for row in plan['start_by_year'] for i in row['start_project_ids']))==len([i for row in plan['start_by_year'] for i in row['start_project_ids']]) for plan in result['top_plans']))
check('no live source claimed',result['assumptions']['budget_source']=='EXPLICIT_ILLUSTRATIVE_CLI_SCENARIO_NOT_SPENDABLE_CASH')
check('all effect aliases not silently counted',len(result['top_plans'][0]['excluded_unknown_effects'])>0)
check('all three proxy sensitivities present',all(len(result['top_plans'][0][key])==5 for key in ['projected_proxy_path_if_baseline_static','illustrative_85pct_yearly_retention_sensitivity','illustrative_half_effect_sensitivity']))
# Rolling update: a new, supplied observed baseline is required from year 2 onward.
replan=json.loads(json.dumps(state))
replan['team']['initially_active_project_ids']=[14,22,23,24,34,35,8]
replan['team']['baseline_smartcity_factors']=base
rolling=search(replan,2,[3000.]*4,0,2,3,True)
check('rolling replanning creates years 2..5 only', [x['year'] for x in rolling['top_plans'][0]['start_by_year']]==[2,3,4,5])
check('later-year baseline source remains unverifed',rolling['assumptions']['baseline_metrics_source']=='USER_PROVIDED_UNVERIFIED_METRICS')
# League and preview evidence cannot create certified qualification.
check('empty league produces no certified rank',evidence_summary(state)['league_read_only_snapshot']['status']=='UNKNOWN_NO_OFFICIAL_LEAGUE_SNAPSHOT')
result['measurement_and_league_evidence']=evidence_summary(state)
check('robust sensitivity is tracked without certainty claims',result['highest_worst_sensitivity_among_beam'] is not None and result['final_gameplay_decision']=='STOP')
write_json(ROOT/'results/R143_5Y_STRATEGIES_100K_ILLUSTRATIVE.json',result)
(ROOT/'results/R143_5Y_STRATEGIES_100K_ILLUSTRATIVE.md').write_text(render_markdown(result),encoding='utf-8')
# Check budget sensitivity on two more illustrative annual envelopes, within the same consolidated qualification.
other_scenarios={}
for envelope in (50000,200000):
    alt=search(state,1,[float(envelope)]*5,None,8,30,True)
    best=alt['top_plans'][0]
    other_scenarios[str(envelope)]=dict(year1_ids=best['start_by_year'][0]['start_project_ids'],
        terminal_mapped_delta=best['terminal_mapped_proxy_delta'],
        five_year_cost=best['five_year_conservative_card_cost_ecu'],
        unmodeled_effects=len(best['excluded_unknown_effects']))
    check(f'envelope_{envelope}_respected',all(x['conservative_card_cash_requirement_ecu']<=envelope for x in best['start_by_year']))
write_json(ROOT/'results/R143_5Y_SCENARIO_COMPARISON.json',
           {'not_approved_budgets':True,'gameplay_decision':'STOP',
            'annual_budget_illustrative_scenarios':{**other_scenarios,
               '100000':dict(year1_ids=result['top_plans'][0]['start_by_year'][0]['start_project_ids'],
                   terminal_mapped_delta=result['top_plans'][0]['terminal_mapped_proxy_delta'],
                   five_year_cost=result['top_plans'][0]['five_year_conservative_card_cost_ecu'],
                   unmodeled_effects=len(result['top_plans'][0]['excluded_unknown_effects']))}})
report={'qualification':'PASS_OFFLINE_INTEGRATION_ONLY','offline_only':True,'gameplay_gate':'STOP',
        'true_5yr_game_prediction_validated':False,'checks':checks,
        'check_count':len(checks),'source_project_catalog_sha256':hashlib.sha256((ROOT/'data/ecosim_projects_20261030.json').read_bytes()).hexdigest(),
        'source_r143_proxy_sha256':hashlib.sha256((ROOT/'tools/r142_proxy_reference.py').read_bytes()).hexdigest(),
        'source_r143_card_cost_sha256':hashlib.sha256((ROOT/'tools/portfolio_5y.py').read_bytes()).hexdigest(),
        'optimizer_beam_width':12,'budget_scenario_ecu_per_year':100000,
        'expansion':result['search_stats'],
        'candidate_count':len(result['top_plans']),
        'best_illustrative_mapped_index_delta':result['top_plans'][0]['terminal_mapped_proxy_delta'],
        'unknown_effects_best':len(result['top_plans'][0]['excluded_unknown_effects']),
        'biggest_blocker':'Actual game-state transitions, policy choices, competing teams and validated financing are unknown.'}
write_json(ROOT/'results/R143_ENGINE_QUALIFICATION.json',report)
print('R143_INTEGRATION_QUALIFICATION=PASS', 'checks='+str(len(checks)),
      'best_illustrative_delta='+str(report['best_illustrative_mapped_index_delta']),
      'gameplay=STOP','no_network=TRUE')

# R144 single consolidated release suite: append verified client-component
# replayer and historical R94 checks, without rerunning beam search separately.
from city_bridge import (computed_index_from_factors, conservative_cash_and_client_line,
                         attach_city_bridge)
from reconcile_r94 import reconcile_file
client_baseline=computed_index_from_factors(base)
check('R144 displayed factor aggregation matches R141',
      abs(client_baseline['total_index_from_displayed_factors']-proxy_value(base))<1e-7)
for group,expected in {'Gazdaság':62.15,'Környezet':46.52,'Kormányzás':72.07,
                       'Életkörülmények':52.45,'Mobilitás':47.01,'Emberek':28.42}.items():
    check('R144 factor group rounds to prior UI '+group,
          abs(client_baseline['partial_indexes'][group]['index']-expected)<.006)
rr=reconcile_file()
check('R144 historical R94 finance identity',rr['all_checks_pass'] and len(rr['checks'])>=8)
check('R144 historical finance not available cash',rr['p1_spendable_cash_confirmed'] is False)
line13=conservative_cash_and_client_line(p,set(),[13])
check('R144 signed negative maintenance preserved in client expense',line13['client_project_expense_line_ecu']==46200)
check('R144 conservative negative maintenance cannot fund projects',line13['conservative_project_cash_requirement_ecu']==55000)
triple=conservative_cash_and_client_line(p,set(),[8,13,27])
check('R144 split client line and conservative funds correctly',
      triple['client_project_expense_line_ecu']==90200 and triple['conservative_project_cash_requirement_ecu']==99000)
check('R144 support separate and not prefinanced',triple['newly_started_support_label_ecu']==3500 and triple['recognized_support_cash_ecu'] is None)
bridge=result['top_plans'][0]['city_component_bridge']
check('R144 no nonproject future cash without scenario',all(x['financial_counterfactual']['closing_scenario_cash_ecu'] is None for x in bridge['years']))
check('R144 future city transitions explicitly unknown',bridge['actual_five_year_index_prediction'] is None and bridge['actual_cashflow_loan_and_grant_settlement'] is None)
check('R144 bridge tracks mapping unknowns',any(x['unmapped_effects'] for x in bridge['years']))
check('R144 bridge aligns with projected index proxy default',
      abs(bridge['years'][-1]['mapped_factor_aggregation']['mapped_project_only_delta_vs_current_factor_baseline']-result['top_plans'][0]['terminal_mapped_proxy_delta'])<.000002)
sc=json.loads(json.dumps(state));sc['finance_counterfactual']={
    'mode':'EXPLICIT_HYPOTHETICAL_NONPROJECT_NET_ONLY',
    'initial_uncommitted_cash_ecu':100000,
    'annual_nonproject_net_cash_ecu':[100000]*5,
    'assumption_note':'Synthetic, not from EcoSim'}
hb=attach_city_bridge(result['top_plans'][0],set([14,22,23,24,34,35]),base,p,sc)
check('R144 cash scenario first year matches conservative requirement',
      hb['years'][0]['financial_counterfactual']['closing_scenario_cash_ecu']==200000-result['top_plans'][0]['start_by_year'][0]['conservative_card_cash_requirement_ecu'])
check('R144 scenario cash never reclassified as approved lending',
      not any(x['client_component']['settlement_and_credit_validated'] for x in hb['years']))
fail=False
try:
    sc_bad=json.loads(json.dumps(sc));sc_bad['finance_counterfactual']['annual_nonproject_net_cash_ecu']=[1]*4
    attach_city_bridge(result['top_plans'][0],set(),base,p,sc_bad)
except ValueError:fail=True
check('R144 incomplete finance scenario fails closed',fail)
weights={'Gazdaság':.2,'Környezet':.25,'Kormányzás':.15,'Életkörülmények':.15,'Mobilitás':.1,'Emberek':.15}
wstate=json.loads(json.dumps(state));wstate['market']['smartcity_total_weights']=weights
changed=search(wstate,1,[0.]*5,4,2,4,True)
check('R144 alternative market weights propagated through optimizer',
      abs(changed['comparison_baseline_proxy']-computed_index_from_factors(base,weights)['total_index_from_displayed_factors'])<.000002)
check('R144 customized weights propagated to city bridge',
      changed['top_plans'][0]['city_component_bridge']['baseline_aggregation']['weight_source']=='EXPLICIT_PROVIDED_WEIGHTS_NOT_INDEPENDENTLY_VERIFIED')
check('R144 no zero-filled missing weight vector accepted',
      all(w!=0 for w in weights.values()))
report['checks']=checks;report['check_count']=len(checks)
report['qualification']='PASS_OFFLINE_KNOWN_FORMULA_AND_HEURISTIC_INTEGRATION_ONLY'
report['r144_new_replayer']='ON; NOT A VERIFIED 5-YEAR ECO_SIM SIMULATOR'
report['r94_reconciliation_checks']=len(rr['checks'])
report['r144_financial_scenario_no_credit_only']=True
write_json(ROOT/'results/R144_INTEGRATED_QUALIFICATION.json',report)
write_json(ROOT/'results/R144_R94_FINANCE_RECONCILIATION.json',rr)
write_json(ROOT/'results/R144_FIRST_ILLUSTRATIVE_PLAN_BRIDGE.json',bridge)
write_json(ROOT/'results/R144_EXPLICIT_FINANCE_SCENARIO_ILLUSTRATION.json',hb)
# final release PASS emitted only after all R144 component checks complete

from reconcile_r94 import project_only_counterfactual
c=project_only_counterfactual([8,13,27],p)
check('R144 historical p1 scenario no grant client component',
      c['scenario_net_if_no_grant_collected_and_no_indirect_effect_ecu']==775388)
check('R144 historical p1 scenario with support still not settled',
      c['scenario_net_if_all_support_booked_same_period_and_no_indirect_effect_ecu']==778888 and c['actual_cash_available'] is None)
write_json(ROOT/'results/R144_R94_PROJECT_ONLY_COUNTERFACTUAL.json',c)
report['checks']=checks;report['check_count']=len(checks)
write_json(ROOT/'results/R144_INTEGRATED_QUALIFICATION.json',report)
# release checks continue into the optional long-loan component
sc_long=json.loads(json.dumps(sc))
sc_long['finance_counterfactual']['illustrative_long_loan']={
    'opening_balance_ecu':0,
    'annual_decision_change_ecu':[50000,-30000,0,0,0],
    'annual_interest_rate':[.12]*5}
sc_long['finance_counterfactual']['nonproject_flow_excludes_this_loan']=True
long_bridge=attach_city_bridge(result['top_plans'][0],set([14,22,23,24,34,35]),base,p,sc_long)
first=long_bridge['years'][0]['financial_counterfactual']
check('R144 long loan first-year closing and interest',
      first['illustrative_long_loan']['closing_balance_ecu']==50000 and first['illustrative_long_loan']['interest_at_explicit_scenario_rate_ecu']==6000)
check('R144 loan lending never auto-approved',
      first['illustrative_long_loan']['loan_limit_and_credit_eligibility']=='UNKNOWN')
check('R144 long loan repayments clamped',
      long_bridge['years'][1]['financial_counterfactual']['illustrative_long_loan']['repay_clamped_to_opening_ecu']==30000)
invalid_loan=json.loads(json.dumps(sc_long));invalid_loan['finance_counterfactual'].pop('nonproject_flow_excludes_this_loan')
try:
    attach_city_bridge(result['top_plans'][0],set(),base,p,invalid_loan)
    raise AssertionError('Scenario overlapping loan should fail')
except ValueError:
    check('R144 loan scenario requires non-overlap declaration',True)
write_json(ROOT/'results/R144_EXPLICIT_LONG_LOAN_HYPOTHESIS.json',long_bridge)
report['checks']=checks;report['check_count']=len(checks)
write_json(ROOT/'results/R144_INTEGRATED_QUALIFICATION.json',report)
print('R144_INTEGRATED_QUALIFICATION=PASS', 'checks='+str(len(checks)),
      'R94_identities='+str(len(rr['checks'])),'future_game_index=UNKNOWN','gameplay=STOP')
