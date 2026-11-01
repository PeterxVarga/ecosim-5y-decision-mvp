#!/usr/bin/env python3
"""R191 safe offline admission for R156 CURRENT_READONLY bundles and year-one finance.

Evidence may be operator declared, NEVER authenticated to the EcoSim server here.
Read-only only. Reject historical/live cross-over, stale/contradictory source records.
"""
from __future__ import annotations
import csv
import hashlib
import math
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

class AdmissionHold(ValueError):
    pass

EXTRA_FUTURE_BUDGET_STATUS='SCENARIOS_ONLY_UNVERIFIED'


def _need(v,name):
    if not isinstance(v,str) or not v.strip() or len(v)>512:
        raise AdmissionHold('MISSING_OR_BAD_'+name)
    return v.strip()


def _number(v,name):
    if type(v) not in (int,float) or not math.isfinite(v) or v<0:
        raise AdmissionHold('INVALID_'+name)
    return float(v)


def _ids(v,name):
    if not isinstance(v,list) or len(v)!=len(set(map(str,v))) or any(type(i) is not int or i<1 or i>35 for i in v):
        raise AdmissionHold('INVALID_'+name)
    return sorted(v)


def _date(text):
    try:
        dt=datetime.fromisoformat(text.replace('Z','+00:00'))
    except (ValueError,AttributeError):
        raise AdmissionHold('BAD_CAPTURE_TIMESTAMP') from None
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise AdmissionHold('CAPTURE_TIMESTAMP_MUST_HAVE_TIMEZONE')
    return dt


def _same_period(a,b):
    return str(a).strip()==str(b).strip() or str(a).strip()==str(b).strip()+'/5'


def _read_csv(p,fieldnames):
    with p.open(encoding='utf-8-sig',newline='') as h:
        reader=csv.DictReader(h)
        if reader.fieldnames!=fieldnames:raise AdmissionHold('CSV_SCHEMA_MISMATCH_'+p.name)
        result=list(reader)
    if any(None in row for row in result):raise AdmissionHold('CSV_UNKNOWN_COLUMNS_'+p.name)
    return result


def validate_state(state,*,mode,now=None):
    if mode not in ('historical','current'):
        raise AdmissionHold('EXPLICIT_MODE_REQUIRED')
    if not isinstance(state,dict):raise AdmissionHold('STATE_MUST_BE_OBJECT')
    p=state.get('provenance') or {};t=state.get('team') or {};m=state.get('market') or {}
    if not all(isinstance(x,dict) for x in (p,t,m)):
        raise AdmissionHold('INVALID_STATE_SECTIONS')
    label=' '.join(str(p.get(k,'') or '') for k in ('source','round','source_evidence_id'))
    historical=bool(re.search(r'(?i)(historical|test.round|tesztfordul|r141_test|r94_test)',label))
    if mode=='current' and historical:raise AdmissionHold('HISTORICAL_OR_TEST_SOURCE_AS_CURRENT')
    if mode=='historical' and not historical:raise AdmissionHold('HISTORICAL_TAG_REQUIRED')
    for k in ('source','team','market','round','source_evidence_id'):_need(p.get(k),k.upper())
    when=_date(p.get('captured_at_local'))
    period=p.get('current_period')
    if type(period) is not int or not 1<=period<=5:raise AdmissionHold('INVALID_CURRENT_PERIOD')
    if mode=='current':
        now=now or datetime.now(ZoneInfo('Europe/Budapest'))
        if now.tzinfo is None:raise AdmissionHold('CLOCK_MISSING_TIMEZONE')
        age=now.astimezone(timezone.utc)-when.astimezone(timezone.utc)
        if not -timedelta(minutes=5)<=age<=timedelta(hours=48):raise AdmissionHold('CURRENT_SOURCE_STALE_OR_FUTURE')
    active=_ids(t.get('initially_active_project_ids'),'ACTIVE_IDS')
    fixed=_ids(t.get('already_selected_new_project_ids_current_period'),'CURRENT_SELECTIONS')
    if set(active)&set(fixed):raise AdmissionHold('ACTIVE_AND_NEW_OVERLAP')
    prior=t.get('project1_active_previous_period')
    if type(prior) is not bool:raise AdmissionHold('PRIOR_PROJECT1_UNKNOWN')
    cap=m.get('maxProjectPerTurn')
    if type(cap) is not int or not 0<=cap<=20:raise AdmissionHold('CAP_UNKNOWN_OR_ASSUMED')
    if len(fixed)>cap+int(prior):raise AdmissionHold('SELECTED_EXCEEDS_DECLARED_CAP')
    factors=t.get('baseline_smartcity_factors')
    if not isinstance(factors,dict) or len(factors)!=29 or any(type(v) not in (int,float) or not math.isfinite(v) for v in factors.values()):
        raise AdmissionHold('ALL_29_DIRECT_FACTORS_REQUIRED')
    if mode=='current':
        weights=m.get('smartcity_total_weights')
        if not isinstance(weights,dict) or len(weights)!=6 or any(type(v) not in (int,float) or not math.isfinite(v) or v<0 for v in weights.values()) or abs(sum(weights.values())-1)>1e-9:
            raise AdmissionHold('CURRENT_SIX_INDEX_WEIGHTS_REQUIRED')
        if not _need(m.get('cap_source'),'CAP_SOURCE') or re.search(r'(?i)(assum|hypothet|spoken|test)',m['cap_source']):
            raise AdmissionHold('UNVERIFIED_CAP_SOURCE')
    return {'mode':mode,'current_period':period,'cap':cap,'active':active,'fixed':fixed,
            'capture_timestamp':when.isoformat(),'official_server_attested':False,'gameplay_gate':'STOP'}


def validate_r156_bundle(state,bundle,*,now=None):
    """Verify SHA-linked R156 export without converting it into server truth."""
    original=Path(bundle)
    if original.is_symlink():raise AdmissionHold('R156_SYMLINK_BUNDLE_FORBIDDEN')
    base=original.resolve()
    if not base.is_dir() or base.is_symlink():raise AdmissionHold('R156_BUNDLE_DIRECTORY_REQUIRED')
    # Caller supplies already strict-parsed JSON (R162 json_integrity_r162.read_json).
    from json_integrity_r162 import read_json
    r=read_json(base/'R156_ACQUISITION_RECEIPT.json');manifest=read_json(base/'manifest.json');params=read_json(base/'parameters.json')
    if r.get('schema')!='ECOSIM_R156_ACQUISITION_RECEIPT_V1' or r.get('capture_mode')!='CURRENT_READONLY':
        raise AdmissionHold('R156_CURRENT_RECEIPT_REQUIRED')
    if manifest.get('capture_mode')!='CURRENT_READONLY' or manifest.get('kind')!='PLAN':
        raise AdmissionHold('R156_CURRENT_PLAN_REQUIRED')
    if r.get('provided_by')!='OPERATOR_EXPORT_NOT_INDEPENDENTLY_SERVER_VERIFIED':raise AdmissionHold('R156_PROVENANCE_UNRECOGNIZED')
    if r.get('gameplay_gate')!='STOP':raise AdmissionHold('R156_GAME_ACTION_GATE_INVALID')
    if not r.get('market_cap_observed') or not r.get('market_index_weights_observed'):
        raise AdmissionHold('CURRENT_CAP_OR_WEIGHTS_MISSING')
    sources=r.get('sources') or {}
    for k in ('factors','projects','market_project_cap','market_index_weights'):_need(sources.get(k),'R156_'+k.upper()+'_SOURCE')
    for key in ('team','market','round','source_evidence_id'):
        if str(manifest.get(key,'')).strip()!=str(state['provenance'].get(key,'')).strip():raise AdmissionHold('R156_STATE_PROVENANCE_MISMATCH_'+key)
    if not _same_period(state['provenance']['current_period'],manifest.get('period')):
        raise AdmissionHold('R156_PERIOD_MISMATCH')
    if _date(manifest.get('captured_at_local'))!=_date(state['provenance']['captured_at_local']):
        raise AdmissionHold('R156_TIMESTAMP_MISMATCH')
    hashes=r.get('file_sha256') or {}
    for fname in ('manifest.json','factors.csv','projects.csv','parameters.json'):
        fp=base/fname
        if not fp.is_file() or fp.is_symlink():raise AdmissionHold('MISSING_OR_SYMLINK_R156_FILE_'+fname)
        if hashlib.sha256(fp.read_bytes()).hexdigest()!=hashes.get(fname):raise AdmissionHold('R156_SHA256_MISMATCH_'+fname)
    fm={}
    for row in _read_csv(base/'factors.csv',['metric','value']):
        label=row['metric']
        if label in fm:raise AdmissionHold('DUPLICATE_FACTOR')
        try:fm[label]=float(row['value'])
        except ValueError:raise AdmissionHold('INVALID_FACTOR_VALUE') from None
    observed=state['team']['baseline_smartcity_factors']
    if len(fm)!=len(observed)+1 or set(observed)-set(fm):raise AdmissionHold('R156_FACTOR_IDENTITY_MISMATCH')
    for label,value in observed.items():
        if not math.isfinite(fm[label]) or abs(fm[label]-value)>1e-7:raise AdmissionHold('R156_FACTOR_VALUE_MISMATCH')
    project_rows=_read_csv(base/'projects.csv',['project_id','previous_running','selected_new'])
    if len(project_rows)!=35:raise AdmissionHold('R156_PROJECT_COUNT')
    prev=[];selected=[];ids=[]
    for row in project_rows:
        try:pid=int(row['project_id'])
        except ValueError:raise AdmissionHold('R156_PROJECT_ID') from None
        if str(pid)!=row['project_id'] or not 1<=pid<=35:raise AdmissionHold('R156_PROJECT_ID')
        ids.append(pid)
        if row['previous_running']=='true':prev.append(pid)
        elif row['previous_running']!='false':raise AdmissionHold('R156_PROJECT_STATUS')
        if row['selected_new']=='true':selected.append(pid)
        elif row['selected_new']!='false':raise AdmissionHold('R156_PROJECT_STATUS')
    if len(set(ids))!=35:raise AdmissionHold('R156_PROJECT_ID_SET')
    if sorted(prev)!=sorted(state['team']['initially_active_project_ids']) or sorted(selected)!=sorted(state['team']['already_selected_new_project_ids_current_period']):
        raise AdmissionHold('R156_PROJECT_STATE_MISMATCH')
    market=params.get('market') or {};team=params.get('team') or {}
    for field in ('maxProjectPerTurn','smartcity_total_weights'):
        if market.get(field)!=state['market'].get(field):raise AdmissionHold('R156_MARKET_PARAM_MISMATCH_'+field)
    if team.get('project1_active_previous_period')!=state['team'].get('project1_active_previous_period'):
        raise AdmissionHold('R156_PRIOR_PROJECT1_MISMATCH')
    return {'schema':'ECOSIM_R191_LIVE_CAPTURE_ADMISSION_V1',
            'status':'PASS_OPERATOR_CAPTURE_CONSISTENCY_ONLY',
            'r156_receipt_sha256':hashlib.sha256((base/'R156_ACQUISITION_RECEIPT.json').read_bytes()).hexdigest(),
            'bundle_source_evidence_id':manifest['source_evidence_id'],
            'capture_age_hours':round(((now or datetime.now(ZoneInfo('Europe/Budapest'))).astimezone(timezone.utc)-_date(manifest['captured_at_local']).astimezone(timezone.utc)).total_seconds()/3600,3),
            'finance': 'HOLD_UNTIL_SEPARATE_SAME_PERIOD_YEAR1_FINANCE_EVIDENCE',
            'current_source_is_server_authenticated':False,'gameplay_gate':'STOP'}


def year1_finance(finance, state, *,illustrative_first_year_budget):
    if not isinstance(finance,dict):raise AdmissionHold('CURRENT_YEAR1_FINANCE_EVIDENCE_REQUIRED')
    if finance.get('mode')!='CURRENT_YEAR1_OPERATOR_READONLY':raise AdmissionHold('CURRENT_YEAR1_FINANCE_MODE_REQUIRED')
    for k in ('source_evidence_id','captured_at_local'):_need(finance.get(k),'FINANCE_'+k.upper())
    if abs((_date(finance['captured_at_local'])-_date(state['provenance']['captured_at_local'])).total_seconds())>3600:
        raise AdmissionHold('FINANCE_CAPTURE_TIME_DIFFERENCE_EXCEEDS_ONE_HOUR')
    if finance.get('period')!=state['provenance']['current_period']:
        raise AdmissionHold('FINANCE_PERIOD_MISMATCH')
    spendable=_number(finance.get('operator_observed_spendable_ecu'),'SPENDABLE_CURRENT_ECU')
    committed=_number(finance.get('operator_observed_committed_ecu'),'COMMITTED_CURRENT_ECU')
    budget=_number(illustrative_first_year_budget,'FIRST_YEAR_SCENARIO_BUDGET')
    if committed>spendable:raise AdmissionHold('FINANCE_COMMITMENTS_EXCEED_OBSERVED_SPENDABLE')
    if budget>spendable-committed+1e-7:raise AdmissionHold('SCENARIO_FIRST_YEAR_EXCEEDS_OBSERVED_RESIDUAL')
    return {'schema':'ECOSIM_R191_YEAR1_FINANCE_V1',
            'status':'PASS_OPERATOR_DECLARED_YEAR1_ENVELOPE_ONLY',
            'current_year_budget_ceiling_ecu':round(spendable-committed,4),
            'tested_first_year_scenario_ecu':budget,'future_years':'SCENARIOS_ONLY_UNVERIFIED',
            'actual_server_financing_approved':False,'gameplay_gate':'STOP'}
