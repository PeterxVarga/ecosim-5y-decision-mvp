#!/usr/bin/env python3
"""R146 passive-only index reconciliation; NEVER infers causal decisions from UI pairs."""
from __future__ import annotations
from json_integrity_r162 import read_json
import argparse
import json
from pathlib import Path
from city_bridge import computed_index_from_factors
from r142_proxy_reference import COEFF

ROOT = Path(__file__).resolve().parent.parent

def reconcile_snapshots(data):
    if not isinstance(data,dict) or data.get('schema')!='ECOSIM_R146_PASSIVE_INDEX_SNAPSHOTS_V1':
        raise ValueError('Snapshot schema mismatch')
    records=data.get('snapshots')
    if not isinstance(records,list) or not records: raise ValueError('Snapshot list required')
    ids=set();output=[];matched={}
    for s in records:
        if not isinstance(s,dict):raise ValueError('Snapshot must be object')
        ident=s.get('id')
        if not isinstance(ident,str) or not ident or ident in ids:raise ValueError('Unique snapshot ID required')
        ids.add(ident)
        if s.get('kind') not in ('PLAN','FACT'):raise ValueError('Snapshot kind PLAN or FACT required')
        if not all(s.get(k) for k in ('team','market','captured_at','source_evidence_id')):raise ValueError('Provenance fields mandatory')
        if type(s.get('period')) is not int or not (0<=s['period']<=5):raise ValueError('Period 0..5 required')
        f=s.get('factors')
        if not isinstance(f,dict) or set(COEFF)-set(f):raise ValueError('Missing displayed index factor values')
        out=computed_index_from_factors(f,s.get('weights'))
        display=s.get('displayed_total_index')
        if type(display) not in (int,float):raise ValueError('Displayed total index required')
        residual=round(out['total_index_from_displayed_factors']-display,8)
        finance=None
        if type(s.get('revenue_ecu')) in (int,float) and type(s.get('expense_ecu')) in (int,float):
            finance={'revenue_ecu':s['revenue_ecu'],'expense_ecu':s['expense_ecu'],
                     'arithmetic_difference_ecu':round(s['revenue_ecu']-s['expense_ecu'],2),
                     'not_certified_spendable_cash':True}
        row={'id':ident,'kind':s['kind'],'team':s['team'],'market':s['market'],
             'period':s['period'],'captured_at':s['captured_at'],'source_evidence_id':s['source_evidence_id'],
             'displayed_total_index':display,
             'reconstructed_from_display_factors':out['total_index_from_displayed_factors'],
             'display_factor_rounding_residual':residual,
             'index_close_at_two_decimal_precision':abs(residual)<=0.02,
             'six_component_indices':out['partial_indexes'],
             'finance_arithmetic':finance,
             'annual_transition_or_causal_effect_validated':False}
        output.append(row)
        matched.setdefault((s['market'],s['team'],s['period']),{})[s['kind']]=row
    pairs=[]
    for key,pair in matched.items():
        if 'PLAN' in pair and 'FACT' in pair:
            a,b=pair['PLAN'],pair['FACT']
            pairs.append({'market':key[0],'team':key[1],'period':key[2],
                          'plan_index':a['displayed_total_index'],'fact_index':b['displayed_total_index'],
                          'descriptive_fact_minus_plan_index':round(b['displayed_total_index']-a['displayed_total_index'],6),
                          'causal_explanation_identified':False,
                          'reason':'Interactions, changed decisions and league movement not controlled'})
    return {'schema':'ECOSIM_R146_PASSIVE_RECONCILIATION_V1',
            'snapshots':output,'paired_same_period_plan_fact':pairs,
            'p0_fact_vs_p1_plan_is_not_a_realized_transition':True,
            'calibrated_five_year_transition':False,
            'passive_read_only':True,'gameplay_gate':'STOP',
            'actual_forecast_accuracy':None}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshots',default=str(ROOT/'inputs/historical_passive_summary_20261030.json'))
    ap.add_argument('--out',default=str(ROOT/'results/R146_PASSIVE_HISTORICAL_RECONCILIATION.json'))
    args=ap.parse_args()
    o=reconcile_snapshots(read_json(args.snapshots))
    target=Path(args.out);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(o,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print('R146_PASSIVE_RECONCILIATION=PASS; records='+str(len(o['snapshots']))+'; game_actions=0')

if __name__=='__main__':main()
