#!/usr/bin/env python3
"""R160 independent offline replay of project constraints and cash needs.

Independently checks candidate search outputs against the saved R94 card catalog,
without calling the search implementation. No server legality, live cash or
realized outcome can be inferred.  Unknown eligibility is never promoted to PASS.
"""
from __future__ import annotations
import math
from collections import Counter

SCHEMA='ECOSIM_R160_INDEPENDENT_PLAN_AUDIT_V1'


def valid_money(v):
    return type(v) in (int,float) and math.isfinite(v) and v>=0


def _ids(seq, known, field):
    if not isinstance(seq,(list,tuple)) or any(type(i) is not int or i not in known for i in seq):
        raise ValueError(field+': unknown/noninteger project ID')
    if len(seq)!=len(set(seq)):
        raise ValueError(field+': duplicate project ID')
    return set(seq)


def _conditions(project, names, previous, current):
    """Display labels, NOT server condition expressions."""
    evidence=[]; errors=[]; unknown=[]
    for raw in project.get('project_conditions',[]):
        if not isinstance(raw,str) or not raw.strip():
            unknown.append('BAD_DISPLAY_CONDITION')
            continue
        label=raw.split(' — ',1)[0].strip()
        negative=label.startswith('not ')
        if negative: label=label[4:].strip()
        pid=names.get(label)
        if pid is None:
            unknown.append('UNMAPPED_DISPLAY_CONDITION_'+str(raw))
            continue
        if negative:
            if pid in previous or pid in current:errors.append('NEGATIVE_CONDITION_CONFLICT_'+str(pid))
            else:evidence.append('NEGATIVE_DISPLAY_CONDITION_CONSISTENT_'+str(pid))
        elif pid in previous:
            evidence.append('PRIOR_RUNNING_DISPLAY_CONDITION_'+str(pid))
        elif pid in current:
            unknown.append('SAME_YEAR_FUT_CONDITION_SERVER_ORDER_UNKNOWN_'+str(pid))
        else:
            errors.append('UNMET_DISPLAY_CONDITION_'+str(pid))
    return evidence,errors,unknown


def audit_plan(idx, *, start_year, active_ids, fixed_first_ids, previous_project1_active,
               base_project_cap, annual_budgets, starts, advertised_costs=None,
               advertised_total=None, allow_same_year=True):
    """Independent replay. Raises on malformed data; records plan violations.

    annual_budgets are hypothetical or user-declared; this audit never certifies
    them as spendable. previous_project1_active=None yields uncertainty in Y1.
    """
    if type(start_year) is not int or not 1<=start_year<=5:
        raise ValueError('Invalid initial year')
    if type(base_project_cap) is not int or not 0<=base_project_cap<=20:
        raise ValueError('Missing or invalid cap')
    if previous_project1_active is not None and type(previous_project1_active) is not bool:
        raise ValueError('Prior project1 must be bool or unknown')
    if not isinstance(idx,dict) or not idx or any(type(i) is not int or not isinstance(p,dict) for i,p in idx.items()):
        raise ValueError('Invalid catalog')
    names={};known=set(idx)
    for pid,p in idx.items():
        n=p.get('name')
        if not isinstance(n,str) or not n.strip() or n in names:
            raise ValueError('Nonunique catalog name')
        names[n]=pid
        for k in ('startup_cost','investment','maintenance_cost'):
            v=p.get(k)
            if type(v) not in (int,float) or not math.isfinite(v):
                raise ValueError('Invalid source card money')
    active=_ids(active_ids,known,'active')
    fixed=_ids(fixed_first_ids,known,'fixed current year')
    if active&fixed:raise ValueError('Overlapping initial active and fixed new starts')
    horizon=6-start_year
    if not isinstance(starts,(list,tuple)) or len(starts)!=horizon:
        raise ValueError('Wrong horizon')
    if annual_budgets is not None and (not isinstance(annual_budgets,(list,tuple)) or len(annual_budgets)!=horizon or not all(valid_money(v) for v in annual_budgets)):
        raise ValueError('Invalid hypothetical budget horizon')
    if advertised_costs is not None and (not isinstance(advertised_costs,(list,tuple)) or len(advertised_costs)!=horizon or not all(valid_money(v) for v in advertised_costs)):
        raise ValueError('Invalid advertised costs')
    if advertised_total is not None and not valid_money(advertised_total):
        raise ValueError('Invalid advertised total')
    issued=set();prev=set(active);rows=[];failures=[];unknowns=[];warnings=[]
    for offset,ids in enumerate(starts):
        y=start_year+offset
        new=_ids(ids,known,'year '+str(y))
        errors=[];unknown=[]
        if prev&new:errors.append('RESTART_OR_INITIAL_ACTIVE_ALREADY_RUNNING')
        if issued&new:errors.append('DUPLICATE_STARTED_PRIOR_YEAR')
        if offset==0 and not fixed<=new:
            errors.append('ALREADY_SELECTED_PROJECT_MISSING_FROM_FIRST_YEAR')
        if offset==0:
            if previous_project1_active is None:
                allowed_min=base_project_cap
                allowed_max=base_project_cap+1
                unknown.append('PREVIOUS_PERIOD_PROJECT1_BONUS_UNKNOWN')
            else:
                allowed_min=allowed_max=base_project_cap+int(previous_project1_active)
        else:
            allowed_min=allowed_max=base_project_cap+int(1 in prev)
        if len(new)>allowed_max:errors.append('PROJECT_CAP_EXCEEDED')
        elif len(new)>allowed_min:unknown.append('PROJECT_CAP_REQUIRES_UNVERIFIED_BONUS')
        for pid in sorted(new):
            _,e,u=_conditions(idx[pid],names,prev,new)
            errors.extend(str(pid)+':'+x for x in e)
            unknown.extend(str(pid)+':'+x for x in u)
            if not allow_same_year and any(x.startswith('SAME_YEAR_FUT') for x in u):
                errors.append(str(pid)+':SAME_YEAR_DEPENDENCY_FORBIDDEN_BY_ASSUMPTION')
        current=prev|new
        starts_expense=sum(idx[i]['startup_cost']+idx[i]['investment'] for i in new)
        maintenance_positive=sum(max(0,idx[i]['maintenance_cost']) for i in current)
        maintenance_signed=sum(idx[i]['maintenance_cost'] for i in current)
        cash=starts_expense+maintenance_positive
        if cash < 0 or not math.isfinite(cash):errors.append('COST_NUMERIC_INVALID')
        if advertised_costs is not None and abs(advertised_costs[offset]-cash)>max(1e-6,abs(cash)*1e-10):
            errors.append('SEARCH_REPORTED_COST_MISMATCH')
        if annual_budgets is not None and cash>annual_budgets[offset]+1e-7:
            errors.append('ILLUSTRATIVE_ENVELOPE_EXCEEDED')
        status='INVALID' if errors else ('CONDITIONAL' if unknown else 'PASS_PARTIAL_RULE_REPLAY')
        failures.extend({'year':y,'issue':x} for x in errors)
        unknowns.extend({'year':y,'issue':x} for x in unknown)
        rows.append({'year':y,'new_project_ids':sorted(new),'running_after_start_ids':sorted(current),
                     'counted_new_project_slots':len(new),'effective_cap_min':allowed_min,'effective_cap_max':allowed_max,
                     'startup_and_investment_ecu':round(starts_expense,8),
                     'positive_annual_maintenance_ecu':round(maintenance_positive,8),
                     'signed_annual_maintenance_ecu':round(maintenance_signed,8),
                     'independently_replayed_conservative_cash_need_ecu':round(cash,8),
                     'hypothetical_envelope_ecu':annual_budgets[offset] if annual_budgets is not None else None,
                     'client_card_cost_replay_status':status,'violations':errors,'unverified':unknown})
        issued|=new;prev=current
    total=sum(r['independently_replayed_conservative_cash_need_ecu'] for r in rows)
    if advertised_total is not None and abs(advertised_total-total)>max(1e-5,abs(total)*1e-10):
        failures.append({'year':None,'issue':'SEARCH_REPORTED_FIVE_YEAR_COST_MISMATCH'})
    if annual_budgets is None:warnings.append('NO_ANNUAL_FINANCING_ENVELOPE; NOT_A_CASH_APPROVAL')
    warnings.extend(['CLIENT_DISPLAY_CONDITIONS_NOT_SERVER_VERIFIED',
                     'FUTURE_PROJECT_CAP_AND_PROJECT1_BONUS_NOT_SERVER_VERIFIED',
                     'PROJECT_SUPPORT_SETTLEMENT_AND_ACTUAL_CASH_AVAILABILITY_UNKNOWN',
                     'UNKNOWN_ECONOMIC_EFFECTS_ARE_NOT_ZERO'])
    return {'schema':SCHEMA,'hard_rule_violations':failures,'conditional_eligibility_items':unknowns,
            'status':'FAIL_REPLAY' if failures else ('CONDITIONAL_NOT_SERVER_VERIFIED' if unknowns else 'PASS_DISPLAY_RULES_ONLY_NOT_SERVER_APPROVAL'),
            'years':rows,'replayed_card_cost_total_ecu':round(total,8),
            'budget_if_supplied_is_not_verified_spendable_cash':True,
            'actual_game_eligibility':None,'actual_funding_approval':None,'true_eco_sim_outcome':None,
            'warnings':warnings,'gameplay_gate':'STOP'}
