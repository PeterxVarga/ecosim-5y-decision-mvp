#!/usr/bin/env python3
"""R150 sampled Pareto / scenario opportunity-cost analysis.

This evaluates only candidates the existing heuristic found. It cannot establish
server feasibility, actual scores, global optimality, probabilities, or game GO.
"""
from __future__ import annotations
import math


def _finite_nonneg(x):
    return type(x) in (float,int) and math.isfinite(x) and x >= 0


def _feasible(candidate, envelope_id):
    row=candidate['envelope_comparison'][envelope_id]
    return row['passes_this_hypothetical_envelope'] is True


def _dominates(a,b,eps=1e-7):
    """Quantified *partial-model* dominance on sampled candidates only.

    Neither count of unknown effects nor conditional eligibility is a numeric
    outcome objective; both remain audit flags. No actual-game dominance claim.
    """
    ac=a['conservative_project_need_ecu_by_year']
    bc=b['conservative_project_need_ecu_by_year']
    if len(ac)!=len(bc):return False
    dimensions=[
      (a['mapped_terminal_proxy_delta'],b['mapped_terminal_proxy_delta'],'higher'),
      (a['worst_of_existing_illustrative_mapped_sensitivities'],b['worst_of_existing_illustrative_mapped_sensitivities'],'higher'),
    ]
    dimensions += [(x,y,'lower') for x,y in zip(ac,bc)]
    weak=all(x>=y-eps if direction=='higher' else x<=y+eps for x,y,direction in dimensions)
    strict=any(x>y+eps if direction=='higher' else x<y-eps for x,y,direction in dimensions)
    return weak and strict


def assess_candidate_quality(candidates, envelopes, start_year):
    if type(start_year) is not int or not 1<=start_year<=5:raise ValueError('start_year must be 1..5')
    ids=set()
    for c in candidates:
        if c['candidate_id'] in ids:raise ValueError('Duplicate candidate id')
        ids.add(c['candidate_id'])
        if len(c['project_ids_by_year']) != 6-start_year:raise ValueError('Wrong horizon')
        if len(c['conservative_project_need_ecu_by_year']) != 6-start_year:raise ValueError('Wrong cost horizon')
        if not all(_finite_nonneg(x) for x in c['conservative_project_need_ecu_by_year']):raise ValueError('Invalid costs')
    by_envelope={}; sampled_gaps=[]
    for e in envelopes:
        eid=e['id']
        sample=[c for c in candidates if _feasible(c,eid)]
        if sample:
            best_proxy=max(c['mapped_terminal_proxy_delta'] for c in sample)
            best_stress=max(c['worst_of_existing_illustrative_mapped_sensitivities'] for c in sample)
        else:best_proxy=best_stress=None
        frontier=[]; dominated={}
        for c in sample:
            witnesses=[p['candidate_id'] for p in sample if p['candidate_id']!=c['candidate_id'] and _dominates(p,c)]
            if witnesses:dominated[c['candidate_id']]=witnesses[:8]
            else:frontier.append(c['candidate_id'])
            sampled_gaps.append({
              'envelope_id':eid,'candidate_id':c['candidate_id'],
              'gap_to_best_sampled_mapped_proxy_delta':round(max(0.,best_proxy-c['mapped_terminal_proxy_delta']),8),
              'gap_to_best_sampled_stressed_proxy_delta':round(max(0.,best_stress-c['worst_of_existing_illustrative_mapped_sensitivities']),8),
              'not_game_score_regret':True})
        by_envelope[eid]={
          'within_hypothetical_budget_count':len(sample),
          'nondominated_in_sample_ids':frontier,
          'sampled_dominance_witnesses':dominated,
          'highest_sampled_mapped_proxy_delta':best_proxy,
          'highest_sampled_illustrative_stress_proxy_delta':best_stress,
          'server_feasible':None, 'globally_optimal':None,
        }
    clusters={}
    for c in candidates:
        key=tuple(c['project_ids_by_year'][0])
        x=clusters.setdefault(key,{'first_year_project_ids':list(key),'candidate_ids':[],
                                   'found_feasible_under_hypothetical_envelopes':set(),
                                   'mapped_proxy_deltas':[], 'missing_effect_counts':[]})
        x['candidate_ids'].append(c['candidate_id'])
        x['found_feasible_under_hypothetical_envelopes'].update(c['inside_explicit_hypothetical_envelopes'])
        x['mapped_proxy_deltas'].append(c['mapped_terminal_proxy_delta'])
        x['missing_effect_counts'].append(c['unmapped_or_uncertain_project_effect_occurrences'])
    families=[]
    for v in clusters.values():
        families.append({
          'first_year_project_ids':v['first_year_project_ids'],
          'sampled_candidate_count_not_probability':len(v['candidate_ids']),
          'candidate_ids':v['candidate_ids'],
          'seen_within_hypothetical_envelopes':sorted(v['found_feasible_under_hypothetical_envelopes']),
          'sampled_terminal_mapped_proxy_delta_min':min(v['mapped_proxy_deltas']),
          'sampled_terminal_mapped_proxy_delta_max':max(v['mapped_proxy_deltas']),
          'unmapped_effect_occurrence_min':min(v['missing_effect_counts']),
          'unmapped_effect_occurrence_max':max(v['missing_effect_counts']),
          'action_authorized':False,
        })
    families.sort(key=lambda v:(-len(v['seen_within_hypothetical_envelopes']),
                                -v['sampled_candidate_count_not_probability'],
                                v['unmapped_effect_occurrence_max'],v['first_year_project_ids']))
    return {
      'schema':'ECOSIM_R150_SAMPLED_DECISION_QUALITY_V1',
      'sampled_candidate_count':len(candidates),
      'r160_dominance_compares_only_quantified_partial_model_dimensions':True,
      'r160_unknown_effect_counts_not_treated_as_negative_objectives':True,
      'r160_unverified_dependency_not_quantified_as_score_penalty':True,
      'r160_real_outcome_dominance_for_any_two_candidates':'UNDETERMINED_UNKNOWN_CITY_DYNAMICS',
      'candidate_search_is_heuristic':True,
      'pareto_on_partial_metrics_not_realized_city_outcomes':True,
      'unknown_effect_count_is_evidence_indicator_not_signed_impact':True,
      'scenario_budget_not_verified_cash':True,
      'envelope_frontiers':by_envelope,
      'sampled_opportunity_gaps':sampled_gaps,
      'first_year_action_clusters':families[:15],
      'actual_optimality_claim':None,'real_world_win_probability':None,
      'gameplay_gate':'STOP'
    }
