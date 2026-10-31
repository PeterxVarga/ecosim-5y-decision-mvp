#!/usr/bin/env python3
"""R147 current single local entrypoint for passive reconciliation and bounded joint search.

stdlib only. Reads *provided* JSON, never opens websites or changes the game.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT_PARENT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_PARENT))
from strategy_5y import ROOT, read_json, parse_budget, write_json
from policy_tracks import load_tracks
from joint_5y import evaluate_tracks, render_joint_md
from passive_r146 import reconcile_snapshots
from paired_calibration_r147 import measure_pairs

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--state',default=str(ROOT/'inputs/official_state.template.json'))
    p.add_argument('--policy-tracks',default=str(ROOT/'inputs/policy_tracks.synthetic.example.json'))
    p.add_argument('--passive-snapshots',default=str(ROOT/'inputs/historical_passive_summary_20261030.json'))
    p.add_argument('--paired-plan-observations',default=str(ROOT/'inputs/paired_plan.template.json'))
    p.add_argument('--budget-per-year',default=None)
    p.add_argument('--project-cap',type=int,default=None)
    p.add_argument('--start-year',type=int,default=1)
    p.add_argument('--beam',type=int,default=8)
    p.add_argument('--shortlist',type=int,default=16)
    p.add_argument('--out-prefix',default=str(ROOT/'results/R147_DEMONSTRATION'))
    a=p.parse_args()
    if not 1<=a.start_year<=5:p.error('start-year 1..5')
    state=read_json(a.state)
    tracks=load_tracks(a.policy_tracks)
    budgets=parse_budget(a.budget_per_year,6-a.start_year)
    reconciliation=reconcile_snapshots(read_json(a.passive_snapshots))
    calibration=measure_pairs(read_json(a.paired_plan_observations))
    report=evaluate_tracks(state,a.start_year,tracks,budgets,a.project_cap,a.beam,a.shortlist)
    prefix=Path(a.out_prefix)
    write_json(str(prefix)+'_JOINT.json',report)
    Path(str(prefix)+'_JOINT.md').write_text(render_joint_md(report),encoding='utf8')
    write_json(str(prefix)+'_PASSIVE.json',reconciliation)
    write_json(str(prefix)+'_PAIRED_CALIBRATION.json',calibration)
    manifest={'schema':'ECOSIM_R147_OFFLINE_OUTPUT_GATE_V1','game_state_changed':False,
              'external_actions':0,'codex_used':False,'gameplay_gate':'STOP',
              'verified_5y_winning_strategy':False,
              'policy_conditioned_search':report['policy_conditioned_joint_project_search'],
              'actual_game_outcome_bounds':None,
              'read_only_reconciliation_records':len(reconciliation['snapshots']),
              'real_controlled_client_plan_pairs':calibration['pair_count'],
              'client_source_factor_anchor_provenance': 'R147_SOURCE_ANCHORS.json',
              'actual_five_year_score_predictive_accuracy':None,
              'illustrative_tracks':len(report['tracks']),
              'requires_user_action_now':False}
    write_json(str(prefix)+'_STATUS.json',manifest)
    print('R147_OFFLINE=PASS GAME=STOP CODEX=NO; REAL_ACCURACY=UNKNOWN; output='+str(prefix))

if __name__=='__main__':main()
