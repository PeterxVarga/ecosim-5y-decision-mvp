#!/usr/bin/env python3
"""Source-bounded SIX service fees + partial institutional wages/materials.

Client formulas from 840.41fdc8e1.chunk.js module 5168, *not* the EcoSim
server. Exogenous future population, occupancy, workforce, prices and market
parameters are operator-declared, not forecast. Does not authorize spending.
"""
from __future__ import annotations
import math

SCHEMA='ECOSIM_R155_SOURCE_OPERATING_COMPONENTS_V1'
FEES=('burial','parking','communal','services','rental','transport')
STAFF=('edu_nursery','edu_kindergarten','edu_primary','edu_middle','sport','culture','health','social',
       'service_water','service_waste','service_3','service_4','service_5','service_6','office')
WAGE=('education','sport','health','social','services','bureau')
MATERIAL=('education','sport','health','social','services','bureau')
BASES=('population','parking_car_index','burial_units','housing_unit_count','rental_unit_count',
       'rental_factor','transport_units','transport_ratio','transport_wages_ecu','staff','wage_rates','material_ratios',
       'service_material_multiplier')
PARKING=('ratio','elasticity','damper','reference_fee')

def val(v,name,positive=False):
    if type(v) not in (int,float) or not math.isfinite(v) or v<0 or (positive and v<=0):
        raise ValueError(name+' must be finite '+('positive' if positive else 'nonnegative'))
    return float(v)

def exact_dict(v,keys,label):
    if not isinstance(v,dict) or set(v)!=set(keys):raise ValueError(label+' has missing or unexpected keys')
    return v

def validate(doc,expected_years=5):
    exact_dict(doc,('schema','source_class','assumption_note','market','annual_city_bases','baseline_fees','paths',
                    'fixed_exogenous_bases_across_paths','excluded_from_nonproject_cash'),'document')
    if doc['schema']!=SCHEMA:raise ValueError('Wrong R155 schema')
    if doc['source_class'] not in ('SYNTHETIC_TEST_ONLY','OPERATOR_DECLARED_READONLY_HYPOTHESIS'):
        raise ValueError('Unverified future data must not be labelled official')
    if not isinstance(doc['assumption_note'],str) or not doc['assumption_note'].strip():raise ValueError('Assumption note required')
    if doc['fixed_exogenous_bases_across_paths'] is not True or doc['excluded_from_nonproject_cash'] is not True:
        raise ValueError('Anti-double-counting and fixed exogenous base declaration required')
    market=exact_dict(doc['market'],('parking','rental_multiplier'),'market')
    val(market['rental_multiplier'],'rental multiplier')
    p=exact_dict(market['parking'],PARKING,'parking market')
    for key in PARKING:
        if not isinstance(p[key],list) or len(p[key])!=expected_years:raise ValueError('Parking annual market vector missing')
        for v in p[key]:val(v,'parking '+key,positive=key in ('ratio','damper','reference_fee'))
    fees=exact_dict(doc['baseline_fees'],FEES,'baseline fees')
    for k,v in fees.items():val(v,k,positive=k=='parking')
    bases=doc['annual_city_bases']
    if not isinstance(bases,list) or len(bases)!=expected_years:raise ValueError('Five annual city bases required')
    for year,b in enumerate(bases):
        exact_dict(b,BASES,f'city base {year+1}')
        for k in BASES:
            if k not in ('staff','wage_rates','material_ratios'):val(b[k],f'{year+1}.{k}')
        for dict_key,keys in (('staff',STAFF),('wage_rates',WAGE),('material_ratios',MATERIAL)):
            d=exact_dict(b[dict_key],keys,dict_key)
            for k,v in d.items():val(v,f'{year+1}.{dict_key}.{k}')
    paths=doc['paths']
    if not isinstance(paths,list) or not 1<=len(paths)<=12:raise ValueError('1-12 operating paths required')
    ids=set()
    for path in paths:
        exact_dict(path,('id','assumption_note','fees_by_year','staff_by_year'),'operating path')
        if not isinstance(path['id'],str) or not path['id'] or path['id'] in ids:
            raise ValueError('Duplicate or missing path ID')
        ids.add(path['id'])
        if not isinstance(path['assumption_note'],str) or not path['assumption_note'].strip():raise ValueError('Path assumptions required')
        for k,keys in (('fees_by_year',FEES),('staff_by_year',STAFF)):
            if not isinstance(path[k],list) or len(path[k])!=expected_years:raise ValueError('Complete five-year path required')
            for year,d in enumerate(path[k]):
                exact_dict(d,keys,k)
                for name,v in d.items():val(v,f'{k}.{year+1}.{name}',positive=k=='fees_by_year' and name=='parking')
    return doc


def service_fees(market,year,base,fees):
    """Source Xi/eo/to/ao/no/io. Price-response beyond these formulas unknown."""
    exact_dict(base,BASES,'year base');exact_dict(fees,FEES,'fee decisions')
    q={k:val(v,k,positive=k=='parking') for k,v in fees.items()}
    p=market['parking'];i=year-1
    ratio=val(p['ratio'][i],'parking ratio',True)
    damper=val(p['damper'][i],'parking damper',True)
    ref=val(p['reference_fee'][i],'parking reference',True)
    elasticity=val(p['elasticity'][i],'parking elasticity')
    r=q['parking']/ref
    items={
        'burial':q['burial']*base['burial_units'],
        'parking':base['population']*base['parking_car_index']/1000 *q['parking']*(ratio**(r/damper))*(r**(-elasticity)),
        'communal':q['communal']*base['housing_unit_count'],
        'services':q['services']*base['housing_unit_count'],
        'rental':q['rental']*base['rental_unit_count']*min(1+market['rental_multiplier']*base['rental_factor'],.99),
        'transport':q['transport']*base['transport_units']*base['transport_ratio'],
    }
    if any(not math.isfinite(x) for x in items.values()) or not math.isfinite(sum(items.values())):raise ValueError('Fee arithmetic overflow')
    return {'channels_ecu':{k:round(v,8) for k,v in items.items()},'six_fee_subtotal_ecu':round(sum(items.values()),8),
            'actual_service_income_ecu':None,'source_scope':'CLIENT_SIX_SERVICE_FEE_COMPONENTS_ONLY'}


def staff_expenses(base,staff):
    """Source Vn/Wn/Hn/On/Bn/_n/Un/Yn and Zn/qn/Gn/$n/Kn/Jn/Xn.

    Transport wages are separately provided exogenous subtotal. Excludes
    training, public transport material, other operating costs, capital costs.
    """
    exact_dict(staff,STAFF,'staff vector')
    rates=base['wage_rates'];m=base['material_ratios'];s=staff
    wage={
        'education':rates['education']*sum(s[k] for k in STAFF[:4]),
        'sport':rates['sport']*s['sport'],
        'culture':rates['sport']*s['culture'], # Hn client uses A.sport!
        'health':rates['health']*s['health'],
        'social':rates['social']*s['social'],
        'services':rates['services']*sum(s[k] for k in STAFF[8:14]),
        'transport':base['transport_wages_ecu'],
        'bureau':rates['bureau']*s['office'],
    }
    mat={
        'education':wage['education']*m['education'],
        'sport':wage['sport']*m['sport'],
        'culture':wage['culture']*m['sport'],
        'health':wage['health']*m['health'],
        'social':wage['social']*m['social'],
        'services':wage['services']*m['services']*base['service_material_multiplier'],
        'bureau':wage['bureau']*m['bureau'],
    }
    if any(not math.isfinite(v) for v in list(wage.values())+list(mat.values())) or not math.isfinite(sum(wage.values())+sum(mat.values())):
        raise ValueError('Institution payroll/material arithmetic overflow')
    return {'wage_components_ecu':{k:round(v,8) for k,v in wage.items()},
            'material_components_ecu':{k:round(v,8) for k,v in mat.items()},
            'wage_subtotal_ecu':round(sum(wage.values()),8),
            'material_subtotal_ecu':round(sum(mat.values()),8),
            'covered_payroll_material_expense_ecu':round(sum(wage.values())+sum(mat.values()),8),
            'training_transit_material_and_other_expenses_ecu':None,
            'actual_total_city_expenses_ecu':None}


def evaluate(doc,path,start_year=1):
    validate(doc)
    if type(start_year) is not int or not 1<=start_year<=5:raise ValueError('Invalid rolling start year')
    result=[]
    for year in range(start_year,6):
        b=doc['annual_city_bases'][year-1]
        before=service_fees(doc['market'],year,b,doc['baseline_fees'])
        after=service_fees(doc['market'],year,b,path['fees_by_year'][year-1])
        cb=staff_expenses(b,b['staff']);ca=staff_expenses(b,path['staff_by_year'][year-1])
        revenue_delta=after['six_fee_subtotal_ecu']-before['six_fee_subtotal_ecu']
        cost_delta=ca['covered_payroll_material_expense_ecu']-cb['covered_payroll_material_expense_ecu']
        result.append({'year':year,'six_fee_baseline_ecu':before['six_fee_subtotal_ecu'],
                       'six_fee_counterfactual_ecu':after['six_fee_subtotal_ecu'],
                       'six_fee_delta_ecu':round(revenue_delta,8),
                       'six_fee_channel_deltas_ecu':{k:round(after['channels_ecu'][k]-before['channels_ecu'][k],8) for k in FEES},
                       'covered_institution_payroll_material_baseline_ecu':cb['covered_payroll_material_expense_ecu'],
                       'covered_institution_payroll_material_counterfactual_ecu':ca['covered_payroll_material_expense_ecu'],
                       'covered_institution_cost_delta_ecu':round(cost_delta,8),
                       'partial_annual_operating_net_delta_ecu':round(revenue_delta-cost_delta,8),
                       'server_settled_net_ecu':None,'unmodeled_population_and_staff_feedback':'UNKNOWN_NOT_ZERO'})
    return {'schema':'ECOSIM_R155_SOURCE_OPERATING_COUNTERFACTUAL_V1',
            'source_class':doc['source_class'],'path_id':path['id'],
            'annual_rows':result,
            'five_year_partial_operating_net_delta_ecu':round(sum(y['partial_annual_operating_net_delta_ecu'] for y in result),8),
            'five_year_six_fee_delta_ecu':round(sum(y['six_fee_delta_ecu'] for y in result),8),
            'five_year_covered_institution_cost_delta_ecu':round(sum(y['covered_institution_cost_delta_ecu'] for y in result),8),
            'actual_city_cashflow_ecu':None,'actual_market_and_migration_response':None,
            'full_city_expenses_and_revenues':'UNMODELLED_NOT_ZERO',
            'available_budget_from_partial_delta_ecu':None,
            'gameplay_gate':'STOP'}


def combined_front(candidates,tax_report,operating_report,tax_response):
    if tax_report is None or tax_response is None:
        return {'status':'UNJOINABLE_MISSING_TAX_EVIDENCE','front':[],'evaluated':0,'gameplay_gate':'STOP'}
    t={p['tax_path_id']:p['fiscal_comparison'] for p in tax_report['path_counterfactuals']}
    o={p['path_id']:p for p in operating_report['path_counterfactuals']}
    if set(t)!=set(o):raise ValueError('Tax and fee/staff path IDs cannot be joined')
    cand={c['candidate_id']:c for c in candidates}
    if len(cand)!=len(candidates):raise ValueError('Duplicate candidate')
    rows=[]
    for path in tax_response['paths']:
        name=path['path_id']
        if name not in t:raise ValueError('Unmatched response path')
        fiscal=t[name]['five_year_fixed_base_tax_delta_ecu']+o[name]['five_year_partial_operating_net_delta_ecu']
        for entry in path['conditional_candidate_comparison']:
            sc=entry['mapped_terminal_proxy_plus_tax_path_delta'];c=cand[entry['candidate_id']]
            if sc is None:continue
            rows.append({'candidate_id':entry['candidate_id'],'path_id':name,
                         'terminal_partial_index_proxy_delta':sc,
                         'five_year_conditional_net_operating_delta_ecu':round(fiscal,8),
                         'five_year_project_card_need_ecu':c['five_year_conservative_project_need_ecu'],
                         'actual_available_money_ecu':None,'actual_year_5_index':None,
                         'source_coverage':'FOUR_TAXES_SIX_FEES_PARTIAL_INSTITUTION_WAGES_AND_MATERIALS'})
    def dominates(a,b):
        vals=((a['terminal_partial_index_proxy_delta'],b['terminal_partial_index_proxy_delta'],1),
              (a['five_year_conditional_net_operating_delta_ecu'],b['five_year_conditional_net_operating_delta_ecu'],1),
              (a['five_year_project_card_need_ecu'],b['five_year_project_card_need_ecu'],-1))
        return all((x-y)*d>=-1e-8 for x,y,d in vals) and any((x-y)*d>1e-8 for x,y,d in vals)
    front=[x for x in rows if not any(dominates(y,x) for y in rows if y is not x)]
    front.sort(key=lambda x:(-x['terminal_partial_index_proxy_delta'],
                              -x['five_year_conditional_net_operating_delta_ecu'],x['five_year_project_card_need_ecu']))
    return {'schema':'ECOSIM_R155_PARTIAL_OPERATING_THREE_AXIS_SAMPLED_PARETO_V1',
            'status':'CONDITIONAL_SAMPLED_NOT_GLOBAL_OPTIMUM','evaluated':len(rows),
            'front':front,'exogenous_bases_fixed_across_paths':True,
            'unknown_fiscal_components_not_assumed_zero':True,
            'real_budget_or_terminal_score_validated':False,'gameplay_gate':'STOP'}
