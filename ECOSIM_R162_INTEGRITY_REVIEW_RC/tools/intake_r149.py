#!/usr/bin/env python3
"""Convert an explicitly classified OFFLINE read-only snapshot to a partial state.

This is *not* a connector, parser of arbitrary web/API data, or independent
verification that a user-authored capture describes the actual current game.
Unknown fields remain null. Never infer live state from a historical export.
"""
from __future__ import annotations
import argparse,copy,hashlib,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))
from city_bridge import computed_index_from_factors
from r142_proxy_reference import COEFF
from strategy_5y import read_json,write_json


def normalize_capture(capture, base_template=None):
    if not isinstance(capture,dict) or capture.get('schema')!='ECOSIM_R149_READONLY_CAPTURE_V1':
        raise ValueError('Not an R149 read-only capture')
    for k in ('team','market','captured_at_local','source_evidence_id'):
        if not isinstance(capture.get(k),str) or not capture[k].strip():
            raise ValueError('Missing provenance '+k)
    if capture.get('capture_mode')=='CURRENT_READONLY':
        for k in ('captured_at_local','source_evidence_id'):
            if capture[k].upper().startswith(('REPLACE','EXAMPLE','TODO')):
                raise ValueError('Placeholder current capture provenance not accepted: '+k)
    year=capture.get('period')
    if type(year) is not int or not 1<=year<=5:raise ValueError('Capture period must be 1..5')
    capture_mode=capture.get('capture_mode')
    if capture_mode not in ('HISTORICAL_REFERENCE','CURRENT_READONLY'):
        raise ValueError('Capture must distinguish historic from current')
    if capture.get('kind') not in ('PLAN','FACT'):
        raise ValueError('PLAN/FACT distinction required')
    factors=capture.get('factors')
    if not isinstance(factors,dict) or set(COEFF)-set(factors):
        raise ValueError('All 29 displayed factors required')
    if any(type(factors.get(k)) not in (int,float) or not math.isfinite(factors[k]) for k in COEFF):
        raise ValueError('All factors must be finite numeric values')
    params=capture.get('parameters') or {}
    if not isinstance(params,dict) or set(params)-{'market','team'}:
        raise ValueError('Parameters allow market and team only')
    market=params.get('market') or {};team=params.get('team') or {}
    if not isinstance(market,dict) or not isinstance(team,dict):raise ValueError('Parameter parts must be objects')
    baseline=copy.deepcopy(base_template) if base_template is not None else read_json(ROOT/'inputs/official_state.template.json')
    # Never accept arbitrary keys (credentials, cookies, tokens, extraneous state).
    for category,provided in [('market',market),('team',team)]:
        allow=set(baseline[category])
        if set(provided)-allow:raise ValueError('Undocumented '+category+' parameter keys: '+repr(sorted(set(provided)-allow)))
        baseline[category].update(provided)
    baseline['team']['baseline_smartcity_factors']={k:factors[k] for k in COEFF}
    baseline['provenance']={
        'source':'USER_SUPPLIED_OFFLINE_READONLY_CAPTURE_NOT_INDEPENDENTLY_VERIFIED',
        'source_evidence_id':capture['source_evidence_id'],
        'captured_at_local':capture['captured_at_local'],
        'team':capture['team'],'market':capture['market'],
        'current_period':year,
        'round':capture.get('round'),
        'capture_mode':capture_mode,
        'observed_column_kind':capture['kind']
    }
    supplied_weights=market.get('smartcity_total_weights')
    if capture_mode=='CURRENT_READONLY' and supplied_weights is None:
        calculated=None
    else:
        calculated=computed_index_from_factors(factors,supplied_weights)['total_index_from_displayed_factors']
    actual=capture.get('displayed_index')
    if type(actual) not in (int,float) or not math.isfinite(actual):
        raise ValueError('displayed_index must be finite')
    residual=round(calculated-actual,8) if calculated is not None else None
    if residual is not None and abs(residual)>0.03:
        raise ValueError('Displayed index inconsistent with factor aggregation; inspect market weights')
    meta={'source_evidence_id':capture['source_evidence_id'],
          'capture_mode':capture_mode,'kind':capture['kind'],
          'recomputed_display_index':round(calculated,6) if calculated is not None else None,
          'index_reconciliation_status':('BLOCKED_MISSING_CURRENT_WEIGHTS' if calculated is None else 'AGREES_WITH_DISPLAYED_FACTORS_NOT_SERVER_VERIFIED'),
          'original_display_index':actual,
          'rounding_residual':residual,
          'live_state_verified_from_capture':False,
          'operator_trust_not_server_verified':True,
          'gameplay_gate':'STOP'}
    return baseline,meta


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--capture',required=True)
    ap.add_argument('--out-state',required=True)
    ap.add_argument('--out-check',required=True)
    a=ap.parse_args()
    captured=read_json(a.capture)
    state,receipt=normalize_capture(captured)
    receipt['source_sha256']=hashlib.sha256(Path(a.capture).read_bytes()).hexdigest()
    write_json(a.out_state,state)
    write_json(a.out_check,receipt)
    print('R149_READONLY_INTAKE=PASS; GAME_WRITE=0; LIVE_VERIFICATION=UNKNOWN; STOP')

if __name__=='__main__':main()
