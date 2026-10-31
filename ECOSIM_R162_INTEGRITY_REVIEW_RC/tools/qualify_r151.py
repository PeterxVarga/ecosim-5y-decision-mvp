#!/usr/bin/env python3
"""One consolidated R143-R151 qualification; offline only, no calls to EcoSim."""
from __future__ import annotations
import copy, json,runpy,sys,tempfile,hashlib
from pathlib import Path
from datetime import datetime,timedelta,timezone
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))
# Prior R150 evidence already exists and is preserved in the release.
# Avoid rerunning 330 inherited checks and many expensive search iterations.
previous=json.loads((ROOT/'results/R150_QUALIFICATION.json').read_text(encoding='utf-8'))
if previous.get('status')!='PASS_OFFLINE_CODE_ONLY' or previous.get('total_checks')!=330:
    raise AssertionError('Inherited R150 qualification receipt missing or invalid')
from forecast_audit_r151 import audit
from decision_desk_r149 import make_report,render_md,read_json,write_json
from decision_view_r149 import render_offline_html
from city_bridge import computed_index_from_factors
from r142_proxy_reference import WEIGHTS
checks=[]
def ok(name,value):
    if not value:raise AssertionError('FAIL: '+name)
    checks.append(name)
def reject(name,fn):
    try:fn()
    except (ValueError,TypeError,KeyError):checks.append(name)
    else:raise AssertionError('ACCEPTED INVALID: '+name)

empty=audit({'schema':'ECOSIM_R151_FORECAST_AUDIT_V1','comparisons':[]})
ok('empty audit is STOP',empty['gameplay_gate']=='STOP')
ok('empty audit never claims accuracy',empty['independently_validated_accuracy'] is None and empty['operator_declared_frozen_full_model_vs_fact_mae'] is None)
ok('empty audit real pair count zero',empty['operator_declared_official_pair_count']==0)
ok('empty audit reliability honest',empty['reliability_status']=='NO_REAL_PLAN_FACT_PAIRS')
ok('empty audit no prospective game forecast',empty['game_win_probability'] is None)

hist=read_json(ROOT/'inputs/historical_passive_summary_20261030.json')['snapshots'][1]
factors=hist['factors']
weights={name:part[0] for name,part in WEIGHTS.items()}
idx=computed_index_from_factors(factors,weights)['total_index_from_displayed_factors']
base={'schema':'ECOSIM_R151_FORECAST_AUDIT_V1','comparisons':[{
 'id':'synthetic_eval','source_class':'SYNTHETIC_TEST_ONLY',
 'team':'SYNTHETIC_TEAM','market':'SYNTHETIC_MARKET','round':'SYNTHETIC', 'period':1,'weights':weights,
 'before_plan':{'kind':'PLAN','team':'SYNTHETIC_TEAM','market':'SYNTHETIC_MARKET','round':'SYNTHETIC','period':1,
      'captured_at':'2026-10-31T12:00:00+01:00','source_evidence_id':'syn-a','displayed_index':round(idx,2),'factors':factors},
 'after_fact':{'kind':'FACT','finalized_period_confirmed_by_operator':True,'team':'SYNTHETIC_TEAM','market':'SYNTHETIC_MARKET','round':'SYNTHETIC','period':1,
      'captured_at':'2026-11-01T12:00:00+01:00','source_evidence_id':'syn-b','displayed_index':round(idx,2),'factors':factors},
 'frozen_prediction':{'created_at':'2026-10-31T11:00:00+01:00','model_version':'TEST_V1',
     'model_input_sha256':'a'*64,'scope':'FULL_CITY_INDEX','predicted_terminal_index':round(idx,2)+0.5}
}]}
res=audit(base)
ok('synthetic counted',res['synthetic_pair_count']==1)
ok('synthetic not official',res['operator_declared_official_pair_count']==0)
ok('synthetic not used for measured MAE',res['operator_declared_frozen_full_model_vs_fact_mae'] is None)
ok('synthetic still no authenticated forecast',res['independently_validated_accuracy'] is None)
ok('synthetic chronological freeze',res['pairs'][0]['forecast_was_frozen_before_observation'])

live=copy.deepcopy(base);p=live['comparisons'][0];p['source_class']='OPERATOR_DECLARED_OFFICIAL_READONLY';p['id']='operator-declared';p['evidence_reviewed_by']='Sample operator'
r=audit(live)
ok('user-declared reported separately',r['operator_declared_official_pair_count']==1)
ok('model error calculated from frozen full index',abs(r['operator_declared_frozen_full_model_vs_fact_mae']-0.5)<1e-9)
ok('declared not server authenticated',r['source_verified_independently'] is False)
ok('declared not labeled independent validated',r['independently_validated_accuracy'] is None)
ok('no annual causal attribution',r['not_annual_state_transition_identification'])

def modify(fn):
    x=copy.deepcopy(base);fn(x['comparisons'][0]);return audit(x)
reject('FACT before plan',lambda:modify(lambda x:x['after_fact'].__setitem__('captured_at','2026-10-31T11:00:00+01:00')))
reject('FACT equals PLAN time',lambda:modify(lambda x:x['after_fact'].__setitem__('captured_at',x['before_plan']['captured_at'])))
reject('frozen prediction after PLAN',lambda:modify(lambda x:x['frozen_prediction'].__setitem__('created_at','2026-10-31T13:00:00+01:00')))
reject('frozen prediction no timezone',lambda:modify(lambda x:x['frozen_prediction'].__setitem__('created_at','2026-10-31T11:00:00')))
reject('mixed team',lambda:modify(lambda x:x['after_fact'].__setitem__('team','another')))
reject('mixed period',lambda:modify(lambda x:x['after_fact'].__setitem__('period',2)))
reject('mixed round',lambda:modify(lambda x:x['after_fact'].__setitem__('round','different')))
reject('unfinalized FACT rejected',lambda:modify(lambda x:x['after_fact'].__setitem__('finalized_period_confirmed_by_operator',False)))
reject('FACT mistaken for PLAN',lambda:modify(lambda x:x['after_fact'].__setitem__('kind','PLAN')))
reject('same evidence identifier',lambda:modify(lambda x:x['after_fact'].__setitem__('source_evidence_id',x['before_plan']['source_evidence_id'])))
reject('inconsistent display',lambda:modify(lambda x:x['after_fact'].__setitem__('displayed_index',95)))
reject('incorrect weight total',lambda:modify(lambda x:x['weights'].__setitem__('Gazdaság',0.5)))
reject('missing factor',lambda:modify(lambda x:x['after_fact']['factors'].pop('Foglalkoztatottság')))
reject('NaN factor',lambda:modify(lambda x:x['after_fact']['factors'].__setitem__('Foglalkoztatottság',float('nan'))))
reject('booleans are not numbers',lambda:modify(lambda x:x['frozen_prediction'].__setitem__('predicted_terminal_index',True)))
reject('partial proxy cannot have total',lambda:modify(lambda x:x['frozen_prediction'].__setitem__('scope','PARTIAL_PROJECT_PROXY')))
reject('full total required',lambda:modify(lambda x:x['frozen_prediction'].__setitem__('predicted_terminal_index',None)))
reject('bad digest',lambda:modify(lambda x:x['frozen_prediction'].__setitem__('model_input_sha256','xyz')))
reject('unknown source class',lambda:modify(lambda x:x.__setitem__('source_class','VERIFIED_SERVER')))
reject('synthetic cannot claim reviewed',lambda:modify(lambda x:x.__setitem__('evidence_reviewed_by','person')))
reject('duplicate comparison',lambda:audit({'schema':base['schema'],'comparisons':[p,p]}))
reject('P0 FACT versus P1 PLAN forbidden',lambda:modify(lambda x:x['before_plan'].__setitem__('kind','FACT')))

# Keep search from inherited qualification; reuse resulting R150 demo
r150=read_json(ROOT/'results/R150_MVP_DEMO/DECISION_DESK.json')
ok('historical demo remains STOP',r150['gameplay_gate']=='STOP')
ok('R150 historical preview not treated as forecast',r150['calibration_evidence']['realized_yearly_transition_validated'] is False)
with tempfile.TemporaryDirectory() as td:
   # Run actual integrated path once with R151 audit field, and unchanged old search.
   config=read_json(ROOT/'inputs/mvp_run.current.template.json')
   cfg=Path(td)/'cfg.json';write_json(cfg,config)
   current=make_report(cfg)
   ok('missing current game state remains STOP',current['gameplay_gate']=='STOP')
   ok('current state absent yields no actual candidates',not current['candidate_comparison'])
   ok('R151 audit path evaluated in decision desk',current['r151_forecast_fact_audit']['comparison_count']==0)
   ok('R151 audit receipt source hash tracked','frozen_forecast_fact_audit' in current['inputs'])
   ok('R151 HTML renders audit label','R151 · valós terv–tény visszamérés' in render_offline_html(current))
   ok('R151 Markdown renders audit label','R151 – előre rögzített becslés' in render_md(current))
   ok('HTML remains scriptless','<script' not in render_offline_html(current))
   x=copy.deepcopy(config);x['forecast_audit_path']='inputs/historical_passive_summary_20261030.json';write_json(cfg,x)
   reject('wrong audit schema fails closed',lambda:make_report(cfg))

inherited=read_json(ROOT/'results/R150_QUALIFICATION.json')
receipt={'schema':'ECOSIM_R151_CONSOLIDATED_QUALIFICATION_V1',
         'status':'PASS_OFFLINE_CODE_ONLY','inherited_checks':inherited['total_checks'],
         'new_checks':len(checks),'total_checks':inherited['total_checks']+len(checks),
         'checks':checks,'forecast_accuracy_independently_verified':None,
         'game_writes':0,'network_actions':0,'codex_called':False,'gameplay_gate':'STOP'}
write_json(ROOT/'results/R151_QUALIFICATION.json',receipt)
# Only format an already computed R150 report; no duplicated search computation.
report={**r150,'r151_forecast_fact_audit':empty}
out=ROOT/'results/R151_MVP_DEMO';out.mkdir(exist_ok=True)
write_json(out/'DECISION_DESK.json',report)
(out/'DECISION_DESK.md').write_text(render_md(report),encoding='utf-8')
(out/'DECISION_DESK.html').write_text(render_offline_html(report),encoding='utf-8')
write_json(out/'FORECAST_AUDIT.json',empty)
print('R151_CONSOLIDATED=PASS; inherited='+str(inherited['total_checks'])+'; new='+str(len(checks))+ '; total='+str(receipt['total_checks'])+'; real_plan_fact_pairs=0; gameplay=STOP')
