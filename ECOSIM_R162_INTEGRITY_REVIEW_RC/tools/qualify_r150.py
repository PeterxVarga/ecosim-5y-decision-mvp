#!/usr/bin/env python3
"""ONE consolidated qualification: inherited R149 + new R150 decision quality.

Synthetic counterexamples check dominance, incomplete evidence and period
comparability. No network, Codex, browser or EcoSim write.
"""
from __future__ import annotations
import copy, json, runpy,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))

# One inherited qualification, retaining the entire real R143→R149 code path.
runpy.run_path(str(ROOT/'tools/qualify_r149.py'),run_name='r149_consolidated')
from decision_desk_r149 import make_report,read_json,write_json,render_md
from decision_quality_r150 import assess_candidate_quality,_dominates
from compare_runs_r150 import compare
from decision_view_r149 import render_offline_html
checks=[]
def check(name,value):
    if not value:raise AssertionError(name)
    checks.append(name)
def fails(name, fn):
    try:fn()
    except (ValueError,TypeError,KeyError,IndexError):checks.append(name)
    else:raise AssertionError('Expected fail: '+name)

report=read_json(ROOT/'results/R149_MVP_DEMO/DECISION_DESK.json')
q=report['r150_sampled_quality']
check('R150 source context and start year',report['start_year']==1 and 'source_context' in report)
check('R149 original report schema preserved',report['schema']=='ECOSIM_R149_OFFLINE_DECISION_DESK_RESULT_V1')
check('quality schema recognized',q['schema']=='ECOSIM_R150_SAMPLED_DECISION_QUALITY_V1')
check('quality provenance and game STOP',q['gameplay_gate']=='STOP' and q['real_world_win_probability'] is None and q['actual_optimality_claim'] is None)
check('quality no causal certainty',q['pareto_on_partial_metrics_not_realized_city_outcomes'])
check('quality sample contains shown candidates',q['sampled_candidate_count']>=len(report['candidate_comparison']))
check('one frontier per envelope',set(q['envelope_frontiers'])==set(e['id'] for e in report['comparison_envelopes']))
check('all sampled frontiers refer only to candidate IDs',all(len(v['nondominated_in_sample_ids'])<=v['within_hypothetical_budget_count'] for v in q['envelope_frontiers'].values()))
check('zero actual approvals',all(e['server_feasible'] is None and e['globally_optimal'] is None for e in q['envelope_frontiers'].values()))
check('quality sampled gap not actual score regret',all(x['not_game_score_regret'] for x in q['sampled_opportunity_gaps']))
check('sampled gaps nonnegative',all(x['gap_to_best_sampled_mapped_proxy_delta']>=0 and x['gap_to_best_sampled_stressed_proxy_delta']>=0 for x in q['sampled_opportunity_gaps']))
check('first action groups cannot authorize gameplay',all(x['action_authorized'] is False for x in q['first_year_action_clusters']))
check('first action groups do not call count probability',all('sampled_candidate_count_not_probability' in x for x in q['first_year_action_clusters']))
check('HTML contains R150 quality section','R150 · részleges Pareto-összevetés' in render_offline_html(report))
check('MD contains R150 quality section','R150 – mintán belüli Pareto-szűrés' in render_md(report))
check('HTML remains scriptless','<script' not in render_offline_html(report) and 'href=' not in render_offline_html(report))
check('year labels honor start_year=3', 'É3:' in render_offline_html({**report,'start_year':3}))

# Controlled sampled Pareto counterexample: A dominates B; C is expensive but
# higher partial proxy and cannot be silently discarded by cheapness.
def plan(cid,cost,proxy,stress,unknown,conditional=False):
    return {'candidate_id':cid,'project_ids_by_year':[[1],[],[],[],[]],
            'conservative_project_need_ecu_by_year':[cost,0,0,0,0],
            'five_year_conservative_project_need_ecu':cost,
            'mapped_terminal_proxy_delta':proxy,'worst_of_existing_illustrative_mapped_sensitivities':stress,
            'unmapped_or_uncertain_project_effect_occurrences':unknown,
            'same_year_co_start_condition_unverified':conditional,
            'inside_explicit_hypothetical_envelopes':['test'] if cost<=100 else [],
            'envelope_comparison':{'test':{'passes_this_hypothetical_envelope':cost<=100}}}
A=plan('a',50,1.2,0.5,0);B=plan('b',70,1.1,0.4,1);C=plan('c',90,1.5,0.6,2);D=plan('d',110,3,2,0)
env=[{'id':'test','limits_ecu':[100]*5}]
x=assess_candidate_quality([A,B,C,D],env,1)
check('Pareto A dominates B',_dominates(A,B) and x['envelope_frontiers']['test']['sampled_dominance_witnesses']['b']==['a'])
check('Pareto preserves tradeoff high effect expensive',set(x['envelope_frontiers']['test']['nondominated_in_sample_ids'])=={'a','c'})
check('outside envelope excluded from regret',all(y['candidate_id']!='d' for y in x['sampled_opportunity_gaps']))
check('Pareto sampled feasibility 3',x['envelope_frontiers']['test']['within_hypothetical_budget_count']==3)
check('Pareto no forecast',x['real_world_win_probability'] is None and x['gameplay_gate']=='STOP')
fails('duplicate candidate IDs fail closed',lambda:assess_candidate_quality([A,A],env,1))
fails('negative cost cannot be masked',lambda:assess_candidate_quality([{**A,'conservative_project_need_ecu_by_year':[-1,0,0,0,0]}],env,1))
fails('wrong year count fail closed',lambda:assess_candidate_quality([A],env,3))

before=copy.deepcopy(report);after=copy.deepcopy(report)
check('historical comparisons cannot be yearly causal',compare(before,after)['comparison_class']=='HISTORICAL_OR_NONCURRENT_COMPARISON_ONLY')
check('compare never approves gameplay',compare(before,after)['gameplay_gate']=='STOP' and not compare(before,after)['causal_change_identified'])
fails('non-STOP report rejected',lambda:compare({**before,'gameplay_gate':'GO'},after))
fails('fake schema rejected',lambda:compare({'schema':'fake','gameplay_gate':'STOP','game_writes':0},after))
for obj in (before,after):
    obj['run_mode']='CURRENT_SNAPSHOT_REVIEW'
    obj['source_context']={'team':'Synthetic','market':'SYNTHETIC','period':1,
                           'capture_mode':'CURRENT_READONLY','observed_column_kind':'PLAN','round':'TEST'}
check('same-period compare is descriptive',compare(before,after)['comparison_class']=='SAME_PERIOD_DESCRIPTIVE_COMPARISON_ONLY')
check('same-period signatures compared only descriptively',compare(before,after)['same_period_candidate_id_set_comparable'])
after['comparison_envelopes'][0]['limits_ecu'][0]+=500
check('changed scenario envelope exposed',len(compare(before,after)['hypothetical_envelope_changes'])==1)
after['source_context']['period']=2
check('adjacent year compare cannot certify result',compare(before,after)['comparison_class']=='SEQUENTIAL_YEAR_DESCRIPTIVE_REPLAN_NOT_REALIZED_VALIDATION' and compare(before,after)['same_period_candidate_id_set_comparable'] is False)
after['source_context']['market']='OTHER'
check('mixed city report cannot claim transition',compare(before,after)['comparison_class']=='INCOMPARABLE_CITY_IDENTITY')
after['source_context']['market']='SYNTHETIC';after['source_context']['period']=4
check('noncontiguous period cannot infer drift',compare(before,after)['comparison_class']=='NONCONSECUTIVE_OR_REVERSED_PERIODS_NO_DRIFT_INFERENCE')

# Regression: incomplete current-state input must remain STOP and produce no
# candidate. Reuse the R149 test case, avoid a second costly search.
with tempfile.TemporaryDirectory() as d:
    cfg=read_json(ROOT/'inputs/mvp_run.current.template.json')
    path=Path(d)/'cfg.json';write_json(path,cfg)
    blocked=make_report(path)
    check('R150 current no real fields stays blocked',blocked['gameplay_gate']=='STOP' and not blocked['candidate_comparison'])
    check('R150 blocked still exposes empty quality',blocked['r150_sampled_quality']['sampled_candidate_count']==0)
    check('R150 blocked does not claim known finance',not blocked['proof_gates']['actual_spendable_cash_and_loan_authority_confirmed'])
    a=Path(d)/'old.json';b=Path(d)/'new.json';z=Path(d)/'compared.json'
    write_json(a,report);write_json(b,report)
    # Import the native comparison function without shelling out/using external tools
    value=compare(read_json(a),read_json(b));write_json(z,value)
    check('comparison JSON serializes without NAN',read_json(z)['gameplay_gate']=='STOP')

inherited=read_json(ROOT/'results/R149_QUALIFICATION.json')
receipt={'schema':'ECOSIM_R150_CONSOLIDATED_QUALIFICATION_V1',
         'status':'PASS_OFFLINE_CODE_ONLY',
         'inherited_checks':inherited['total_checks'],
         'new_checks':len(checks),'total_checks':inherited['total_checks']+len(checks),
         'checks':checks,'game_writes':0,'network_actions':0,'codex_called':False,
         'actual_game_score_accuracy':None,'real_win_probability':None,'gameplay_gate':'STOP'}
write_json(ROOT/'results/R150_QUALIFICATION.json',receipt)
# New R150 output uses the same actual R149 engine, now extended with a full
# sampled quality inventory. No alternative planning engine is invented.
output=ROOT/'results/R150_MVP_DEMO';output.mkdir(exist_ok=True)
write_json(output/'DECISION_DESK.json',report)
(output/'DECISION_DESK.md').write_text(render_md(report),encoding='utf8')
(output/'DECISION_DESK.html').write_text(render_offline_html(report),encoding='utf8')
write_json(output/'INPUT_HASHES.json',report['inputs'])
write_json(output/'REPORT_COMPARISON_ILLUSTRATIVE.json',compare(report,report))
print('R150_CONSOLIDATED=PASS; inherited='+str(inherited['total_checks'])+'; new='+str(len(checks))+
      '; total='+str(receipt['total_checks'])+'; examined_sample='+str(report['r150_sampled_quality']['sampled_candidate_count'])+
      '; gameplay=STOP; actual_accuracy=UNKNOWN')
