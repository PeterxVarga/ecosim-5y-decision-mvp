#!/usr/bin/env python3
"""Run alongside a local, pinned R162 worktree. NO mutation to R162 or game.

Example: python run_r162_shadow.py --repo-root ./ECOSIM_R162_INTEGRITY_REVIEW_RC --state ./state.json --annual-budget 50000 --cap 4 --out ./r189_result.json

Explicitly hypothetical test settings; never use output for automatic gameplay.
"""
import argparse,hashlib,json,sys,subprocess
from pathlib import Path
from bounded_shadow_r189 import improve,Hold
PIN='9d2d17d822bb97a210151e269454a0432a1952ae'

def run(root,state,annual_budget,cap):
    tools=root/'tools'
    try:
        head=subprocess.run(['git','-C',str(root),'rev-parse','HEAD'],capture_output=True,text=True,check=True,timeout=10).stdout.strip()
    except (OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired):
        raise Hold('PINNED_GIT_REPOSITORY_REQUIRED')
    if head!=PIN:
        raise Hold('R162_GIT_PIN_MISMATCH')
    try:
        dirty=subprocess.run(['git','-C',str(root),'status','--porcelain'],capture_output=True,text=True,check=True,timeout=10).stdout
    except (OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired):
        raise Hold('SOURCE_CLEANLINESS_NOT_VERIFIED')
    if dirty.strip():raise Hold('SOURCE_WORKTREE_NOT_CLEAN')
    if not (tools/'strategy_5y.py').is_file() or not (tools/'independent_audit_r160.py').is_file():
        raise Hold('PINNED_R162_MODULES_NOT_PRESENT')
    sys.path.insert(0,str(tools))
    from strategy_5y import search,derive_config
    from portfolio_5y import project_index
    from robust_decision_r157 import replay
    from independent_audit_r160 import audit_plan
    idx=project_index();source=json.loads(state.read_text(encoding='utf8'))
    start_year=(source.get('provenance') or {}).get('current_period')
    if type(start_year) is not int or not 1<=start_year<=5:raise Hold('EXPLICIT_CURRENT_PERIOD_REQUIRED')
    n=6-start_year
    if source.get('market',{}).get('maxProjectPerTurn') not in (cap,):
        raise Hold('EXPLICIT_CAP_NOT_MATCHING_STATE')
    if source.get('team',{}).get('initially_active_project_ids') is None or source.get('team',{}).get('already_selected_new_project_ids_current_period') is None:
        raise Hold('MISSING_EXPLICIT_PROJECT_BASELINE')
    if type(source.get('team',{}).get('project1_active_previous_period')) is not bool:
        raise Hold('PRIOR_PROJECT1_BONUS_UNKNOWN')
    budgets=[annual_budget]*n
    cfg=derive_config(source,idx,start_year,budgets,cap)
    result=search(source,start_year,budgets,cap,beam_width=14,shortlist=36,
                  allow_same_year=False,objective='scenario_min')
    if not result.get('top_plans'):raise Hold('NO_SOURCE_SEARCH_PLANS')
    best=result['top_plans'][0];starts=[x['start_project_ids'] for x in best['start_by_year']]
    def scorer(rows):return replay(idx,rows,cfg['baseline'],start_year=start_year,
                                   weights=source.get('market',{}).get('smartcity_total_weights'))['scenario_min_clamp_only_mapped_delta']
    def auditor(rows):return audit_plan(idx,start_year=start_year,
        active_ids=sorted(cfg['initial_active']),fixed_first_ids=sorted(cfg['fixed_first']),
        previous_project1_active=cfg['project1prev'],base_project_cap=cap,
        annual_budgets=budgets,starts=rows,allow_same_year=False)
    receipt=improve(starts,idx,initial_active=sorted(cfg['initial_active']),
        fixed_first_ids=sorted(cfg['fixed_first']),start_year=start_year,
        annual_budgets=budgets,base_project_cap=cap,
        previous_project1_active=cfg['project1prev'],score_fn=scorer,audit_fn=auditor)
    receipt['original_source_pin_expected']=PIN
    receipt['input_state_sha256']=hashlib.sha256(state.read_bytes()).hexdigest()
    receipt['catalog_sha256']=hashlib.sha256((root/'data/ecosim_projects_20261030.json').read_bytes()).hexdigest()
    receipt['execution_scope']='PINNED_R162_LOCAL_HISTORICAL_ILLUSTRATIVE_ONLY'
    return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo-root',type=Path,required=True)
    p.add_argument('--state',type=Path,required=True);p.add_argument('--annual-budget',type=int,required=True)
    p.add_argument('--cap',type=int,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if a.out.resolve()==a.state.resolve():raise SystemExit('HOLD: Cannot overwrite state')
    if a.out.resolve().is_relative_to(a.repo_root.resolve()):raise SystemExit('HOLD: Cannot write into the R162 source tree')
    if a.out.exists():raise SystemExit('HOLD: output already exists; overwrite forbidden')
    try:r=run(a.repo_root.resolve(),a.state.resolve(),a.annual_budget,a.cap)
    except (Hold,ValueError) as e:raise SystemExit('HOLD: '+str(e))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('R189_STATUS='+r['status']+' R189_SCORE='+str(r['final_score'])+' GAME_ACTION_GATE=STOP')
