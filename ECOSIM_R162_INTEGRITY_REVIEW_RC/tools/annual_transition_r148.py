#!/usr/bin/env python3
"""R148 bounded annual state bridge, reusing the R147 engine.

Only project effects/client-accounting primitives are source anchored. Policy
factor multipliers, nonproject cash, loan decisions and persistence are explicit
hypotheses. There is no EcoSim server simulation or validated causal forecast.
"""
from __future__ import annotations
import math
from city_bridge import computed_index_from_factors, conservative_cash_and_client_line
from effect_replay_r147 import BOUNDS, normalize_metric
from r142_proxy_reference import COEFF


def finite(v):return type(v) in (int,float) and math.isfinite(v)


def factor_multiplier_map(pairs, *, scale=1.0):
    """Group only mapped source-project multipliers, before the single clamp."""
    if not finite(scale) or scale<0:raise ValueError('finite nonnegative scenario intensity')
    multipliers={k:1.0 for k in COEFF}
    missing=[]; applied=[]
    for project_id,e in pairs:
        name=e['metric']; label=normalize_metric(name); pct=e['value_percent']
        if not finite(pct):raise ValueError('finite relative project effect required')
        if label not in COEFF:
            missing.append({'project_id':project_id,'effect_label':name,'reason':'INDIRECT_EFFECT_NOT_MAPPED'})
            continue
        m=1+scale*pct/100.0
        if m<=0:raise ValueError('nonpositive project multiplier')
        multipliers[label]*=m
        applied.append({'project_id':project_id,'effect_label':name,'mapped_factor':label,'multiplier':m})
    return multipliers,missing,applied


def _cap_interval(baseline,mult,lo,hi):
    """Conditional interval when a displayed input has hidden saturation.

    For an upper-clamped input and a product below one, the latent pre-clamp
    value may be anywhere above displayed max; resulting post-clamp belongs to
    [max(lo, hi*m), hi] if lo exists, otherwise [hi*m, hi].
    For a lower-clamped input and a product above one, it may be anywhere below
    the displayed min, hence post-clamp in [lo, min(hi,lo*m)].
    """
    raw=baseline*mult
    if hi is not None and math.isclose(baseline,hi,abs_tol=1e-8) and mult<1:
        low=hi*mult
        if lo is not None:low=max(lo,low)
        return (low,hi),'UPPER_SATURATED_LATENT_UNOBSERVED'
    if lo is not None and math.isclose(baseline,lo,abs_tol=1e-8) and mult>1:
        high=lo*mult
        if hi is not None:high=min(high,hi)
        return (lo,high),'LOWER_SATURATED_LATENT_UNOBSERVED'
    value=max(lo,raw) if lo is not None else raw
    value=min(hi,value) if hi is not None else value
    return (value,value),None


def combined_factor_replay(baseline, project_pairs=(), policy_multipliers=None, *,scale=1., weights=None):
    """Single clamp after combined project and explicit policy multipliers.

    Numeric values are CONDITIONALLY displayed-factor replay values. With
    latent saturated inputs, intervals are conditional on no other game drift;
    they are not validated uncertainty bands, and unmodeled effects have no bound.
    """
    if not isinstance(baseline,dict) or set(COEFF)-set(baseline):raise ValueError('All baseline factor keys required')
    if any(not finite(baseline[k]) for k in COEFF):raise ValueError('Nonfinite baseline')
    p,missing,applied=factor_multiplier_map(project_pairs,scale=scale)
    if policy_multipliers is None: policy_multipliers={k:1. for k in COEFF}
    if not isinstance(policy_multipliers,dict) or set(policy_multipliers)!=set(COEFF) or any(not finite(v) or v<=0 for v in policy_multipliers.values()):
        raise ValueError('Policy scenario requires complete positive finite factor multiplier map')
    factors={}; intervals={};ambiguous=[]
    for k in COEFF:
        m=p[k]*policy_multipliers[k]
        lo,hi=BOUNDS.get(k,(None,None))
        (low,high),warning=_cap_interval(float(baseline[k]),m,lo,hi)
        raw=baseline[k]*m
        value=max(raw,lo) if lo is not None else raw
        value=min(value,hi) if hi is not None else value
        factors[k]=value
        intervals[k]=[round(low,10),round(high,10)]
        if warning:ambiguous.append({'factor':k,'reason':warning,'conditional_range':[low,high]})
    # The displayed-index aggregation is linear in the 28 factor values.
    nominal=computed_index_from_factors(factors,weights)['total_index_from_displayed_factors']
    base_index=computed_index_from_factors(baseline,weights)['total_index_from_displayed_factors']
    lower=dict(factors);upper=dict(factors)
    for k,(lo,hi) in intervals.items():
        if COEFF[k]>=0:lower[k],upper[k]=lo,hi
        else:lower[k],upper[k]=hi,lo
    return {'factors_conditional':factors,
            'baseline_mapped_index':base_index,
            'mapped_conditional_index':nominal,
            'mapped_index_if_only_saturation_uncertain':[
                computed_index_from_factors(lower,weights)['total_index_from_displayed_factors'],
                computed_index_from_factors(upper,weights)['total_index_from_displayed_factors']],
            'ambiguous_saturated_factors':ambiguous,
            'unmapped_project_effects':missing,
            'direct_effects_used':len(applied),
            'policy_multipliers_are_user_supplied_hypotheses':True,
            'partial_score_is_full_city_or_server_forecast':False,
            'total_score_uncertainty_is_bounded':False}


def long_loan_component(opening_balance,decision_change,interest_rate):
    """Source 840: opening + max(change,0) + clamp(change,-opening,0),
    then interest = closing * client period rate. No authorization claim.
    """
    if not all(finite(x) for x in [opening_balance,decision_change,interest_rate]) or opening_balance<0 or interest_rate<0:
        raise ValueError('Invalid loan component')
    borrow=max(decision_change,0)
    repayment=min(max(-decision_change,0),opening_balance)
    end=opening_balance+borrow-repayment
    return {'opening_ecu':opening_balance,'borrow_ecu':borrow,'repaid_ecu':repayment,
            'closing_ecu':end,'interest_ecu':end*interest_rate,
            'net_cash_component_ecu':borrow-repayment-end*interest_rate,
            'loan_permission_and_maximum':'UNKNOWN_NOT_IN_COMPONENT'}


def short_loan_prior_service(prior_short_borrow,prior_short_rate):
    """Source 840: next-year short repayment and interest on previous borrow."""
    if not all(finite(x) for x in [prior_short_borrow,prior_short_rate]) or prior_short_borrow<0 or prior_short_rate<0:
        raise ValueError('Invalid prior short borrowing or rate')
    return {'next_year_repayment_ecu':prior_short_borrow,'next_year_interest_ecu':prior_short_borrow*prior_short_rate,
            'short_loan_limit_and_credit_approval':'UNKNOWN'}


def annual_component_rollout(idx, initial_active, starts, baseline, *, start_year=1,
                             policy_multiplier_by_year=None, loan_scenario=None, short_loan_scenario=None,
                             nonproject_finance_scenario=None, weights=None):
    """One shared year-carrying ledger for search output and scenario comparison.

    Inputs are not treated as authoritative. No hidden policy effects are
    assumed zero. Cash remains null unless complete *explicit* hypothetical
    nonproject net flow and opening funds are given. Loan decisions are also
    hypothetical, not bank approval.
    """
    active=set(initial_active); seen_starts=set(); years=[]
    if not isinstance(starts,list) or not 1<=start_year<=5 or len(starts)!=6-start_year:
        raise ValueError('One start list for every remaining year required')
    cash=None; opening_cash=None
    if nonproject_finance_scenario is not None:
        sc=nonproject_finance_scenario
        if sc.get('mode')!='EXPLICIT_HYPOTHETICAL_NONPROJECT_NET_ONLY' or not sc.get('nonproject_flow_excludes_policy_track',False):
            raise ValueError('Explicit hypothetical nonproject flow and non-overlap declaration required')
        flows=sc.get('annual_nonproject_net_cash_ecu');opening_cash=sc.get('initial_uncommitted_cash_ecu')
        if not finite(opening_cash) or opening_cash<0 or not isinstance(flows,list) or len(flows)!=len(starts) or any(not finite(v) for v in flows):
            raise ValueError('Incomplete nonproject finance scenario')
        cash=float(opening_cash)
    if loan_scenario is not None:
        if cash is None or not nonproject_finance_scenario.get('nonproject_flow_excludes_this_loan'):
            raise ValueError('Loan scenario needs explicit nonoverlap with nonproject flow')
        s=loan_scenario
        if not isinstance(s.get('changes'),list) or len(s['changes'])!=len(starts) or not isinstance(s.get('rates'),list) or len(s['rates'])!=len(starts) or not finite(s.get('opening_balance')) or s['opening_balance']<0:
            raise ValueError('Incomplete hypothetical loan path')
        balance=float(s['opening_balance'])
    if short_loan_scenario is not None:
        if cash is None or not nonproject_finance_scenario.get('nonproject_flow_excludes_short_loan_component'):
            raise ValueError('Short-loan scenario needs explicit nonoverlap with nonproject cash')
        ss=short_loan_scenario
        rates=ss.get('annual_interest_rates');borrowings=ss.get('annual_new_borrow_assumptions')
        if (not finite(ss.get('prior_borrow_ecu')) or ss['prior_borrow_ecu']<0 or
            not finite(ss.get('prior_rate')) or ss['prior_rate']<0 or
            not isinstance(rates,list) or len(rates)!=len(starts) or any(not finite(x) or x<0 for x in rates) or
            not isinstance(borrowings,list) or len(borrowings)!=len(starts) or any(not finite(x) or x<0 for x in borrowings)):
            raise ValueError('Explicit nonnegative short-borrow and interest scenario for every year required')
        prev_borrow=float(ss['prior_borrow_ecu']);prev_rate=float(ss['prior_rate'])
    for offset,ids in enumerate(starts):
        year=start_year+offset
        if any(type(i) is not int or i not in idx or i in seen_starts or i in active for i in ids) or len(ids)!=len(set(ids)):
            raise ValueError('Invalid or duplicate yearly new project IDs')
        new=set(ids);active.update(new);seen_starts.update(new)
        pairs=[(i,e) for i in sorted(seen_starts) for e in idx[i]['effects']]
        policy=policy_multiplier_by_year[offset] if policy_multiplier_by_year else None
        replay=combined_factor_replay(baseline,pairs,policy,weights=weights)
        index=computed_index_from_factors(replay['factors_conditional'],weights)
        cost=conservative_cash_and_client_line(idx,active-new,new)
        loan=None
        if loan_scenario is not None:
            loan=long_loan_component(balance,loan_scenario['changes'][offset],loan_scenario['rates'][offset]);balance=loan['closing_ecu']
        short=None
        if short_loan_scenario is not None:
            short=short_loan_prior_service(prev_borrow,prev_rate)
            short['illustrative_new_short_borrow_ecu']=short_loan_scenario['annual_new_borrow_assumptions'][offset]
            short['source']='SOURCE_PRIOR_SHORT_SERVICE_PLUS_HYPOTHETICAL_NEW_BORROW'
            prev_borrow=short['illustrative_new_short_borrow_ecu']
            prev_rate=short_loan_scenario['annual_interest_rates'][offset]
        fin={'source':'EXPLICIT_HYPOTHETICAL_COMPONENT_LEDGER_NOT_ECOSIM_CASHFLOW',
             'project_client_expense_line_ecu':cost['client_project_expense_line_ecu'],
             'conservative_project_funding_need_ecu':cost['conservative_project_cash_requirement_ecu'],
             'support_separate_label_ecu':cost['newly_started_support_label_ecu'],
             'support_guaranteed_cash_ecu':None,
             'loan':loan,'short_loan':short,'project_budget_approval':False,
             'actual_cashflow_ecu':None}
        if cash is not None:
            old=cash;cash+=flows[offset]-cost['conservative_project_cash_requirement_ecu']+(loan['net_cash_component_ecu'] if loan else 0)
            if short:
                cash+=short['illustrative_new_short_borrow_ecu']-short['next_year_repayment_ecu']-short['next_year_interest_ecu']
            fin.update(hypothetical_opening_cash_ecu=old,hypothetical_nonproject_net_ecu=flows[offset],
                       hypothetical_closing_cash_ecu=round(cash,8),hypothetical_shortfall_ecu=round(max(0,-cash),8))
        else:fin.update(hypothetical_closing_cash_ecu=None,hypothetical_shortfall_ecu=None)
        years.append({'year':year,'new_project_ids':sorted(new),'active_project_ids':sorted(active),
                      'factor_replay':replay,'index_snapshot_aggregation':index,
                      'finance_components':fin,'actual_annual_city_state_transition':None,
                      'unobserved_city_drift_and_competitors':'UNKNOWN'})
    return {'schema':'ECOSIM_R148_PARTIAL_ANNUAL_LEDGER_V1',
            'yearly_state_records':years,
            'cash_projection_if_no_explicit_nonproject_scenario':None if cash is None else round(cash,8),
            'actual_terminal_game_score':None,
            'gameplay_action':'STOP'}
