#!/usr/bin/env python3
"""R161 adversarial release-candidate qualification; one historic E2E run.

Only qualifies our *offline* software and its provenance gates. Does not make a
prediction accuracy, cash solvency, server acceptance, or compliance claim.
"""
from __future__ import annotations
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))
from strategy_5y import read_json, derive_config, project_index, write_json
from decision_desk_r149 import _resolve, make_report
from independent_audit_r160 import audit_plan
from release_guard_r161 import allowed_rel, validate_sums, inventory, sha_bytes, verify_tree, verify_zip

checks=[]
def check(name,passed):
    if not passed:raise AssertionError('R161_FAIL: '+name)
    checks.append({'name':name,'result':'PASS'})
def reject(name,fn):
    try:fn()
    except (ValueError,TypeError,KeyError,OSError,UnicodeError,json.JSONDecodeError):check(name,True)
    else:raise AssertionError('R161_FAIL_ACCEPTED: '+name)

with tempfile.TemporaryDirectory(prefix='ecosim-r161-audit-') as tmp:
    tmp=Path(tmp)
    def parse_raw(raw):
        f=tmp/'input.json';f.write_text(raw,encoding='utf-8');return read_json(f)
    check('Normal JSON parses',parse_raw('{"a":1,"b":{"v":0}}')=={'a':1,'b':{'v':0}})
    check('Booleans and null remain typed',parse_raw('{"x":true,"y":null}')=={'x':True,'y':None})
    reject('Top-level duplicate provenance rejected',lambda:parse_raw('{"source_evidence_id":"one","source_evidence_id":"two"}'))
    reject('Nested duplicate market cap rejected',lambda:parse_raw('{"market":{"maxProjectPerTurn":4,"maxProjectPerTurn":20}}'))
    reject('Duplicate financial source class rejected',lambda:parse_raw('{"finance":{"source_class":"HISTORICAL","source_class":"CURRENT"}}'))
    for x in ('NaN','Infinity','-Infinity'):
        reject('Nonstandard JSON constant rejected '+x,lambda x=x:parse_raw('{"v":'+x+'}'))
    reject('Malformed JSON rejected',lambda:parse_raw('{not-json}'))
    reject('Missing JSON file rejected',lambda:read_json(tmp/'nonexistent.json'))
    big=tmp/'big.json';big.write_bytes(b' '+b'0'*10_000_010)
    reject('Oversized JSON rejected',lambda:read_json(big))
    conf=ROOT/'inputs/mvp_run.r157_robust_historical.json'
    check('Legacy relative release-root input retained',_resolve(conf,'inputs/official_state.template.json')==ROOT/'inputs/official_state.template.json')
    check('Legacy nested config input retained',_resolve(conf,'inputs/paired_plan.template.json')==ROOT/'inputs/paired_plan.template.json')
    check('Inside-root absolute input retained',_resolve(conf,str(ROOT/'inputs/official_state.template.json'))==ROOT/'inputs/official_state.template.json')
    reject('Host absolute secrets path rejected',lambda:_resolve(conf,'/etc/passwd'))
    reject('Traversal outside release rejected',lambda:_resolve(conf,'../../../../etc/passwd'))
    reject('Missing input file rejected',lambda:_resolve(conf,'inputs/does-not-exist.json'))
    reject('NUL path rejected',lambda:_resolve(conf,'inputs/x\\x00.json'))
    (tmp/'source.json').write_text('{}',encoding='utf-8')
    external_conf=tmp/'run.json';external_conf.write_text('{}',encoding='utf-8')
    check('User-provided adjacent input is allowed',_resolve(external_conf,'source.json')==tmp/'source.json')
    (tmp/'escape.json').symlink_to('/etc/passwd')
    reject('Config sibling symlink escape rejected',lambda:_resolve(external_conf,'escape.json'))
    for name in ('../bad','/absolute','a\\b','foo/../bar','.env','.git/config','__pycache__/code.py','id_rsa','foo/./bar'):
        reject('Invalid archive member '+name,lambda name=name:allowed_rel(name))
    check('Canonical nested release member allowed',allowed_rel('tools/strategy_5y.py')=='tools/strategy_5y.py')
    good='a'*64+'  tools/example.py'
    check('Checksum line parsed',validate_sums(good)=={'tools/example.py':'a'*64})
    reject('Duplicate checksum member rejected',lambda:validate_sums(good+'\n'+good))
    reject('Incorrect digest rejected',lambda:validate_sums('xyz  example'))
    symlinks=tmp/'invent';symlinks.mkdir();(symlinks/'safe.txt').write_text('okay');(symlinks/'link.txt').symlink_to('/etc/passwd')
    reject('Release inventory refuses symlink',lambda:inventory(symlinks))
    (symlinks/'link.txt').unlink()
    check('Release inventory checks bytes',inventory(symlinks)=={'safe.txt':hashlib.sha256(b'okay').hexdigest()})
    # Real immutable-release gate: independently corrupt bytes and file sets.
    mini=tmp/'MINI_RELEASE';mini.mkdir()
    (mini/'sample.txt').write_text('known-good',encoding='utf-8')
    digest=sha_bytes((mini/'sample.txt').read_bytes())
    (mini/'SHA256SUMS').write_text(digest+'  sample.txt\n',encoding='utf-8')
    meta={'schema':'ECOSIM_R161_IMMUTABLE_OFFLINE_RELEASE_V1','qualifier':'PASS_OFFLINE_ONLY',
          'sha256sums_sha256':sha_bytes((mini/'SHA256SUMS').read_bytes()),
          'file_count':1,'gameplay_gate':'STOP','game_actions':0,'live_eco_sim_data_verified':False}
    (mini/'R161_RELEASE_MANIFEST.json').write_text(json.dumps(meta),encoding='utf-8')
    check('Unmodified miniature release verifies',verify_tree(mini)['checked_files']==1)
    (mini/'sample.txt').write_text('tampered',encoding='utf-8')
    reject('Release guard rejects modified bytes',lambda:verify_tree(mini))
    (mini/'sample.txt').write_text('known-good',encoding='utf-8')
    (mini/'unexpected.txt').write_text('extra',encoding='utf-8')
    reject('Release guard rejects extra members',lambda:verify_tree(mini))
    (mini/'unexpected.txt').unlink()
    with zipfile.ZipFile(tmp/'good-mini.zip','w') as z:
        for path in sorted(mini.iterdir()):z.write(path,'MINI_RELEASE/'+path.name)
    check('Matching ZIP entry hashes verified',verify_zip(tmp/'good-mini.zip',mini)['zip_verified_files']==3)
    with zipfile.ZipFile(tmp/'bad-mini.zip','w') as z:
        for path in sorted(mini.iterdir()):z.write(path,'MINI_RELEASE/'+path.name)
        z.writestr('MINI_RELEASE/../bad.txt','malicious')
    reject('ZIP traversal member blocked',lambda:verify_zip(tmp/'bad-mini.zip',mini))
    meta['gameplay_gate']='GO'
    (mini/'R161_RELEASE_MANIFEST.json').write_text(json.dumps(meta),encoding='utf-8')
    reject('Release gate refuses fabricated gameplay authorization',lambda:verify_tree(mini))
    for value in (False,True):
        fake={'provenance':{'source':'SYNTHETIC_CLAIM','source_evidence_id':'declared','captured_at_local':'2026-10-31T15:00:00+01:00','team':'T','market':'M','current_period':1},
              'team':{'initially_active_project_ids':[],'already_selected_new_project_ids_current_period':[],'project1_active_previous_period':False},
              'market':{'maxProjectPerTurn':4,'cap_source':'SPOOFED_SERVER'}}
        if value:fake['team']['baseline_smartcity_factors']=read_json(ROOT/'data/ECOSIM_R141_PROJECT_PROXY.json')['baseline_from_UI']
        d=derive_config(fake,project_index(),1,[100_000]*5,None)
        check('Self-asserted source cannot verify server state '+str(value),d['verified'] is False)
        check('Claimed cap remains explicitly unverified '+str(value),'NOT_SERVER_VERIFIED' in d['cap_source'])
        check('Operator metadata does not become authority '+str(value),d['operator_declared_metadata_present'] is True)
        if value:check('Baseline label preserves declared unverified source',d['baseline_source'].startswith('OPERATOR_DECLARED_'))
    idx=project_index();active=[i for i,p in idx.items() if p['status_p1']=='Fut']
    audit=audit_plan(idx,start_year=1,active_ids=active,fixed_first_ids=[],previous_project1_active=None,
        base_project_cap=4,annual_budgets=[100000]*5,starts=[[8,13,27],[4,9,21,28],[5,16,17,26],[1,29],[6,20,25,30]])
    check('Independent historical plan replay still valid',not audit['hard_rule_violations'])
    check('Server authorization remains null',audit['actual_game_eligibility'] is None)
    check('Budget never marked approved',audit['actual_funding_approval'] is None)

# ONE real historical pipeline run through unchanged R160 search, not a shadow optimizer.
report=make_report(ROOT/'inputs/mvp_run.r157_robust_historical.json')
old=read_json(ROOT/'results/R160_HISTORICAL_CONSISTENCY_DEMO/DECISION_DESK.json')
check('Report schema preserved',report['schema']==old['schema'])
check('Historic mode not live',report['run_mode']=='HISTORICAL_ILLUSTRATION')
check('All game writes remain zero',report['game_writes']==0)
check('Gameplay gate STOP',report['gameplay_gate']=='STOP')
check('No game score prediction certified',report['game_result_prediction_validated'] is False)
check('Candidate count remains consistent',len(report['candidate_comparison'])==len(old['candidate_comparison']))
check('Candidate starts unchanged',set(x['candidate_id'] for x in report['candidate_comparison'])==set(x['candidate_id'] for x in old['candidate_comparison']))
check('R160 independent audits remain active',all(not c['r160_independent_constraint_replay']['hard_rule_violations'] for c in report['candidate_comparison']))
check('Reported hypothetical envelopes preserved',len(report['comparison_envelopes'])==3)
check('New provenance guard does not promote server authenticity',report['gameplay_gate']=='STOP')
check('No true accuracy is invented',report['realized_prediction_accuracy'] is None if 'realized_prediction_accuracy' in report else report['game_result_prediction_validated'] is False)

receipt={'schema':'ECOSIM_R161_OFFLINE_ADVERSARIAL_QUALIFICATION_V1',
 'status':'PASS_OFFLINE_ONLY','new_checks':len(checks),'checks':checks,
 'full_historical_end_to_end_runs':1,'prior_r160_checks_documented_not_rerun':63,
 'historical_sample_candidate_count':len(report['candidate_comparison']),
 'historical_candidate_set_unchanged':True,'official_live_server_state_confirmed':False,
 'true_forecast_accuracy_measured':False,'game_writes':0,'gameplay_gate':'STOP',
 'independent_fresh_context_human_review_performed':False}
write_json(ROOT/'results/R161_QUALIFICATION.json',receipt)
print('R161_ADVERSARIAL_RELEASE=PASS; CHECKS='+str(len(checks))+'; FULL_E2E=1; PLANS='+str(len(report['candidate_comparison']))+'; GAME=STOP')
