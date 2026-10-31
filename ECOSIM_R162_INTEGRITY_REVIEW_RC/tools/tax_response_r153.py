#!/usr/bin/env python3
"""Source-anchored conditional corporate-friendliness tax/fee *factor*.

Implements the 840.41fdc8e1.chunk.js Re(e,t) branch.  Results are not a tax
revenue model, migration model, or forecast. No JS execution or network.
"""
from __future__ import annotations
from json_integrity_r162 import read_json
import json,math,hashlib
from pathlib import Path
from portfolio_5y import project_index
from r142_proxy_reference import WEIGHTS

SCHEMA='ECOSIM_R153_TAX_COUNTERFACTUAL_V1'
SOURCE_EXPRESSION_SHA256='cd4c23b0e57a2019ca3fe69151e19fb9c314e94e8cf5e0920f258e370eb3abf0'
FIELDS=('services_fee_percentage','business_tax_percentage','vehicle_tax_amount','building_tax_amount')

def finite_number(value, label, *, positive=False, nonnegative=False):
    if type(value) not in (int,float) or not math.isfinite(value):raise ValueError(label+' must be finite numeric')
    if positive and value<=0:raise ValueError(label+' must be positive')
    if nonnegative and value<0:raise ValueError(label+' must be nonnegative')
    return float(value)

def tax_formula(market,decisions,project_multiplier=1.0):
    """Return percent factor; *only* the evidenced client algebra.

    Does not infer market inputs, project active state, or server acceptance.
    """
    if not isinstance(market,dict) or set(market)!={'base_multiplier','weights','tax_index_divisors'}:
        raise ValueError('Exact market formula configuration required')
    if not isinstance(decisions,dict) or set(decisions)!=set(FIELDS):
        raise ValueError('Four distinct, complete source tax/service decisions required')
    weights=market['weights']; divisors=market['tax_index_divisors']
    if not isinstance(weights,dict) or set(weights)!={'services_and_building','business_tax','environment_and_vehicle'}:
        raise ValueError('Exact source weight fields required')
    if not isinstance(divisors,dict) or set(divisors)!={'business','vehicle','building'}:
        raise ValueError('Exact source tax index divisors required')
    bw=finite_number(market['base_multiplier'],'base_multiplier',positive=True)
    w={k:finite_number(v,'weight '+k,nonnegative=True) for k,v in weights.items()}
    d={k:finite_number(v,'index divisor '+k,positive=True) for k,v in divisors.items()}
    q={k:finite_number(v,'decision '+k,nonnegative=True) for k,v in decisions.items()}
    pm=finite_number(project_multiplier,'project_multiplier',positive=True)
    subtotal=(1 - q['services_fee_percentage']/100*w['services_and_building']
                - (q['business_tax_percentage']/100)/d['business']*w['business_tax']
                - q['vehicle_tax_amount']/d['vehicle']*w['environment_and_vehicle']
                - q['building_tax_amount']/d['building']*w['services_and_building'])
    latent=bw*subtotal*pm
    # Client branch uses Math.min(1,...), NOT Math.max(0,...).
    return {'factor_percent':100*min(1.0,latent),
            'uncapped_factor_percent':100*latent,
            'upper_cap_applied':latent>=1.0,
            'source_expression_sha256':SOURCE_EXPRESSION_SHA256}

def read_document(path):
    p=Path(path)
    if not p.is_file() or p.stat().st_size>250_000:raise ValueError('Local tax scenario JSON missing or oversized')
    doc=read_json(p,max_bytes=250_000)
    if not isinstance(doc,dict) or set(doc)!={'schema','source_class','assumption_note','market','baseline','paths'} or doc.get('schema')!=SCHEMA:
        raise ValueError('Invalid R153 schema and allowed top-level keys')
    if doc['source_class'] not in ('SYNTHETIC_TEST_ONLY','OPERATOR_DECLARED_READONLY_HYPOTHESIS'):
        raise ValueError('Source class required; never mark scenarios officially verified')
    if not isinstance(doc['assumption_note'],str) or not doc['assumption_note'].strip():raise ValueError('Assumption note required')
    b=doc['baseline']
    if not isinstance(b,dict) or set(b)!={'decisions','project_multiplier','observed_company_friendliness_percent'}:
        raise ValueError('Baseline needs full tax decisions, explicit project multiplier, and observed factor')
    declared=finite_number(b['observed_company_friendliness_percent'],'observed company friendliness')
    baseline=tax_formula(doc['market'],b['decisions'],b['project_multiplier'])
    if abs(baseline['factor_percent']-declared)>0.04:
        raise ValueError('Formula baseline does not reproduce observed factor; cannot use delta to rank project candidates')
    paths=doc['paths']
    if not isinstance(paths,list) or not 1<=len(paths)<=12:raise ValueError('1..12 paths required')
    seen=set()
    for path in paths:
        if not isinstance(path,dict) or set(path)!={'id','decisions_by_year','assumption_note'}:
            raise ValueError('Tax path keys unexpected')
        if not isinstance(path['id'],str) or not path['id'].strip() or path['id'] in seen:raise ValueError('Unique path ID required')
        seen.add(path['id'])
        if not isinstance(path['assumption_note'],str) or not path['assumption_note'].strip():raise ValueError('Path explanation required')
        seq=path['decisions_by_year']
        if not isinstance(seq,list) or len(seq)!=5:raise ValueError('Exactly five annual tax decisions required; use explicit unchanged copies')
        for item in seq:tax_formula(doc['market'],item,b['project_multiplier'])
    return doc,baseline

def project_factor_multiplier(start_lists,year,initial_multiplier):
    """Conditional active nonrepeatable effects from historical project cards.

    The explicit baseline multiplier already includes previous running projects.
    It must not be blindly re-multiplied by initial active projects.
    """
    idx=project_index(); pm=initial_multiplier
    for i,ids in enumerate(start_lists):
        if i>year:break
        for pid in ids:
            if pid not in idx:raise ValueError('Project absent from historical 35-card catalog')
            for eff in idx[pid]['effects']:
                if eff['metric']=='Vállalkozóbarátság':
                    v=finite_number(eff['value_percent'],'project effect percent')
                    if v<=-100:raise ValueError('Invalid project multiplier')
                    pm*=1+v/100
    return pm

def evaluate(doc, candidate_rows, start_year, weights=None):
    if type(start_year) is not int or not 1<=start_year<=5:raise ValueError('Invalid start year')
    # Validate even if the user supplied the dictionary in memory.
    baseline=tax_formula(doc['market'],doc['baseline']['decisions'],doc['baseline']['project_multiplier'])
    if abs(baseline['factor_percent']-doc['baseline']['observed_company_friendliness_percent'])>0.04:
        raise ValueError('Tax baseline not reconciled')
    if weights is None:
        composite=None;wsource='UNKNOWN_CURRENT_INDEX_WEIGHTS'
    else:
        if set(weights)!=set(WEIGHTS) or any(type(v) not in (int,float) or not math.isfinite(v) or v<0 for v in weights.values()) or abs(sum(weights.values())-1)>1e-9:
            raise ValueError('Current index weights invalid')
        composite=float(weights['Gazdaság'])/4  # One of four market subindex terms.
        wsource='OPERATOR_DECLARED_MARKET_WEIGHTS_NOT_SERVER_AUTHENTICATED'
    results=[]
    for path in doc['paths']:
        data=[]
        for row in candidate_rows:
            starts=row['project_ids_by_year']; years=[]
            if len(starts)!=6-start_year:raise ValueError('Candidate horizon mismatch')
            for offset,startids in enumerate(starts):
                year=start_year+offset
                pm=project_factor_multiplier(starts,offset,doc['baseline']['project_multiplier'])
                same=tax_formula(doc['market'],doc['baseline']['decisions'],pm)
                changed=tax_formula(doc['market'],path['decisions_by_year'][year-1],pm)
                delta=changed['factor_percent']-same['factor_percent']
                contribution=delta*composite if composite is not None else None
                years.append({'year':year,'project_multiplier_if_active':round(pm,10),
                              'business_friendliness_factor_if_baseline_tax':round(same['factor_percent'],7),
                              'business_friendliness_factor_if_tax_path':round(changed['factor_percent'],7),
                              'source_conditional_factor_difference':round(delta,7),
                              'static_partial_index_delta_from_tax_only':round(contribution,8) if contribution is not None else None,
                              'actual_market_or_migration_response':None,
                              'tax_income_effect':None})
            terminal=years[-1]['static_partial_index_delta_from_tax_only']
            data.append({'candidate_id':row['candidate_id'],
                         'project_ids_by_year':starts,
                         'mapped_terminal_proxy_plus_tax_path_delta':round(row['mapped_terminal_proxy_delta']+terminal,8) if terminal is not None else None,
                         'tax_delta_in_terminal_partial_index':terminal,
                         'yearly_factor_counterfactual':years,
                         'real_five_year_score':None,'real_budget_impact':None,
                         'not_a_new_optimizer':True})
        data.sort(key=lambda r:(r['mapped_terminal_proxy_plus_tax_path_delta'] is None,
                                -(r['mapped_terminal_proxy_plus_tax_path_delta'] if r['mapped_terminal_proxy_plus_tax_path_delta'] is not None else float('-inf'))))
        results.append({'path_id':path['id'],'assumption_note':path['assumption_note'],
                        'conditional_candidate_comparison':data,
                        'not_actual_tax_policy_ranking':True})
    return {'schema':'ECOSIM_R153_SOURCE_BACKED_TAX_RESPONSE_REPORT_V1',
            'source_expression_sha256':SOURCE_EXPRESSION_SHA256,
            'source_class':doc['source_class'],
            'baseline_factor_reproduced_within_0_04':True,
            'baseline_formula_factor_percent':round(baseline['factor_percent'],8),
            'observed_company_friendliness_percent':doc['baseline']['observed_company_friendliness_percent'],
            'index_weight_source':wsource,
            'tax_revenue_and_migration_model':'UNMODELLED_NOT_ZERO',
            'future_project_effects_persistent':'CONDITIONAL_ASSUMPTION',
            'gameplay_gate':'STOP',
            'paths':results}
