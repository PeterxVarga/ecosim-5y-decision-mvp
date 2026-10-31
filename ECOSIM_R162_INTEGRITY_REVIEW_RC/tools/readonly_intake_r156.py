#!/usr/bin/env python3
"""R156: local, operator-authorized copy of displayed EcoSim data -> existing R152/R155 pipeline.

Never accesses EcoSim, does not fetch URLs, does not use network, browser,
credentials, saved sessions, HAR or undocumented server endpoints.
All inputs are user-declared snapshots; no independent server verification.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, math, os, re, shutil, sys, tempfile
from pathlib import Path
from datetime import datetime
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))
from observation_bundle_r152 import compile_bundle, INDEX_LABEL, _iso
from r142_proxy_reference import COEFF, WEIGHTS
from portfolio_5y import project_index
from strategy_5y import write_json,read_json
from readiness_r148 import check_state

SCHEMA='ECOSIM_R156_LOCAL_OPERATOR_EXPORT_V1'
BUNDLE_SCHEMA='ECOSIM_R152_LOCAL_OBSERVATION_BUNDLE_V1'
CSV_MAX=200_000
FORBIDDEN_PATTERNS=[
    re.compile(r'(?i)\b(?:bearer\s+|authorization\s*[:=]|cookie\s*[:=]|set-cookie\s*[:=]|access_token\s*[:=]|refresh_token\s*[:=]|password\s*[:=]|sessionid\s*[:=])'),
    re.compile(r'\beyJ[A-Za-z0-9_\-]{18,}\.eyJ[A-Za-z0-9_\-]{18,}\.[A-Za-z0-9_\-]+\b'),
]

class IntakeError(ValueError):pass

def _reject_secrets(obj):
    serialized=json.dumps(obj,ensure_ascii=False)
    if len(serialized.encode('utf-8'))>350_000:raise IntakeError('Oversized capture; only whitelisted displayed data allowed')
    for p in FORBIDDEN_PATTERNS:
        if p.search(serialized):raise IntakeError('Potential sensitive credential/session material: REFUSED')

def _expected_keys(obj, allowed, name):
    if not isinstance(obj,dict) or set(obj)-set(allowed):
        raise IntakeError('Unsupported '+name+' object/keys: '+repr(sorted(set(obj)-set(allowed)) if isinstance(obj,dict) else type(obj).__name__))

def _csv_from_string(text,headers,name):
    if not isinstance(text,str) or not 0<len(text.encode('utf-8'))<=CSV_MAX:raise IntakeError(name+' CSV missing/too large')
    if '\x00' in text:raise IntakeError('NUL byte forbidden')
    reader=csv.DictReader(io.StringIO(text.lstrip('\ufeff'),newline=''))
    if reader.fieldnames is None or set(reader.fieldnames)!=set(headers):
        raise IntakeError(name+' CSV columns must equal '+','.join(headers))
    rows=list(reader)
    if any(None in r or None in r.values() for r in rows):raise IntakeError(name+' malformed row')
    return rows

def _as_csv(rows,columns):
    io_obj=io.StringIO(newline='');w=csv.DictWriter(io_obj,fieldnames=columns,lineterminator='\n')
    w.writeheader();w.writerows(rows)
    return io_obj.getvalue()

def validate_export(packet):
    _reject_secrets(packet)
    _expected_keys(packet,['schema','capture_mode','kind','team','market','round','period','captured_at_local','source_evidence_id','source_note','factors_csv','projects_csv','parameters','field_sources'], 'R156 packet')
    if packet.get('schema')!=SCHEMA:raise IntakeError('Unrecognized export schema')
    mode=packet.get('capture_mode')
    if mode not in ('HISTORICAL_REFERENCE','CURRENT_READONLY'):raise IntakeError('Capture mode must be HISTORICAL_REFERENCE or CURRENT_READONLY')
    if packet.get('kind') not in ('PLAN','FACT'):raise IntakeError('Column kind must be PLAN or FACT')
    period=packet.get('period')
    if type(period) is not int or not 1<=period<=5:raise IntakeError('Period outside 1..5')
    for key in ('team','market','round','captured_at_local','source_evidence_id'):
        v=packet.get(key)
        if not isinstance(v,str) or not v.strip() or len(v)>256:raise IntakeError('Invalid provenance '+key)
        if mode=='CURRENT_READONLY' and re.match(r'(?i)^(replace|todo|example|unknown|fill_from)',v):
            raise IntakeError('Current provenance placeholder forbidden: '+key)
    if mode=='CURRENT_READONLY':_iso(packet['captured_at_local'])
    else:
        try:datetime.fromisoformat(packet['captured_at_local'].replace('Z','+00:00'))
        except ValueError as e:raise IntakeError('Invalid historical date') from e
    note=packet.get('source_note','')
    if not isinstance(note,str) or len(note)>1024:raise IntakeError('Source note invalid')
    sources=packet.get('field_sources',{})
    _expected_keys(sources,['factors','projects','market_project_cap','market_index_weights','finance','other'],'field_sources')
    for k,v in sources.items():
        if not isinstance(v,str) or not 0<len(v)<=256:raise IntakeError('Invalid field source '+k)
    if mode=='CURRENT_READONLY' and (not sources.get('factors') or not sources.get('projects')):
        raise IntakeError('Current capture must identify factor and project data sources')
    fr=_csv_from_string(packet.get('factors_csv'),['metric','value'],'factors')
    pr=_csv_from_string(packet.get('projects_csv'),['project_id','previous_running','selected_new'],'projects')
    if len(fr)!=len(COEFF)+1:raise IntakeError('Exactly 29 SmartCity factors and displayed index required')
    if len(pr)!=len(project_index()):raise IntakeError('Exactly 35 project status rows required')
    fm={}
    for row in fr:
        k=row['metric']
        if k in fm or k not in set(COEFF)|{INDEX_LABEL}:raise IntakeError('Duplicate/unknown factor '+str(k))
        try:x=float(row['value'])
        except (ValueError,TypeError):raise IntakeError('Non-numeric factor '+str(k))
        if not math.isfinite(x):raise IntakeError('Nonfinite factor')
        fm[k]=x
    if set(fm)!=set(COEFF)|{INDEX_LABEL}:raise IntakeError('Missing required factor')
    seen=set()
    for r in pr:
        try:id_=int(r['project_id'])
        except ValueError:raise IntakeError('Noninteger project ID')
        if str(id_)!=r['project_id'] or id_ not in project_index() or id_ in seen:
            raise IntakeError('Unknown or duplicate project ID')
        seen.add(id_)
        if r['previous_running'] not in ('true','false') or r['selected_new'] not in ('true','false'):
            raise IntakeError('Invalid project booleans')
        if r['previous_running']=='true' and r['selected_new']=='true':raise IntakeError('Overlapping project flags')
    params=packet.get('parameters',{})
    _expected_keys(params,['market','team'],'parameters')
    market=params.get('market',{})
    team=params.get('team',{})
    from intake_r149 import normalize_capture
    template=read_json(ROOT/'inputs/official_state.template.json')
    for category,vals in [('market',market),('team',team)]:
        _expected_keys(vals,template[category].keys(),category+' parameters')
    cap=market.get('maxProjectPerTurn')
    if cap is not None and (type(cap) is not int or not 0<=cap<=20):raise IntakeError('Project cap outside 0..20')
    if mode=='CURRENT_READONLY' and cap is not None and not sources.get('market_project_cap'):
        raise IntakeError('Source needed for claimed current market project cap')
    weights=market.get('smartcity_total_weights')
    if weights is not None:
        if not isinstance(weights,dict) or set(weights)!=set(WEIGHTS) or not all(type(v) in (float,int) and math.isfinite(v) and v>=0 for v in weights.values()) or abs(sum(weights.values())-1)>1e-9:
            raise IntakeError('Invalid six market weights')
        if mode=='CURRENT_READONLY' and not sources.get('market_index_weights'):
            raise IntakeError('Source needed for claimed current index weights')
    if mode=='CURRENT_READONLY' and 'confirmed_spendable_cash_ecu_by_year' in team:
        raise IntakeError('Do not claim future funds are confirmed via read-only observation')
    return {'factor_rows':fr,'project_rows':pr,'mode':mode,'market_cap_observed':cap is not None,
            'market_weights_observed':weights is not None,'field_sources':sources}

def create_bundle(packet,destination):
    """Create an R152-compatible packet without ever silently filling missing live fields."""
    meta=validate_export(packet)
    final=Path(destination).resolve()
    if final.exists():raise IntakeError('Destination already exists; immutable evidence packets cannot be overwritten')
    final.parent.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='.r156-staging-',dir=final.parent))
    files={
       'factors.csv':_as_csv(meta['factor_rows'],['metric','value']),
       'projects.csv':_as_csv(meta['project_rows'],['project_id','previous_running','selected_new']),
       'parameters.json':json.dumps(packet.get('parameters',{}),indent=2,ensure_ascii=False)+'\n'
    }
    try:
        for name,content in files.items():
            (stage/name).write_text(content,encoding='utf-8')
        manifest={k:packet[k] for k in ('capture_mode','kind','team','market','round','period','captured_at_local','source_evidence_id')}
        manifest.update(schema=BUNDLE_SCHEMA,factor_table_path='factors.csv',project_states_path='projects.csv',parameters_path='parameters.json')
        write_json(stage/'manifest.json',manifest)
        # Verify through existing R152/R149 validators, no independent duplicate bypass.
        capture,state,receipt=compile_bundle(stage/'manifest.json')
        src={k:hashlib.sha256((stage/k).read_bytes()).hexdigest() for k in ('manifest.json','factors.csv','projects.csv','parameters.json')}
        readout={'schema':'ECOSIM_R156_ACQUISITION_RECEIPT_V1','capture_mode':meta['mode'],
             'provided_by':'OPERATOR_EXPORT_NOT_INDEPENDENTLY_SERVER_VERIFIED',
             'gameplay_gate':'STOP','has_live_ecosim_session':False,
             'sources':meta['field_sources'],'source_note':packet.get('source_note',''),
             'file_sha256':src,'market_cap_observed':meta['market_cap_observed'],
             'market_index_weights_observed':meta['market_weights_observed'],
             'index_reconciliation':receipt['index_reconciliation_status'],
             'index_residual':receipt['rounding_residual'],
             'project_states':receipt['project_states'],
             'readiness':check_state(state),
             'not_a_server_certification':True,
             'not_a_future_index_prediction':True}
        write_json(stage/'R156_ACQUISITION_RECEIPT.json',readout)
        stage.rename(final)
    finally:
        if stage.exists():shutil.rmtree(stage)
    return final,readout

def run(packet_path,dest,config=None):
    path=Path(packet_path)
    if path.stat().st_size>350_000:raise IntakeError('Input file too large')
    packet=read_json(path)
    if config:
        cfg=read_json(config)
        is_current=packet.get('capture_mode')=='CURRENT_READONLY'
        if is_current:
            if cfg.get('mode')!='CURRENT_SNAPSHOT_REVIEW' or cfg.get('project_cap_assumption') is not None:
                raise IntakeError('Current mode requires CURRENT_SNAPSHOT_REVIEW and no assumed project cap')
            if any(cfg.get(k) for k in ('tax_scenarios_path','tax_revenue_scenarios_path','operating_scenarios_path','policy_tracks_path')):
                raise IntakeError('Current mode must not inject stale/synthetic policy, tax or operating scenarios')
            if packet.get('kind')!='PLAN':raise IntakeError('Current decision search needs PLAN; FACT is for validation only')
    dest,receipt=create_bundle(packet,dest)
    output={'packet':str(dest),'receipt':str(dest/'R156_ACQUISITION_RECEIPT.json'),
            'gameplay_gate':'STOP','server_verified':False,'decision_run':None}
    if config:
        from run_evidence_pipeline_r152 import execute
        output['decision_run']=execute(dest/'manifest.json',config,dest/'decision')
    return output

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--export',required=True);p.add_argument('--out-dir',required=True)
    p.add_argument('--decision-config',default=None)
    a=p.parse_args()
    result=run(a.export,a.out_dir,a.decision_config)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
