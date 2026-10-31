#!/usr/bin/env python3
"""Independent targeted R162 adversarial checks and ONE historical end-to-end run.

No access to the game, no real data verification, no signed release attestation.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))
from json_integrity_r162 import loads_strict, read_json
from strategy_5y import permitted,parse_dependencies,project_index,derive_config
from policy_tracks import load_tracks
from tax_response_r153 import read_document as load_tax_scenarios
from decision_evidence import read_json as load_evidence
from decision_desk_r149 import make_report
from independent_audit_r160 import audit_plan

checks=[]
def ok(label, condition):
    if not condition:raise AssertionError('R162_FAILED: '+label)
    checks.append(label)
def blocked(label,callback):
    try:callback()
    except (ValueError,TypeError,UnicodeError,json.JSONDecodeError):ok(label,True)
    else:raise AssertionError('R162_ACCEPTED_INVALID: '+label)

with tempfile.TemporaryDirectory(prefix='ecosim-r162-') as tmp:
    tmp=Path(tmp)
    p=tmp/'data.json'
    def raw(contents):
        p.write_text(contents,encoding='utf-8')
        return read_json(p)
    ok('Conforming JSON accepted',raw('{"amount":12.5,"active":true,"v":null}')=={'amount':12.5,'active':True,'v':None})
    ok('Finite exponent retained',raw('{"amount":1e20}')['amount']==1e20)
    ok('Subnormal exponent retained',raw('{"amount":1e-310}')['amount']>0)
    for number in ('1e999','-1e999','9.99e9999','1e309','-1e309'):
        blocked('Overflow exponent rejected '+number,lambda n=number:raw('{"cash":'+n+'}'))
    for number in ('NaN','Infinity','-Infinity'):
        blocked('Nonstandard literal rejected '+number,lambda n=number:raw('{"v":'+n+'}'))
    blocked('Nested duplicate rejected',lambda:raw('{"a":{"limit":4,"limit":9}}'))
    blocked('Top-level duplicate rejected',lambda:raw('{"period":1,"period":2}'))
    blocked('Malformed JSON rejected',lambda:raw('{"broken":1,}'))
    blocked('Missing JSON rejected',lambda:read_json(tmp/'missing.json'))
    blocked('Size guard retained',lambda:read_json(p,max_bytes=1))
    ok('Legacy strategy import uses shared strict reader',__import__('strategy_5y').read_json is read_json)
    for txt in ('{"v":1e999}','{"a":1,"a":2}','{"v":NaN}'):
        blocked('Raw shared parser rejects '+txt,lambda x=txt:loads_strict(x))
    p.write_text('{"schema":"ECOSIM_R145_POLICY_TRACKS_V1","tracks":[],"overflow":1e999}')
    blocked('Policy track input guards exponent overflow',lambda:load_tracks(p))
    p.write_text('{"schema":"ECOSIM_R145_POLICY_TRACKS_V1","tracks":[],"schema":"FAKE"}')
    blocked('Policy track guards ambiguous schema',lambda:load_tracks(p))
    p.write_text('{"schema":"ECOSIM_R153_TAX_COUNTERFACTUAL_V1","source_class":"SYNTHETIC_TEST_ONLY","market":1e999}')
    blocked('Tax path input guards overflow',lambda:load_tax_scenarios(p))
    p.write_text('{"verified_observations":[],"verified_observations":[1]}')
    blocked('Passive evidence input guards duplicate',lambda:load_evidence(p))
    deps={1:[(2,True,'not other')],2:[]}
    ok('Negative condition rejects same-year forbidden project in strict mode',permitted((1,2),set(),deps,False)==(False,False))
    ok('Negative condition rejects same-year forbidden project in conditional mode',permitted((1,2),set(),deps,True)==(False,False))
    ok('Negative condition rejects prior-year forbidden project',permitted((1,),{2},deps,False)==(False,False))
    ok('Negative condition allows absence of forbidden project',permitted((1,),set(),deps,False)==(True,False))
    pos={1:[(2,False,'other')],2:[]}
    ok('Positive condition disallows same-year strict',permitted((1,2),set(),pos,False)==(False,False))
    ok('Positive condition allows explicitly conditional same-year',permitted((1,2),set(),pos,True)==(True,True))
    ok('Positive condition allows prior-year running',permitted((1,),{2},pos,False)==(True,False))
    idx=project_index(); actual,unresolved=parse_dependencies(idx)
    ok('Historical 30 positive requires 29',any(d[0]==29 and not d[1] for d in actual[30]))
    ok('Historical 31 positive requires 27',any(d[0]==27 and not d[1] for d in actual[31]))
    ok('Historical display label mapping remains complete',not unresolved)
    histstate=read_json(ROOT/'inputs/official_state.template.json')
    config=derive_config(histstate,idx,1,[100000]*5,None)
    ok('No input promoted to verified game state',config['verified'] is False)
    ok('STOP authority remains outside search',not config['verified'])

# Exactly ONE historical full decision run through the retained optimizer.
report=make_report(ROOT/'inputs/mvp_run.r157_robust_historical.json')
old=read_json(ROOT/'results/R160_HISTORICAL_CONSISTENCY_DEMO/DECISION_DESK.json')
ok('Historical report schema unchanged',report['schema']==old['schema'])
ok('Twenty candidate IDs remain identical',set(x['candidate_id'] for x in report['candidate_comparison'])==set(x['candidate_id'] for x in old['candidate_comparison']))
ok('Historical candidate count retained',len(report['candidate_comparison'])==len(old['candidate_comparison'])==20)
ok('Independent plan auditing retained',all(not x['r160_independent_constraint_replay']['hard_rule_violations'] for x in report['candidate_comparison']))
ok('Historical, not live mode',report['run_mode']=='HISTORICAL_ILLUSTRATION')
ok('No game writes',report['game_writes']==0)
ok('Mandatory STOP',report['gameplay_gate']=='STOP')
ok('No true game result claimed',report['game_result_prediction_validated'] is False)

receipt={'schema':'ECOSIM_R162_FRESH_CONTEXT_SECURITY_AND_DEPENDENCY_REVIEW_V1',
         'new_checks_executed':len(checks),'status':'PASS_OFFLINE_ONLY',
         'checks':[{'name':name,'status':'PASS'} for name in checks],
         'historical_e2e_runs_now':1,'historic_r161_tests_not_rerun':62,
         'historic_candidates_identical':True,
         'authenticated_live_state_confirmed':False,
         'actual_predictive_accuracy_validated':False,'game_writes':0,
         'gameplay_gate':'STOP'}
(ROOT/'results/R162_QUALIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('R162_OFFLINE_REVIEW=PASS; NEW_CHECKS='+str(len(checks))+'; HISTORIC_CANDIDATES=20; GAME=STOP')
