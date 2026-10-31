#!/usr/bin/env python3
"""R158 annual temporal fiscal bridge, no new search and no game execution.

All underlying direct formula results are R154/R155 FIXED-EXOGENOUS-BASE
counterfactuals. 'Funding pressure' means an arithmetic hypothetical balance
against ZERO unknown opening cash, NOT available credit or a game cash forecast.
"""
from __future__ import annotations
import math
from operating_cash_r155 import FEES
from tax_revenue_r154 import REVENUE_CHANNELS

SCHEMA='ECOSIM_R159_COMPONENT_RESOLVED_PARTIAL_FISCAL_TIMING_V1'


def number(v,label):
    if type(v) not in (int,float) or not math.isfinite(v):
        raise ValueError(label+' must be a finite number')
    return float(v)


def unique_map(items,key,label):
    if not isinstance(items,list):raise ValueError(label+' must be a list')
    result={}
    for item in items:
        if not isinstance(item,dict) or not isinstance(item.get(key),str) or not item[key] or item[key] in result:
            raise ValueError('Invalid/duplicate '+label)
        result[item[key]]=item
    return result


def _year_map(rows,year_field,amount_field,expected_years,label):
    if not isinstance(rows,list) or len(rows)!=len(expected_years):
        raise ValueError(label+' requires exact remaining-year rows')
    out={}
    for row in rows:
        if not isinstance(row,dict) or type(row.get(year_field)) is not int or row[year_field] in out:
            raise ValueError(label+' missing/duplicate year')
        out[row[year_field]]=number(row.get(amount_field),label+' '+amount_field)
    if set(out)!=set(expected_years):raise ValueError(label+' periods mismatch')
    return out


def _check_total(rows,reported,key,label):
    total=sum(rows.values())
    if abs(total-number(reported,label))>max(1e-4,abs(total)*1e-9):
        raise ValueError('Inconsistent '+label+' five-year total')


def _year_details(rows, expected_years, field, expected_totals, label, required_keys):
    """Require source component evidence; no fabricated split of a net result."""
    if not isinstance(rows,list):raise ValueError(label+' rows required')
    out={}
    for row in rows:
        if not isinstance(row,dict) or type(row.get('year')) is not int:
            raise ValueError(label+' year missing')
        y=row['year']
        if y in out or y not in expected_years:raise ValueError(label+' invalid/duplicate year')
        obj=row.get(field)
        if not isinstance(obj,dict) or set(obj)!=set(required_keys):
            raise ValueError(label+' requires all individually proven channels')
        values={k:number(v,label+' '+k) for k,v in obj.items()}
        if expected_totals is not None and abs(sum(values.values())-expected_totals[y])>max(1e-4,abs(expected_totals[y])*1e-9):
            raise ValueError(label+' channel totals do not reconcile')
        out[y]=values
    if set(out)!=set(expected_years):raise ValueError(label+' year horizon incomplete')
    return out


def timeline_for_candidate(candidate, tax_rows, op_rows, start_year):
    if type(start_year) is not int or not 1<=start_year<=5:raise ValueError('Invalid start year')
    years=list(range(start_year,6))
    if not isinstance(candidate,dict) or not isinstance(candidate.get('candidate_id'),str) or not candidate['candidate_id'].strip():
        raise ValueError('Candidate identifier required')
    starts=candidate.get('project_ids_by_year')
    costs=candidate.get('conservative_project_need_ecu_by_year')
    if not isinstance(starts,list) or len(starts)!=len(years) or any(not isinstance(x,list) for x in starts):
        raise ValueError('Candidate start-year horizon mismatch')
    if not isinstance(costs,list) or len(costs)!=len(years):raise ValueError('Candidate cost years mismatch')
    if any(type(i) is not int or i<=0 for ids in starts for i in ids) or len([i for ids in starts for i in ids])!=len({i for ids in starts for i in ids}):
        raise ValueError('Invalid or repeatedly launched project ID')
    cost_by_year={y:number(costs[i],'project cost') for i,y in enumerate(years)}
    if any(c<0 for c in cost_by_year.values()):raise ValueError('Project costs nonnegative')
    if abs(sum(cost_by_year.values())-number(candidate.get('five_year_conservative_project_need_ecu'),'cost total'))>1e-4:
        raise ValueError('Project total does not match annual costs')
    tax=_year_map(tax_rows['yearly'],'year','fixed_base_four_tax_delta_ecu',years,'tax')
    op=_year_map(op_rows['annual_rows'],'year','partial_annual_operating_net_delta_ecu',years,'operation')
    _check_total(tax,tax_rows['five_year_fixed_base_tax_delta_ecu'],'four_tax','tax')
    _check_total(op,op_rows['five_year_partial_operating_net_delta_ecu'],'operation','operation')
    # Critical R159 correction: operate on INDIVIDUAL tax/fee income channels,
    # NOT a net of receipts minus payroll. Netting before timing would allow
    # same-year staff expenses to be invisibly financed by delayed fees.
    tax_detail=_year_details(tax_rows['yearly'],years,'four_tax_channel_deltas_ecu',
                             tax,'tax channels',required_keys=REVENUE_CHANNELS)
    fee_detail=_year_details(op_rows['annual_rows'],years,'six_fee_channel_deltas_ecu',
                             None,'fee channels',required_keys=FEES)
    cost_detail=_year_map(op_rows['annual_rows'],'year','covered_institution_cost_delta_ecu',years,'institution costs')
    for y in years:
        fee_sum=sum(fee_detail[y].values())
        op_expected=fee_sum-cost_detail[y]
        if abs(op_expected-op[y])>max(1e-4,abs(op[y])*1e-9):
            raise ValueError('Operating fee and institution components do not reconcile')
    immediate=0.;deferred=0.;held_positive_income=0.
    first_immediate_negative=None;first_deferred_negative=None
    max_imm=0.;max_def=0.;peak_imm_year=None;peak_def_year=None
    data=[]
    for y in years:
        t=tax[y];o=op[y];cost=cost_by_year[y]
        net=t+o-cost
        immediate+=net
        components=list(tax_detail[y].values())+list(fee_detail[y].values())
        newly_positive=sum(max(v,0.) for v in components)
        immediate_negative_income=sum(min(v,0.) for v in components)
        # A decrease in staff/material spending is an immediate cost saving,
        # NOT a delayed cash receipt. Increases in expense are also immediate.
        net_deferred=held_positive_income+immediate_negative_income-cost_detail[y]-cost
        deferred+=net_deferred
        if immediate< -1e-8 and first_immediate_negative is None:first_immediate_negative=y
        if deferred< -1e-8 and first_deferred_negative is None:first_deferred_negative=y
        if -immediate>max_imm+1e-8:max_imm=-immediate;peak_imm_year=y
        if -deferred>max_def+1e-8:max_def=-deferred;peak_def_year=y
        data.append({'year':y,'projects_started_ids':starts[y-start_year],
                     'four_tax_delta_ecu':round(t,6),'six_fee_minus_covered_institutions_delta_ecu':round(o,6),
                     'direct_six_fee_delta_ecu':round(sum(fee_detail[y].values()),6),
                     'institutional_cost_delta_ecu':round(cost_detail[y],6),
                     'new_positive_tax_and_fee_deltas_deferred_ecu':round(newly_positive,6),
                     'negative_tax_and_fee_deltas_immediate_ecu':round(immediate_negative_income,6),
                     'project_card_need_ecu':round(cost,6),
                     'partial_net_after_card_cost_ecu':round(net,6),
                     'cumulative_partial_net_zero_opening_cash_ecu':round(immediate,6),
                     'deferred_positive_receipts_recognized_ecu':round(held_positive_income,6),
                     'deferred_net_after_card_cost_ecu':round(net_deferred,6),
                     'cumulative_deferred_net_zero_opening_cash_ecu':round(deferred,6)})
        held_positive_income=newly_positive
    return {'candidate_id':candidate['candidate_id'],
            'annual_rows':data,
            'five_year_fixed_base_tax_plus_partial_operating_delta_ecu':round(sum(tax.values())+sum(op.values()),6),
            'five_year_project_card_cost_ecu':round(sum(cost_by_year.values()),6),
            'five_year_partial_net_after_card_cost_ecu':round(immediate,6),
            'hypothetical_peak_zero_opening_cash_shortfall_immediate_ecu':round(max_imm,6),
            'hypothetical_peak_zero_opening_cash_shortfall_positive_receipts_deferred_ecu':round(max_def,6),
            'earliest_negative_cumulative_year_immediate':first_immediate_negative,
            'earliest_negative_cumulative_year_deferred':first_deferred_negative,
            'largest_immediate_shortfall_year':peak_imm_year,'largest_deferred_shortfall_year':peak_def_year,
            'positive_receipts_remaining_unrecognized_after_final_year_ecu':round(held_positive_income,6),
            'delayed_income_unit':'PER_TAX_AND_FEE_CHANNEL_NOT_NET_OF_INSTITUTIONAL_COSTS',
            'pre_horizon_delayed_positive_receipts_known':start_year==1,
            'pre_horizon_carry_in_assumed_zero_not_verified':start_year>1,
            'actual_opening_cash_ecu':None,'actual_spendable_cash_ecu':None,
            'server_cash_timing_and_credit_rules_known':False,
            'true_funding_gap_ecu':None,'affordability_authorized':False,'gameplay_gate':'STOP'}


def build_timing_bridge(candidates, tax_report, op_report, response_report, start_year):
    """Join EXACT same R153/154/155 paths and sampled R149/157 plans."""
    if tax_report is None or op_report is None or response_report is None:
        return {'schema':SCHEMA,'status':'BLOCKED_MISSING_JOINABLE_SOURCE_COMPONENTS','combinations':[],
                'actual_financing_authorized':False,'gameplay_gate':'STOP'}
    if tax_report.get('source_class')!=op_report.get('source_class') or tax_report.get('source_class')!=response_report.get('source_class'):
        raise ValueError('Mixed source classes in temporal cash bridge')
    cand=unique_map(candidates,'candidate_id','candidate')
    fiscal=unique_map(tax_report['path_counterfactuals'],'tax_path_id','tax path')
    oper=unique_map(op_report['path_counterfactuals'],'path_id','operation path')
    response=unique_map(response_report['paths'],'path_id','response path')
    if set(fiscal)!=set(oper) or set(fiscal)!=set(response):
        raise ValueError('Tax, operating, response path identifiers do not match')
    if set(cand)!={row['candidate_id'] for p in response.values() for row in p['conditional_candidate_comparison']}:
        raise ValueError('Candidate coverage across response paths inconsistent')
    by_path=[]; combos=[]; temporal_front_by_path=[]
    for path in sorted(fiscal):
        r=fiscal[path]['fiscal_comparison'];o=oper[path]
        by_path.append({'path_id':path,'five_year_fixed_base_tax_plus_partial_operating_delta_ecu':
                        round(number(r['five_year_fixed_base_tax_delta_ecu'],'tax total')+
                              number(o['five_year_partial_operating_net_delta_ecu'],'operating total'),6)})
        response_ids=[v['candidate_id'] for v in response[path]['conditional_candidate_comparison']]
        if len(response_ids)!=len(set(response_ids)) or set(response_ids)!=set(cand):
            raise ValueError('Incomplete/duplicate candidate response within path')
        response_scores={v['candidate_id']:v['mapped_terminal_proxy_plus_tax_path_delta']
                         for v in response[path]['conditional_candidate_comparison']}
        path_rows=[]
        for cid in sorted(cand):
            t=timeline_for_candidate(cand[cid],r,o,start_year)
            t['path_id']=path
            t['conditional_terminal_mapped_proxy_delta']=response_scores[cid]
            if t['conditional_terminal_mapped_proxy_delta'] is not None:
                number(t['conditional_terminal_mapped_proxy_delta'],'mapped index delta')
            combos.append(t);path_rows.append(t)
        # A descriptive *sampled* three-objective frontier, per policy path:
        # higher mapped terminal index, higher partial net AFTER project cards,
        # lower zero-opening hypothetical peak negative cumulative balance.
        # This is NOT an EcoSim funding rule or a new optimizer.
        valid=[v for v in path_rows if v['conditional_terminal_mapped_proxy_delta'] is not None]
        def dominates(a,b):
            cols=(('conditional_terminal_mapped_proxy_delta',1.),
                  ('five_year_partial_net_after_card_cost_ecu',1.),
                  ('hypothetical_peak_zero_opening_cash_shortfall_positive_receipts_deferred_ecu',-1.))
            return (all((a[k]-b[k])*direction>=-1e-8 for k,direction in cols)
                    and any((a[k]-b[k])*direction>1e-8 for k,direction in cols))
        front=[v for v in valid if not any(dominates(w,v) for w in valid if w is not v)]
        front.sort(key=lambda v:(-v['conditional_terminal_mapped_proxy_delta'],
                                 -v['five_year_partial_net_after_card_cost_ecu'],
                                 v['hypothetical_peak_zero_opening_cash_shortfall_positive_receipts_deferred_ecu'],
                                 v['candidate_id']))
        temporal_front_by_path.append({'path_id':path,'evaluated_with_mapped_index':len(valid),
                                       'nondominated_in_sample':len(front),
                                       'nondominated_candidate_ids':[v['candidate_id'] for v in front],
                                       'not_game_or_global_pareto':True})
    return {'schema':SCHEMA,'status':'CONDITIONAL_PARTIAL_CASH_TIMING_NOT_GAME_SOLVENCY',
            'source_class':tax_report['source_class'],'start_year':start_year,
            'path_summaries':by_path,'evaluated_combinations':len(combos),'combinations':combos,
            'sampled_three_axis_timing_front_by_path':temporal_front_by_path,
            'immediate_profile':'POSITIVE_AND_NEGATIVE_DELTAS_RECOGNIZED_IN_SAME_YEAR_AS_CARD_SPEND_HYPOTHESIS',
            'delayed_profile':'POSITIVE_INDIVIDUAL_TAX_AND_FEE_DELTAS_ONE_YEAR_LATE_EXPENSE_DELTAS_SAME_YEAR_HYPOTHESIS',
            'zero_opening_balance_assumption':'FOR_ARITHMETIC_ONLY_NOT_ACTUAL_CITY_TREASURY',
            'prior_period_delayed_receipts_for_rolling_start':'UNKNOWN_UNLESS_START_YEAR_1',
            'missing_cash_components':['baseline treasury','other taxes and fees','other operating expenses',
                                       'reserves','grants','loan principal and interest',
                                       'firm/population dynamics','server settlement timing'],
            'known_exogenous_future_bases_are_hypotheses':True,
            'true_cash_availability_or_financing_proven':False,'gameplay_gate':'STOP'}
