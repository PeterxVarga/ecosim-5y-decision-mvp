#!/usr/bin/env python3
"""Pinned, offline-only EcoSim R162 -> R189 optional team shadow.

Live CURRENT_READONLY is accepted only with fresh, hash-linked R156 and an
independent operator-observed current-year finance source. This is *not* a
server-verified snapshot, gameplay recommendation, or permission to write.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from bounded_shadow_r189 import improve,Hold
from admission_r191 import AdmissionHold,validate_state,validate_r156_bundle,year1_finance
from catalog_gate_r192 import CatalogHold,validate_catalog
from hungarian_decision_r193 import explain as hungarian_explain

R162_PIN='9d2d17d822bb97a210151e269454a0432a1952ae'


def verify_source(root):
    root=Path(root).resolve()
    if not root.is_dir():raise Hold('R162_ROOT_MISSING')
    def command(*arguments):
        try:
            return subprocess.run(['git','-C',str(root),*arguments],
                check=True,capture_output=True,text=True,timeout=15).stdout.strip()
        except (OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired):
            raise Hold('PINNED_GIT_SOURCE_NOT_VERIFIED') from None
    head=command('rev-parse','HEAD')
    if head!=R162_PIN:raise Hold('R162_GIT_PIN_MISMATCH')
    top=Path(command('rev-parse','--show-toplevel')).resolve()
    if command('status','--porcelain'):
        raise Hold('R162_SOURCE_WORKTREE_NOT_CLEAN')
    if root!=top/'ECOSIM_R162_INTEGRITY_REVIEW_RC':
        raise Hold('R162_ROOT_PATH_MISMATCH')
    needed=['strategy_5y.py','independent_audit_r160.py','json_integrity_r162.py',
            'robust_decision_r157.py','portfolio_5y.py']
    for name in needed:
        if not (root/'tools'/name).is_file():raise Hold('REQUIRED_R162_MODULE_MISSING_'+name)
    return top


def run(root,state_path,annual_budget,cap,*,mode,r156_bundle=None,year1_finance_path=None,card_catalog_path=None,now=None):
    root=Path(root).resolve();state_path=Path(state_path).resolve()
    verify_source(root)
    if type(annual_budget) is not int or not 0<=annual_budget<=1_000_000_000_000:
        raise Hold('INVALID_HYPOTHETICAL_BUDGET')
    if type(cap) is not int or not 0<=cap<=20:raise Hold('INVALID_EXPLICIT_CAP')
    # Import exactly the pinned R162 hardened parser, not json.loads in this runner.
    sys.path.insert(0,str(root/'tools'))
    from json_integrity_r162 import read_json

    state=read_json(state_path)
    state_mode={'historical-test':'historical','current-readonly':'current'}.get(mode)
    if not state_mode:raise Hold('EXPLICIT_HISTORICAL_OR_CURRENT_MODE_REQUIRED')
    admission=validate_state(state,mode=state_mode,now=now)
    if state['market']['maxProjectPerTurn']!=cap:raise Hold('DECLARED_CAP_MISMATCH')
    if state_mode=='current':
        if r156_bundle is None or year1_finance_path is None:
            raise Hold('CURRENT_R156_BUNDLE_AND_YEAR1_FINANCE_REQUIRED')
        if card_catalog_path is None:
            raise Hold('CURRENT_35_CARD_OBSERVATION_REQUIRED')
        capture=validate_r156_bundle(state,r156_bundle,now=now)
        finance=year1_finance(read_json(Path(year1_finance_path)),state,
                              illustrative_first_year_budget=annual_budget)
        admission['r156_capture']=capture
        admission['year1_finance']=finance
        admission['catalog_parity']=validate_catalog(read_json(Path(card_catalog_path)),state,
            read_json(root/'data/ecosim_projects_20261030.json'),now=now)
    else:
        if r156_bundle is not None or year1_finance_path is not None or card_catalog_path is not None:
            raise Hold('HISTORICAL_RUN_MUST_NOT_ACCEPT_LIVE_ADMISSION_DOCUMENTS')
        admission['year1_finance']={'status':'HISTORICAL_HYPOTHETICAL_ENVELOPE_ONLY'}
    start_year=admission['current_period'];budgets=[annual_budget]*(6-start_year)
    from strategy_5y import search,derive_config
    from portfolio_5y import project_index
    from robust_decision_r157 import replay
    from independent_audit_r160 import audit_plan
    idx=project_index();cfg=derive_config(state,idx,start_year,budgets,cap)
    if cfg['initial_active']!=frozenset(admission['active']) or cfg['fixed_first']!=frozenset(admission['fixed']):
        raise Hold('R162_NORMALIZATION_OR_CAPTURE_DRIFT')
    result=search(state,start_year,budgets,cap,beam_width=14,shortlist=36,
                  allow_same_year=False,objective='scenario_min')
    if not result.get('top_plans'):raise Hold('NO_SOURCE_SEARCH_PLANS')
    def scorer(rows):
        return replay(idx,rows,cfg['baseline'],start_year=start_year,
            weights=state.get('market',{}).get('smartcity_total_weights'))['scenario_min_clamp_only_mapped_delta']
    def auditor(rows):
        return audit_plan(idx,start_year=start_year,active_ids=sorted(cfg['initial_active']),
            fixed_first_ids=sorted(cfg['fixed_first']),
            previous_project1_active=cfg['project1prev'],base_project_cap=cap,
            annual_budgets=budgets,starts=rows,allow_same_year=False)
    selected=None;selected_rank=None
    for rank,plan in enumerate(result['top_plans'],1):
        starts=[x['start_project_ids'] for x in plan['start_by_year']]
        a=auditor(starts)
        if a.get('schema')!='ECOSIM_R160_INDEPENDENT_PLAN_AUDIT_V1':raise Hold('R160_CONTRACT_MISMATCH')
        if not a.get('hard_rule_violations') and not a.get('conditional_eligibility_items') and a.get('status')=='PASS_DISPLAY_RULES_ONLY_NOT_SERVER_APPROVAL':
            selected=starts;selected_rank=rank;break
    if selected is None:raise Hold('R162_NO_UNCONDITIONALLY_AUDITABLE_CANDIDATE')
    receipt=improve(selected,idx,initial_active=sorted(cfg['initial_active']),
        fixed_first_ids=sorted(cfg['fixed_first']),start_year=start_year,
        annual_budgets=budgets,base_project_cap=cap,
        previous_project1_active=cfg['project1prev'],score_fn=scorer,audit_fn=auditor)
    receipt.update(schema='ECOSIM_R191_HARDENED_PINNED_SHADOW_V1',
        r189_schema='ECOSIM_R189_BOUNDED_SHADOW_V1',
        mode=mode,r162_source_pin=R162_PIN,
        seed_rank_within_R162_top_plans=selected_rank,
        r162_result_game_action=result.get('final_gameplay_decision'),
        input_state_sha256=hashlib.sha256(state_path.read_bytes()).hexdigest(),
        original_35_catalog_sha256=hashlib.sha256((root/'data/ecosim_projects_20261030.json').read_bytes()).hexdigest(),
        admission=admission,
        annual_envelopes=[{'year':start_year+i,'scenario_ceiling_ecu':annual_budget,
                           'basis':'OPERATOR_YEAR1_NOT_SERVER_APPROVED' if i==0 and state_mode=='current'
                           else 'HYPOTHETICAL_UNVERIFIED'} for i in range(len(budgets))],
        actual_gameplay_approved=False,actual_live_score_forecast_verified=False,
        live_ready_decision_authorization=False,gameplay_gate='STOP')
    if receipt['r162_result_game_action']!='STOP':raise Hold('R162_GAME_ACTION_GATE_NOT_STOP')
    # R193: generate an auditable Hungarian recommendation only AFTER all original
    # R156/R160/R162/R189/R191/R192 gates succeeded. Pure, deterministic prose.
    from r142_proxy_reference import COEFF
    receipt['human_explanation_hu']=hungarian_explain(receipt,idx,modeled_metrics=set(COEFF))
    return receipt


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root',type=Path,required=True)
    p.add_argument('--state',type=Path,required=True)
    p.add_argument('--mode',choices=['historical-test','current-readonly'],required=True)
    p.add_argument('--r156-bundle',type=Path)
    p.add_argument('--year1-finance',type=Path)
    p.add_argument('--current-card-catalog',type=Path)
    p.add_argument('--annual-budget',type=int,required=True)
    p.add_argument('--cap',type=int,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args(argv)
    repo=a.repo_root.resolve()
    dest=a.out.resolve()
    if dest==a.state.resolve() or dest.is_relative_to(repo) or dest.is_relative_to(repo.parent.resolve()):
        raise SystemExit('HOLD: Output cannot overwrite evidence or the pinned repository')
    if dest.exists():raise SystemExit('HOLD: Existing output cannot be overwritten')
    try:
        receipt=run(repo,a.state,a.annual_budget,a.cap,mode=a.mode,
                    r156_bundle=a.r156_bundle,year1_finance_path=a.year1_finance,
                    card_catalog_path=a.current_card_catalog)
    except (Hold,AdmissionHold,CatalogHold,ValueError,OSError,KeyError,TypeError) as exc:
        raise SystemExit('HOLD: '+str(exc)) from None
    # Atomic exclusive create: never modify existing output or input evidence.
    dest.parent.mkdir(parents=True,exist_ok=True)
    try:
        with dest.open('x',encoding='utf-8') as f:
            json.dump(receipt,f,ensure_ascii=False,indent=2,allow_nan=False)
            f.write('\n')
    except FileExistsError:raise SystemExit('HOLD: Output already created by another process') from None
    print('R191=PASS_MODEL_SHADOW_ONLY GAME_ACTION_GATE=STOP OUTPUT='+str(dest))
    print(receipt['human_explanation_hu']['markdown'])
    return receipt

if __name__=='__main__':main()
