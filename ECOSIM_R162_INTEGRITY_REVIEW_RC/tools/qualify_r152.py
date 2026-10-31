#!/usr/bin/env python3
"""R152 targeted adversarial qualification. Reuse inherited 377-check receipt.

Only one previously prepared integrated demo is inspected; no duplicate
expensive 5-year search or historical backfitting.
"""
from __future__ import annotations
import copy,csv,json,shutil,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))
from observation_bundle_r152 import compile_bundle
from run_evidence_pipeline_r152 import execute
from strategy_5y import read_json,write_json
old=read_json(ROOT/'results/R151_QUALIFICATION.json')
if old.get('total_checks')!=377 or old.get('status')!='PASS_OFFLINE_CODE_ONLY':
    raise AssertionError('R151 baseline receipt absent or unexpected')
packet=ROOT/'examples/R152_HISTORICAL_R94_READONLY_PACKET'
checks=[]
def ok(desc,cond):
    if not cond:raise AssertionError('FAIL: '+desc)
    checks.append(desc)
def reject(desc,fn):
    try:fn()
    except (ValueError,TypeError,KeyError):checks.append(desc)
    else:raise AssertionError('INVALID ACCEPTED: '+desc)

cap,state,receipt=compile_bundle(packet/'manifest.json')
ok('historical captures remain historical',cap['capture_mode']=='HISTORICAL_REFERENCE')
ok('all 29 current factor labels present',len(cap['factors'])==29)
ok('observed client index reconciled',abs(receipt['recomputed_display_index']-52.483733)<0.001)
ok('R94 observed display remains 52.48',receipt['original_display_index']==52.48)
ok('R94 finance balance 865588',receipt['finance_R94_reconciliation']['p1_observed_net_ecu']==865588)
ok('R94 finance 8 known checks',len(receipt['finance_R94_reconciliation']['checks'])==8)
ok('finance not spendable cash',receipt['finance_R94_reconciliation']['status'].endswith('NOT_SPENDABLE_BUDGET'))
ok('35 status lines',receipt['project_states']['rows']==35)
ok('six previously running',len(state['team']['initially_active_project_ids'])==6)
ok('none selected in historical plan',not state['team']['already_selected_new_project_ids_current_period'])
ok('no verified market cap is inferred',state['market']['maxProjectPerTurn'] is None)
ok('no future cash inferred',state['team']['confirmed_spendable_cash_ecu_by_year']==[None]*5)
ok('provenance not independently authenticated',not receipt['authoritative_server_state_verified'])
ok('gameplay STOP',receipt['gameplay_gate']=='STOP')
resultdir=ROOT/'results/R152_HISTORICAL_END_TO_END'
r=read_json(resultdir/'DECISION_DESK.json')
ok('existing planner reused with 15 sampled candidates',len(r['candidate_comparison'])==15)
ok('historical cannot claim current usability',not r['current_snapshot_usable_for_conditional_search'])
ok('end-to-end report still STOP',r['gameplay_gate']=='STOP')
ok('operator packet chained to decision',r['r152_offline_evidence_packet']['source_classification']=='HISTORICAL_TEST_ROUND_NOT_CURRENT')
ok('R152 HTML file has no script', '<script' not in (resultdir/'DECISION_DESK.html').read_text())
ok('source digest recorded',len(r['r152_offline_evidence_packet']['source_file_hashes']['factors']['sha256'])==64)
ok('evidence blockers for cash still unknown','confirmed_spendable_cash' in {x['name'] for x in read_json(resultdir/'R152_MISSING_EVIDENCE.json')['fields'] if x['status']=='MISSING_OR_UNVERIFIED'})

with tempfile.TemporaryDirectory() as tmp:
    p=Path(tmp)/'packet';shutil.copytree(packet,p)
    manifest=p/'manifest.json'
    def altered(mutator):
        m=read_json(manifest);mutator(m);write_json(manifest,m);return compile_bundle(manifest)
    base=read_json(manifest)
    reject('current cannot use historic finance R94',lambda:altered(lambda m:m.__setitem__('capture_mode','CURRENT_READONLY')))
    write_json(manifest,base)
    reject('traversal cannot leave packet',lambda:altered(lambda m:m.__setitem__('factor_table_path','../x.csv')))
    write_json(manifest,base)
    reject('remote file sources cannot be read',lambda:altered(lambda m:m.__setitem__('factor_table_path','https://example.com/x.csv')))
    write_json(manifest,base)
    reject('missing source is blocked',lambda:altered(lambda m:m.__setitem__('source_evidence_id','')))
    write_json(manifest,base)
    reject('unknown extra metadata blocked',lambda:altered(lambda m:m.__setitem__('session_cookie','secret')))
    write_json(manifest,base)
    reject('different market cannot reuse R94 finance',lambda:altered(lambda m:m.__setitem__('market','X')))
    write_json(manifest,base)
    reject('period 0 rejected',lambda:altered(lambda m:m.__setitem__('period',0)))
    write_json(manifest,base)
    reject('timestamp no offset in current rejected',lambda:altered(lambda m: m.update({'capture_mode':'CURRENT_READONLY','captured_at_local':'2026-10-31T13:45:00'})))
    write_json(manifest,base)
    reject('current placeholder evidence rejected',lambda:altered(lambda m: m.update({'capture_mode':'CURRENT_READONLY','captured_at_local':'2026-10-31T13:45:00+01:00','source_evidence_id':'REPLACE_ME'})))
    write_json(manifest,base)
    table=p/'factors_p1_plan.csv';original=table.read_text()
    rows=list(csv.DictReader(original.splitlines()))
    def replace_rows(newrows):
        with table.open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=['metric','value']);w.writeheader();w.writerows(newrows)
        return compile_bundle(manifest)
    reject('duplicate metric rejected',lambda:replace_rows(rows+[rows[0]]))
    reject('missing metric rejected',lambda:replace_rows(rows[:-2]+[rows[-1]]))
    reject('NaN metric rejected',lambda:replace_rows([{**r,'value':'nan'} if i==0 else r for i,r in enumerate(rows)]))
    reject('index mismatch rejected',lambda:replace_rows([{**r,'value':'90'} if r['metric']=='Okosváros index' else r for r in rows]))
    table.write_text(original)
    project=p/'projects_p0_to_p1.csv';origp=project.read_text()
    prow=list(csv.DictReader(origp.splitlines()))
    def replace_proj(new):
        with project.open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=['project_id','previous_running','selected_new']);w.writeheader();w.writerows(new)
        return compile_bundle(manifest)
    reject('project status incomplete rejected',lambda:replace_proj(prow[:-1]))
    reject('project status duplicate rejected',lambda:replace_proj(prow+[prow[0]]))
    reject('invalid boolean project status rejected',lambda:replace_proj([{**r,'previous_running':'1'} if i==0 else r for i,r in enumerate(prow)]))
    reject('contradictory project states rejected',lambda:replace_proj([{**r,'previous_running':'true','selected_new':'true'} if i==0 else r for i,r in enumerate(prow)]))
    project.write_text(origp)
    target=p/'outside.csv';target.write_text(original)
    (p/'linked.csv').symlink_to(target)
    reject('symlink inputs rejected',lambda:altered(lambda m:m.__setitem__('factor_table_path','linked.csv')))
    write_json(manifest,base)
    origparams=p/'parameters.json';op=origparams.read_text()
    origparams.write_text(json.dumps({'market':{'smartcity_total_weights':{'bad':1}}}))
    reject('bad weights rejected',lambda:compile_bundle(manifest))
    origparams.write_text(op)

# Run current-mode (no search) safely, using no fabricated current configuration.
with tempfile.TemporaryDirectory() as t:
    p=Path(t)/'packet';shutil.copytree(packet,p)
    m=read_json(p/'manifest.json')
    m.update({'capture_mode':'CURRENT_READONLY','captured_at_local':'2026-10-31T14:25:00+01:00',
              'source_evidence_id':'OPERATOR_DECLARED_TEST_INPUT_UNVERIFIED'})
    m.pop('finance_r94_path')
    # No actual market cap and no authoritative future finances supplied.
    write_json(p/'manifest.json',m)
    cfg=read_json(ROOT/'inputs/mvp_run.current.template.json')
    cfg['state_path']=None;cfg['capture_path']='inputs/capture_current.template.json'
    config=Path(t)/'cfg.json';write_json(config,cfg)
    # Here a synthetic 'current' copy of historical factors is used ONLY to test
    # the fail-closed behavior. Never ship this as a real-current sample.
    res=execute(p/'manifest.json',config,Path(t)/'out')
    ok('unverified synthetic current packet remains STOP',res['gameplay_gate']=='STOP')
    ok('no cap implies no current candidate search',res['candidates']==0)
    ok('current mode never uses historical fallback budget','confirmed_spendable_cash' in res['missing_fields'])
    reject('historic/current config mixing forbidden',lambda:execute(packet/'manifest.json',config,Path(t)/'wrong'))

write_json(ROOT/'results/R152_QUALIFICATION.json',{
 'schema':'ECOSIM_R152_CONSOLIDATED_QUALIFICATION_V1',
 'status':'PASS_OFFLINE_CODE_ONLY','inherited_checks_not_rerun':377,
 'new_checks':len(checks),'total_documented_checks':377+len(checks),
 'checks':checks,'expensive_search_runs_in_this_qualifier':0,
 'integrated_demo_search_executed_in_preparation':1,
 'gameplay_gate':'STOP','server_authentication':False,
 'validated_model_accuracy':None,'actual_five_year_winner':None})
print('R152_QUALIFICATION=PASS inherited=377 new='+str(len(checks))+
      ' documented_total='+str(377+len(checks))+' online_actions=0 gameplay=STOP')
