#!/usr/bin/env python3
"""R189: opt-in post-search year reassignment, R162 original scorers/auditors.

No account, network or game action. No change to source search.
Only rearranges projects ALREADY chosen by a candidate plan; does not silently
add/drop projects or equate a score with an EcoSim server result.
"""
from __future__ import annotations
from itertools import combinations
from math import isfinite

SCHEMA='ECOSIM_R189_BOUNDED_SHADOW_V1'

class Hold(ValueError):
    pass


def _shape(starts, idx, active, fixed, start_year, budget, cap, prior_bonus):
    if type(start_year) is not int or not 1<=start_year<=5:raise Hold('INVALID_START_YEAR')
    n=6-start_year
    if not isinstance(idx,dict) or len(idx)!=35 or set(idx)!=set(range(1,36)):
        raise Hold('FULL_35_CARD_SOURCE_REQUIRED')
    if type(cap) is not int or not 0<=cap<=20 or type(prior_bonus) is not bool:
        raise Hold('EXPLICIT_CAP_AND_PREVIOUS_PROJECT1_FLAG_REQUIRED')
    if (not isinstance(budget,(list,tuple)) or len(budget)!=n or
        any(type(b) not in (int,float) or not isfinite(b) or b<0 for b in budget)):
        raise Hold('EXPLICIT_COMPLETE_HYPOTHETICAL_ENVELOPES_REQUIRED')
    if not isinstance(starts,(list,tuple)) or len(starts)!=n:raise Hold('BAD_PLAN_HORIZON')
    if not isinstance(active,(list,tuple,set,frozenset)) or not isinstance(fixed,(list,tuple,set,frozenset)):
        raise Hold('EXPLICIT_ACTIVE_AND_FIXED_SETS_REQUIRED')
    active,fixed=set(active),set(fixed)
    if active&fixed or not active<=idx.keys() or not fixed<=idx.keys():raise Hold('OVERLAPPING_OR_UNKNOWN_PROJECTS')
    seen=set()
    for row in starts:
        if not isinstance(row,(list,tuple)) or any(type(i) is not int or i not in idx or i in active or i in seen for i in row):
            raise Hold('BAD_PROJECT_SELECTION')
        if len(row)!=len(set(row)):raise Hold('DUPLICATE_PROJECT_IN_YEAR')
        seen.update(row)
    if not fixed<=set(starts[0]):raise Hold('FIXED_FIRST_YEAR_NOT_PRESERVED')
    return active,fixed


def improve(starts, idx, *, initial_active, fixed_first_ids, start_year,
            annual_budgets, base_project_cap, previous_project1_active,
            score_fn, audit_fn, max_evaluations=1000, max_passes=3):
    """Return bounded model improvement, or HOLD. No exact oracle.

    score_fn(starts) is ORIGINAL R162 objective (scenario_min or nominal).
    audit_fn(starts) is ORIGINAL R160 audit and must report zero errors AND zero
    conditional items. Strictly improving score only; tie -> preserve seed.
    """
    if type(max_evaluations) is not int or not 1<=max_evaluations<=5000:raise Hold('INVALID_BUDGET')
    if type(max_passes) is not int or not 1<=max_passes<=6:raise Hold('INVALID_PASSES')
    active,fixed=_shape(starts,idx,initial_active,fixed_first_ids,start_year,annual_budgets,base_project_cap,previous_project1_active)
    if not callable(score_fn) or not callable(audit_fn):raise Hold('ORIGINAL_SCORER_AND_AUDITOR_REQUIRED')
    def canonical(rows):return tuple(tuple(sorted(row)) for row in rows)
    current=canonical(starts)
    def audit(rows):
        d=audit_fn([list(x) for x in rows]);
        if not isinstance(d,dict) or d.get('schema')!='ECOSIM_R160_INDEPENDENT_PLAN_AUDIT_V1':raise Hold('R160_AUDIT_CONTRACT_MISMATCH')
        return d
    base_audit=audit(current)
    if base_audit.get('hard_rule_violations') or base_audit.get('conditional_eligibility_items') or base_audit.get('status')!='PASS_DISPLAY_RULES_ONLY_NOT_SERVER_APPROVAL':
        raise Hold('BASELINE_NOT_UNCONDITIONALLY_VALID_BY_R160')
    value=float(score_fn([list(x) for x in current]));
    if not isfinite(value):raise Hold('NONFINITE_ORIGINAL_SCORE')
    start_value=value
    trials=0;scored=0;feasible=0;passes=0;improvements=[];terminated='LOCAL_STATIONARY_WITHIN_SAMPLED_NEIGHBORHOOD'
    seen={current}
    for _ in range(max_passes):
        if trials>=max_evaluations:terminated='EVALUATION_CAP';break
        assignment={pid:y for y,ids in enumerate(current) for pid in ids}
        movable=tuple(sorted(i for i in assignment if i not in fixed))
        best=None; best_value=value
        # Always cover all feasible radius-1 shifts before the radius-2 scan.
        for radius in (1,2):
            if radius>len(movable):break
            stop=False
            for indices in combinations(movable,radius):
                if stop:break
                from itertools import product
                for years in product(range(len(current)),repeat=radius):
                    if all(assignment[i]==y for i,y in zip(indices,years)):continue
                    if trials>=max_evaluations:stop=True;break
                    candidate=[list(x) for x in current]
                    for i,y in zip(indices,years):
                        if i in candidate[assignment[i]]:candidate[assignment[i]].remove(i)
                        candidate[y].append(i)
                    c=canonical(candidate)
                    if c==current or c in seen:continue
                    seen.add(c);trials+=1
                    chk=audit(c)
                    if chk.get('hard_rule_violations') or chk.get('conditional_eligibility_items') or chk.get('status')!='PASS_DISPLAY_RULES_ONLY_NOT_SERVER_APPROVAL':continue
                    feasible+=1
                    new_value=float(score_fn([list(x) for x in c]));scored+=1
                    if not isfinite(new_value):raise Hold('NONFINITE_CANDIDATE_SCORE')
                    if new_value>best_value+1e-10:
                        best,best_value=c,new_value
            if stop:break
        if best is None:
            if trials>=max_evaluations:terminated='EVALUATION_CAP'
            break
        improvements.append({'before':round(value,9),'after':round(best_value,9),'first_year_before':list(current[0]),'first_year_after':list(best[0])})
        current=best;value=best_value;passes+=1
        if trials>=max_evaluations:terminated='EVALUATION_CAP';break
    final_audit=audit(current)
    replay=float(score_fn([list(x) for x in current]))
    if (final_audit.get('hard_rule_violations') or final_audit.get('conditional_eligibility_items') or
        final_audit.get('status')!='PASS_DISPLAY_RULES_ONLY_NOT_SERVER_APPROVAL' or
        abs(replay-value)>1e-9 or replay<start_value-1e-10):
        raise Hold('FINAL_INDEPENDENT_REPLAY_FAILED')
    return {'schema':SCHEMA,'status':'PASS_CONDITIONAL_MODEL_SHADOW_ONLY',
            'source_search_modified':False,'project_set_preserved':True,
            'initial_score':round(start_value,9),'final_score':round(replay,9),
            'strictly_improved':replay>start_value+1e-10,
            'initial_first_year_ids':list(sorted(starts[0])),
            'final_first_year_ids':list(current[0]),
            'years':[list(x) for x in current],
            'evaluated_candidates':trials,'feasible_candidates':feasible,
            'scored_candidates':scored,'passes':passes,'improvements':improvements,
            'termination':terminated,
            'independent_replay':{'status':final_audit['status'], 'hard_violations':0,'conditional_items':0},
            'certifies_35_card_global_optimum':False,
            'certifies_live_game_score':False,'hypothetical_budget_not_authorized_cash':True,
            'gameplay_gate':'STOP'}
