#!/usr/bin/env python3
"""R152: strictly local, read-only CSV/JSON evidence packet -> R149 capture.

No remote API, no browser, no hidden game mutations.  A packet is an operator-
provided transcription/export, NOT cryptographic proof of an EcoSim server state.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,sys
from pathlib import Path
from datetime import datetime

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))
from intake_r149 import normalize_capture
from r142_proxy_reference import COEFF,WEIGHTS
from strategy_5y import read_json,write_json
from portfolio_5y import project_index
from reconcile_r94 import reconcile_file

SCHEMA='ECOSIM_R152_LOCAL_OBSERVATION_BUNDLE_V1'
PLACEHOLDERS=('REPLACE','EXAMPLE','TODO','UNKNOWN')
INDEX_LABEL='Okosváros index'

def _iso(value):
    try: d=datetime.fromisoformat(value.replace('Z','+00:00'))
    except (AttributeError,ValueError) as ex:raise ValueError('Timestamp is not ISO 8601: '+str(value)) from ex
    if d.tzinfo is None or d.utcoffset() is None:raise ValueError('Timestamp must include timezone offset')
    return d

def _local_file(manifest_path,rel):
    if not isinstance(rel,str) or not rel or '://' in rel or rel.startswith('~'):raise ValueError('Local file path required')
    origin=manifest_path.resolve().parent
    if '..' in Path(rel).parts:raise ValueError('Parent traversal forbidden')
    try:path=(origin/rel).resolve(strict=True)
    except (FileNotFoundError,OSError) as ex:raise ValueError('Missing local evidence file') from ex
    if not path.is_relative_to(origin):raise ValueError('File must be inside local evidence packet')
    # Avoid escaping through symlinked directories and unexpected external targets.
    test=origin
    for piece in Path(rel).parts:
        if piece in ('.',''):continue
        if piece=='..':raise ValueError('Parent traversal forbidden')
        test=test/piece
        if test.is_symlink():raise ValueError('Symlinks forbidden')
    if not path.is_file() or not 0<path.stat().st_size<=4_000_000:raise ValueError('Invalid or oversized file')
    return path

def _sha(path):
    return {'filename':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}

def _csv(path,required):
    with path.open('r',encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if reader.fieldnames is None or set(reader.fieldnames)!=set(required):
            raise ValueError(f'Unexpected CSV columns in {path.name}; expected {required}')
        rows=list(reader)
    if not rows:raise ValueError('Empty CSV '+path.name)
    return rows

def _number(x):
    try:v=float(x)
    except (TypeError,ValueError):raise ValueError('Expected finite numeric value: '+repr(x))
    if not math.isfinite(v):raise ValueError('Nonfinite numeric value')
    return v

def _bool(s):
    if s=='true':return True
    if s=='false':return False
    raise ValueError('Boolean field must be exactly true or false')

def _project_states(path):
    rows=_csv(path,['project_id','previous_running','selected_new'])
    idx=project_index(); seen={};active=[];selected=[]
    for r in rows:
        try:i=int(r['project_id'])
        except (TypeError,ValueError):raise ValueError('project_id not integer')
        if str(i)!=r['project_id'] or i not in idx or i in seen:raise ValueError('Invalid/duplicate project ID')
        old=_bool(r['previous_running']);new=_bool(r['selected_new'])
        if old and new:raise ValueError('Running and newly selected overlap; repeatable flags require separate model')
        if old:active.append(i)
        if new:selected.append(i)
        seen[i]=True
    if set(seen)!=set(idx):raise ValueError('All 35 project IDs required, with explicit true/false states')
    return {'initially_active_project_ids':sorted(active),
            'already_selected_new_project_ids_current_period':sorted(selected),
            'project1_active_previous_period':1 in active}, {'rows':len(rows),'prior_running':len(active),'new_selected':len(selected),
                                                             'previous_project1':1 in active,
                                                             'is_operator_transcription_not_server_verified':True}

def compile_bundle(manifest_path):
    manifest_path=Path(manifest_path).resolve(strict=True)
    if not manifest_path.is_file():raise ValueError('Manifest not a file')
    m=read_json(manifest_path)
    if not isinstance(m,dict) or m.get('schema')!=SCHEMA:raise ValueError('R152 manifest schema required')
    allowed={'schema','capture_mode','kind','team','market','round','period','captured_at_local',
             'source_evidence_id','factor_table_path','project_states_path','parameters_path','finance_r94_path'}
    if set(m)-allowed:raise ValueError('Undocumented manifest keys')
    mode=m.get('capture_mode');kind=m.get('kind');period=m.get('period')
    if mode not in ('HISTORICAL_REFERENCE','CURRENT_READONLY') or kind not in ('PLAN','FACT'):
        raise ValueError('Explicit capture mode and PLAN/FACT required')
    if type(period) is not int or not 1<=period<=5:raise ValueError('Period must be integer 1..5')
    for k in ('team','market','round','captured_at_local','source_evidence_id'):
        if not isinstance(m.get(k),str) or not m[k].strip():raise ValueError('Required provenance: '+k)
    if mode=='CURRENT_READONLY':
        _iso(m['captured_at_local'])
        if any(m[k].upper().startswith(PLACEHOLDERS) for k in ('round','source_evidence_id')):
            raise ValueError('Placeholder provenance forbidden in current mode')
    else:
        # Historical observations may have a date-only capture.
        datetime.fromisoformat(m['captured_at_local'].replace('Z','+00:00'))
    table=_local_file(manifest_path,m.get('factor_table_path'))
    rows=_csv(table,['metric','value']);factors={};index=None
    for row in rows:
        k=row['metric']
        if k in factors or (k==INDEX_LABEL and index is not None):raise ValueError('Duplicate index/factor '+k)
        if k!=INDEX_LABEL and k not in COEFF:raise ValueError('Unrecognized factor '+k)
        v=_number(row['value'])
        if k==INDEX_LABEL:index=v
        else:factors[k]=v
    if set(factors)!=set(COEFF) or index is None:raise ValueError('Exactly 29 factors and displayed total required')
    evidence={'manifest':_sha(manifest_path),'factors':_sha(table)}
    parameters={'market':{},'team':{}}
    if m.get('parameters_path'):
        p=_local_file(manifest_path,m['parameters_path']);params=read_json(p)
        if not isinstance(params,dict) or set(params)-{'market','team'}:raise ValueError('Parameters must contain market/team only')
        for group in ('market','team'):
            val=params.get(group,{})
            if not isinstance(val,dict):raise ValueError('Non-object parameter group')
            parameters[group]=val
        evidence['parameters']=_sha(p)
    status=None
    if m.get('project_states_path'):
        p=_local_file(manifest_path,m['project_states_path'])
        states,status=_project_states(p)
        for k,v in states.items():
            if k in parameters['team'] and parameters['team'][k]!=v:
                raise ValueError('Contradictory team/project status '+k)
            parameters['team'][k]=v
        evidence['project_status']=_sha(p)
    finance=None
    if m.get('finance_r94_path'):
        if mode!='HISTORICAL_REFERENCE' or period!=1 or m['market']!='Z' or m['team']!='Jutalom a nap végén':
            raise ValueError('R94 historical finance is only valid for the original historical market/team/period')
        p=_local_file(manifest_path,m['finance_r94_path'])
        if _sha(p)['sha256'] != _sha(ROOT/'data/finance_R94_test_snapshot.csv')['sha256']:
            raise ValueError('Historical R94 finance must match the retained exact reference file')
        finance=reconcile_file(p)
        if finance['provenance']['source_rows']!=113:
            raise ValueError('Unexpected historical finance row count')
        evidence['finance_R94']=_sha(p)
    capture={'schema':'ECOSIM_R149_READONLY_CAPTURE_V1','capture_mode':mode,'kind':kind,
             'team':m['team'],'market':m['market'],'period':period,'round':m['round'],
             'captured_at_local':m['captured_at_local'],'source_evidence_id':m['source_evidence_id'],
             'factors':factors,'displayed_index':index,'parameters':parameters}
    state,receipt=normalize_capture(capture)
    receipt['bundle_schema']=SCHEMA
    receipt['evidence_files']=evidence
    receipt['finance_R94_reconciliation']={
       'status':'HISTORICAL_ACCOUNTING_RECONCILED_NOT_SPENDABLE_BUDGET',
       'p1_observed_net_ecu':finance['p1_observed_net_ecu'],
       'all_checks_pass':finance['all_checks_pass'],
       'checks':finance['checks']} if finance else None
    receipt['project_states']=status
    receipt['input_classification']='HISTORICAL_TEST_ROUND_NOT_CURRENT' if mode=='HISTORICAL_REFERENCE' else 'OPERATOR_DECLARED_CURRENT_NOT_INDEPENDENTLY_VERIFIED'
    receipt['realized_transition_pair_count']=0
    receipt['authoritative_server_state_verified']=False
    receipt['gameplay_gate']='STOP'
    return capture,state,receipt

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bundle',required=True);p.add_argument('--out-dir',required=True)
    a=p.parse_args();capture,state,receipt=compile_bundle(a.bundle)
    target=Path(a.out_dir);target.mkdir(parents=True,exist_ok=True)
    write_json(target/'NORMALIZED_CAPTURE.json',capture)
    write_json(target/'NORMALIZED_STATE.json',state)
    write_json(target/'EVIDENCE_RECEIPT.json',receipt)
    print('R152_BUNDLE=PASS; mode='+capture['capture_mode']+'; live_server_verified=FALSE; gameplay=STOP')

if __name__=='__main__':main()
