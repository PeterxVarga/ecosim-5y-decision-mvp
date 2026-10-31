#!/usr/bin/env python3
"""R149 offline decision desk: existing R148 engine, multiple explicit envelopes,
provenance gates, illustrative robustness, and one auditable decision report.

No network/browser, no JS execution, no writes to EcoSim, and NO game GO output.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))
from strategy_5y import search, read_json, write_json
from readiness_r148 import check_state
from passive_r146 import reconcile_snapshots
from policy_tracks import load_tracks
from joint_5y import evaluate_tracks
from decision_evidence import evidence_summary
from intake_r149 import normalize_capture
from decision_view_r149 import render_offline_html, summarize_first_actions, derived_proof_gates
from paired_calibration_r147 import measure_pairs
from decision_quality_r150 import assess_candidate_quality
from forecast_audit_r151 import audit as audit_frozen_forecasts
from tax_response_r153 import read_document as read_tax_document, evaluate as evaluate_tax_response
from tax_revenue_r154 import validate as validate_tax_revenue, evaluate_counterfactual, build_joint_tradeoff_front
from operating_cash_r155 import validate as validate_operating, evaluate as evaluate_operating, combined_front
from robust_decision_r157 import sampled_first_action_regret
from temporal_cash_r158 import build_timing_bridge

SCHEMA='ECOSIM_R149_OFFLINE_DECISION_MVP_V1'
MODES={'HISTORICAL_ILLUSTRATION','CURRENT_SNAPSHOT_REVIEW'}


def _number(v):
    return type(v) in (int,float) and math.isfinite(v) and v>=0


def _load_config(path):
    cfg=read_json(path)
    if not isinstance(cfg,dict) or cfg.get('schema')!=SCHEMA:
        raise ValueError('Expected '+SCHEMA+' JSON object')
    if cfg.get('mode') not in MODES:raise ValueError('Invalid run mode')
    year=cfg.get('start_year')
    if type(year) is not int or not 1<=year<=5:raise ValueError('start_year must be 1..5')
    cap=cfg.get('project_cap_assumption')
    if cap is not None and (type(cap) is not int or not 0<=cap<=20):
        raise ValueError('project_cap_assumption must be integer 0..20 or null')
    s=cfg.get('search') or {}
    for k,lo,hi in [('beam',1,20),('shortlist',1,40),('options_per_envelope',1,10)]:
        v=s.get(k)
        if type(v) is not int or not lo<=v<=hi:raise ValueError('Invalid bounded search.'+k)
    if s.get('r157_include_scenario_min_search',False) not in (True,False) or type(s.get('r157_include_scenario_min_search',False)) is not bool:
        raise ValueError('Invalid R157 robust search switch')
    if s.get('same_year_conditions') not in ('CONDITIONAL','PRIOR_YEAR_ONLY'):
        raise ValueError('Invalid same_year_conditions')
    state_given=isinstance(cfg.get('state_path'),str) and bool(cfg.get('state_path'))
    capture_given=isinstance(cfg.get('capture_path'),str) and bool(cfg.get('capture_path'))
    if state_given==capture_given:raise ValueError('Provide exactly one: state_path or capture_path (not both)')
    env=cfg.get('annual_envelopes')
    if not isinstance(env,list) or not 1<=len(env)<=5:raise ValueError('1..5 envelopes required')
    ids=set()
    for e in env:
        if not isinstance(e,dict):raise ValueError('Invalid envelope')
        if not isinstance(e.get('id'),str) or not e['id'] or e['id'] in ids:raise ValueError('Envelope IDs unique')
        ids.add(e['id'])
        if e.get('source_class') not in ('EXPLICIT_HYPOTHESIS','USER_DECLARED_BUDGET_NOT_SERVER_VERIFIED'):
            raise ValueError('Envelope must be marked as assumption, never approved budget')
        if not isinstance(e.get('reason'),str) or not e['reason'].strip():raise ValueError('Envelope reason missing')
        vals=e.get('limits_ecu')
        if not isinstance(vals,list) or len(vals)!=(6-year) or not all(_number(v) for v in vals):
            raise ValueError('Envelope requires exactly one nonnegative finite ECU value per remaining year')
    if cfg.get('tax_scenarios_path') is not None and (not isinstance(cfg['tax_scenarios_path'],str) or not cfg['tax_scenarios_path'].strip()):
        raise ValueError('tax_scenarios_path must be a nonempty local path')
    if cfg.get('tax_revenue_scenarios_path') is not None:
        if not isinstance(cfg['tax_revenue_scenarios_path'],str) or not cfg['tax_revenue_scenarios_path'].strip() or not cfg.get('tax_scenarios_path'):
            raise ValueError('Tax-revenue scenario requires an existing source tax path and local filename')
    if cfg.get('operating_scenarios_path') is not None:
        if (not isinstance(cfg['operating_scenarios_path'],str) or not cfg['operating_scenarios_path'].strip()
            or not cfg.get('tax_scenarios_path') or not cfg.get('tax_revenue_scenarios_path')):
            raise ValueError('Operating fiscal scenario needs explicit source tax and tax revenue paths')
    idx=cfg.get('policy_envelope_index',0)
    if type(idx) is not int or not 0<=idx<len(env):raise ValueError('policy_envelope_index outside envelopes')
    return cfg


def _resolve(config_path, filename):
    """Read-only input resolver with an explicit finite trust boundary.

    Configuration paths may refer only to the release tree or the directory
    containing the user's run config (including its subfolders). This prevents
    a pasted config from reading arbitrary host files. Symlink escapes fail.
    Paths relative to the config remain backward-compatible with root-relative
    paths when the config lives inside the release tree.
    """
    if not isinstance(filename,str) or not filename.strip() or '\x00' in filename:
        raise ValueError('R161_INVALID_EVIDENCE_PATH')
    cfg_dir=Path(config_path).resolve().parent
    release=ROOT.resolve()
    raw=Path(filename)
    if raw.is_absolute():
        possibilities=[raw]
    else:
        # Legacy run configs use release-root-relative paths.
        possibilities=[release/raw,cfg_dir/raw]
    for option in possibilities:
        resolved=option.resolve()
        if not resolved.is_relative_to(release) and not resolved.is_relative_to(cfg_dir):
            continue
        if resolved.is_file():return resolved
    raise ValueError('R161_INPUT_PATH_NOT_ALLOWED_OR_MISSING: '+filename)


def _admissible_current_state(state, year):
    """Sufficient for read-only conditional exploration; never server certified.

    In particular, nothing is substituted from the historical R94 fallback.
    No future financial envelope is required: each future envelope remains a
    declared scenario. A formal server validation is impossible here.
    """
    p=state.get('provenance') or {};team=state.get('team') or {};market=state.get('market') or {}
    required=[p.get('source_evidence_id'),p.get('captured_at_local'),p.get('team'),
              p.get('market'),p.get('source')]
    missing=[]
    if not all(isinstance(x,str) and x.strip() for x in required):missing.append('AUTHORED_SOURCE_PROVENANCE')
    if p.get('current_period')!=year:missing.append('CURRENT_PERIOD_MISMATCH_OR_MISSING')
    if not (isinstance(team.get('initially_active_project_ids'),list) and
            isinstance(team.get('already_selected_new_project_ids_current_period'),list)):
        missing.append('ACTIVE_AND_SELECTED_PROJECTS')
    if type(team.get('project1_active_previous_period')) is not bool:missing.append('PRIOR_PROJECT1_BOOLEAN')
    if type(market.get('maxProjectPerTurn')) is not int:missing.append('MARKET_PROJECT_CAP')
    if p.get('capture_mode') != 'CURRENT_READONLY':missing.append('HISTORICAL_OR_UNCLASSIFIED_CAPTURE_IS_NOT_LIVE')
    if not isinstance(team.get('baseline_smartcity_factors'),dict):missing.append('CURRENT_FACTOR_VECTOR')
    if (p.get('source_evidence_id') or '').upper().startswith(('REPLACE','EXAMPLE','TODO')):
        missing.append('PLACEHOLDER_SOURCE_EVIDENCE_ID')
    if (p.get('captured_at_local') or '').upper().startswith(('REPLACE','EXAMPLE','TODO')):
        missing.append('PLACEHOLDER_CAPTURE_TIMESTAMP')
    if not isinstance(market.get('smartcity_total_weights'),dict):missing.append('CURRENT_MARKET_WEIGHTS')
    # Supplementary validation done by the existing R148 gate and strategy input parser.
    return missing


def _scenario_family(cfg, state):
    missing=_admissible_current_state(state,cfg['start_year']) if cfg['mode']=='CURRENT_SNAPSHOT_REVIEW' else []
    if cfg['mode']=='CURRENT_SNAPSHOT_REVIEW' and cfg['project_cap_assumption'] is not None:
        # The user supplied an actual market cap in state; avoid accidentally overriding it.
        missing.append('PROJECT_CAP_OVERRIDE_FORBIDDEN_IN_CURRENT_SNAPSHOT_MODE')
    if missing:return missing
    return []


def _plan_key(plan):
    return tuple(tuple(x['start_project_ids']) for x in plan['start_by_year'])


def _scenario_status(costs, envelope, start_year):
    rows=[{'year':start_year+i,'hypothetical_envelope_ecu':round(float(b),2),
           'conservative_project_need_ecu':round(float(c),2),
           'within_hypothetical_envelope':c<=b+1e-8}
          for i,(c,b) in enumerate(zip(costs,envelope))]
    return {'passes_this_hypothetical_envelope':all(x['within_hypothetical_envelope'] for x in rows),
            'per_year':rows,'verified_financing':False}


def _build_candidate_union(rows, cfg, max_results=20):
    unique={}
    for s in rows:
        for p in s['candidates']:
            key=_plan_key(p)
            if key not in unique:unique[key]={'plan':p,'found_in_envelopes':[]}
            unique[key]['found_in_envelopes'].append(s['id'])
    combined=[]
    for k,v in unique.items():
        p=v['plan'];costs=[x['conservative_card_cash_requirement_ecu'] for x in p['start_by_year']]
        r160=p.get('r160_independent_constraint_replay')
        if not isinstance(r160,dict) or r160.get('hard_rule_violations') or r160.get('gameplay_gate')!='STOP':
            raise ValueError('R160 independent constraint replay required for every compared candidate')
        checks={e['id']:_scenario_status(costs,e['limits_ecu'],cfg['start_year']) for e in cfg['annual_envelopes']}
        within=[i for i,c in checks.items() if c['passes_this_hypothetical_envelope']]
        # All plans in the set are inspected across every envelope. This is
        # *not* a probability, and unknown actual cash is not silently inferred.
        record={
            'candidate_id': 'P-'+hashlib.sha256(json.dumps(k).encode()).hexdigest()[:12],
            'project_ids_by_year':[list(yy) for yy in k],
            'project_names_by_year':[r['names'] for r in p['start_by_year']],
            'conservative_project_need_ecu_by_year':[round(x,2) for x in costs],
            'five_year_conservative_project_need_ecu':p['five_year_conservative_card_cost_ecu'],
            'found_by_search_in':v['found_in_envelopes'],
            'inside_explicit_hypothetical_envelopes':within,
            'envelope_comparison':checks,
            'r157_hypothetical_15pct_cash_shock':{e['id']:{'all_years_fit':all(cost<=0.85*limit+1e-8 for cost,limit in zip(costs,e['limits_ecu'])),
                'verified_spendable_cash':False} for e in cfg['annual_envelopes']},
            'mapped_terminal_proxy_delta':p['terminal_mapped_proxy_delta'],
            'r157_robust_sensitivity':p['r157_robust_sensitivity'],
            'r157_scenario_min_clamp_only_mapped_delta':p['r157_robust_sensitivity']['scenario_min_clamp_only_mapped_delta'],
            'worst_of_existing_illustrative_mapped_sensitivities':p['worst_of_illustrative_mapped_sensitivities'],
            'unmapped_or_uncertain_project_effect_occurrences':len(p['excluded_unknown_effects']),
            'same_year_co_start_condition_unverified':p['same_year_dependency_conditional'],
            'r160_independent_constraint_replay':r160,
            'r160_actual_game_outcome_comparability':'UNDETERMINED_NO_FULL_CITY_TRANSITION',
            'actual_game_terminal_index':None,
            'server_project_acceptance':None,
            'cash_and_credit_authorized':False,
            'gameplay_gate':'STOP',
            'qualification':'OFFLINE_HYPOTHETICAL_CANDIDATE_NOT_A_GAME_FORECAST'
        }
        combined.append(record)
    # No "winning" candidate without model calibration. Order the DESCRIPTIVE
    # exploratory shortlist by how many budgets it fits then mapped worst stress.
    if cfg['search'].get('r157_include_scenario_min_search',False):
        combined.sort(key=lambda p:(-len(p['inside_explicit_hypothetical_envelopes']),
                                    -p['r157_scenario_min_clamp_only_mapped_delta'],
                                    -p['mapped_terminal_proxy_delta'],
                                    p['unmapped_or_uncertain_project_effect_occurrences'],
                                    p['five_year_conservative_project_need_ecu']))
    else:
        combined.sort(key=lambda p:(-len(p['inside_explicit_hypothetical_envelopes']),
                                    -p['worst_of_existing_illustrative_mapped_sensitivities'],
                                    -p['mapped_terminal_proxy_delta'],
                                    p['unmapped_or_uncertain_project_effect_occurrences'],
                                    p['five_year_conservative_project_need_ecu']))
    # Deliberately expose the complete source-conditioned minimax comparison,
    # while keeping R150's original descriptive ranking intact.
    return combined if max_results is None else combined[:max_results]


def _priority_questions(state, gate, scenario_rows, policy_rows):
    missing={x['field'] for x in gate['specific_missing_or_invalid_evidence']}
    questions=[]
    def add(k,why,method,blocks):
        questions.append({'key':k,'reason':why,'smallest_safe_evidence':method,
                          'blocks':blocks,'does_not_authorize_ui_mutation':True})
    if {'source_evidence_id','timestamp','team','market','period'} & missing:
        add('CURRENT_PROVENANCE','Without current team/period provenance the baseline may be stale',
            'Authorized official export or unchanged summary screenshot with market, team, period, timestamp',
            ['CURRENT_GAME_SPECIFIC_SEARCH'])
    if {'project_cap','active_projects','current_selections','prior_project1'} & missing:
        add('PROJECT_CAP_AND_STATE','A 4/year spoken statement does not establish the effective current allowance',
            'Official market cap plus previous project1 and already-selected/currently-running IDs',
            ['SERVER_ELIGIBILITY'])
    if {'baseline_index_factors','current_index_weights'} & missing:
        add('BASELINE_AND_WEIGHTS','The proxy score cannot be transferred from historical R94 without them',
            'Same-period factor table and market weight configuration',
            ['CURRENT_SCORE_CALCULATION'])
    if 'loan_rates' in missing or {'confirmed_spendable_cash','committed_costs'} & missing:
        add('FINANCE_PROOF','Net operating result and hypothetical envelopes are not spendable money',
            'Official available cash, obligations, lending terms and support settlement by period',
            ['AFFORDABILITY_AND_CREDIT'])
    if 'official_preview' in missing:
        add('PAIRED_PREVIEW','Without matched before/after model residuals predictive accuracy remains unknown',
            'Only an approved, preverified reversible same-period comparison or official preview export',
            ['MODEL_CALIBRATION'])
    if policy_rows:
        add('POLICY_CAUSAL_RESPONSES','Tax, fees and institutions are still user assumptions, not calibrated controls',
            'Official rules, passive observations and independently matched safe measurement pairs',
            ['COMPLETE_CITY_POLICY_OPTIMIZATION'])
    add('COMPETITION_DYNAMICS','Competitor moves and migration can alter realized terminal rankings',
        'Read-only league snapshots after each finalized period, with contemporaneous ranks and decisions',
        ['YEAR5_RELATIVE_RANK_PREDICTION'])
    add('COMPETITION_PERMISSION','The competition may regulate third-party automation/optimization',
        'Current written competition rules or organizer confirmation',
        ['COMPLIANCE'])
    return questions


def _one_envelope(state,cfg,envelope):
    a=cfg['search']
    result=search(state,cfg['start_year'],envelope['limits_ecu'],cfg['project_cap_assumption'],
                  a['beam'],a['shortlist'],a['same_year_conditions']=='CONDITIONAL')
    picked=list(result['top_plans'][:a['options_per_envelope']])
    if a.get('r157_include_scenario_min_search',False):
        # Reuse EXACT same beam implementation; only its ranking changes.
        alternative=search(state,cfg['start_year'],envelope['limits_ecu'],cfg['project_cap_assumption'],
                           a['beam'],a['shortlist'],a['same_year_conditions']=='CONDITIONAL',
                           objective='scenario_min')
        seen={_plan_key(p) for p in picked}
        for plan in alternative['top_plans'][:a['options_per_envelope']]:
            if _plan_key(plan) not in seen:
                seen.add(_plan_key(plan));picked.append(plan)
    return {'id':envelope['id'],'source_class':envelope['source_class'],
            'stated_reason':envelope['reason'],
            'start_year':cfg['start_year'],
            'candidate_count':len(picked),
            'candidates':picked,
            'search_method':'BOUNDED_BEAM_HEURISTIC_NOT_PROVEN_GLOBAL_OPTIMUM',
            'official_state_ready':not result['r148_input_readiness']['specific_missing_or_invalid_evidence'],
            'finance_is_real_world_approved':False,
            'gameplay_gate':'STOP'}


def _metadata(path):
    raw=path.read_bytes()
    return {'filename':path.name,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}


def validate_tax_context(cfg, state, tax_doc):
    """Fail before running five-year search if tax data contradict the input mode."""
    if cfg['mode']=='CURRENT_SNAPSHOT_REVIEW' and tax_doc['source_class']=='SYNTHETIC_TEST_ONLY':
        raise ValueError('Synthetic tax scenarios forbidden in current snapshot decision report')
    current_factor=(state.get('team') or {}).get('baseline_smartcity_factors')
    if current_factor is None and cfg['mode']=='HISTORICAL_ILLUSTRATION':
        current_factor=read_json(ROOT/'data/ECOSIM_R141_PROJECT_PROXY.json')['baseline_from_UI']
    if current_factor is not None and abs(current_factor['Vállalkozóbarátság']-tax_doc['baseline']['observed_company_friendliness_percent'])>0.04:
        raise ValueError('Tax source formula baseline differs from actual decision state factor')
    weights=(state.get('market') or {}).get('smartcity_total_weights')
    if cfg['mode']=='HISTORICAL_ILLUSTRATION' and weights is None:
        from r142_proxy_reference import WEIGHTS
        weights={k:p[0] for k,p in WEIGHTS.items()}
    return weights

def make_report(cfg_path):
    cfg_path=Path(cfg_path).resolve();cfg=_load_config(cfg_path)
    source_name='state'
    if cfg.get('capture_path'):
        state_path=_resolve(cfg_path,cfg['capture_path'])
        state,capture_receipt=normalize_capture(read_json(state_path))
        source_name='read_only_capture'
        if cfg['mode']=='CURRENT_SNAPSHOT_REVIEW' and state['provenance']['capture_mode']!='CURRENT_READONLY':
            raise ValueError('Historical capture cannot be used as current read-only snapshot')
        if cfg['start_year']!=state['provenance']['current_period']:
            raise ValueError('Capture period and requested start_year disagree')
    else:
        state_path=_resolve(cfg_path,cfg['state_path']);state=read_json(state_path)
        capture_receipt=None
    gate=check_state(state)
    problems=_scenario_family(cfg,state)
    if cfg['mode']=='CURRENT_SNAPSHOT_REVIEW' and not problems:
        # Strict typed validation, fail closed without a fallback to test-round data.
        from portfolio_5y import project_index
        from strategy_5y import derive_config
        derive_config(state,project_index(),cfg['start_year'],[0.]*(6-cfg['start_year']),None)
    baseline_filename=cfg.get('historical_read_only_snapshots_path')
    historical=None
    if baseline_filename:
        baseline_path=_resolve(cfg_path,baseline_filename)
        historical=reconcile_snapshots(read_json(baseline_path))
    provenance_inputs={'run_config':_metadata(cfg_path),source_name:_metadata(state_path)}
    if baseline_filename:provenance_inputs['historical_passive_summary']=_metadata(baseline_path)
    tax_doc=None;tax_weights=None
    if cfg.get('tax_scenarios_path'):
        tax_path=_resolve(cfg_path,cfg['tax_scenarios_path'])
        tax_doc,_=read_tax_document(tax_path)
        tax_weights=validate_tax_context(cfg,state,tax_doc)
        provenance_inputs['tax_scenarios']=_metadata(tax_path)
    fiscal_doc=None
    if cfg.get('tax_revenue_scenarios_path'):
        revenue_path=_resolve(cfg_path,cfg['tax_revenue_scenarios_path'])
        fiscal_doc=validate_tax_revenue(read_json(revenue_path))
        provenance_inputs['tax_revenue_scenarios']=_metadata(revenue_path)
        if fiscal_doc['source_class']!=tax_doc['source_class']:
            raise ValueError('Tax and fiscal provenance modes must agree; never silently mix synthetic and operator sources')
        if cfg['mode']=='CURRENT_SNAPSHOT_REVIEW' and fiscal_doc['source_class']=='SYNTHETIC_TEST_ONLY':
            raise ValueError('Synthetic fiscal bases prohibited in current game review')
    operating_doc=None
    if cfg.get('operating_scenarios_path'):
        operating_path=_resolve(cfg_path,cfg['operating_scenarios_path'])
        operating_doc=validate_operating(read_json(operating_path))
        provenance_inputs['operating_scenarios']=_metadata(operating_path)
        if operating_doc['source_class']!=tax_doc['source_class'] or operating_doc['source_class']!=fiscal_doc['source_class']:
            raise ValueError('Operating, tax and tax-revenue source classes must match')
        if cfg['mode']=='CURRENT_SNAPSHOT_REVIEW' and operating_doc['source_class']=='SYNTHETIC_TEST_ONLY':
            raise ValueError('Synthetic operating bases prohibited in current snapshot mode')
        if {p['id'] for p in operating_doc['paths']}!={p['id'] for p in tax_doc['paths']}:
            raise ValueError('Operating path IDs must match source tax path IDs')
    rows=[]
    if not problems:
        for e in cfg['annual_envelopes']:
            rows.append(_one_envelope(state,cfg,e))
    policies=[]
    policy_path=cfg.get('policy_tracks_path')
    if policy_path:
        path=_resolve(cfg_path,policy_path)
        tracks=load_tracks(path);provenance_inputs['policy_tracks']=_metadata(path)
        if not problems:
            # One designated envelope avoids an O(envelopes x tracks x search)
            # explosion; descriptive and not a global policy optimization.
            base=cfg['annual_envelopes'][cfg.get('policy_envelope_index',0)]
            pr=evaluate_tracks(state,cfg['start_year'],tracks,base['limits_ecu'],
                               cfg['project_cap_assumption'],
                               min(4,cfg['search']['beam']),min(10,cfg['search']['shortlist']))
            for row in pr['tracks']:
                # Expose a compact, bounded, provenance-labelled policy comparison.
                opts=row.get('joint_options') or []
                policies.append({'track_id':row['track_id'],'scenario_mode':row.get('scenario_mode'),
                                 'search_status':row['status'],
                                 'illustrative_first_option':({
                                     'project_ids_by_year':[x['start_project_ids'] for x in opts[0]['project_starts']],
                                     'mapped_terminal_delta':opts[0]['joint_terminal_counterfactual_delta'],
                                     'finance_proof':False,'actual_terminal_score':None}
                                     if opts else None),
                                 'gameplay_gate':'STOP'})
    league_file=cfg.get('league_observations_path')
    calibration_file=cfg.get('paired_plan_observations_path')
    if league_file:
        path=_resolve(cfg_path,league_file)
        provenance_inputs['league_readonly']=_metadata(path)
    if calibration_file:
        path=_resolve(cfg_path,calibration_file)
        provenance_inputs['paired_plan_observations']=_metadata(path)
        paired=measure_pairs(read_json(path))
    else:
        paired=measure_pairs({'schema':'ECOSIM_R147_PAIRED_PLAN_OBSERVATIONS_V1','pairs':[]})
    forecast_file=cfg.get('forecast_audit_path')
    if forecast_file:
        path=_resolve(cfg_path,forecast_file)
        provenance_inputs['frozen_forecast_fact_audit']=_metadata(path)
        frozen_audit=audit_frozen_forecasts(read_json(path))
    else:
        frozen_audit=audit_frozen_forecasts({'schema':'ECOSIM_R151_FORECAST_AUDIT_V1','comparisons':[]})
    evidence=evidence_summary(state,str(_resolve(cfg_path,league_file)) if league_file else None,None)
    # The full *sampled* union (at most envelopes × options_per_envelope)
    # is used for quality comparisons; the R149 top-20 public list remains
    # backwards compatible and cannot hide an efficient sampled candidate.
    all_sampled=_build_candidate_union(rows,cfg,max_results=None)
    quality=assess_candidate_quality(all_sampled,cfg['annual_envelopes'],cfg['start_year'])
    r157_families={row['id']:sampled_first_action_regret(row['candidates']) for row in rows}
    tax_report=None
    if tax_doc is not None:
        tax_report=evaluate_tax_response(tax_doc,all_sampled,cfg['start_year'],tax_weights)
        tax_report['current_market_state_authenticity']='UNVERIFIED'
        if cfg['mode']=='HISTORICAL_ILLUSTRATION' and (state.get('market') or {}).get('smartcity_total_weights') is None:
            tax_report['index_weight_source']='R141_HISTORICAL_TEST_UI_WEIGHTS'
    fiscal_report=None
    if fiscal_doc is not None:
        fiscal_rows=[]
        for path in tax_doc['paths']:
            val=evaluate_counterfactual(fiscal_doc,tax_doc['baseline']['decisions'],path['decisions_by_year'],start_year=cfg['start_year'])
            fiscal_rows.append({'tax_path_id':path['id'], 'fiscal_comparison':val})
        fiscal_report={'schema':'ECOSIM_R154_SOURCE_ANCHORED_FOUR_TAX_TRADEOFFS_V1',
                       'source_class':fiscal_doc['source_class'],
                       'calculation_source':'840.41fdc8e1.chunk.js Webpack module 5168 Bi/_i/Ui/Yi',
                       'path_counterfactuals':fiscal_rows,
                       'all_project_candidates_share_the_same_exogenous_tax_bases':True,
                       'candidate_dependent_business_car_population_or_housing':'UNMODELLED',
                       'taxable_base_feedback':'UNMODELLED_NOT_ZERO',
                       'revenue_cannot_be_added_to_project_budget':True,
                       'actual_five_year_cash_or_profit':None,
                       'gameplay_gate':'STOP'}
    operating_report=None;operating_front=None
    if operating_doc is not None:
        operating_report={'schema':'ECOSIM_R155_SOURCE_OPERATING_PATHS_V1',
                          'source_class':operating_doc['source_class'],
                          'path_counterfactuals':[evaluate_operating(operating_doc,p,cfg['start_year']) for p in operating_doc['paths']],
                          'source_coverage':'SIX_FEES_EIGHT_WAGE_COMPONENTS_SEVEN_MATERIAL_COMPONENTS',
                          'population_company_capacity_and_competitor_feedback':'UNKNOWN_NOT_ZERO',
                          'partial_income_not_spendable_budget':True,'gameplay_gate':'STOP'}
        operating_front=combined_front(all_sampled,fiscal_report,operating_report,tax_report)
    # R158: describe temporally aligned partial fiscal/project-card cash
    # exposure. Does not feed hypothetical receipts back into search budgets.
    temporal_cash=build_timing_bridge(all_sampled,fiscal_report,operating_report,tax_report,cfg['start_year'])
    pctx=state.get('provenance') or {}
    context={k:pctx.get(k) for k in ('team','market','round','source_evidence_id','capture_mode','observed_column_kind')}
    context['period']=pctx.get('current_period')
    output={
        'schema':'ECOSIM_R149_OFFLINE_DECISION_DESK_RESULT_V1',
        'run_mode':cfg['mode'],'start_year':cfg['start_year'],
        'source_context':context,'r150_sampled_quality':quality,
        'game_writes':0,'browser_actions':0,'network_actions':0,
        'codex_called':False,'gameplay_gate':'STOP',
        'game_result_prediction_validated':False,
        'r160_independent_plan_audits':{'schema':'ECOSIM_R160_REPORT_AUDITS_V1',
            'plans_replayed':len(all_sampled),
            'hard_errors':sum(bool(c['r160_independent_constraint_replay']['hard_rule_violations']) for c in all_sampled),
            'conditional_or_unknown_server_acceptance':sum(c['r160_independent_constraint_replay']['status']=='CONDITIONAL_NOT_SERVER_VERIFIED' for c in all_sampled),
            'all_real_economy_pareto_dominance_unknown':True,'gameplay_gate':'STOP'},
        'current_snapshot_usable_for_conditional_search':cfg['mode']=='CURRENT_SNAPSHOT_REVIEW' and not problems,
        'current_snapshot_blockers':problems,
        'inputs':provenance_inputs,
        'normalized_capture_receipt':capture_receipt,
        'first_year_action_families':summarize_first_actions(rows,cfg),
        'proof_gates':derived_proof_gates(cfg,state,gate,problems),
        'input_readiness':gate,
        'comparison_envelopes':[{'id':x['id'],'limits_ecu':x['limits_ecu'],
                                 'source_class':x['source_class'],'reason':x['reason'],
                                 'not_approved_money':True} for x in cfg['annual_envelopes']],
        'scenario_searches':[{k:v for k,v in row.items() if k!='candidates'} for row in rows],
        'candidate_comparison':all_sampled[:20],
        'policy_track_comparison':policies,
        'r153_source_backed_tax_sensitivity':tax_report,
        'r154_source_four_tax_fiscal_tradeoffs':fiscal_report,
        'r154_conditional_joint_pareto':build_joint_tradeoff_front(all_sampled,tax_report,fiscal_report) if fiscal_report else None,
        'r155_source_operating_cash_tradeoffs':operating_report,
        'r155_conditional_joint_operating_pareto':operating_front,
        'r158_annual_partial_cash_timing':temporal_cash,
        'passive_historical_reconciliation':historical,
        'league_readonly_evidence':evidence['league_read_only_snapshot'],
        'r151_forecast_fact_audit':frozen_audit,
        'calibration_evidence':{'paired_approved_plan_observations':paired['pairs_with_operator_control_declarations'],
                                'paired_descriptive_plan_comparisons':paired,
                                'realized_yearly_transition_validated':False,
                                'historical_p0_fact_vs_p1_plan_not_a_realized_transition':True,
                                'descriptive_only_legacy_evidence':evidence['paired_candidate_preview_comparison']['status']},
        'next_evidence_to_collect':_priority_questions(state,gate,rows,policies),
        'r157_robust_search_enabled':bool(cfg['search'].get('r157_include_scenario_min_search',False)),
        'r157_sampled_first_year_regret_by_envelope':r157_families,
        'r157_robust_scenarios_are_probabilities':False,
        'r157_scenario_min_is_true_outcome_bound':False,
        'known_unmodeled_dynamics':['Business count feedback','Labor/population migration',
                                    'Tax and fee causal responses','Institution capacities and payroll responses',
                                    'Unverified server lending rules','Actual competition opponents'],
        'recommended_game_action':None,
        'decision_message':('STOP: current snapshot lacks required facts; no actual game-specific plan produced'
                            if problems else 'STOP: only bounded offline hypotheses, no verified five-year winner')
    }
    return output


def render_md(out):
    result=['# EcoSim R149 — belső, offline döntési MVP','',
            '**Kizárólag döntéselőkészítés. Játékbeli művelet: 0. Véglegesítés: STOP.**','',
            f"Mód: `{out['run_mode']}`; kezdőév: **{out['start_year']}**. Aktuális állapothoz kapcsolható: **{'igen, feltételesen' if out['current_snapshot_usable_for_conditional_search'] else 'nem'}**.",
            '','## Forrásintegritás', '']
    for key,v in out['inputs'].items():result.append(f"- `{key}`: `{v['filename']}` — SHA-256 `{v['sha256']}`")
    result.extend(['','## Ötéves, feltételezett projektkeretek','',
                   '| Keret | Éves összegek (ECU) | Jelleg |','|---|---|---|'])
    for x in out['comparison_envelopes']:
        result.append(f"| {x['id']} | {', '.join(f'{v:,.0f}' for v in x['limits_ecu'])} | {x['source_class']} |")
    result.extend(['','## Többkeretes jelöltösszehasonlítás','',
                  'A *fedettség* az itt megadott, feltételezett keretekre vonatkozik, **nem valószínűség** és nem valódi pénzügyi jóváhagyás.','',
                  '| Jelölt | Évenként indított projektek | Keretfedettség | 5. évi részleges proxy Δ | Stresszelt részleges proxy Δ (minimum) |','|---|---|---|---:|---:|'])
    for p in out['candidate_comparison'][:8]:
        starts='; '.join(','.join(map(str,v)) or '—' for v in p['project_ids_by_year'])
        result.append(f"| `{p['candidate_id']}` | {starts} | {len(p['inside_explicit_hypothetical_envelopes'])}/{len(out['comparison_envelopes'])} | {p['mapped_terminal_proxy_delta']:+.4f} | {p['worst_of_existing_illustrative_mapped_sensitivities']:+.4f} |")
    if not out['candidate_comparison']:
        result.extend(['','**Nincs kiadható jelölt:** hiányzik a minimális, megfelelő eredetű aktuális adat vagy a kereséshez szükséges konfiguráció.'])
    robust=out.get('r157_sampled_first_year_regret_by_envelope') or {}
    if robust:
        result.extend(['','## R157 – mintabeli legrosszabb forgatókönyv szerinti elsőéves lépések', '',
          'Négy, **szintetikus** hatásintenzitás és fennmaradási pálya. A számítás csak az ismert faktorokra és a telítettségi bizonytalanságra vonatkozik. Nem előrejelzés, nem valódi regret és nem győzelmi valószínűség.',
          '| Feltételezett keret | Elsőéves projektek | Legjobb mintabeli forgatókönyv-minimum Δ | Mintabeli különbség |',
          '|---|---|---:|---:|'])
        for eid,p in robust.items():
            for family in p['families'][:5]:
                result.append(f"| {eid} | {','.join(map(str,family['first_year_project_ids'])) or '—'} | {family['best_sampled_scenario_min']:+.5f} | {family['gap_from_best_sampled_scenario_min']:.5f} |")
    r160=out.get('r160_independent_plan_audits') or {}
    if r160:
        result.extend(['','## R160 – független korlát- és költségellenőrzés','',
          f"**{r160['plans_replayed']} mintaterv újraszámítva**, hard eltérés: **{r160['hard_errors']}**,",
          f"feltételes szerverelfogadás: **{r160['conditional_or_unknown_server_acceptance']}**.",
          'A kártya- és kijelzett előfeltétel-szabályok következetessége **nem** szerverjogosultság. A nem modellezett hatások száma nem negatív indexhatás; valódi pontszám-dominancia **ISMERETLEN**.'])
    q=out['r150_sampled_quality']
    result.extend(['','## R150 – mintán belüli Pareto-szűrés és szcenáriós veszteségek','',
      'A Pareto-szűrés **csak a heurisztika által talált tervekre és részleges, nem kalibrált mutatókra** vonatkozik; nem bizonyít valódi dominanciát vagy globális optimumot.','',
      '| Feltételezett keret | Mintában beleférő tervek | Mintabeli nem dominált jelöltek |','|---|---:|---|'])
    for eid, data in q['envelope_frontiers'].items():
        result.append(f"| {eid} | {data['within_hypothetical_budget_count']} | {', '.join(data['nondominated_in_sample_ids'][:12]) or '—'} |")
    result.extend(['','Az „elszalasztott részleges indexnyereség” csak **a megvizsgált, feltételes tervekhez képest** értelmezhető, nem játékbeli regret vagy győzelmi esély.'])
    if out['policy_track_comparison']:
        result.extend(['','## Működési döntési szcenáriók',''])
        for r in out['policy_track_comparison']:
            msg='nincs feltételes jelölt' if r['illustrative_first_option'] is None else f"első ismert részleges proxy Δ: {r['illustrative_first_option']['mapped_terminal_delta']:+.4f}"
            result.append(f"- `{r['track_id']}` ({r['scenario_mode']}): {msg}; **nem kalibrált EcoSim-válasz**.")
    tax=out.get('r153_source_backed_tax_sensitivity')
    if tax:
        result.extend(['','## R153 – forrásképlettel számított adó-/díjérzékenység', '',
           f"Forrásosztály: `{tax['source_class']}`. A kliens `Re(e,t)` képletének SHA-256 hivatkozása: `{tax['source_expression_sha256']}`.",
           'A vállalkozóbarátság közvetlen részindex-hozzájárulása **feltételesen** számolható. Nem számoljuk a megváltozó adóbevételeket, vállalatmozgást és az évenkénti gazdasági visszacsatolást.', '',
           '| Adó/díj forgatókönyv | Kandidátus | Ötödik évi közvetlen adóhatás (részleges indexpont) | Projektproxy + adóhatás |',
           '|---|---|---:|---:|'])
        for path in tax['paths']:
            for cand in path['conditional_candidate_comparison'][:3]:
                d=cand['tax_delta_in_terminal_partial_index']; v=cand['mapped_terminal_proxy_plus_tax_path_delta']
                d_text=format(d,"+.5f") if d is not None else "ismeretlen"
                v_text=format(v,"+.5f") if v is not None else "ismeretlen"
                result.append(f"| {path['path_id']} | `{cand['candidate_id']}` | {d_text} | {v_text} |")
        result.append('**Nincs igazolt adóbevétel, hitelkeret vagy játékbeli nyerő eredmény.**')
    operating=out.get('r155_source_operating_cash_tradeoffs')
    if operating:
        result.extend(['','## R155 – hat szolgáltatási bevétel, intézményi bér és anyag részkiadás','',
          '**KIZÁRÓLAG szintetikus/feltételes működési pályák; nem teljes városmérleg vagy engedélyezett költségvetés.**',
          '| Forgatókönyv | Ötéves díjbevétel Δ ECU | Ötéves lefedett intézményi kiadás Δ ECU | Részleges nettó Δ ECU |',
          '|---|---:|---:|---:|'])
        for p in operating['path_counterfactuals']:
            result.append(f"| `{p['path_id']}` | {p['five_year_six_fee_delta_ecu']:+,.0f} | {p['five_year_covered_institution_cost_delta_ecu']:+,.0f} | {p['five_year_partial_operating_net_delta_ecu']:+,.0f} |")
        front=out.get('r155_conditional_joint_operating_pareto') or {}
        result.append('A 3 tengelyes Pareto-front kizárólag a megtalált jelöltek részleges, változatlan külső állapotú összehasonlítása; a vállalati és lakossági dinamika ismeretlen.')
        result.append(f"Mintabeli összevetés: **{front.get('evaluated',0)}**, nem dominált: **{len(front.get('front',[]))}**.")
    timing=out.get('r158_annual_partial_cash_timing') or {}
    if timing.get('status')=='CONDITIONAL_PARTIAL_CASH_TIMING_NOT_GAME_SOLVENCY':
        result.extend(['','## R159 – komponensenként korrigált éves pénzügyi időzítés','',
          '**Az ötéves adó- és működési különbség nem egyenlő az azonnal elérhető pénzzel.** Nincs igazolt nyitó készpénz, támogatási időpont, hitelkeret vagy szerveroldali elszámolás. Az alábbi nulla nyitó pénzes kísérlet NEM tényleges finanszírozási hiány.', '',
          '| Projekt | Adó/díj/intézmény pálya | 5 év részleges nettó projektkártya után | Azonnali elszámolás: legnagyobb hipotetikus kumulált hiány | Pozitív pénzáram +1 év: legnagyobb hipotetikus kumulált hiány |',
          '|---|---|---:|---:|---:|'])
        for v in timing['combinations'][:12]:
            result.append(f"| `{v['candidate_id']}` | `{v['path_id']}` | {v['five_year_partial_net_after_card_cost_ecu']:+,.0f} | {v['hypothetical_peak_zero_opening_cash_shortfall_immediate_ecu']:,.0f} | {v['hypothetical_peak_zero_opening_cash_shortfall_positive_receipts_deferred_ecu']:,.0f} |")
        result.extend(['', '| Pálya | Feltételes indexszel vizsgált jelöltek | A három hipotetikus szempont szerint nem dominált jelöltek |','|---|---:|---:|'])
        for f in timing['sampled_three_axis_timing_front_by_path']:
            result.append(f"| `{f['path_id']}` | {f['evaluated_with_mapped_index']} | {f['nondominated_in_sample']} |")
        result.append('**Döntési kapu: STOP.** Sem a pozitív részbevétel, sem az éves szintetikus cash-nyomás nem jogosít projektindításra.')
    cal=out['calibration_evidence']['paired_descriptive_plan_comparisons']
    result.extend(['','## Azonos periódusú PLAN-párok (nem éves ténykalibráció)', '',
                   f"Megadott pár: **{cal['pair_count']}**; saját nyilatkozatú kontrollokkal: **{cal['pairs_with_operator_control_declarations']}**; valódi ötéves predikciós pontosság: **ismeretlen**."])
    forecast=out.get('r151_forecast_fact_audit')
    if forecast:
        result.extend(['','## R151 – előre rögzített becslés és későbbi tény egyeztetése','',
          f"Tényleges, operátor által hivatalosnak jelölt PLAN–FACT pár: **{forecast['operator_declared_official_pair_count']}**; teljes indexre szóló modelljóslattal párosítható: **{forecast['paired_full_model_prediction_count']}**.",
          f"Operátor által megadott, teljes modellre számolt MAE: **{forecast['operator_declared_frozen_full_model_vs_fact_mae'] if forecast['operator_declared_frozen_full_model_vs_fact_mae'] is not None else 'ismeretlen'}**; függetlenül hitelesített pontosság: **ismeretlen**.",
          'A tesztfordulós p0 tény és p1 terv **nem** egy megfigyelt PLAN–FACT mérési pár.'])
    league=out['league_readonly_evidence']
    result.extend(['','## Liga pillanatkép','',
                   f"Állapot: `{league['status']}`. Teljes ligaadat és szervezői helyezési szabály hiányában továbbjutás nem állapítható meg."])
    if out['passive_historical_reconciliation']:
        result.extend(['','## Történeti, passzív egyeztetés',''])
        for s in out['passive_historical_reconciliation']['snapshots']:
            result.append(f"- `{s['id']}` ({s['kind']} p{s['period']}): megjelenített {s['displayed_total_index']:.2f}; visszaszámolt {s['reconstructed_from_display_factors']:.4f}; ez **nem** megfigyelt állapotátmenet.")
    result.extend(['','## A következő legkisebb biztonságos bizonyítékok',''])
    for x in out['next_evidence_to_collect']:
        result.append(f"- **{x['key']}**: {x['smallest_safe_evidence']}. ({x['reason']})")
    result.extend(['','## Végső kapu','',
                   '**STOP.** A projektlimit, a hitel/likviditás, a teljes várospolitikai hatásfüggvények és a terv–tény kalibráció nem igazoltak teljes körűen. A kereső heurisztikus, a stresszértékek nem megbízhatósági intervallumok. Az EcoSimben semmilyen műveletet nem hajtunk végre.',''])
    return '\n'.join(result)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',default=str(ROOT/'inputs/mvp_run.illustrative.json'))
    p.add_argument('--out-dir',default=str(ROOT/'results/R149_MVP_DEMO'))
    a=p.parse_args()
    report=make_report(a.config)
    out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True)
    write_json(out/'DECISION_DESK.json',report)
    (out/'DECISION_DESK.md').write_text(render_md(report),encoding='utf8')
    (out/'INPUT_HASHES.json').write_text(json.dumps(report['inputs'],ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (out/'DECISION_DESK.html').write_text(render_offline_html(report),encoding='utf8')
    print('R149_MVP=PASS; candidates='+str(len(report['candidate_comparison']))+
          '; actual_game_approval=STOP; real_model_accuracy=UNKNOWN; output='+str(out))

if __name__=='__main__':main()
