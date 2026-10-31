#!/usr/bin/env python3
"""R145 single integrated portfolio engine + EXPLICIT operating-policy tracks.

Outputs are scenarios, never official forecasts. Project selection is reoptimized
for each supplied policy track, not globally optimized over all possible policies.
"""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from strategy_5y import ROOT, read_json, write_json, search, parse_budget, derive_config
from portfolio_5y import project_index
from policy_tracks import load_tracks, cost_reservation_for_year, replay_policy_joint, policy_money_replay, policy_factor_replay
from robust_r146 import stress_plan
from annual_transition_r148 import annual_component_rollout


def combine_counterfactual_cash(plan,track,state,start_year):
    """Optional independent replay; strict non-overlap prevents double counting.

    The R144 bridge already holds hypothetical project + nonproject + long-loan
    components. Only add policy cash deltas if the supplied nonproject path
    explicitly excludes them. If any policy cash effect is unknown, return null.
    """
    finance=state.get('finance_counterfactual')
    if not finance:
        return {'status':'UNKNOWN_NO_EXPLICIT_NONPROJECT_CASH_SCENARIO','years':[],
                'actual_cash_forecast':None}
    if finance.get('nonproject_flow_excludes_policy_track') is not True:
        return {'status':'UNKNOWN_POSSIBLE_DOUBLE_COUNT_OF_OPERATING_POLICY','years':[],
                'actual_cash_forecast':None}
    bridge=plan['city_component_bridge']
    rows=[]; cumulative=0.;known=True
    for yr in bridge['years']:
        y=yr['year'];cash=yr['financial_counterfactual']['closing_scenario_cash_ecu']
        policy=policy_money_replay(track,y,start_year)
        if not policy['complete'] or cash is None:known=False
        if known:
            cumulative+=policy['disclosed_policy_cash_delta_ecu']
            adjusted=round(cash+cumulative,2)
        else:adjusted=None
        rows.append({'year':y,'cash_if_all_declared_assumptions_hold_ecu':adjusted,
                     'unknown_cash_policy_decisions':policy['undisclosed_policy_cash_decisions'],
                     'status':'CONDITIONAL_NO_SERVER_VALIDATION' if adjusted is not None else 'UNKNOWN'})
    return {'status':'EXPLICIT_HYPOTHETICAL_NO_DOUBLE_COUNT_ASSUMED',
            'years':rows,'actual_cash_forecast':None,'credit_and_grant_approval':None}


def render_joint_md(output):
    lines=['# R146 — Ötéves integrált, stresszelt projekt + várospolitika (feltételes)', '',
           '**Játékbeli módosítás: 0. Eredmények: nem validált forgatókönyvek, nem döntési ajánlások.**', '',
           '| Szcenárió | Forrás | Elsőéves projektindítás | 5. évi kombinált proxy Δ | Finanszírozási kapu |',
           '|---|---|---|---:|---|']
    for t in output['tracks']:
        options=t.get('joint_options') or []
        if options:
            p=options[0];first=','.join(map(str,p['project_starts'][0]['start_project_ids'])) or '—'
            lines.append(f"| {t['track_id']} | {t['scenario_mode']} | {first} | {p['joint_terminal_counterfactual_delta']:+.4f} | STOP |")
        else:
            lines.append(f"| {t['track_id']} | {t['scenario_mode']} | — | N/A | STOP ({t['status']}) |")
    lines += ['', '## Értelmezési korlátok', '',
              '- A felsorolt szintetikus hatások **nem EcoSim-szabályok**; csak a program tesztjére valók.',
              '- A játék valós adó-, díj- és intézményi hatásfüggvénye **ismeretlen**. A modellezett nulladik pálya nem jelenti, hogy a valós hatás nulla.',
              '- A modell nem igazolja a hitelfelvételi jogosultságot, a szabadon elkölthető keretet vagy a projektindítás szerveroldali elfogadását.',
              '- A keresés korlátos beam heurisztika. Az előre rögzített működési forgatókönyvek között hasonlít, nem keresi meg az összes lehetséges adó- és intézményi döntést.',
              '- A tesztfordulós történeti állapot nem éles, hitelesített kezdőállapot.',
              '', '## Mi kell a következő kalibrációhoz?', '',
              'Hivatalos, verziózott piac- és csapatállapot; a működési döntésmezők dokumentált tartományai; ellenőrizhető tervoszlop-változások; hitelek, projekttámogatások és migráció érvényes szabályai. A jóváhagyás és visszaállíthatóság tisztázása előtt nincs játékbeli A/B próba.', '']
    return '\n'.join(lines)


def evaluate_tracks(state,start_year,tracks,budgets,cap,beam,shortlist):
    idx=project_index()
    config=derive_config(state,idx,start_year,budgets,cap)
    baseline=config['baseline'];weights=(state.get('market') or {}).get('smartcity_total_weights')
    years=list(range(start_year,6))
    effective_budgets=budgets if budgets is not None else config['budgets']
    rows=[]
    for track in tracks:
        reserve=[cost_reservation_for_year(track,y) for y in years]
        explicit_exclusion=track.get('project_envelope_excludes_policy_cash_deltas') is True
        if effective_budgets is None:
            residual=None;funding='UNKNOWN_NO_EXPLICIT_CASH_ENVELOPE'
        elif not explicit_exclusion and any(x>0 for x in reserve):
            # Preserve only the RAW search-bound as a non-actionable upper envelope.
            # Never report it as policy-adjusted or available project cash.
            residual=list(effective_budgets)
            funding='UNKNOWN_POSSIBLE_POLICY_PROJECT_BUDGET_DOUBLE_COUNT'
        else:
            residual=[max(0,b-c) for b,c in zip(effective_budgets,reserve)]
            funding='CONDITIONAL_PROJECT_ENVELOPE_NET_OF_DISCLOSED_POLICY_NEGATIVE_CASH_ONLY'
        # Unknown operating costs can be positive or negative; do not certify a
        # residual project envelope without complete policy cash components.
        unknown_policy_cash = [
            a['decision_key'] for a in track['actions']
            if a.get('annual_cash_delta_ecu') is None and
            any((a['year']<=y if a['duration']=='PERSISTENT_FROM_START' else a['year']==y)
                for y in years)
        ]
        if unknown_policy_cash:
            funding='UNKNOWN_UNBOUNDED_POLICY_CASH_EFFECT'
        # A purported cap <= annual reservations should not create false feasibility.
        infeasible=(residual is not None and any(r>b+1e-8 for r,b in zip(reserve,effective_budgets)))
        if infeasible:
            rows.append({'track_id':track['track_id'],'scenario_mode':track['mode'],'status':'INFEASIBLE_UNDER_SCENARIO_RESERVATIONS','proposed_policy_reservations_ecu':reserve,'gameplay_gate':'STOP'})
            continue
        # The terminal project ranking now incorporates the supplied mapped
        # policy factors, rather than reusing a project-only top-three shortlist.
        terminal_policy_multipliers,_,unknown_final=policy_factor_replay(
            {k:1.0 for k in baseline},track,5,start_year
        )
        candidate=search(state,start_year,residual,cap,beam,shortlist,True,
                         terminal_policy_factor_multipliers=terminal_policy_multipliers)
        choices=[]
        for p in candidate['top_plans'][:10]:
            replay=replay_policy_joint(p,track,baseline,idx,weights,start_year)
            joint_cash=combine_counterfactual_cash(p,track,state,start_year)
            stress=stress_plan(p,track,baseline,idx,weights,start_year,residual,
                               budget_component_nonoverlap_declared=(funding=='CONDITIONAL_PROJECT_ENVELOPE_NET_OF_DISCLOSED_POLICY_NEGATIVE_CASH_ONLY'))
            multipliers_by_year=[policy_factor_replay({k:1.0 for k in baseline},track,y,start_year)[0]
                                 for y in years]
            carried=annual_component_rollout(idx,config['initial_active'],
                      [q['start_project_ids'] for q in p['start_by_year']],baseline,
                      start_year=start_year,policy_multiplier_by_year=multipliers_by_year,weights=weights)
            choices.append({'r148_carried_annual_components':carried,
                            'project_starts':p['start_by_year'],
                            'policy_conditioned_search_project_gain':p['terminal_project_gain_under_policy_assumption'],
                            'illustrative_robustness':stress,
                            'project_heuristic_terminal_proxy_delta':p['terminal_mapped_proxy_delta'],
                            'joint_factor_counterfactual_by_year':replay,
                            'joint_terminal_counterfactual_delta':replay[-1]['joint_mapped_delta_from_input_baseline'],
                            'joint_cash_counterfactual':joint_cash,
                            'missing_project_metric_effects':p['excluded_unknown_effects'],
                            'missing_policy_factor_actions':sum(len(x['policy_unmapped_actions']) for x in replay),
                            'financial_funding_proof':False,
                            'comparison_quality':'SYNTHETIC_ONLY' if track['mode']=='SYNTHETIC_TEST_ONLY' else 'UNCALIBRATED_OBSERVATIONAL_OR_USER_HYPOTHESIS',
                            'known_component_is_full_decision_response':False,
                            'actual_terminal_index_prediction':None,
                            'candidate_financially_authorized':False,
                            'gameplay_decision':'STOP'})
        # Reorder conditional alternatives using their own explicitly provided
        # POLICY + PROJECT factor replay, without inventing other dynamics.
        choices.sort(key=lambda x:(-x['illustrative_robustness']['worst_mapped_terminal_index_delta'],
                                   -x['joint_terminal_counterfactual_delta'],
                                   len(x['missing_project_metric_effects'])+x['missing_policy_factor_actions']))
        rows.append({'track_id':track['track_id'],'scenario_mode':track['mode'],
                     'scenario_note':track['assumption_note'],
                     'status':'ILLUSTRATIVE_SCENARIO_ONLY_NOT_A_GAME_POLICY_RECOMMENDATION',
                     'policy_project_budget_interpretation':funding,
                     'project_budgets_after_policy_reservation_ecu':(residual if funding=='CONDITIONAL_PROJECT_ENVELOPE_NET_OF_DISCLOSED_POLICY_NEGATIVE_CASH_ONLY' else None),
                     'search_only_raw_project_envelope_ecu':(residual if funding!='CONDITIONAL_PROJECT_ENVELOPE_NET_OF_DISCLOSED_POLICY_NEGATIVE_CASH_ONLY' else None),
                     'unknown_policy_cash_decisions':unknown_policy_cash,
                     'policy_conditioned_search_used':True,
                     'choice_sorting':'MIN_OVER_EXPLICIT_ILLUSTRATIVE_FACTOR_STRESSES_NOT_EXPECTED_GAME_SCORE',
                     'proposed_policy_reservations_ecu':reserve,
                     'not_modeled_policy_choices':'All operating decisions not explicitly enumerated in this track',
                     'joint_options':choices,
                     'gameplay_gate':'STOP'})
    return {'schema':'ECOSIM_R146_POLICY_AND_PROJECT_STRESS_COMPARISON_V1',
            'source_basis':'R144 existing project search, R144 city bridge, R145 explicitly supplied policy tracks',
            'actual_city_transition_model':None,
            'policy_conditioned_joint_project_search':True,
            'robust_stress_profiles_are_probabilities':False,
            'actual_score_uncertainty_bounds':None,
            'model_confidence':'UNVALIDATED_HYPOTHETICAL_COUNTERFACTUALS',
            'actual_five_year_game_score':None,
            'comparison_is_global_optimum':False,
            'tracks_not_ranked_against_each_other_as_expected_real_outcomes':True,
            'game_writes':0,'external_calls':0,'gameplay_decision':'STOP',
            'start_year':start_year,
            'underlying_market_and_budget_provenance':config['provenance'],
            'tracks':rows,
            'unresolved':['Actual operating policy response function unknown',
                          'Market and team parameters are unverified until official export',
                          'Policy effects in tracks are supplied assumptions, not inferred EcoSim constants',
                          'Other teams and migration not predicted',
                          'No game preview or credit approval'],}


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--policy-tracks',required=True)
    a.add_argument('--state',default=str(ROOT/'inputs/official_state.template.json'))
    a.add_argument('--start-year',type=int,default=1)
    a.add_argument('--budget-per-year',default=None)
    a.add_argument('--project-cap',type=int,default=None)
    a.add_argument('--beam',type=int,default=12)
    a.add_argument('--shortlist',type=int,default=30)
    a.add_argument('--out',default=str(ROOT/'results/R145_POLICY_AND_PROJECT_SCENARIOS.json'))
    ns=a.parse_args()
    if not 1<=ns.start_year<=5:a.error('start-year must be 1..5')
    state=read_json(ns.state)
    b=parse_budget(ns.budget_per_year,6-ns.start_year)
    o=evaluate_tracks(state,ns.start_year,load_tracks(ns.policy_tracks),b,ns.project_cap,ns.beam,ns.shortlist)
    write_json(ns.out,o)
    Path(ns.out).with_suffix('.md').write_text(render_joint_md(o),encoding='utf8')
    print('R146_POLICY_JOINT_STRESS=PASS; scenario_tracks='+str(len(o['tracks']))+'; no_game_actions=TRUE; decision=STOP; out='+ns.out)
if __name__=='__main__':main()
