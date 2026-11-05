#!/usr/bin/env python3
"""Evidence-bounded five-year offline EcoSim PROJECT strategy search.

Reuses R142 proxy and R143.2.1 card cost calendar. Nothing executes JS, uses a
browser, accesses the network or changes a game state. No deterministic forecast.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from itertools import combinations
from heapq import heappush, heappushpop
from pathlib import Path
import json
import math
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/'tools'))
from portfolio_5y import project_index, classify_conditions, verify_inputs
from r142_proxy_reference import evaluate, proxy_value, COEFF
from city_bridge import attach_city_bridge, computed_index_from_factors
from effect_replay_r147 import replay_effects, normalize_metric
from annual_transition_r148 import combined_factor_replay, annual_component_rollout
from robust_decision_r157 import replay as robust_replay, sampled_first_action_regret
from independent_audit_r160 import audit_plan


# The public input parser remains importable from strategy_5y for legacy callers.
from json_integrity_r162 import read_json


def write_json(path, data):
    dest=Path(path); dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False)+'\n', encoding='utf-8')


def int_list(ids, all_ids, field):
    if not isinstance(ids, list) or any(type(i) is not int or i not in all_ids for i in ids) or len(ids)!=len(set(ids)):
        raise ValueError('Invalid or duplicate IDs: '+field)
    return frozenset(ids)


def parse_budget(text, n):
    if text is None: return None
    vals=[float(v.strip()) for v in text.split(',')]
    if len(vals)==1: vals*=n
    if len(vals)!=n or any(not math.isfinite(v) or v<0 for v in vals):
        raise ValueError('Budget must be one nonnegative finite number or one per remaining year')
    return vals


@dataclass(frozen=True)
class Node:
    starts: tuple[tuple[int,...], ...]
    selected: frozenset[int]
    costs: tuple[float,...]
    score_history: tuple[float,...]
    approximate_gain: float
    conditional_co_start: bool=False


def derive_config(state, idx, start_year, budget_override, cap_override):
    provenance=state.get('provenance',{})
    if provenance.get('current_period') is not None and provenance['current_period']!=start_year:
        raise ValueError('Input current_period does not match requested start_year')
    team=state.get('team',{})
    market=state.get('market',{})
    all_ids=set(idx)
    source=provenance.get('source') or 'UNVERIFIED'
    operator_declared_metadata = bool(provenance.get('source_evidence_id') and provenance.get('captured_at_local') and provenance.get('team') and provenance.get('market'))
    # Presence of provenance fields does NOT authenticate an EcoSim server origin.
    # No cryptographically verified live state is available in this offline engine.
    actual_provenance = False
    active_ids=team.get('initially_active_project_ids')
    if active_ids is None:
        if start_year!=1:
            raise ValueError('Replanning after year 1 requires current initially_active_project_ids')
        active=frozenset(i for i,p in idx.items() if p['status_p1']=='Fut')
        active_source='HISTORICAL_TEST_ROUND_FALLBACK_NOT_LIVE'
    else:
        active=int_list(active_ids, all_ids, 'initially_active_project_ids')
        active_source=('OPERATOR_DECLARED_'+source if operator_declared_metadata else 'USER_INPUT_NOT_VERIFIED')
    project1prev=team.get('project1_active_previous_period')
    selected_current=team.get('already_selected_new_project_ids_current_period')
    fixed_first=int_list(selected_current, all_ids, 'already_selected_new_project_ids_current_period') if selected_current is not None else frozenset()
    if fixed_first & active:
        raise ValueError('Current newly selected IDs overlap previously active IDs')
    cap=market.get('maxProjectPerTurn') if cap_override is None else cap_override
    cap_source=('EXPLICIT_ILLUSTRATIVE_CLI_ASSUMPTION' if cap_override is not None else
                'USER_MARKET_INPUT_OPERATOR_DECLARED_NOT_SERVER_VERIFIED')
    if cap is None:
        cap=4
        cap_source='OFFICIAL_SPOKEN_FOUR_PER_YEAR_NOT_LIVE_MARKET_VERIFIED'
    if type(cap) is not int or not (0<=cap<=20):
        raise ValueError('Invalid project cap')
    n=6-start_year
    # Annual cash envelope is an external scenario, not a net income inference.
    if budget_override is not None:
        budgets=budget_override
        budget_source='EXPLICIT_ILLUSTRATIVE_CLI_SCENARIO_NOT_SPENDABLE_CASH'
    else:
        raw=team.get('confirmed_spendable_cash_ecu_by_year')
        if not (isinstance(raw,list) and len(raw)==5 and all(type(v) in (float,int) and math.isfinite(v) and v>=0 for v in raw[start_year-1:])):
            budgets=None;budget_source='UNKNOWN_NO_CASH_ENVELOPE_PROVIDED'
        else:
            committed=team.get('committed_costs_ecu_by_year')
            if not (isinstance(committed,list) and len(committed)==5 and all(type(v) in (float,int) and math.isfinite(v) and v>=0 for v in committed[start_year-1:])):
                raise ValueError('Official cash provided but committed costs are missing; cannot apply envelope')
            budgets=[float(a-b) for a,b in zip(raw[start_year-1:], committed[start_year-1:])]
            budget_source='USER_INPUT_NET_OF_COMMITMENTS_NOT_SERVER_APPROVAL'
    if budgets is not None and any(v<0 for v in budgets):
        raise ValueError('Negative residual budget after committed costs')
    own_metrics=team.get('baseline_smartcity_factors')
    if own_metrics is not None:
        if not isinstance(own_metrics,dict) or set(COEFF)-set(own_metrics) or any(type(v) not in (int,float) or not math.isfinite(v) for v in own_metrics.values()):
            raise ValueError('baseline_smartcity_factors must include all proxy metric keys')
        baseline={k:float(own_metrics[k]) for k in COEFF}
        baseline_source=('OPERATOR_DECLARED_'+source if operator_declared_metadata else 'USER_PROVIDED_UNVERIFIED_METRICS')
    else:
        if start_year!=1:
            raise ValueError('Replanning after year 1 requires current baseline_smartcity_factors')
        baseline=read_json(ROOT/'data/ECOSIM_R141_PROJECT_PROXY.json')['baseline_from_UI']
        baseline_source='2026_10_30_TEST_P1_UI_BASELINE_NOT_LIVE'
    return dict(initial_active=active,active_source=active_source,fixed_first=fixed_first,
                project1prev=project1prev,cap=cap,cap_source=cap_source,
                budgets=budgets,budget_source=budget_source,baseline=baseline,
                baseline_source=baseline_source,verified=actual_provenance,
                operator_declared_metadata_present=operator_declared_metadata,
                provenance=provenance)


def parse_dependencies(idx):
    names={p['name']:i for i,p in idx.items()}
    deps={}; unresolved=[]
    for i,p in idx.items():
        rows=[]
        for raw in p.get('project_conditions',[]):
            name=raw.split(' — ',1)[0].strip()
            negate=name.startswith('not ')
            if negate:name=name[4:].strip()
            other=names.get(name)
            if other is None:
                unresolved.append(dict(project_id=i,condition=raw))
            rows.append((other,negate,raw))
        deps[i]=rows
    return deps,unresolved


def permitted(combo, before, deps, allow_same_year):
    subset=set(combo)
    used_same=False
    for i in combo:
        for other,negate,_ in deps[i]:
            if other is None: return False,False
            # A negative condition can never coexist with the forbidden
            # project in the same year, even in strict prior-year mode.
            # The co-start switch applies ONLY to positive dependencies.
            present_before=other in before
            present_same_year=other in subset
            if negate and (present_before or present_same_year):return False,False
            if not negate and not (present_before or (allow_same_year and present_same_year)):
                return False,False
            if not negate and not present_before:used_same=True
    return True,used_same


def yearly_cost(idx, previous, new):
    active=previous|set(new)
    return (sum(idx[i]['startup_cost']+idx[i]['investment'] for i in new)
            +sum(max(idx[i]['maintenance_cost'],0) for i in active))


def _metric_score(factors, weights=None):
    return computed_index_from_factors(factors,weights)['total_index_from_displayed_factors']


def evaluate_proxy(idx, selected, baseline, weights=None, policy_multipliers=None):
    chosen=[idx[i] for i in sorted(selected)]
    if policy_multipliers is not None:
        mixed=combined_factor_replay(baseline,[(p['id'],e) for p in chosen for e in p['effects']],
                                    policy_multipliers,weights=weights)
        neutral=combined_factor_replay(baseline,[],policy_multipliers,weights=weights)
        unknown=[{'metric':x['effect_label'],'reason':x['reason']} for x in mixed['unmapped_project_effects']]
        unknown.extend({'metric':x['factor'],'reason':x['reason']} for x in mixed['ambiguous_saturated_factors'])
        return mixed['mapped_conditional_index']-neutral['mapped_conditional_index'],len(unknown),sorted(set(x['metric'] for x in unknown))
    factors=dict(baseline)
    records=replay_effects(factors,[(p['id'],e) for p in chosen for e in p['effects']],COEFF)
    unknown=[{'metric':r.get('project_metric') or (r.get('project_metric_labels') or [None])[0],
              'reason':r.get('reason','SATURATION_UNIDENTIFIED')}
             for r in records if not r['mapped'] or r.get('uncertain_due_to_saturation')]
    return _metric_score(factors,weights)-_metric_score(baseline,weights),len(unknown),sorted(set(x['metric'] for x in unknown))


def proxy_sensitivity(idx, starts, baseline, start_year, retention=1.0, intensity=1.0, weights=None):
    """Counterfactual mapped-card-only sensitivity, NOT a predictive confidence bound."""
    years=[]
    for offset,start_ids in enumerate(starts):
        y=start_year+offset
        metrics=dict(baseline)
        pairs=[]
        for t,ids in enumerate(starts[:offset+1]):
            age=offset-t
            scale=intensity * retention**age
            for i in ids:
                pairs.extend((i,{**e,'value_percent':e['value_percent']*scale}) for e in idx[i]['effects'])
        records=replay_effects(metrics,pairs,COEFF)
        unknown=[dict(project_id=r.get('project_id'),project_ids=r.get('project_ids'),
                      metric=r.get('project_metric') or (r.get('project_metric_labels') or [None])[0],
                      reason=r.get('reason','SATURATION_UNIDENTIFIED'))
                 for r in records if not r['mapped'] or r.get('uncertain_due_to_saturation')]
        years.append(dict(year=y,mapped_proxy_index=round(_metric_score(metrics,weights),6),
                          mapped_proxy_delta=round(_metric_score(metrics,weights)-_metric_score(baseline,weights),6),
                          excluded_unknown_effect_count=len(unknown)))
    return years


def count_indices(idx, active, starts):
    unknown=[]
    for i in sorted(active|set(i for year in starts for i in year)):
        if i not in idx:continue
        for e in idx[i]['effects']:
            if normalize_metric(e['metric']) not in COEFF:
                unknown.append((i,e['metric'],e['value_percent']))
    return [dict(project_id=i,metric=m,pct=p) for i,m,p in unknown]


def candidate_pool(idx, base_active, baseline, weights=None, policy_multipliers=None):
    # All available historical projects (29 in test); no silent arbitrary pruning.
    ids=[i for i in sorted(idx) if i not in base_active]
    single={i:evaluate_proxy(idx,{i},baseline,weights,policy_multipliers)[0] for i in ids}
    return ids,single


def search(state, start_year=1, budget_override=None, cap_override=None,
           beam_width=14, shortlist=36, allow_same_year=True,
           terminal_policy_factor_multipliers=None, objective='nominal',
           announced_absolute_cap=None):
    if objective not in ('nominal','scenario_min'):
        raise ValueError('Unsupported R157 search objective')
    if announced_absolute_cap is not None and (
            type(announced_absolute_cap) is not int or not 0<=announced_absolute_cap<=20):
        raise ValueError('Announced absolute project cap must be an integer 0..20')
    idx=project_index();config=derive_config(state,idx,start_year,budget_override,cap_override)
    initial=config['initial_active'];bas=config['baseline']
    weights=(state.get('market') or {}).get('smartcity_total_weights')
    base_score=_metric_score(bas,weights)
    # Condition the PROJECT search on the named policy track's terminal
    # *explicit* factor assumptions. This changes candidate selection, not
    # just post-hoc ranking of the old project-only shortlist.
    ranking_baseline=dict(bas)
    if terminal_policy_factor_multipliers is not None:
        if (not isinstance(terminal_policy_factor_multipliers,dict) or
            set(terminal_policy_factor_multipliers)!=set(bas) or
            any(type(v) not in (int,float) or not math.isfinite(v) or v<=0
                for v in terminal_policy_factor_multipliers.values())):
            raise ValueError('Explicit complete finite positive terminal policy multiplier map required')
        ranking_baseline=dict(bas)
    ranking_base_score=(combined_factor_replay(bas,[],terminal_policy_factor_multipliers,weights=weights)['mapped_conditional_index']
                        if terminal_policy_factor_multipliers is not None else base_score)
    deps,unresolved=parse_dependencies(idx)
    ids,single=candidate_pool(idx,initial,bas,weights,terminal_policy_factor_multipliers)
    if objective=='scenario_min':
        # Cheap scenario-aware shortlist score; exact score below uses the
        # complete retained starts, annual decay, and latent clamp intervals.
        single={i:robust_replay(idx,((i,),),bas,start_year=start_year,
                               weights=weights,policy_multipliers=terminal_policy_factor_multipliers)
                   ['scenario_min_clamp_only_mapped_delta'] for i in ids}
    if type(beam_width) is not int or not (1<=beam_width<=100) or type(shortlist) is not int or not (1<=shortlist<=200):
        raise ValueError('Beam / shortlist outside bounded range')
    prior=Node((),frozenset(),(),(),0.,False)
    beam=[prior];statistics=[]
    for offset in range(6-start_year):
        year=start_year+offset
        best={}; feasible_count=0
        for node in beam:
            before=initial|node.selected
            already_in_year=config['fixed_first'] if offset==0 else frozenset()
            remaining=[i for i in ids if i not in node.selected and i not in already_in_year]
            # The bonus is derived from the prior-period project1 state, not from
            # year t co-start. For years >1, prior selected id 1 remains active.
            is_prev_project1=(config['project1prev'] if offset==0 else (1 in before))
            cap=config['cap'] + (int(is_prev_project1) if isinstance(is_prev_project1,bool) else 0)
            # The client's special project-1 allowance can exceed the
            # organizer's explicitly announced four-per-year competition cap.
            # In verified-organizer scenario mode, never silently plan that
            # optional fifth start; server semantics still need independent proof.
            if announced_absolute_cap is not None:
                cap=min(cap,announced_absolute_cap)
            if len(already_in_year)>cap:
                raise ValueError('Existing current-year selections already exceed assumed effective cap')
            max_extra=max(0, min(cap-len(already_in_year), len(remaining)))
            # For every state, keep several candidate year actions, evaluated with
            # a cheap first-order bound before exact cumulative proxy evaluation.
            shortlist_heap=[]
            n_local=0
            for k in range(max_extra+1):
                for choices in combinations(remaining,k):
                    union=tuple(sorted(already_in_year|set(choices)))
                    ok,used_same=permitted(union,before,deps,allow_same_year)
                    if not ok: continue
                    c=yearly_cost(idx,before,union)
                    if config['budgets'] is not None and c>config['budgets'][offset]+1e-9:continue
                    n_local+=1
                    gain=node.approximate_gain+sum(single[i] for i in union)
                    # approximate utility is terminal gain; slightly favor earlier
                    # useful effects and lower costs only as search tie breakers.
                    approx=gain+0.00001*(5-year)*gain
                    key=(approx,-c,-len(union))
                    record=(key,union,c,used_same,gain)
                    if len(shortlist_heap)<shortlist:
                        heappush(shortlist_heap,record)
                    elif key>shortlist_heap[0][0]:
                        heappushpop(shortlist_heap,record)
            feasible_count+=n_local
            for _,union,c,used_same,gain in shortlist_heap:
                new_ids=node.selected|set(union)
                exact_gain,unknown_count,_=evaluate_proxy(idx,new_ids,bas,weights,terminal_policy_factor_multipliers)
                newstarts=node.starts+(union,)
                newcosts=node.costs+(c,)
                newhist=node.score_history+(ranking_base_score+exact_gain,)
                fresh=Node(newstarts,frozenset(new_ids),newcosts,newhist,gain,
                           node.conditional_co_start or used_same)
                # A few years of index improvement can help a tie but primary
                # objective remains terminal mapped index under assumptions.
                if objective=='scenario_min':
                    # Explicit hypothetical minimax, not a game-score bound.
                    rank_score=robust_replay(idx,newstarts,bas,start_year=start_year,
                                             weights=weights,policy_multipliers=terminal_policy_factor_multipliers)
                    rank_value=rank_score['scenario_min_clamp_only_mapped_delta']
                else:rank_value=exact_gain
                rank=(rank_value, sum((a-ranking_base_score) for a in newhist)*0.000001,
                      -unknown_count, -sum(newcosts))
                old=best.get(fresh.starts)
                if old is None or rank>old[0]:best[fresh.starts]=(rank,fresh)
        if not best:
            raise ValueError('No feasible actions under assumptions at year '+str(year))
        # Prevent near-identical plans crowding out lower-cost alternatives:
        # retain distinct number-of-projects/cumulative-spend buckets as well.
        ranked=sorted(best.values(),key=lambda x:x[0],reverse=True)
        keep=[];seen=set()
        for _,node in ranked:
            if len(keep)>=beam_width:break
            bucket=(len(node.selected)//2, int(sum(node.costs)//50000))
            if bucket in seen:continue
            seen.add(bucket); keep.append(node)
        if len(keep)<beam_width:
            done={n.starts for n in keep}
            keep.extend(node for _,node in ranked if node.starts not in done for _ in [done.add(node.starts)] if len(keep)<beam_width)
        beam=keep[:beam_width]
        statistics.append(dict(year=year,expanded_valid_actions=feasible_count,
                               distinct_shortlisted=len(best),beam_kept=len(beam)))
    results=[]
    for node in beam:
        full=evaluate_proxy(idx,node.selected,bas,weights)
        conditional_full=evaluate_proxy(idx,node.selected,bas,weights,terminal_policy_factor_multipliers)
        rows=proxy_sensitivity(idx,node.starts,bas,start_year,1,1,weights=weights)
        decay=proxy_sensitivity(idx,node.starts,bas,start_year,.85,1,weights=weights)
        half=proxy_sensitivity(idx,node.starts,bas,start_year,1,.5,weights=weights)
        initial_active=set(initial)
        conditions=[]
        previous=initial_active
        for y,ids_this in enumerate(node.starts,start_year):
            for i in ids_this:
                for check in classify_conditions(idx[i],previous,set(ids_this),idx):
                    conditions.append(dict(year=y,project_id=i,**check))
            previous|=set(ids_this)
        robust=robust_replay(idx,node.starts,bas,start_year=start_year,
                             weights=weights,policy_multipliers=terminal_policy_factor_multipliers)
        results.append(dict(r157_robust_sensitivity=robust,
                            start_by_year=[dict(year=start_year+k,
                                                start_project_ids=list(ids_this),
                                                names=[idx[i]['name'] for i in ids_this],
                                                conservative_card_cash_requirement_ecu=round(node.costs[k],2))
                                            for k,ids_this in enumerate(node.starts)],
                            total_new_project_ids=sorted(node.selected),
                            projected_proxy_path_if_baseline_static=rows,
                            illustrative_85pct_yearly_retention_sensitivity=decay,
                            illustrative_half_effect_sensitivity=half,
                            terminal_mapped_proxy_delta=round(full[0],6),
                            terminal_project_gain_under_policy_assumption=round(conditional_full[0],6),
                            worst_of_illustrative_mapped_sensitivities=round(min(full[0],decay[-1]['mapped_proxy_delta'],half[-1]['mapped_proxy_delta']),6),
                            excluded_unknown_effects=count_indices(idx,set(),node.starts),
                            same_year_dependency_conditional=node.conditional_co_start,
                            condition_interpretations=conditions,
                            five_year_conservative_card_cost_ecu=round(sum(node.costs),2),
                            spendable_cash_and_credit_verified=False,
                            eco_sim_preview_verified=False,
                            confidence_class='UNVALIDATED_STATIC_PROXY_NOT_A_FIVE_YEAR_GAME_FORECAST'))
    # R160 independent financial/dependency/cap replay: the search cannot self-
    # certify its own result. Malformed or inconsistent results are fail-closed.
    independent_audits=[]
    for row in results:
        starts=[x['start_project_ids'] for x in row['start_by_year']]
        audit=audit_plan(idx,start_year=start_year,active_ids=sorted(initial),
                         fixed_first_ids=sorted(config['fixed_first']),
                         previous_project1_active=config['project1prev'],
                         base_project_cap=config['cap'],annual_budgets=config['budgets'],
                         starts=starts,
                         advertised_costs=[x['conservative_card_cash_requirement_ecu'] for x in row['start_by_year']],
                         advertised_total=row['five_year_conservative_card_cost_ecu'],
                         allow_same_year=allow_same_year)
        if audit['hard_rule_violations']:
            raise ValueError('R160_INDEPENDENT_REPLAY_REJECTED_SEARCH_PLAN: '+str(audit['hard_rule_violations']))
        if announced_absolute_cap is not None and any(
                len(year_ids)>announced_absolute_cap for year_ids in starts):
            raise ValueError('ANNOUNCED_ABSOLUTE_YEAR_LIMIT_VIOLATION')
        row['r160_independent_constraint_replay']=audit
        independent_audits.append(audit)
    # R144: integrate client-supported aggregation and financial components.
    # This is not a second optimizer or a replacement for the legacy ranking.
    for row in results:
        row['city_component_bridge']=attach_city_bridge(row, initial, bas, idx, state, start_year)
        row['r148_carried_known_components']=annual_component_rollout(
            idx, initial, [s['start_project_ids'] for s in row['start_by_year']], bas,
            start_year=start_year, weights=weights)
    if objective=='scenario_min':
        results.sort(key=lambda p:(-p['r157_robust_sensitivity']['scenario_min_clamp_only_mapped_delta'],
                                   -p['terminal_project_gain_under_policy_assumption'],
                                   len(p['excluded_unknown_effects']),p['five_year_conservative_card_cost_ecu']))
    else:
        results.sort(key=lambda p:(-p['terminal_project_gain_under_policy_assumption'],len(p['excluded_unknown_effects']),p['five_year_conservative_card_cost_ecu']))
    robust_order=sorted(results,key=lambda p:(-p['worst_of_illustrative_mapped_sensitivities'],len(p['excluded_unknown_effects']),p['five_year_conservative_card_cost_ecu']))
    assumptions=dict(annual_project_limit=config['cap'],annual_limit_source=config['cap_source'],
                     official_cash_envelopes_or_illustrative_scenario=config['budgets'],
                     budget_source=config['budget_source'],
                     initial_active_source=config['active_source'],
                     baseline_metrics_source=config['baseline_source'],
                     year1_prior_project1_state=config['project1prev'],
                     co_start_conditions='ALLOWED_BUT_NOT_SERVER_VERIFIED' if allow_same_year else 'PRIOR_YEAR_ONLY',
                     project_status='Nonrepeatable only, historical test export',
                     index='R148 one-clamp source-anchored conditional direct card multipliers with four explicit caps and unemployment alias; other transitions unknown',
                     candidate_search='BOUNDED_BEAM_HEURISTIC_NOT_GLOBAL_OPTIMUM',
                     unknown_effects='Never implicitly valued at zero; displayed proxy omits them and reports each',
                     baseline_static='No exogenous economic drift, no migration, no institution or tax action effects',
                     market_weights_source=('EXPLICIT_USER_MARKET_INPUT_NOT_INDEPENDENTLY_VERIFIED' if weights is not None else 'HISTORICAL_TEST_UI_R141'),
                     video_loan_rate='12 pct spoken example, NOT used for cash and credit calculations')
    if announced_absolute_cap is not None:
        assumptions['organizer_announced_absolute_limit_not_server_verified']=announced_absolute_cap
    gaps=['Full city transition remains unknown despite R144 known-formula bridge',
          'Actual market/team state, caps and loans from live authoritative export',
          'Finance affordability requires verified spendable amount, commitments and grant timing',
          'Taxes, tariffs, institution capacity, staffing and other policy actions are NOT modeled',
          'Migration and other teams reactions mean plan is not a fact forecast',
          'Unmodeled indirect company-count effects and capped-factor latent base are UNKNOWN',
          'No accepted candidate preview; project rendering or draft changes may be unsafe',
          'Historical six running projects are NOT live-round baseline',
          'Regulations/competition permission for external optimization not independently verified']
    from readiness_r148 import check_state
    state_gate=check_state(state)
    r157_first_year=sampled_first_action_regret(results)
    r160_summary={'audit_schema':'ECOSIM_R160_INDEPENDENT_PLAN_AUDIT_V1',
                  'audited_sampled_plans':len(independent_audits),
                  'hard_failures':sum(bool(v['hard_rule_violations']) for v in independent_audits),
                  'plans_with_unverified_display_or_bonus_eligibility':sum(bool(v['conditional_eligibility_items']) for v in independent_audits),
                  'actual_server_eligibility_verified':False,
                  'gameplay_gate':'STOP'}
    return dict(schema='ECOSIM_R148_SOURCE_BOUNDED_OFFLINE_STRATEGY_V1',
                r157_search_objective=objective,
                r160_independent_audit_summary=r160_summary,
                r157_first_year_sampled_action_comparison=r157_first_year,
                r157_scenario_set_is_hypothetical=True,
                produced_from='R143_V2.1_REUSE_NO_REVERSE_ENGINEERING',
                game_write_actions=0,network_actions=0,final_gameplay_decision='STOP',
                r148_input_readiness=state_gate,
                actual_five_year_score_forecast_validated=False,
                research_to_reuse_to_build='Project costs from portfolio_5y; score proxy from R142; exact displayed-factor and client expense component bridge R144',
                provenance=config['provenance'],start_year=start_year,comparison_baseline_proxy=round(base_score,6),
                assumptions=assumptions,unresolved_dependency_labels=unresolved,
                search_stats=statistics,top_plans=results[:min(10,len(results))],
                highest_worst_sensitivity_among_beam=(dict(start_by_year=robust_order[0]['start_by_year'],
                    worst_mapped_sensitivity_delta=robust_order[0]['worst_of_illustrative_mapped_sensitivities']) if robust_order else None),
                evidence_gaps=gaps,eligibility_warning='No server validation, repeatable/delayed projects and negative conditions not fully established')


def render_markdown(data):
    lines=['# EcoSim R143 — integrált ötéves offline projektstratégia','',
           '**Nem validált EcoSim-előrejelzés. Nem bizonyított győztes döntéssorozat. Játékbeli művelet: 0.**','',
           f"Kiinduló proxyindex: **{data['comparison_baseline_proxy']:.4f}**; indítási év: **{data['start_year']}**.",
           '',f"Projektlimit: **{data['assumptions']['annual_project_limit']}**, forrás: `{data['assumptions']['annual_limit_source']}`.",
           f"Pénzügyi korlát: `{data['assumptions']['budget_source']}`. ",
           '', 'A kijelzett indexértékek kizárólag a kártyák *leképezett, egy alkalommal jelentkező és változatlanul megmaradó* hatásainak érzékenységi számításai, nem valódi öt évre előre jelzett EcoSim-eredmények.',
           '', '## Offline feltételes alternatívák', '',
           '| Rang | Projektindítás évente | 5. évi ismert hatás proxy Δ | 5 év konzervatív projektráfordítás ECU | Nem leképezett hatások |',
           '|---:|---|---:|---:|---:|']
    for n,p in enumerate(data['top_plans'][:5],1):
        years='; '.join(f"{x['year']}: {','.join(map(str,x['start_project_ids'])) or '—'}" for x in p['start_by_year'])
        lines.append(f"| {n} | {years} | {p['terminal_mapped_proxy_delta']:+.4f} | {p['five_year_conservative_card_cost_ecu']:,.0f} | {len(p['excluded_unknown_effects'])} |")
    if data['top_plans']:
        best=data['top_plans'][0]
        lines.extend(['','## Első helyen végzett offline *jelölt*, nem jóváhagyott döntés','',
                      '| Év | Indított projektek | Konzervatív kártyateher (ECU) | Feltételes proxyindex |',
                      '|---:|---|---:|---:|'])
        for row,sc in zip(best['start_by_year'],best['projected_proxy_path_if_baseline_static']):
            lines.append(f"| {row['year']} | {', '.join(row['names']) or 'Nincs új indítás'} | {row['conservative_card_cash_requirement_ecu']:,.0f} | {sc['mapped_proxy_index']:.4f} |")
        s=best['illustrative_half_effect_sensitivity'][-1]
        d=best['illustrative_85pct_yearly_retention_sensitivity'][-1]
        lines.append('')
        lines.append(f"Érzékenység (nem valószínűségi intervallum): felezett projektindex-hatással terminális proxy Δ **{s['mapped_proxy_delta']:+.4f}**, évi 85%-os fennmaradás mellett Δ **{d['mapped_proxy_delta']:+.4f}**.")
        if best['same_year_dependency_conditional']:
            lines.append('**Figyelmeztetés:** azonos évben teljesülő projektelőfeltételt használ; szerveroldali elfogadás nem igazolt.')
    lines.extend(['','## Döntési kapu: STOP','',
                  'Az eredmények hipotetikus projektválasztások, nem bizonyítottan finanszírozhatók vagy szabályosan indíthatók. A gazdaságpolitika, az intézményi működés és a liga nem része a számszerűsített előrejelzésnek.','',
                  '## Hiányzó bizonyítékok',''])
    lines.extend('- '+x for x in data['evidence_gaps'])
    lines.extend(['','## Reprodukálhatóság','',
                  'Használd a `run_offline_strategy.sh` scriptet. A `--budget-per-year` paraméter csak megadott **szcenárió**, nem automatikusan rendelkezésre álló pénz. A keresés korlátos beam search, nem egzakt globális optimum.',''])
    return '\n'.join(lines)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state',default=str(ROOT/'inputs/official_state.template.json'))
    parser.add_argument('--league',default=None,help='Read-only official league snapshot, JSON')
    parser.add_argument('--calibration',default=None,help='Previously approved & restored observations, JSON')
    parser.add_argument('--start-year',type=int,default=1)
    parser.add_argument('--budget-per-year',default=None,help='Illustrative nonnegative ECU envelope, single value or comma-list')
    parser.add_argument('--project-cap',type=int,default=None,help='ILLUSTRATIVE annual cap override')
    parser.add_argument('--beam',type=int,default=14)
    parser.add_argument('--shortlist',type=int,default=36)
    parser.add_argument('--co-start',choices=('conditional','strict'),default='conditional')
    parser.add_argument('--out',default=str(ROOT/'results'/'R143_5Y_STRATEGIES.json'))
    p=parser.parse_args()
    if not 1<=p.start_year<=5:parser.error('start-year must be between 1 and 5')
    state=read_json(p.state)
    budgets=parse_budget(p.budget_per_year,6-p.start_year)
    result=search(state,p.start_year,budgets,p.project_cap,p.beam,p.shortlist,p.co_start=='conditional')
    from decision_evidence import evidence_summary
    result['measurement_and_league_evidence']=evidence_summary(state,p.league,p.calibration)
    write_json(p.out,result)
    md=Path(p.out).with_suffix('.md');md.write_text(render_markdown(result),encoding='utf-8')
    print('R143_INTEGRATED_OFFLINE=PASS; GAME_WRITE=0; PLANS='+str(len(result['top_plans']))+
          '; YEAR5_GAMERESULT=UNVALIDATED; GAMEPLAY_DECISION=STOP; OUT='+str(p.out))

if __name__=='__main__':main()
