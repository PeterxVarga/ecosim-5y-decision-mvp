#!/usr/bin/env python3
"""Four source-bounded EcoSim client-side tax-income components.

Source: 840.41fdc8e1.chunk.js, Webpack module 5168 Bi/_i/Ui/Yi.
Only a counterfactual with operator-declared, FIXED exogenous bases; in
particular business counts, car/population/housing movements are UNMODELLED.
No server authority, available-cash assertion, or market-parameter inference.
"""
from __future__ import annotations
import json
import math
from pathlib import Path

SCHEMA = 'ECOSIM_R154_FIXED_BASE_TAX_REVENUE_V1'
REVENUE_CHANNELS = ('business', 'vehicle', 'communal', 'building')
BASE_FIELDS = ('business_taxable_base_ecu', 'car_count_index', 'population',
               'housing_unit_count', 'communal_tax_amount')


def number(value, label, positive=False):
    if type(value) not in (int,float) or not math.isfinite(value) or value<0 or (positive and value<=0):
        raise ValueError(label+' must be finite and '+('positive' if positive else 'nonnegative'))
    return float(value)


def validate(doc, *, expected_years=5):
    if not isinstance(doc,dict) or set(doc)!={'schema','source_class','assumption_note','market','annual_city_bases','fixed_bases_across_paths','excluded_from_nonproject_cash'} or doc.get('schema')!=SCHEMA:
        raise ValueError('R154 exact tax revenue scenario schema required')
    if doc['source_class'] not in ('SYNTHETIC_TEST_ONLY','OPERATOR_DECLARED_READONLY_HYPOTHESIS'):
        raise ValueError('No verified or official source class without independent proof')
    if not isinstance(doc['assumption_note'],str) or not doc['assumption_note'].strip():
        raise ValueError('Explicit unsupported assumptions required')
    if doc['fixed_bases_across_paths'] is not True or doc['excluded_from_nonproject_cash'] is not True:
        raise ValueError('Fixed-base and anti-double-counting declarations mandatory')
    params=doc['market']
    if not isinstance(params,dict) or set(params)!=set(REVENUE_CHANNELS)-{'business'}:
        raise ValueError('Three tax sensitivities/divisors required')
    for k in params:
        if not isinstance(params[k],dict) or set(params[k])!={'revenue_sensitivity','index_divisor'}:
            raise ValueError('Exact channel market parameters required')
        number(params[k]['revenue_sensitivity'],k+'.revenue_sensitivity')
        number(params[k]['index_divisor'],k+'.index_divisor',positive=True)
    bases=doc['annual_city_bases']
    if not isinstance(bases,list) or len(bases)!=expected_years:raise ValueError('Complete annual city-state base vector required')
    for year,b in enumerate(bases,1):
        if not isinstance(b,dict) or set(b)!=set(BASE_FIELDS):raise ValueError('Year '+str(year)+' has incomplete bases')
        for k,v in b.items():number(v,'year '+str(year)+' '+k)
    return doc


def tax_revenue(market, base, decisions, *, communal_tax_amount):
    """Direct source arithmetic with no revenues from other fee/grant channels.

    Bi = Nr * business_tax_pct / 100
    _i = Ta * vehicle_tax * max(0, 1 - vehicle_tax*sensitivity/divisor) * population / 1000
    Ui = communal_tax * housing_count * max(0, 1 - communal_tax*sensitivity/divisor)
    Yi = building_tax * housing_count * max(0, 1 - building_tax*sensitivity/divisor)
    """
    if not isinstance(base,dict) or set(base)!={'business_taxable_base_ecu','car_count_index','population','housing_unit_count'}:
        raise ValueError('Exactly four measured/declared exogenous tax bases required')
    if not isinstance(decisions,dict) or not {'business_tax_percentage','vehicle_tax_amount','building_tax_amount'}.issubset(decisions):
        raise ValueError('Incomplete tax decisions')
    b={k:number(v,k) for k,v in base.items()}
    rates={k:number(decisions[k],k) for k in ('business_tax_percentage','vehicle_tax_amount','building_tax_amount')}
    communal=number(communal_tax_amount,'communal_tax_amount')
    params={}
    for k in ('vehicle','communal','building'):
        if k not in market or not isinstance(market[k],dict):raise ValueError(k+' market tax parameters missing')
        sens=number(market[k].get('revenue_sensitivity'),k+' sensitivity')
        div=number(market[k].get('index_divisor'),k+' index divisor',positive=True)
        params[k]=(sens,div)
    def taxable_factor(channel,amount):
        sens,div=params[channel]
        return max(0.,1.-amount*sens/div)
    business=b['business_taxable_base_ecu']*rates['business_tax_percentage']/100.
    vehicle=b['car_count_index']*rates['vehicle_tax_amount']*taxable_factor('vehicle',rates['vehicle_tax_amount'])*b['population']/1000.
    municipal=communal*b['housing_unit_count']*taxable_factor('communal',communal)
    building=rates['building_tax_amount']*b['housing_unit_count']*taxable_factor('building',rates['building_tax_amount'])
    values={'business':business,'vehicle':vehicle,'communal':municipal,'building':building}
    if any(not math.isfinite(x) for x in values.values()) or not math.isfinite(sum(values.values())):
        raise ValueError('Overflow / nonfinite tax income rejected')
    return {'channels_ecu':{k:round(v,8) for k,v in values.items()},
            'four_channel_subtotal_ecu':round(sum(values.values()),8),
            'actual_total_revenue_ecu':None,'other_income_ecu':None,
            'available_project_cash_ecu':None,
            'provenance':'STATIC_CLIENT_SOURCE_FORMULA_WITH_EXPLICIT_FIXED_BASE_ASSUMPTIONS',
            'tax_rate_changes_induce_population_or_firm_changes':False}


def evaluate_counterfactual(document, baseline_decisions, path, *, start_year):
    """Conditional fiscal differences for one tax path, not city forecasts.

    Uses full five-year decision paths even when rolling from year 2 onward.
    Future city bases are explicit exogenous hypotheses, not model outputs.
    """
    validate(document)
    if type(start_year) is not int or not 1<=start_year<=5:raise ValueError('start_year 1..5')
    if len(path)!=5:raise ValueError('Complete five-year decision path required')
    out=[]
    for year in range(start_year,6):
        raw=document['annual_city_bases'][year-1]
        b={k:raw[k] for k in BASE_FIELDS if k!='communal_tax_amount'}
        shared={'market':document['market'],'base':b,'communal_tax_amount':raw['communal_tax_amount']}
        before=tax_revenue(**shared,decisions=baseline_decisions)
        after=tax_revenue(**shared,decisions=path[year-1])
        diff=after['four_channel_subtotal_ecu']-before['four_channel_subtotal_ecu']
        channels={k:round(after['channels_ecu'][k]-before['channels_ecu'][k],8) for k in REVENUE_CHANNELS}
        out.append({'year':year,'baseline_four_tax_income_ecu':before['four_channel_subtotal_ecu'],
                    'counterfactual_four_tax_income_ecu':after['four_channel_subtotal_ecu'],
                    'fixed_base_four_tax_delta_ecu':round(diff,8),
                    'four_tax_channel_deltas_ecu':channels,
                    'base_response_to_policy':'UNMODELLED',
                    'real_cash_available_ecu':None,
                    'server_settled_tax_income_ecu':None})
    return {'schema':'ECOSIM_R154_FIXED_BASE_FISCAL_COUNTERFACTUAL_V1',
            'source_class':document['source_class'],
            'yearly':out,
            'five_year_fixed_base_tax_delta_ecu':round(sum(y['fixed_base_four_tax_delta_ecu'] for y in out),8),
            'year_5_delta_ecu':out[-1]['fixed_base_four_tax_delta_ecu'],
            'fiscal_tradeoff_not_an_authorized_budget':True,
            'unmodeled_city_state_and_indirect_revenue':'UNKNOWN_NOT_ZERO',
            'gameplay_gate':'STOP'}


def build_joint_tradeoff_front(candidate_rows, tax_report, fiscal_report):
    """Sampled candidate x tax-path comparisons, *not* a new search or a win rank.

    Three conditional objectives: mapped terminal proxy (up), cumulative fixed-
    base tax delta (up), card cost (down). No claim about multi-year liquidity,
    indirect feedback, server restrictions, or total score.
    """
    if tax_report is None or fiscal_report is None:
        return {'status':'UNKNOWN_NO_JOINABLE_EVIDENCE','front':[],'evaluated':0,'gameplay_gate':'STOP'}
    cmap={c['candidate_id']:c for c in candidate_rows}
    if len(cmap)!=len(candidate_rows):raise ValueError('Duplicate candidate identifiers')
    fpaths={p['tax_path_id']:p['fiscal_comparison'] for p in fiscal_report['path_counterfactuals']}
    if len(fpaths)!=len(fiscal_report['path_counterfactuals']):raise ValueError('Duplicate fiscal path identifiers')
    if set(fpaths)!={p['path_id'] for p in tax_report['paths']}:
        raise ValueError('Tax and fiscal scenario path identifiers disagree')
    rows=[]
    for path in tax_report['paths']:
        f=fpaths[path['path_id']]
        for c in path['conditional_candidate_comparison']:
            cid=c['candidate_id']
            if cid not in cmap:raise ValueError('Unrecognized tax candidate ID')
            proxy=c['mapped_terminal_proxy_plus_tax_path_delta']
            if proxy is None:continue
            cost=cmap[cid]['five_year_conservative_project_need_ecu']
            cash=f['five_year_fixed_base_tax_delta_ecu']
            if not all(type(x) in (float,int) and math.isfinite(x) for x in (proxy,cost,cash)):
                raise ValueError('Finite tradeoff values required')
            rows.append({'candidate_id':cid,'tax_path_id':path['path_id'],
                         'conditional_mapped_terminal_proxy_delta':proxy,
                         'five_year_fixed_base_four_tax_delta_ecu':cash,
                         'five_year_conservative_card_cost_ecu':cost,
                         'hypothetical_budget_authorized':False,
                         'real_five_year_smartcity_score':None})
    def dominates(a,b):
        x=a['conditional_mapped_terminal_proxy_delta'];y=b['conditional_mapped_terminal_proxy_delta']
        f=a['five_year_fixed_base_four_tax_delta_ecu'];g=b['five_year_fixed_base_four_tax_delta_ecu']
        ca=a['five_year_conservative_card_cost_ecu'];cb=b['five_year_conservative_card_cost_ecu']
        return x>=y-1e-10 and f>=g-1e-8 and ca<=cb+1e-8 and (x>y+1e-10 or f>g+1e-8 or ca<cb-1e-8)
    front=[a for i,a in enumerate(rows) if not any(dominates(b,a) for j,b in enumerate(rows) if i!=j)]
    front.sort(key=lambda v:(-v['conditional_mapped_terminal_proxy_delta'], -v['five_year_fixed_base_four_tax_delta_ecu'],v['five_year_conservative_card_cost_ecu']))
    return {'schema':'ECOSIM_R154_CONDITIONAL_THREE_AXIS_SAMPLED_PARETO_V1',
            'status':'CONDITIONAL_SAMPLED_NONDOMINATED_NOT_GLOBAL_OPTIMUM',
            'evaluated':len(rows),'front':front,
            'objectives':['higher partial mapped index proxy','higher direct four-tax revenue difference under fixed exogenous bases','lower conservative card cost'],
            'actual_cash_effect':'UNKNOWN', 'tax_base_feedback':'UNKNOWN',
            'all_35_cards_and_5_years_server_validated':False,
            'gameplay_gate':'STOP'}
