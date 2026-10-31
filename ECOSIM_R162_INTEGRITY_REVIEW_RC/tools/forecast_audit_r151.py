#!/usr/bin/env python3
"""Offline frozen-forecast vs subsequently observed FACT audit.

Never treats PLAN as realized, never equates partial project proxies with full
EcoSim score. All evidence is user-supplied, never independent server attestation.
No browser, network, account, or game calls.
"""
from __future__ import annotations
from json_integrity_r162 import read_json
import argparse, json, math, hashlib, statistics
from datetime import datetime
from pathlib import Path
from city_bridge import computed_index_from_factors
from r142_proxy_reference import COEFF, WEIGHTS

SCHEMA='ECOSIM_R151_FORECAST_AUDIT_V1'
KIND={'PLAN','FACT'}


def fail(reason):
    raise ValueError(reason)


def number(value):
    return type(value) in (int,float) and math.isfinite(value)


def timestamp(text):
    if not isinstance(text,str) or not text.strip():fail('Missing timestamp')
    try:
        v=datetime.fromisoformat(text.replace('Z','+00:00'))
    except ValueError as ex:raise ValueError('Invalid ISO timestamp: '+text) from ex
    if v.tzinfo is None or v.utcoffset() is None:fail('Timezone is mandatory')
    return v


def require_string(value,field):
    if not isinstance(value,str) or not value.strip():fail('Missing '+field)
    return value


def observed(row,kind,weights,header,side):
    if not isinstance(row,dict) or row.get('kind')!=kind:fail(side+' must be '+kind)
    if kind=='FACT' and row.get('finalized_period_confirmed_by_operator') is not True:
        fail('FACT must be explicitly marked as finalized by the operator')
    if row.get('team')!=header['team'] or row.get('market')!=header['market'] or row.get('period')!=header['period'] or row.get('round')!=header['round']:
        fail('Observed team/market/period/round mismatch in '+side)
    require_string(row.get('source_evidence_id'),side+'.source_evidence_id')
    time=timestamp(row.get('captured_at'))
    vals=row.get('factors')
    if not isinstance(vals,dict) or set(vals)!=set(COEFF):fail('Exactly 29 factor keys required for '+side)
    if any(not number(x) for x in vals.values()):fail('Nonfinite factor in '+side)
    display=row.get('displayed_index')
    if not number(display):fail('Missing numeric displayed index')
    calculation=computed_index_from_factors(vals,weights)['total_index_from_displayed_factors']
    diff=calculation-display
    if abs(diff)>0.04:fail('Official display and factor aggregation mismatch in '+side)
    return time,round(diff,9),round(calculation,9)


def audit(document):
    if not isinstance(document,dict) or document.get('schema')!=SCHEMA:fail('Wrong R151 schema')
    rows=document.get('comparisons')
    if not isinstance(rows,list) or len(rows)>100:fail('comparisons must be a list of at most 100')
    seen=set(); result=[]
    for p in rows:
        if not isinstance(p,dict):fail('Comparison object required')
        pid=require_string(p.get('id'),'comparison id')
        if pid in seen:fail('Duplicate pair id')
        seen.add(pid)
        cls=p.get('source_class')
        if cls not in ('OPERATOR_DECLARED_OFFICIAL_READONLY','SYNTHETIC_TEST_ONLY'):fail('Source class must be explicit')
        head={k:p.get(k) for k in ('team','market','round','period')}
        for k in ('team','market','round'):require_string(head[k],k)
        if type(head['period']) is not int or not 1<=head['period']<=5:fail('Period 1..5 required')
        weights=p.get('weights')
        if not isinstance(weights,dict) or set(weights)!=set(WEIGHTS):fail('Six explicit market index weights required')
        if any(not number(w) or w<0 for w in weights.values()) or abs(sum(weights.values())-1)>1e-8:fail('Invalid weights')
        first=p.get('before_plan'); last=p.get('after_fact')
        t0,d0,calc0=observed(first,'PLAN',weights,head,'before_plan')
        t1,d1,calc1=observed(last,'FACT',weights,head,'after_fact')
        if not t0<t1:fail('FACT must be later than PLAN')
        if first['source_evidence_id']==last['source_evidence_id']:fail('Independent PLAN/FACT source IDs required')
        forecast=p.get('frozen_prediction')
        if not isinstance(forecast,dict):fail('Frozen prediction record required')
        frozen_time=timestamp(forecast.get('created_at'))
        if frozen_time>t0:fail('Prediction must be frozen before or at PLAN observation')
        require_string(forecast.get('model_version'),'model_version')
        digest=require_string(forecast.get('model_input_sha256'),'model_input_sha256')
        if len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest.lower()):fail('SHA-256 digest required')
        scope=forecast.get('scope')
        if scope not in ('FULL_CITY_INDEX','PARTIAL_PROJECT_PROXY'):fail('Forecast scope required')
        prediction=forecast.get('predicted_terminal_index')
        if scope=='FULL_CITY_INDEX' and not number(prediction):fail('Full-city prediction requires numeric frozen score')
        if scope=='PARTIAL_PROJECT_PROXY' and prediction is not None:fail('Partial proxy must not masquerade as full city index')
        if cls=='SYNTHETIC_TEST_ONLY' and p.get('evidence_reviewed_by') is not None:fail('Synthetic data cannot claim evidence review')
        review=p.get('evidence_reviewed_by')
        if review is not None:require_string(review,'evidence_reviewed_by')
        actual=last['displayed_index']; planned=first['displayed_index']
        model_error=(round(prediction-actual,9) if scope=='FULL_CITY_INDEX' else None)
        result.append({'id':pid,'source_class':cls,'model_version':forecast['model_version'],
                       'period':head['period'],'team':head['team'],'market':head['market'],'round':head['round'],
                       'plan_index':planned,'realized_fact_index':actual,
                       'plan_minus_fact_error':round(planned-actual,9),
                       'model_full_index_prediction':prediction if scope=='FULL_CITY_INDEX' else None,
                       'model_minus_fact_error':model_error,
                       'model_scope':scope,'reconstruction_plan_minus_display':d0,
                       'reconstruction_fact_minus_display':d1,
                       'forecast_was_frozen_before_observation':True,
                       'evidence_reviewed_by_operator':bool(review),
                       'fact_finalization_operator_declared_not_verified':True,
                       'independent_server_source_authenticated':False,
                       'not_a_controlled_causal_effect':True})
    official=[r for r in result if r['source_class']=='OPERATOR_DECLARED_OFFICIAL_READONLY']
    full=[r for r in official if r['model_minus_fact_error'] is not None]
    # These are operator-declared paired figures, not externally authenticated
    # evaluations and never out-of-sample performance claims.
    mae=(sum(abs(r['model_minus_fact_error']) for r in full)/len(full) if full else None)
    plan_mae=(sum(abs(r['plan_minus_fact_error']) for r in official)/len(official) if official else None)
    return {'schema':'ECOSIM_R151_FORECAST_AUDIT_REPORT_V1','comparison_count':len(rows),
            'operator_declared_official_pair_count':len(official),
            'synthetic_pair_count':len(rows)-len(official),
            'paired_full_model_prediction_count':len(full),
            'operator_declared_plan_vs_fact_mae':round(plan_mae,8) if plan_mae is not None else None,
            'operator_declared_frozen_full_model_vs_fact_mae':round(mae,8) if mae is not None else None,
            'independently_validated_accuracy':None,
            'out_of_sample_accuracy':None,
            'game_win_probability':None,
            'reliability_status':('NO_REAL_PLAN_FACT_PAIRS' if not official else
                                  'OPERATOR_PROVIDED_NOT_INDEPENDENTLY_AUTHENTICATED'),
            'not_annual_state_transition_identification':True,
            'source_verified_independently':False,
            'gameplay_gate':'STOP','game_writes':0,'pairs':result}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',required=True);ap.add_argument('--out',required=True)
    args=ap.parse_args();doc=read_json(args.input)
    result=audit(doc);path=Path(args.out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print('R151_PAIRS='+str(result['operator_declared_official_pair_count'])+'; actual_accuracy=UNKNOWN; gameplay=STOP')

if __name__=='__main__':main()
