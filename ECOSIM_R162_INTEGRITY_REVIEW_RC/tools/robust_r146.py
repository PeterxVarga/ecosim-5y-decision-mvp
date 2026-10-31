#!/usr/bin/env python3
"""R146 descriptive stress testing. Never a probability distribution or EcoSim forecast."""
from __future__ import annotations

from city_bridge import computed_index_from_factors
from policy_tracks import policy_factor_replay
from r142_proxy_reference import COEFF
from effect_replay_r147 import normalize_metric
from annual_transition_r148 import combined_factor_replay

# Explicit illustrative stress assumptions, NOT observed bounds.
PROFILES = (
    {"id":"card_effects_constant","project_intensity":1.0,"project_retention":1.0,"policy_intensity":1.0,"budget_haircut":0.0},
    {"id":"project_half_policy_half","project_intensity":0.5,"project_retention":1.0,"policy_intensity":0.5,"budget_haircut":0.15},
    {"id":"project_annual_decay_policy_zero","project_intensity":0.75,"project_retention":0.85,"policy_intensity":0.0,"budget_haircut":0.15},
    {"id":"project_25pct_stronger","project_intensity":1.25,"project_retention":1.0,"policy_intensity":1.25,"budget_haircut":0.0},
)

def stress_plan(plan, track, baseline, idx, weights, start_year, budget,
                budget_component_nonoverlap_declared=False, profiles=PROFILES):
    """Known mapped project + explicitly declared policy deltas under stress.

    Unknown factors are not treated as zero. The numeric range is NOT a
    lower/upper bound on the game's true result.
    """
    base = computed_index_from_factors(baseline, weights)['total_index_from_displayed_factors']
    rows=[]; any_saturation_ambiguity=False
    starts=[p['start_project_ids'] for p in plan['start_by_year']]
    year5 = start_year+len(starts)-1
    all_unmapped = [
        {'project_id':pid, 'metric':x['metric']} for ids in starts for pid in ids
        for x in idx[pid]['effects'] if normalize_metric(x['metric']) not in COEFF
    ]
    unknown_policy=[{'year':a['year'],'decision_key':a['decision_key']}
                    for a in track['actions'] if a['year']<=year5
                    and a.get('factor_relative_percent') is None]
    for profile in profiles:
        pairs=[]
        for offset, ids in enumerate(starts):
            age=year5-(start_year+offset)
            multiplier=profile['project_intensity'] * profile['project_retention']**age
            for pid in ids:
                pairs.extend((pid,{**e,'value_percent':e['value_percent']*multiplier}) for e in idx[pid]['effects'])
        policy_mult, _, _ = policy_factor_replay(
            {k:1.0 for k in baseline},track,year5,start_year,
            scale=profile['policy_intensity'])
        # R157 fix: project and policy multipliers combine BEFORE a single clamp.
        joint=combined_factor_replay(baseline,pairs,policy_mult,weights=weights)
        any_saturation_ambiguity=any_saturation_ambiguity or bool(joint['ambiguous_saturated_factors'])
        val=joint['mapped_conditional_index']
        financial = 'UNKNOWN_NO_CASH_ENVELOPE_OR_POLICY_COST_PROOF'
        b_year=[]
        if budget is not None and budget_component_nonoverlap_declared:
            for i, y in enumerate(plan['start_by_year']):
                limit=budget[i]*(1-profile['budget_haircut'])
                cost=y['conservative_card_cash_requirement_ecu']
                b_year.append({'year':y['year'],'stressed_cap':round(limit,2),
                               'cost':round(cost,2),'inside_hypothetical_envelope':cost<=limit+1e-9})
            financial = ('WITHIN_STRESSED_HYPOTHETICAL_ENVELOPES'
                         if all(y['inside_hypothetical_envelope'] for y in b_year)
                         else 'EXCEEDS_STRESSED_HYPOTHETICAL_ENVELOPE')
        rows.append({'profile_id':profile['id'],
                     'assumptions':profile,
                     'mapped_terminal_delta':round(val-base,6),
                     'mapped_terminal_index':round(val,6),
                     'conditional_clamp_only_index_interval':joint['mapped_index_if_only_saturation_uncertain'],
                     'combined_once_before_clamp':True,
                     'stressed_budget_status':financial,
                     'stressed_budget_rows':b_year,
                     'actual_game_outcome_estimate':None})
    deltas=[r['mapped_terminal_delta'] for r in rows]
    return {'schema':'ECOSIM_R146_ILLUSTRATIVE_STRESS_V1',
            'stress_profiles_are_observed_probabilities':False,
            'stress_minmax_are_actual_outcome_bounds':False,
            'worst_mapped_terminal_index_delta':min(deltas),
            'best_mapped_terminal_index_delta':max(deltas),
            'illustrative_spread':round(max(deltas)-min(deltas),6),
            'unmapped_project_effects':all_unmapped,
            'source_clamp_ambiguities_possible':any_saturation_ambiguity,
            'unknown_policy_factor_actions':unknown_policy,
            'uncertain_project_effect_coverage':bool(all_unmapped),
            'uncertain_policy_response_coverage':bool(unknown_policy),
            'gameplay_decision':'STOP',
            'profiles':rows}
