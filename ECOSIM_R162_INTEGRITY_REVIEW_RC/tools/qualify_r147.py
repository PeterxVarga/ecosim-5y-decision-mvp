#!/usr/bin/env python3
"""R147 single consolidated end-to-end qualification: 131 inherited + new checks.

All inputs are offline; no account, browser, game state, JS evaluation, network.
"""
from __future__ import annotations
from pathlib import Path
import copy, hashlib, json, runpy, sys, math
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))

# Run legacy regression exactly once for the whole release.
runpy.run_path(str(ROOT/'tools/qualify_r146.py'),run_name='r146_regression')
from effect_replay_r147 import apply_effect, replay_effects, normalize_metric, BOUNDS
from r142_proxy_reference import COEFF, evaluate
from portfolio_5y import project_index
from city_bridge import computed_index_from_factors,_project_effects_for_year
from strategy_5y import evaluate_proxy,search,read_json,write_json
from paired_calibration_r147 import measure_pairs
from verify_source_r147 import audit
from passive_r146 import reconcile_snapshots

checks=[]
def check(name,ok):
    if not ok:raise AssertionError(name)
    checks.append(name)

def reject(name,call):
    try:call()
    except (ValueError,TypeError,KeyError):check(name,True)
    else:raise AssertionError(name+' failed open')

old=read_json(ROOT/'results/R146_INTEGRATED_QUALIFICATION.json')
check('inherited R146 131 total checks',old['total_checks']==131)
check('old game writes zero',old['game_writes']==0)
check('source alias unemployment exact',normalize_metric('Munkanélküliség')=='Munkanélküli arány')
check('business aliases not invented',all(normalize_metric(x) not in COEFF for x in ('Kisvállalkozások száma','Középvállalkozások száma')))
check('unemployment display factor recognized',normalize_metric('Munkanélküliség') in COEFF)
check('four anchored display bounds',len(BOUNDS)==4)
check('company friendliness 100% cap',BOUNDS['Vállalkozóbarátság'][1]==100.)
check('public transit 80% cap',BOUNDS['Tömegközlekedők aránya, %'][1]==80.)
check('transport quality 200 display cap',BOUNDS['Közlekedési minőség'][1]==200.)
check('settlement factor cap 2.1–95.6',BOUNDS['Településfejlettség']==(2.1,95.6))

baseline=read_json(ROOT/'data/ECOSIM_R141_PROJECT_PROXY.json')['baseline_from_UI']
idx=project_index();known=set(COEFF)
check('historical baseline sum remains 52.48 displayed',abs(computed_index_from_factors(baseline)['total_index_from_displayed_factors']-52.48)<0.01)
check('35 project cards remain intact',len(idx)==35)
check('baseline project #13 fully mapped',evaluate_proxy(idx,{13},baseline)[1]==0)
check('project #27 small business remains unknown', 'Kisvállalkozások száma' in evaluate_proxy(idx,{27},baseline)[2])
check('project #4 medium business remains unknown','Középvállalkozások száma' in evaluate_proxy(idx,{4},baseline)[2])
temp=dict(baseline)
replay_effects(temp,[(1,{'metric':'Munkanélküliség','value_percent':-1.0})],known)
check('unemployment effect of negative percent decreases unemployment',
      temp['Munkanélküli arány']<baseline['Munkanélküli arány'])

check('legacy and source replay agree on unsaturated #13',abs(evaluate([idx[13]],baseline)[0]-evaluate_proxy(idx,{13},baseline)[0])<1e-10)

f=dict(baseline);recs=replay_effects(f,[(4,{'metric':'Vállalkozóbarátság','value_percent':50})],known)
check('company friendliness upper clamp exact',f['Vállalkozóbarátság']<=100)
check('source replay records grouped flag',recs[0]['grouped_before_single_final_clamp'])
f={'Vállalkozóbarátság':90.}
# Separate premature clamp would produce 90 after +20 then -25;
# source product then single clamp yields 81 from 90 * 1.2 * .75.
rec=replay_effects(f,[(1,{'metric':'Vállalkozóbarátság','value_percent':20}),
                      (2,{'metric':'Vállalkozóbarátság','value_percent':-25})],known)
check('all project multipliers applied BEFORE single clamp',abs(f['Vállalkozóbarátság']-81)<1e-9)
check('project ordering not changing grouped cap',
      (lambda z:(replay_effects(z,[(2,{'metric':'Vállalkozóbarátság','value_percent':-25}),
                                    (1,{'metric':'Vállalkozóbarátság','value_percent':20})],known),abs(z['Vállalkozóbarátság']-81)<1e-9)[1])({'Vállalkozóbarátság':90.}))
f={'Vállalkozóbarátság':100.}
r=replay_effects(f,[(1,{'metric':'Vállalkozóbarátság','value_percent':-10})],known)
check('negative effect from saturated cap is flagged ambiguous',r[0]['uncertain_due_to_saturation'])
f={'Településfejlettség':95.5}
replay_effects(f,[(1,{'metric':'Településfejlettség','value_percent':10})],known)
check('settlement development source cap applied once',abs(f['Településfejlettség']-95.6)<1e-9)
f={'Tömegközlekedők aránya, %':70}
replay_effects(f,[(1,{'metric':'Tömegközlekedők aránya, %','value_percent':30})],known)
check('public transport 80 cap implemented',f['Tömegközlekedők aránya, %']==80)
reject('nonfinite effect rejected',lambda:replay_effects({'Munkanélküli arány':3},[(1,{'metric':'Munkanélküliség','value_percent':float('nan')})],known))
reject('negative total multiplier rejected',lambda:replay_effects({'Munkanélküli arány':3},[(1,{'metric':'Munkanélküliség','value_percent':-150})],known))

pairzero=measure_pairs(read_json(ROOT/'inputs/paired_plan.template.json'),idx)
check('zero pair yields ZERO count not accuracy',pairzero['pair_count']==0 and pairzero['forecast_accuracy_validated'] is False)
check('zero pair explicitly unknown',pairzero['no_observation_means_accuracy_unknown'])
s=read_json(ROOT/'inputs/historical_passive_summary_20261030.json')
check('p0 FACT p1 PLAN historic not controlled',reconcile_snapshots(s)['paired_same_period_plan_fact']==[])
# A synthetic pair purely verifies the calibration interface, not any source observation.
p1=next(x for x in s['snapshots'] if x['kind']=='PLAN')
obs=dict(team=p1['team'],market=p1['market'],period=p1['period'],source_evidence_id='SYNTHETIC_NO_GAME',captured_at=p1['captured_at'],
         kind='PLAN',displayed_index=p1['displayed_total_index'],factors=p1['factors'])
doc={'schema':'ECOSIM_R147_PAIRED_PLAN_OBSERVATIONS_V1',
     'pairs':[{'id':'synthetic-calibration-shape','before':copy.deepcopy(obs),
               'after':copy.deepcopy(obs),'new_project_ids':[], 'controls':{}}]}
res=measure_pairs(doc,idx)
check('same-period PLAN pair schema works',res['pair_count']==1)
check('synthetic pair no causality',res['pairs'][0]['causal_project_effect_isolated'] is False)
check('synthetic pair no transition',res['realized_annual_state_transition_validated'] is False)
check('control declarations absent not inferred',res['pairs'][0]['declared_other_decisions_held_fixed_not_independently_verified'] is False)
check('unchanged synthetic pair index delta zero',res['pairs'][0]['observed_plan_displayed_index_delta']==0)
corrupt=copy.deepcopy(doc);corrupt['pairs'][0]['after']['period']+=1
reject('inter-period pair rejected',lambda:measure_pairs(corrupt,idx))
corrupt=copy.deepcopy(doc);corrupt['pairs'][0]['before']['kind']='FACT'
reject('FACT-vs-PLAN rejected',lambda:measure_pairs(corrupt,idx))
corrupt=copy.deepcopy(doc);corrupt['pairs'][0]['after']['market']='other'
reject('different markets rejected',lambda:measure_pairs(corrupt,idx))
corrupt=copy.deepcopy(doc);corrupt['pairs'][0]['new_project_ids']=[1,1]
reject('duplicated project selected rejected',lambda:measure_pairs(corrupt,idx))
corrupt=copy.deepcopy(doc);corrupt['pairs'][0]['before']['source_evidence_id']=None
reject('missing evidence provenance rejected',lambda:measure_pairs(corrupt,idx))
corrupt=copy.deepcopy(doc);corrupt['pairs'][0]['before']['factors'].pop('Digitalizáció')
reject('incomplete factor vector rejected',lambda:measure_pairs(corrupt,idx))

# Source anchored verification compares against user-supplied R140B original JS,
# iff present in model workspace. The delivered ZIP only contains anchor hashes.
source=Path('/mnt/data/ecosim_r140_review/old/840.41fdc8e1.chunk.js')
if source.exists():
    a=audit(source)
    check('R140B SmartCity file hash and spans verified',a['matching'])
    check('nine anchors verified including qE clamp',a['anchors_checked']==9)
else:
    a={'source_external_verify':'OPTIONAL_NOT_PRESENT','anchors_checked':0}

all_rows=[e for p in idx.values() for e in p['effects']]
missing=[e for e in all_rows if normalize_metric(e['metric']) not in COEFF]
coverage={'schema':'ECOSIM_R147_CARD_EFFECT_COVERAGE_V1',
          'test_round_project_catalog_rows':len(all_rows),
          'distinct_project_count':len(idx),
          'direct_recognized_effect_rows':len(all_rows)-len(missing),
          'indirect_effect_rows_unquantified':len(missing),
          'unquantified_metric_labels':sorted(set(e['metric'] for e in missing)),
          'factor_aliases_source_anchored':{'Munkanélküliség':'Munkanélküli arány'},
          'source_anchored_caps':{k:list(v) for k,v in BOUNDS.items()},
          'partial_effect_replay_is_complete_city_score':False,
          'latency_or_project_effect_delay_known':False,
          'actual_gameplay_approval':False}
write_json(ROOT/'results/R147_EFFECT_COVERAGE.json',coverage)
write_json(ROOT/'results/R147_PAIRED_CALIBRATION.json',pairzero)
count=old['total_checks']+len(checks)
receipt={'schema':'ECOSIM_R147_SINGLE_CONSOLIDATED_QUALIFICATION_V1',
         'status':'PASS_OFFLINE_CODE_ONLY','prior_checks':old['total_checks'],
         'new_checks':len(checks),'total_checks':count,'new_check_names':checks,
         'source_anchor_verification':a,
         'paired_real_observations':0,
         'actual_five_year_score_predictive_accuracy':None,
         'server_calibration':'UNKNOWN',
         'game_writes':0,'external_calls':0,'codex_called':False,'gameplay_gate':'STOP'}
write_json(ROOT/'results/R147_QUALIFICATION.json',receipt)
print(f'R147_CONSOLIDATED_QUALIFICATION=PASS; inherited={old["total_checks"]}; new={len(checks)}; total={count}; gameplay=STOP; real_accuracy=UNKNOWN')
