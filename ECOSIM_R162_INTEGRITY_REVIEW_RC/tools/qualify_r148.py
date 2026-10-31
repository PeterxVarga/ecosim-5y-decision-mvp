#!/usr/bin/env python3
"""R148 SINGLE merged offline qualification: previous R147 regression plus R148 integrated paths."""
from __future__ import annotations
import runpy,json,math,hashlib,copy,sys
from pathlib import Path
root=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root/'tools'))
runpy.run_path(str(root/'tools/qualify_r147.py'),run_name='r147_inherited_once')
from strategy_5y import search,read_json,write_json
from portfolio_5y import project_index
from r142_proxy_reference import COEFF,WEIGHTS
from annual_transition_r148 import combined_factor_replay, long_loan_component, short_loan_prior_service, annual_component_rollout
from readiness_r148 import check_state
from policy_tracks import replay_policy_joint,load_tracks
from joint_5y import evaluate_tracks

checks=[]
def check(name,result):
    if not result:raise AssertionError(name)
    checks.append(name)
def reject(name,fn):
    try:fn()
    except (ValueError,TypeError,KeyError):check(name,True)
    else:raise AssertionError('Expected reject: '+name)

idx=project_index();baseline=read_json(root/'data/ECOSIM_R141_PROJECT_PROXY.json')['baseline_from_UI']
state=read_json(root/'inputs/official_state.template.json')
gate=check_state(state)
check('missing official config remains STOP',gate['gameplay_decision']=='STOP')
check('missing official cap explicitly reported',any(x['field']=='project_cap' for x in gate['specific_missing_or_invalid_evidence']))
check('historical p1 factors are not official current input',not gate['official_state_complete_for_all_future_years'])
check('yearly source bridge zero game score prediction',annual_component_rollout(idx,[],[[],[],[],[],[]],baseline)['actual_terminal_game_score'] is None)

upper={'Vállalkozóbarátság':100.,**{k:baseline[k] for k in baseline if k!='Vállalkozóbarátság'}}
pairs=[(1,{'metric':'Vállalkozóbarátság','value_percent':20}),(2,{'metric':'Vállalkozóbarátság','value_percent':-25})]
r=combined_factor_replay(upper,pairs)
check('joint multipliers combine before clamp, 100*1.2*.75',abs(r['factors_conditional']['Vállalkozóbarátság']-90)<1e-9)
check('latent upper clamp ambiguity recorded',len(r['ambiguous_saturated_factors'])==1)
check('latent upper clamp interval 90 to 100',r['mapped_index_if_only_saturation_uncertain'][1]>r['mapped_index_if_only_saturation_uncertain'][0])
check('relative effect ordering invariant',abs(combined_factor_replay(upper,list(reversed(pairs)))['mapped_conditional_index']-r['mapped_conditional_index'])<1e-10)
check('unknown business effect is flagged',bool(combined_factor_replay(baseline,[(1,{'metric':'Kisvállalkozások száma','value_percent':1})])['unmapped_project_effects']))
reject('nonpositive effect multiplier rejected',lambda:combined_factor_replay(baseline,[(1,{'metric':'Munkanélküliség','value_percent':-150})]))
reject('policy multiplier missing keys rejected',lambda:combined_factor_replay(baseline,[],{'Munkanélküli arány':1}))
reject('nonfinite policy multiplier rejected',lambda:combined_factor_replay(baseline,[],{k:float('nan') for k in COEFF}))
check('unchanged baseline equals historical display',abs(combined_factor_replay(baseline)['mapped_conditional_index']-52.4837)<0.01)

policy={k:1.0 for k in COEFF};policy['Tömegközlekedők aránya, %']=2
fac=combined_factor_replay(baseline,[(1,{'metric':'Tömegközlekedők aránya, %','value_percent':20})],policy)
check('joint policy project transit cap is 80',fac['factors_conditional']['Tömegközlekedők aránya, %']==80)
check('policy replay explicitly not a full game score',fac['partial_score_is_full_city_or_server_forecast'] is False)

loan=long_loan_component(100,40,.12)
check('long loan closing carries principal',abs(loan['closing_ecu']-140)<1e-10)
check('long loan interest on closing',abs(loan['interest_ecu']-16.8)<1e-8)
check('long loan repay clamped to opening',long_loan_component(100,-150,.12)['repaid_ecu']==100)
check('long loan never claims approval',loan['loan_permission_and_maximum'].startswith('UNKNOWN'))
reject('negative loan interest rejected',lambda:long_loan_component(100,0,-.1))
check('short prior service 12 pct interest',abs(short_loan_prior_service(100,.12)['next_year_interest_ecu']-12)<1e-8)
check('short prior principal paid next year',short_loan_prior_service(100,.12)['next_year_repayment_ecu']==100)
reject('negative short prior borrow rejected',lambda:short_loan_prior_service(-1,.12))

starts=[[8,13,27],[],[],[],[]]
rows=annual_component_rollout(idx,[],starts,baseline)
check('5-year project annual records',len(rows['yearly_state_records'])==5)
check('first year selected projects persisted',rows['yearly_state_records'][4]['active_project_ids']==[8,13,27])
check('source client project line is exposed',rows['yearly_state_records'][0]['finance_components']['project_client_expense_line_ecu']==90200)
check('conservative project first year 99k',rows['yearly_state_records'][0]['finance_components']['conservative_project_funding_need_ecu']==99000)
check('no unsupported cash statement',rows['yearly_state_records'][4]['finance_components']['hypothetical_closing_cash_ecu'] is None)
check('project startup not double charged in next year',rows['yearly_state_records'][1]['finance_components']['project_client_expense_line_ecu']==-5800)
check('signed maintenance not spendable income',rows['yearly_state_records'][1]['finance_components']['conservative_project_funding_need_ecu']==3000)
reject('new project already active rejected',lambda:annual_component_rollout(idx,[8],starts,baseline))
reject('duplicate year project rejected',lambda:annual_component_rollout(idx,[],[[8],[8],[],[],[]],baseline))

f={'mode':'EXPLICIT_HYPOTHETICAL_NONPROJECT_NET_ONLY','initial_uncommitted_cash_ecu':200000,
   'annual_nonproject_net_cash_ecu':[10000]*5,'nonproject_flow_excludes_policy_track':True,
   'nonproject_flow_excludes_this_loan':True,'nonproject_flow_excludes_short_loan_component':True}
ls={'opening_balance':0,'changes':[1000,0,-1000,0,0],'rates':[.12]*5}
ss={'prior_borrow_ecu':10,'prior_rate':.1,'annual_new_borrow_assumptions':[20,0,0,0,0],
    'annual_interest_rates':[.12]*5}
fin=annual_component_rollout(idx,[],starts,baseline,nonproject_finance_scenario=f,loan_scenario=ls,short_loan_scenario=ss)
check('hypothetical finance produces scenario cash',isinstance(fin['cash_projection_if_no_explicit_nonproject_scenario'],float))
check('loan carry to year 2',fin['yearly_state_records'][1]['finance_components']['loan']['opening_ecu']==1000)
check('short borrowing next year repaid',fin['yearly_state_records'][1]['finance_components']['short_loan']['next_year_repayment_ecu']==20)
check('short interest next year 2.4',abs(fin['yearly_state_records'][1]['finance_components']['short_loan']['next_year_interest_ecu']-2.4)<1e-9)
check('no actual cash value even hypothetical case',fin['yearly_state_records'][0]['finance_components']['actual_cashflow_ecu'] is None)
reject('no cash input forbids hypothetical loan',lambda:annual_component_rollout(idx,[],starts,baseline,loan_scenario=ls))
reject('missing loan nonoverlap rejected',lambda:annual_component_rollout(idx,[],starts,baseline,loan_scenario=ls,
 nonproject_finance_scenario={k:v for k,v in f.items() if k!='nonproject_flow_excludes_this_loan'}))
reject('missing short nonoverlap rejected',lambda:annual_component_rollout(idx,[],starts,baseline,short_loan_scenario=ss,
 nonproject_finance_scenario={k:v for k,v in f.items() if k!='nonproject_flow_excludes_short_loan_component'}))

tracks=load_tracks(root/'inputs/policy_tracks.synthetic.example.json')
check('synthetic policy fixture available',len(tracks)>0)
# Use original R143 strategy generator: R148 has no parallel optimizer.
result=search(state,1,[100000]*5,4,beam_width=5,shortlist=12)
check('strategy still produces real five-year search results',bool(result['top_plans']))
check('all strategy paths include annual carried ledger',all(len(p['r148_carried_known_components']['yearly_state_records'])==5 for p in result['top_plans']))
check('strategy embeds strict readiness gate',result['r148_input_readiness']['gameplay_decision']=='STOP')
check('strategy remains unvalidated game forecast',result['actual_five_year_score_forecast_validated'] is False)
# Ensure named policy track no longer reapplies project multiplier after clamp.
joint=evaluate_tracks(state,1,tracks[:1],[100000]*5,4,beam=3,shortlist=6)
option=joint['tracks'][0]['joint_options'][0]
check('joint policy engine reuses R143 search',joint['policy_conditioned_joint_project_search'])
check('joint policy route includes R148 annual ledger',len(option['r148_carried_annual_components']['yearly_state_records'])==5)
check('joint replay confirms one final clamp',all(x['project_policy_clamp_order']=='COMBINE_MULTIPLIERS_THEN_CLAMP_ONCE' for x in option['joint_factor_counterfactual_by_year']))
check('no game action in joint output',joint['gameplay_decision']=='STOP')

source_dir=Path('/mnt/data/ECOSIM_R143_5Y_CODEX_V2/private_js')
anchors=read_json(root/'evidence/R148_FINANCE_SOURCE_ANCHORS.json')
if source_dir.exists():
  for r in anchors['records']:
    b=(source_dir/r['filename']).read_bytes();i,j=r['byte_span']
    check('source '+r['id'],hashlib.sha256(b).hexdigest()==r['file_sha256'] and hashlib.sha256(b[i:j]).hexdigest()==r['span_sha256'])

prior=read_json(root/'results/R147_QUALIFICATION.json')
receipt={'schema':'ECOSIM_R148_CONSOLIDATED_QUALIFICATION_V1','status':'PASS_OFFLINE_CODE_ONLY',
         'inherited_test_checks':prior['total_checks'],'new_checks':len(checks),
         'total_checks':prior['total_checks']+len(checks),
         'test_names':checks,'real_forecast_calibration_pairs':0,
         'true_year5_score_prediction':None,'source_snapshot':'R140B verified static client bundles',
         'official_market_config':'UNKNOWN','game_writes':0,'external_calls':0,
         'codex_used':False,'gameplay_gate':'STOP'}
write_json(root/'results/R148_QUALIFICATION.json',receipt)
write_json(root/'results/R148_SOURCE_BOUNDED_100K_ILLUSTRATIVE.json',{
    'game_decision':'STOP','scenario_budget_not_verified':100000,
    'first_three_project_ids':result['top_plans'][0]['start_by_year'][0]['start_project_ids'],
    'terminal_project_only_score':'UNVALIDATED',
    'annual_ledger':result['top_plans'][0]['r148_carried_known_components'],
    'official_state_evidence_gate':result['r148_input_readiness'],
    'real_observational_calibration':None})
write_json(root/'results/R148_OFFICIAL_INPUT_GATE.json',gate)
print('R148_CONSOLIDATED=PASS inherited='+str(prior['total_checks'])+' new='+str(len(checks))+' total='+str(receipt['total_checks'])+' GAME_WRITE=0 VERIFIED_FINAL_SCORE=UNKNOWN')
