#!/usr/bin/env python3
"""R144 known-formula bridge: factor identity, signed project rows, cash scenarios.

This is a bounded COUNTERFACTUAL accounting layer, not an EcoSim state-transition
emulator. Explicit unknown fields are preferable to fabricated future facts.
No network, browser, account or game writes.
"""
from __future__ import annotations
from json_integrity_r162 import read_json
from pathlib import Path
import json
import math
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/'tools'))
from r142_proxy_reference import COEFF, WEIGHTS, proxy_value
from portfolio_5y import project_index
from effect_replay_r147 import replay_effects


def finite(v):
    return type(v) in (int, float) and math.isfinite(v)


def computed_index_from_factors(factors, weights=None):
    """Visible *aggregation* only, using published six weights and factor display values.

    Government contains the documented extra debt/wealth quarter, while Mobility
    and People use minus a quarter of the inverse factor. This is a replayer of
    an existing factor snapshot, NOT a model of how those factors change.
    """
    if not isinstance(factors,dict) or not set(COEFF).issubset(factors):
        raise ValueError('All 28 directly used displayed factor keys are mandatory')
    if any(not finite(factors[k]) for k in COEFF):
        raise ValueError('Non-finite displayed factor')
    if weights is None:
        weights={name:params[0] for name,params in WEIGHTS.items()}
        weight_source='R141_TEST_UI_SIX_WEIGHTS_NOT_LIVE_CONFIG'
    else:
        if set(weights)!=set(WEIGHTS) or any(not finite(x) or x<0 for x in weights.values()) or abs(sum(weights.values())-1)>1e-9:
            raise ValueError('Six finite nonnegative weights adding to one required')
        weight_source='EXPLICIT_PROVIDED_WEIGHTS_NOT_INDEPENDENTLY_VERIFIED'
    b={}
    for name,(default,pos,neg,den) in WEIGHTS.items():
        if name=='Kormányzás':
            raw=sum(factors[k] for k in pos)/3 + factors['Adósság / vagyon']/4
        elif name=='Életkörülmények':
            raw=(sum(factors[k] for k in pos)+100-factors['Rossz szoc. helyzetben lévők aránya'])/8
        elif name in ('Mobilitás','Emberek'):
            raw=sum(factors[k] for k in pos)/3 - factors[neg[0]]/4
        else:
            raw=sum(factors[k] for k in pos)/den
        b[name]={'index':round(raw,9),'weight':weights[name],
                 'weighted_component':round(raw*weights[name],9)}
    total=sum(v['weighted_component'] for v in b.values())
    return {'partial_indexes':b,'total_index_from_displayed_factors':round(total,9),
            'known_display_rounding_uncertainty':True,'weight_source':weight_source,
            'calculates_future_factor_changes':False}


def _project_effects_for_year(idx, starts, baseline, upto_index):
    """One-time lifetime project effect scenario (not repeated every year)."""
    factors=dict(baseline)
    pairs=[(i,row) for ids in starts[:upto_index+1] for i in ids for row in idx[i]['effects']]
    records=replay_effects(factors,pairs,COEFF)
    used=[r for r in records if r['mapped'] and not r.get('uncertain_due_to_saturation')]
    unmapped=[r for r in records if not r['mapped'] or r.get('uncertain_due_to_saturation')]
    return factors,used,unmapped


def conservative_cash_and_client_line(idx, previously_active, new_ids):
    """Client known project expense line and independent safe funding demand.

    Known client branch for non-repeatable cards: startup+investment for newly
    started T(t), plus SIGNED runCost for all active Q(t). Suppresses support from
    cost and reports support as a distinct, NOT VERIFIED income label.
    """
    active=set(previously_active)|set(new_ids)
    startup=sum(idx[i]['startup_cost']+idx[i]['investment'] for i in new_ids)
    signed=sum(idx[i]['maintenance_cost'] for i in active)
    positive=sum(max(0,idx[i]['maintenance_cost']) for i in active)
    support=sum(idx[i]['partner_support'] for i in new_ids)
    return dict(client_project_expense_line_ecu=startup+signed,
                conservative_project_cash_requirement_ecu=startup+positive,
                initial_investment_start_cost_ecu=startup,
                signed_annual_run_cost_ecu=signed,
                positive_only_run_cost_ecu=positive,
                newly_started_support_label_ecu=support,
                recognized_support_cash_ecu=None,
                settlement_and_credit_validated=False)


def validate_finance_scenario(scenario, n):
    """A deliberate independent scenario, never an actual verified future cash flow."""
    if scenario is None:return None
    if not isinstance(scenario,dict) or scenario.get('mode')!='EXPLICIT_HYPOTHETICAL_NONPROJECT_NET_ONLY':
        raise ValueError('Finance scenario must explicitly declare hypothetical mode')
    opening=scenario.get('initial_uncommitted_cash_ecu')
    flows=scenario.get('annual_nonproject_net_cash_ecu')
    if not finite(opening) or opening<0 or not isinstance(flows,list) or len(flows)!=n or any(not finite(v) for v in flows):
        raise ValueError('Finite initial cash and exactly one nonproject net flow per remaining year required')
    if not isinstance(scenario.get('assumption_note'),str) or not scenario['assumption_note'].strip():
        raise ValueError('Human-readable finance scenario provenance/assumption_note required')
    loan=scenario.get('illustrative_long_loan')
    if loan is not None:
        if not isinstance(loan,dict):raise ValueError('Long-loan scenario object required')
        changes=loan.get('annual_decision_change_ecu')
        rates=loan.get('annual_interest_rate')
        opening_loan=loan.get('opening_balance_ecu')
        if (not finite(opening_loan) or opening_loan<0 or
            not isinstance(changes,list) or len(changes)!=n or any(not finite(v) for v in changes) or
            not isinstance(rates,list) or len(rates)!=n or any(not finite(v) or v<0 for v in rates)):
            raise ValueError('Scenario long loan needs opening, changes and rates for all remaining years')
        if scenario.get('nonproject_flow_excludes_this_loan') is not True:
            raise ValueError('Loan scenario needs explicit nonproject-flow non-overlap declaration')
    return scenario


def attach_city_bridge(plan, initial_active, baseline, idx=None, state=None, start_year=1):
    """Add a single connected yearly factor/accounting view to an R143 searched plan.

    Finance bridge is client expense component ONLY unless an explicitly provided
    hypothetical exogenous path is present; no projected market dynamics are inferred.
    """
    idx=idx or project_index();state=state or {}
    starts=[x['start_project_ids'] for x in plan['start_by_year']]
    n=len(starts)
    future=validate_finance_scenario(state.get('finance_counterfactual'),n)
    market=state.get('market') or {}
    weights=market.get('smartcity_total_weights')
    initial_index=computed_index_from_factors(baseline,weights)
    previous=set(initial_active)
    cash=(float(future['initial_uncommitted_cash_ecu']) if future else None)
    long_loan=future.get('illustrative_long_loan') if future else None
    prev_long_loan_balance=(float(long_loan['opening_balance_ecu']) if long_loan else None)
    years=[]
    for offset, ids in enumerate(starts):
        y=start_year+offset
        project_rows=conservative_cash_and_client_line(idx,previous,ids)
        factors,used,unmapped=_project_effects_for_year(idx,starts,baseline,offset)
        index=computed_index_from_factors(factors,weights)
        index['mapped_project_only_delta_vs_current_factor_baseline']=round(index['total_index_from_displayed_factors']-initial_index['total_index_from_displayed_factors'],9)
        net=None
        if future:
            net=float(future['annual_nonproject_net_cash_ecu'][offset])
            opening_cash=cash
            # This is a no-loan, no-grant, no-project-driven-exogenous-feedback
            # SCENARIO ONLY. Do not call the result a forecast/reserve.
            loan_events=None
            loan_cash_delta=0.0
            if long_loan:
                decision=float(long_loan['annual_decision_change_ecu'][offset])
                interest_rate=float(long_loan['annual_interest_rate'][offset])
                borrow=max(decision,0)
                repay=min(max(-decision,0),prev_long_loan_balance)
                loan_close=prev_long_loan_balance+borrow-repay
                interest=loan_close*interest_rate
                loan_cash_delta=borrow-repay-interest
                loan_events={'status':'CLIENT_LONG_LOAN_COMPONENT_ONLY_NOT_AUTHORIZED',
                             'opening_balance_ecu':round(prev_long_loan_balance,2),
                             'requested_decision_change_ecu':round(decision,2),
                             'borrow_component_ecu':round(borrow,2),
                             'repay_clamped_to_opening_ecu':round(repay,2),
                             'closing_balance_ecu':round(loan_close,2),
                             'interest_at_explicit_scenario_rate_ecu':round(interest,2),
                             'loan_limit_and_credit_eligibility':'UNKNOWN'}
                prev_long_loan_balance=loan_close
            cash=cash+net-project_rows['conservative_project_cash_requirement_ecu']+loan_cash_delta
            finance={'status':('HYPOTHETICAL_UNAPPROVED_LONG_LOAN_COMPONENT' if long_loan else 'HYPOTHETICAL_NO_NEW_BORROWING_ONLY'),
                     'illustrative_long_loan':loan_events,
                     'opening_scenario_cash_ecu':round(opening_cash,2),
                     'assumed_nonproject_net_flow_ecu':round(net,2),
                     'closing_scenario_cash_ecu':round(cash,2),
                     'hypothetical_deficit_ecu':round(max(0,-cash),2),
                     'does_not_establish_loan_approval':True}
        else:
            finance={'status':'UNKNOWN_NO_AUTHORIZED_FUTURE_NONPROJECT_CASHFLOW',
                     'closing_scenario_cash_ecu':None,'hypothetical_deficit_ecu':None}
        years.append({'year':y,'new_starts':list(ids),'new_and_ongoing_projects':sorted(previous|set(ids)),
                      'client_component':project_rows,'mapped_factor_aggregation':index,
                      'mapped_effects_used_count':len(used),
                      'unmapped_effects':unmapped,
                      'financial_counterfactual':finance,
                      'full_city_model_status':'UNKNOWN_OTHER_POLICY_AND_COMPETITOR_TRANSITIONS'})
        previous.update(ids)
    return {'bridge_version':'R144_CLIENT_KNOWN_FORMULA_COMPONENTS_V1',
            'source_basis':['R139/R142A static client project cost+support components',
                            'R141 six weight and factor UI snapshot','R140B manual relative effect rule'],
            'baseline_aggregation':initial_index,
            'years':years,
            'financial_scenario_supplied':bool(future),
            'financial_scenario_note':future['assumption_note'] if future else None,
            'actual_five_year_index_prediction':None,
            'actual_cashflow_loan_and_grant_settlement':None,
            'unmodeled_decision_categories':['taxes','service_fees','institution_capacities','staffing_and_payroll','transport_service',
                                             'long_and_short_term_loans','market_population_company_migration',
                                             'repeated_delayed_projects','unmapped_or_indirect_factor_effects'],
            'gameplay_decision':'STOP'}


def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--strategy',required=True)
    p.add_argument('--state',default=str(ROOT/'inputs/official_state.template.json'))
    p.add_argument('--out',required=True);a=p.parse_args()
    strategy=read_json(a.strategy);state=read_json(a.state)
    if not strategy.get('top_plans'):raise ValueError('No strategy plans')
    from strategy_5y import derive_config
    idx=project_index();config=derive_config(state,idx,strategy['start_year'],None,None)
    result=attach_city_bridge(strategy['top_plans'][0],config['initial_active'],config['baseline'],idx,state,strategy['start_year'])
    dst=Path(a.out);dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print('CITY_BRIDGE_OFFLINE_COMPONENTS=PASS gameplay=STOP')

if __name__=='__main__':main()
