#!/usr/bin/env python3
"""R157: Bounded scenario-min project search using the SAME strategy_5y beam.

Ranges are illustrative sensitivity scenarios, NOT outcome bounds or probabilities.
No inference on population, businesses, server approval, or true cash budgets.
"""
from __future__ import annotations
from math import isfinite
from annual_transition_r148 import combined_factor_replay
from r142_proxy_reference import COEFF

# Fixed, explicitly synthetic sensitivity points; no empirical likelihood is assigned.
PROFILES = (
    {"id":"direct_100_persistent", "intensity":1.0,"retention":1.0},
    {"id":"direct_50_persistent", "intensity":0.5,"retention":1.0},
    {"id":"direct_100_retention_85", "intensity":1.0,"retention":0.85},
    {"id":"direct_50_retention_85", "intensity":0.5,"retention":0.85},
)


def replay(idx,starts,baseline,*,start_year=1,weights=None,policy_multipliers=None,profiles=PROFILES):
    """Score *conditional* terminal mapped effects for all declared profiles.

    Lower and upper values bound ONLY the hidden-clamp conditional within a
    profile. Unknown economic feedback has no finite supplied bound.
    """
    if type(start_year) is not int or not 1 <= start_year <= 5:raise ValueError('Invalid year')
    terminal=start_year+len(starts)-1
    if terminal>5 or terminal<start_year:raise ValueError('Invalid plan horizon')
    baseline_replay=combined_factor_replay(baseline,[],policy_multipliers,weights=weights)
    baseline_score=baseline_replay['mapped_conditional_index']
    rows=[];seen_profiles=set()
    for profile in profiles:
        if not (isinstance(profile,dict) and isinstance(profile.get('id'),str) and
                all(type(profile.get(k)) in (int,float) and isfinite(profile[k]) and 0<=profile[k]<=1 for k in ('intensity','retention'))):
            raise ValueError('Profile must have id and bounded finite intensity / retention')
        if profile['id'] in seen_profiles:raise ValueError('Duplicate stress profile')
        seen_profiles.add(profile['id'])
        pairs=[]
        for offset,ids in enumerate(starts):
            scale=profile['intensity']*profile['retention']**(terminal-(start_year+offset))
            for pid in ids:
                if pid not in idx:raise ValueError('Unknown project')
                for e in idx[pid]['effects']:
                    pairs.append((pid,{**e,'value_percent':e['value_percent']*scale}))
        r=combined_factor_replay(baseline,pairs,policy_multipliers,weights=weights)
        lo,hi=r['mapped_index_if_only_saturation_uncertain']
        rows.append({'profile_id':profile['id'],
                     'conditional_mapped_delta':round(r['mapped_conditional_index']-baseline_score,9),
                     'conditional_clamp_only_low_delta':round(lo-baseline_score,9),
                     'conditional_clamp_only_high_delta':round(hi-baseline_score,9),
                     'uncertain_saturated_factors':[a['factor'] for a in r['ambiguous_saturated_factors']],
                     'unmapped_effect_occurrences':len(r['unmapped_project_effects'])})
    return {'scenario_min_clamp_only_mapped_delta':min(x['conditional_clamp_only_low_delta'] for x in rows),
            'scenario_min_nominal_mapped_delta':min(x['conditional_mapped_delta'] for x in rows),
            'scenario_max_clamp_only_mapped_delta':max(x['conditional_clamp_only_high_delta'] for x in rows),
            'scenario_profiles':rows,
            'unmodeled_city_dynamics_uncertainty_bounded':False,
            'actual_five_year_score':None,
            'scenario_min_is_game_lower_bound':False,
            'scenario_probabilities_supplied':False,
            'gameplay_gate':'STOP'}


def sampled_first_action_regret(candidates):
    """Group by first action; compute *sampled* profile-min opportunity gap only.

    Across different assumed envelopes, candidates need not be comparable.
    The caller must supply records from one declared envelope, not merge the
    candidate runs from different affordability assumptions.
    """
    if not candidates:return {'families':[],'actual_regret':None,'decision_authorized':False}
    if any(len(c['start_by_year'])==0 or 'r157_robust_sensitivity' not in c for c in candidates):raise ValueError('Missing plan evidence')
    best=max(c['r157_robust_sensitivity']['scenario_min_clamp_only_mapped_delta'] for c in candidates)
    families={}
    for plan in candidates:
        first=tuple(plan['start_by_year'][0]['start_project_ids'])
        score=plan['r157_robust_sensitivity']['scenario_min_clamp_only_mapped_delta']
        row=families.setdefault(first,{'first_year_project_ids':list(first),'best_sampled_scenario_min':-float('inf'),'sampled_plans':0})
        row['best_sampled_scenario_min']=max(row['best_sampled_scenario_min'],score)
        row['sampled_plans']+=1
    out=[]
    for x in families.values():
        x['gap_from_best_sampled_scenario_min']=round(max(0.,best-x['best_sampled_scenario_min']),9)
        x['game_winning_regret']=None
        out.append(x)
    out.sort(key=lambda x:(x['gap_from_best_sampled_scenario_min'],-x['sampled_plans'],x['first_year_project_ids']))
    return {'families':out,'sampled_best_scenario_min':best,'actual_regret':None,
            'not_comparable_to_other_envelope_families':True,'decision_authorized':False}
