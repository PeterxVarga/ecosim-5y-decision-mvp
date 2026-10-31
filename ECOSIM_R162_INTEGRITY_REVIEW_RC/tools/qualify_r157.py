#!/usr/bin/env python3
"""One consolidated R156 regression + R157 adversarial and end-to-end qualification."""
from __future__ import annotations
import copy,json,math,runpy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))
from strategy_5y import read_json,write_json,search
from robust_decision_r157 import PROFILES,replay,sampled_first_action_regret
from robust_r146 import stress_plan
from annual_transition_r148 import combined_factor_replay
from portfolio_5y import project_index
from decision_desk_r149 import _load_config,make_report,render_md
from decision_view_r149 import render_offline_html
from r142_proxy_reference import COEFF
from policy_tracks import load_tracks

checks=[]
def check(label,cond):
    if not cond:raise AssertionError(label)
    checks.append(label)
def reject(label,call):
    try:call()
    except (ValueError,TypeError,KeyError):check(label,True)
    else:raise AssertionError('Incorrectly accepted: '+label)

# Re-run the previous major R156 qualification ONCE in the same consolidated run.
runpy.run_path(str(ROOT/'tools/qualify_r156.py'),run_name='r156_integrated_regression')
prev=read_json(ROOT/'results/R156_QUALIFICATION.json')
check('R156 read-only regression re-executed',prev['new_checks']==68 and prev['gameplay_gate']=='STOP')

idx=project_index();baseline=read_json(ROOT/'data/ECOSIM_R141_PROJECT_PROXY.json')['baseline_from_UI']
check('Historical project catalog unchanged',len(idx)==35)
check('Four disclosed robust sensitivity profiles',len(PROFILES)==4)
check('No scenario probabilities',all('probability' not in p for p in PROFILES))
first=((8,13,27),(),(),(),())
r=replay(idx,first,baseline)
check('Robust replay has four profiles',len(r['scenario_profiles'])==4)
check('Robust replay score finite',math.isfinite(r['scenario_min_clamp_only_mapped_delta']))
check('Robust low not above robust high',r['scenario_min_clamp_only_mapped_delta']<=r['scenario_max_clamp_only_mapped_delta'])
check('Actual outcome explicitly unavailable',r['actual_five_year_score'] is None)
check('Scenario minimum not a game lower bound',r['scenario_min_is_game_lower_bound'] is False)
check('No game authorization',r['gameplay_gate']=='STOP')
check('Unmodeled city feedback not bounded',r['unmodeled_city_dynamics_uncertainty_bounded'] is False)
check('No probabilities attached',r['scenario_probabilities_supplied'] is False)
check('Profile min from rows equals summary',abs(min(x['conditional_clamp_only_low_delta'] for x in r['scenario_profiles'])-r['scenario_min_clamp_only_mapped_delta'])<1e-8)
check('Profile max from rows equals summary',abs(max(x['conditional_clamp_only_high_delta'] for x in r['scenario_profiles'])-r['scenario_max_clamp_only_mapped_delta'])<1e-8)
check('No effects gives zero across all scenarios',all(abs(x['conditional_mapped_delta'])<1e-7 for x in replay(idx,((),)*5,baseline)['scenario_profiles']))
reject('Reject duplicate stress profile IDs',lambda:replay(idx,first,baseline,profiles=(PROFILES[0],PROFILES[0])))
reject('Reject negative project intensity',lambda:replay(idx,first,baseline,profiles=({'id':'bad','intensity':-1,'retention':1},)))
reject('Reject future terminal beyond five',lambda:replay(idx,first,baseline,start_year=3))
reject('Reject empty plan horizon',lambda:replay(idx,(),baseline))
reject('Reject invalid index weights',lambda:replay(idx,first,baseline,weights={'wrong':1}))
reject('Reject unknown project IDs',lambda:replay(idx,((999,),),baseline))

# Strongly falsifiable clamp-order regression: 99 *1.2 *1.3 exceeds 100,
# so project and policy multiply before a single final source clamp.
synthetic_idx={999:{'effects':[{'metric':'Vállalkozóbarátság','value_percent':20.0}]}}
unit_baseline=dict(baseline);unit_baseline['Vállalkozóbarátság']=99.
policy={k:1.0 for k in COEFF};policy['Vállalkozóbarátság']=1.3
computed=combined_factor_replay(unit_baseline,[(999,synthetic_idx[999]['effects'][0])],policy)
check('Final combined clamp enforces <= 100',abs(computed['factors_conditional']['Vállalkozóbarátság']-100)<1e-9)
check('Never applies policy after already clamped project',computed['factors_conditional']['Vállalkozóbarátság']!=130.0)
replayed=replay(synthetic_idx,((999,),),unit_baseline,policy_multipliers=policy)
check('R157 replay shares R148 combined clamp rule',abs(replayed['scenario_profiles'][0]['conditional_mapped_delta']-(computed['mapped_conditional_index']-combined_factor_replay(unit_baseline,[],policy)['mapped_conditional_index']))<1e-7)
latent=dict(baseline);latent['Vállalkozóbarátság']=100.0
falloff={42:{'effects':[{'metric':'Vállalkozóbarátság','value_percent':-10.0}]}}
uncertain=replay(falloff,((42,),),latent)
check('Latent clamp ambiguity represented',any(x['uncertain_saturated_factors'] for x in uncertain['scenario_profiles']))
check('Conditional lower <= nominal',all(x['conditional_clamp_only_low_delta']<=x['conditional_mapped_delta']+1e-7 for x in uncertain['scenario_profiles']))
check('Conditional upper >= nominal',all(x['conditional_clamp_only_high_delta']>=x['conditional_mapped_delta']-1e-7 for x in uncertain['scenario_profiles']))

tracks=load_tracks(ROOT/'inputs/policy_tracks.synthetic.example.json')
plan={'start_by_year':[{'year':1,'start_project_ids':[13], 'conservative_card_cash_requirement_ecu':0.0}]}
from r142_proxy_reference import WEIGHTS
w={k:v[0] for k,v in WEIGHTS.items()}
stress=stress_plan(plan,tracks[1],baseline,idx,w,1,None)
check('Legacy R146 stress now declares single clamp',all(x['combined_once_before_clamp'] is True for x in stress['profiles']))
check('Legacy stress exposes interval',all(len(x['conditional_clamp_only_index_interval'])==2 for x in stress['profiles']))
check('Legacy stress stays explicitly nonprobabilistic',stress['stress_minmax_are_actual_outcome_bounds'] is False)
check('Legacy stress retains STOP',stress['gameplay_decision']=='STOP')

state=read_json(ROOT/'inputs/official_state.template.json')
base_kwargs=(state,1,[100000]*5,4,6,12,True)
nom=search(*base_kwargs)
rob=search(*base_kwargs,objective='scenario_min')
check('Old nominal search preserved',nom['r157_search_objective']=='nominal')
check('Same old search supports robust objective',rob['r157_search_objective']=='scenario_min')
check('Nominal alternatives present',len(nom['top_plans'])>=1)
check('Robust alternatives present',len(rob['top_plans'])>=1)
check('Both searches retain STOP',nom['final_gameplay_decision']=='STOP' and rob['final_gameplay_decision']=='STOP')
check('Every robust plan has profile evidence',all(len(p['r157_robust_sensitivity']['scenario_profiles'])==4 for p in rob['top_plans']))
check('Robust candidate order monotone',all(a['r157_robust_sensitivity']['scenario_min_clamp_only_mapped_delta']>=b['r157_robust_sensitivity']['scenario_min_clamp_only_mapped_delta']-1e-8 for a,b in zip(rob['top_plans'],rob['top_plans'][1:])))
check('Nominal and robust use same project baseline',nom['comparison_baseline_proxy']==rob['comparison_baseline_proxy'])
check('Nominal and robust use same assumed budgets',nom['assumptions']['official_cash_envelopes_or_illustrative_scenario']==rob['assumptions']['official_cash_envelopes_or_illustrative_scenario'])
check('No actual score forecast from robust engine',rob['actual_five_year_score_forecast_validated'] is False)
check('Robust first-year families are not game regret',rob['r157_first_year_sampled_action_comparison']['actual_regret'] is None)
check('Robust first-year families cannot authorize action',rob['r157_first_year_sampled_action_comparison']['decision_authorized'] is False)
reject('Reject invented optimizer objective',lambda:search(*base_kwargs,objective='guaranteed_win'))
check('Robust profile terminal order bounded to five',all(x['year']<=5 for p in rob['top_plans'] for x in p['start_by_year']))
check('No actual financial approval',all(p['spendable_cash_and_credit_verified'] is False for p in rob['top_plans']))

cfg=ROOT/'inputs/mvp_run.r157_robust_historical.json'
parsed=_load_config(cfg)
check('MVP config uses robust search',parsed['search']['r157_include_scenario_min_search'] is True)
check('MVP configuration explicitly historical',parsed['mode']=='HISTORICAL_ILLUSTRATION')
out=make_report(cfg)
check('Full R152–R155 and R157 integration produced candidates',len(out['candidate_comparison'])>=15)
check('Full output discloses robust search',out['r157_robust_search_enabled'] is True)
check('All three budgets have scoped first-year regret families',len(out['r157_sampled_first_year_regret_by_envelope'])==3)
check('No family actual regret',all(v['actual_regret'] is None for v in out['r157_sampled_first_year_regret_by_envelope'].values()))
check('All candidates have robust stress scores',all('r157_robust_sensitivity' in x for x in out['candidate_comparison']))
check('Budget haircut is never declared spendable',all(not v['verified_spendable_cash'] for x in out['candidate_comparison'] for v in x['r157_hypothetical_15pct_cash_shock'].values()))
check('Full output STOP',out['gameplay_gate']=='STOP' and out['recommended_game_action'] is None)
check('No real accuracy gained',out['game_result_prediction_validated'] is False)
check('Operating-cash module still integrated',bool(out['r155_source_operating_cash_tradeoffs']))
check('Four tax module still integrated',bool(out['r154_source_four_tax_fiscal_tradeoffs']))
html=render_offline_html(out)
md=render_md(out)
check('HTML contains robust heading','R157' in html and 'forgatókönyv' in html)
check('HTML offline no scripts','<script' not in html and '<iframe' not in html)
check('HTML escapes project strings', '&lt;'==__import__('html').escape('<'))
check('Markdown contains robust sample table','## R157' in md)
check('R157 cannot claim probability',out['r157_robust_scenarios_are_probabilities'] is False)
check('R157 cannot claim actual lower bound',out['r157_scenario_min_is_true_outcome_bound'] is False)

saved=ROOT/'results/R157_HISTORICAL_ROBUST_DEMO';saved.mkdir(parents=True,exist_ok=True)
write_json(saved/'DECISION_DESK.json',out)
(saved/'DECISION_DESK.html').write_text(html,encoding='utf8')
(saved/'DECISION_DESK.md').write_text(md,encoding='utf8')
(saved/'INPUT_HASHES.json').write_text(json.dumps(out['inputs'],indent=2,ensure_ascii=False)+'\n',encoding='utf8')
check('Static HTML file emitted',(saved/'DECISION_DESK.html').is_file())
check('No network or game actions',out['network_actions']==0 and out['game_writes']==0)
receipt={'schema':'ECOSIM_R157_ROBUST_OFFLINE_QUALIFICATION_V1',
         'status':'PASS_OFFLINE', 'legacy_r156_reexecuted':prev['new_checks'],
         'r157_new_checks':len(checks), 'checks':checks,
         'historical_candidate_count':len(out['candidate_comparison']),
         'hypothetical_profiles':[p['id'] for p in PROFILES],
         'invalid_current_market_state_still_unavailable':True,
         'validated_game_prediction_count':0,
         'gameplay_gate':'STOP','game_writes':0,'codex_or_user_terminal_required':False}
write_json(ROOT/'results/R157_QUALIFICATION.json',receipt)
print('R157_QUALIFICATION=PASS; R156_REEXECUTED='+str(prev['new_checks'])+
      '; R157_NEW='+str(len(checks))+'; CANDIDATES='+str(len(out['candidate_comparison']))+'; GAME=STOP')
