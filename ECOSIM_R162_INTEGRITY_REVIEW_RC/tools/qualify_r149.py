#!/usr/bin/env python3
"""One consolidated R149 qualification: legacy R148 + end-to-end offline MVP.

Only ephemeral synthetic state is used to exercise current-snapshot code paths.
No outside software, credentials or game state. Source PASS != server prediction.
"""
from __future__ import annotations
import copy,json,math,runpy,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))

# Single inherited regression in this release, no separate testing rounds.
runpy.run_path(str(ROOT/'tools/qualify_r148.py'),run_name='r148_consolidated')
from decision_desk_r149 import _load_config,make_report,render_md,_scenario_status
from intake_r149 import normalize_capture
from decision_view_r149 import render_offline_html
from strategy_5y import read_json,write_json
from r142_proxy_reference import WEIGHTS

checks=[]
def check(name,condition):
    if not condition:raise AssertionError(name)
    checks.append(name)
def fail(name,fn):
    try:fn()
    except (ValueError,TypeError,KeyError,IndexError):check(name,True)
    else:raise AssertionError('Expected rejection: '+name)

cfg_path=ROOT/'inputs/mvp_run.illustrative.json'
run_cfg=_load_config(cfg_path)
check('3 declared hypothetical envelopes',len(run_cfg['annual_envelopes'])==3)
check('mode explicitly historical',run_cfg['mode']=='HISTORICAL_ILLUSTRATION')
check('budget assumptions cannot be called approved',all('VERIFIED' not in x['source_class'] or 'NOT_SERVER_VERIFIED' in x['source_class'] for x in run_cfg['annual_envelopes']))

historical_capture=read_json(ROOT/'inputs/capture_historical_example.json')
historical_state,historical_evidence=normalize_capture(historical_capture)
check('historical capture remains historical',historical_state['provenance']['capture_mode']=='HISTORICAL_REFERENCE')
check('intake preserves old p1 PLAN vs p0 FACT semantics',historical_state['provenance']['observed_column_kind']=='PLAN')
check('intake reconciles historical p1 factor index',abs(historical_evidence['recomputed_display_index']-52.48)<.02)
check('historical capture cannot authenticate live',historical_evidence['live_state_verified_from_capture'] is False)
check('intake does not invent project cap',historical_state['market']['maxProjectPerTurn'] is None)
check('intake does not invent borrowing permission',historical_state['market']['short_loan_max'] is None)

bad=copy.deepcopy(historical_capture);bad['displayed_index']+=3
fail('mismatched displayed index must reject',lambda:normalize_capture(bad))
bad=copy.deepcopy(historical_capture);bad['factors'].pop('Digitalizáció')
fail('missing factor rejects',lambda:normalize_capture(bad))
bad=copy.deepcopy(historical_capture);bad['parameters']['team']['session_token']='secret'
fail('unrecognized input key rejected',lambda:normalize_capture(bad))
bad=copy.deepcopy(historical_capture);bad['capture_mode']='unverified'
fail('unclassified capture rejected',lambda:normalize_capture(bad))

bad=copy.deepcopy(run_cfg);bad['annual_envelopes'][0]['limits_ecu'][0]=-1
with tempfile.TemporaryDirectory() as d:
    path=Path(d)/'invalid.json';write_json(path,bad)
    fail('negative envelopes reject',lambda:_load_config(path))
bad=copy.deepcopy(run_cfg);bad['annual_envelopes'][1]['id']=bad['annual_envelopes'][0]['id']
with tempfile.TemporaryDirectory() as d:
    path=Path(d)/'invalid.json';write_json(path,bad)
    fail('duplicate envelopes reject',lambda:_load_config(path))
bad=copy.deepcopy(run_cfg);bad['policy_envelope_index']=100
with tempfile.TemporaryDirectory() as d:
    path=Path(d)/'invalid.json';write_json(path,bad)
    fail('invalid policy envelope index rejected',lambda:_load_config(path))

# Actual operator MVP path, in one call using the existing R148 optimizer.
out=make_report(cfg_path)
check('MVP output schema',out['schema']=='ECOSIM_R149_OFFLINE_DECISION_DESK_RESULT_V1')
check('3 searches completed',len(out['scenario_searches'])==3)
check('run produced bounded candidate set',0<len(out['candidate_comparison'])<=20)
check('all three scenario searches label no verified finance',all(x['finance_is_real_world_approved'] is False for x in out['scenario_searches']))
check('all candidate finance gate STOP',all(x['gameplay_gate']=='STOP' and not x['cash_and_credit_authorized'] for x in out['candidate_comparison']))
check('all candidate game forecast UNKNOWN',all(x['actual_game_terminal_index'] is None for x in out['candidate_comparison']))
check('all candidate outcome is hypothetical',all(x['qualification']=='OFFLINE_HYPOTHETICAL_CANDIDATE_NOT_A_GAME_FORECAST' for x in out['candidate_comparison']))
check('each candidate has complete 5-year schedule',all(len(x['project_ids_by_year'])==5 for x in out['candidate_comparison']))
check('cross-envelope comparisons exist',all(len(x['envelope_comparison'])==3 for x in out['candidate_comparison']))
check('candidate IDs unique',len(set(x['candidate_id'] for x in out['candidate_comparison']))==len(out['candidate_comparison']))
check('candidate costs and five-year sums agree',all(abs(sum(x['conservative_project_need_ecu_by_year'])-x['five_year_conservative_project_need_ecu'])<.01 for x in out['candidate_comparison']))
check('synthetic policy track compared without certification',bool(out['policy_track_comparison']) and all(x['gameplay_gate']=='STOP' for x in out['policy_track_comparison']))
check('source evidence hashes present',all(len(x['sha256'])==64 for x in out['inputs'].values()))
check('read-only p0 and p1 remain distinct',len(out['passive_historical_reconciliation']['snapshots'])==2 and not out['passive_historical_reconciliation']['paired_same_period_plan_fact'])
check('no measured calibration pairs asserted',out['calibration_evidence']['paired_approved_plan_observations']==0)
check('empty same-period plan evidence stays 0',out['calibration_evidence']['paired_descriptive_plan_comparisons']['pair_count']==0)
check('no league snapshot is not certified rank',out['league_readonly_evidence']['status']=='UNKNOWN_NO_OFFICIAL_LEAGUE_SNAPSHOT')
check('no real five-year prediction claimed',out['game_result_prediction_validated'] is False)
check('no game action is ever emitted',out['game_writes']==0 and out['recommended_game_action'] is None and out['gameplay_gate']=='STOP')
check('no network, Codex or browser claimed',out['network_actions']==0 and not out['codex_called'] and out['browser_actions']==0)
check('rank cannot claim a guaranteed winning plan',out['candidate_comparison'][0]['actual_game_terminal_index'] is None)
check('priority contains project/finance/preview missing',{'PROJECT_CAP_AND_STATE','FINANCE_PROOF','PAIRED_PREVIEW'} <= set(x['key'] for x in out['next_evidence_to_collect']))
check('rendered human-facing markdown has STOP and conditional disclaimers','STOP' in render_md(out) and 'feltételezett' in render_md(out))
check('HTML has offline human-readable summary and STOP', '<!doctype html>' in render_offline_html(out) and 'STOP' in render_offline_html(out))
check('HTML has no external scripts or href', '<script' not in render_offline_html(out) and 'href=' not in render_offline_html(out))
check('action families explicitly not probabilities', bool(out['first_year_action_families']) and all('sampled_plan_occurrences_not_probability' in f for f in out['first_year_action_families']))
check('proof gates never assert authorized money',out['proof_gates']['actual_spendable_cash_and_loan_authority_confirmed'] is False)
check('proof gates block gameplay',out['proof_gates']['gameplay_gate']=='STOP')
check('historical run cannot claim current conditional search',out['proof_gates']['historical_illustration_only'] and not out['proof_gates']['conditional_current_snapshot_usable'])

with tempfile.TemporaryDirectory() as d:
    d=Path(d)
    c=copy.deepcopy(historical_capture)
    c['capture_mode']='CURRENT_READONLY';c['parameters']['market']['smartcity_total_weights']=None
    normalized,receipt=normalize_capture(c)
    check('current capture with unknown weights does not use historical weights',receipt['index_reconciliation_status']=='BLOCKED_MISSING_CURRENT_WEIGHTS' and receipt['recomputed_display_index'] is None)
    c['source_evidence_id']='REPLACE_ME'
    fail('placeholder current source evidence fails closed',lambda:normalize_capture(c))
    one=copy.deepcopy(run_cfg)
    one.pop('state_path');one['capture_path']=str(ROOT/'inputs/capture_historical_example.json')
    one_path=d/'capture_config.json';write_json(one_path,one)
    capture_out=make_report(one_path)
    check('single-pass capture input produces conditional historical comparison',bool(capture_out['candidate_comparison']) and 'read_only_capture' in capture_out['inputs'])
    both=copy.deepcopy(one);both['state_path']='inputs/official_state.template.json'
    both_path=d/'both.json';write_json(both_path,both)
    fail('state and capture together forbidden',lambda:_load_config(both_path))
    wrong=copy.deepcopy(one);wrong['mode']='CURRENT_SNAPSHOT_REVIEW';wrong['project_cap_assumption']=None
    wrong_path=d/'wrong.json';write_json(wrong_path,wrong)
    fail('historical capture cannot enter current search',lambda:make_report(wrong_path))

check('rendered league and calibration status', 'Azonos periódusú PLAN-párok' in render_md(out) and 'Liga pillanatkép' in render_md(out))

# Current-mode safety gate: prior test data must not masquerade as current.
with tempfile.TemporaryDirectory() as d:
    d=Path(d)
    old=copy.deepcopy(run_cfg);old['mode']='CURRENT_SNAPSHOT_REVIEW';old['project_cap_assumption']=None
    old['state_path']=str(ROOT/'inputs/official_state.template.json')
    path=d/'blocked_config.json';write_json(path,old)
    blocked=make_report(path)
    check('missing CURRENT input blocks search',not blocked['scenario_searches'] and not blocked['candidate_comparison'])
    check('current mode does not accept R94 template',not blocked['current_snapshot_usable_for_conditional_search'])
    check('current gate detailed blockers',bool(blocked['current_snapshot_blockers']))

    old['state_path']=str(d/'historical.json');write_json(d/'historical.json',historical_state)
    write_json(path,old);blocked_old=make_report(path)
    check('historical capture specifically blocked from live', 'HISTORICAL_OR_UNCLASSIFIED_CAPTURE_IS_NOT_LIVE' in blocked_old['current_snapshot_blockers'])

    # Use entirely synthetic structurally valid data to demonstrate restartable
    # current-state workflow, without asserting EcoSim live confirmation.
    synthetic=copy.deepcopy(historical_state)
    synthetic['provenance']['capture_mode']='CURRENT_READONLY'
    synthetic['provenance']['source']='SYNTHETIC_TEST_FIXTURE_NOT_REAL'
    synthetic['provenance']['current_period']=1
    synthetic['market']['maxProjectPerTurn']=4
    synthetic['market']['smartcity_total_weights']={k:v[0] for k,v in WEIGHTS.items()}
    synthetic['team']['initially_active_project_ids']=[14,22,23,24,34,35]
    synthetic['team']['already_selected_new_project_ids_current_period']=[]
    synthetic['team']['project1_active_previous_period']=False
    write_json(d/'synthetic.json',synthetic)
    old['state_path']=str(d/'synthetic.json')
    # Small one-envelope, strictly bounded input for the test path.
    old['annual_envelopes']=old['annual_envelopes'][1:2]
    old['policy_tracks_path']=None
    old['policy_envelope_index']=0
    old['search']={'beam':2,'shortlist':4,'options_per_envelope':2,'same_year_conditions':'PRIOR_YEAR_ONLY'}
    write_json(path,old)
    synthetic_out=make_report(path)
    check('synthetic current structure passes preflight',synthetic_out['current_snapshot_usable_for_conditional_search'])
    check('synthetic current route returns candidate hypotheses',bool(synthetic_out['candidate_comparison']))
    check('valid current format still never returns GO',synthetic_out['gameplay_gate']=='STOP' and not synthetic_out['game_result_prediction_validated'])

check('replan year labels from configured start',_scenario_status([10,20],[30,40],3)['per_year'][0]['year']==3)
check('replan cost check can detect a scenario overspend',not _scenario_status([10,50],[30,40],3)['passes_this_hypothetical_envelope'])

receipt={'schema':'ECOSIM_R149_SINGLE_CONSOLIDATED_MVP_QUALIFICATION_V1',
         'status':'PASS_OFFLINE_CODE_ONLY',
         'inherited_checks':read_json(ROOT/'results/R148_QUALIFICATION.json')['total_checks'],
         'new_checks':len(checks),
         'total_checks':read_json(ROOT/'results/R148_QUALIFICATION.json')['total_checks']+len(checks),
         'checks':checks,
         'no_live_game_actions':True,'network_access':False,'codex_executed':False,
         'real_game_prediction_accuracy':None,'actual_budget_or_credit_certification':False,
         'five_year_winning_strategy_proven':False,'gameplay_gate':'STOP'}
write_json(ROOT/'results/R149_QUALIFICATION.json',receipt)
write_json(ROOT/'results/R149_MVP_DEMO/DECISION_DESK.json',out)
(ROOT/'results/R149_MVP_DEMO/DECISION_DESK.md').write_text(render_md(out),encoding='utf8')
write_json(ROOT/'results/R149_MVP_DEMO/INPUT_HASHES.json',out['inputs'])
(ROOT/'results/R149_MVP_DEMO/DECISION_DESK.html').write_text(render_offline_html(out),encoding='utf-8')
print('R149_MVP_CONSOLIDATED=PASS; inherited='+str(receipt['inherited_checks'])+
      '; new='+str(len(checks))+'; total='+str(receipt['total_checks'])+
      '; scenarios='+str(len(out['scenario_searches']))+
      '; candidates='+str(len(out['candidate_comparison']))+
      '; gameplay=STOP; terminal_accuracy=UNKNOWN')
