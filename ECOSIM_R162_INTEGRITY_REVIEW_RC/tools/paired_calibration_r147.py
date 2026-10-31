#!/usr/bin/env python3
"""Read-only paired client PLAN factor observations; no browser, no scenario execution.

Can compare already-provided same-market/team/period before/after snapshots,
without claiming independent evidence or realized future transitions. The only
potential identification here is a *client plan difference*, never next-year fact.
"""
from __future__ import annotations
from json_integrity_r162 import read_json
import argparse, json, math, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from city_bridge import computed_index_from_factors
from r142_proxy_reference import COEFF
from effect_replay_r147 import replay_effects
from portfolio_5y import project_index

ROOT=Path(__file__).resolve().parent.parent

def validate_observation(obs,side):
    if not isinstance(obs,dict):raise ValueError('Observation must be an object: '+side)
    for key in ('team','market','period','source_evidence_id','captured_at','kind','displayed_index','factors'):
        if key not in obs or obs[key] is None: raise ValueError('Missing '+side+'.'+key)
    if obs['kind']!='PLAN':raise ValueError('Only same-period PLAN vs PLAN supported; FACT not counterfactual')
    if type(obs['period']) is not int or not 1<=obs['period']<=5:raise ValueError('Invalid period')
    if any(not isinstance(obs[k],str) or not obs[k].strip() for k in ('team','market','source_evidence_id','captured_at')):
        raise ValueError('Missing provenance strings')
    if type(obs['displayed_index']) not in (float,int) or not math.isfinite(obs['displayed_index']):raise ValueError('Bad index')
    factors=obs['factors']
    if not isinstance(factors,dict) or set(COEFF)-set(factors) or any(type(factors[k]) not in (int,float) or not math.isfinite(factors[k]) for k in COEFF):
        raise ValueError('All direct factor values required')


def measure_pairs(document,idx=None):
    if not isinstance(document,dict) or document.get('schema')!='ECOSIM_R147_PAIRED_PLAN_OBSERVATIONS_V1':
        raise ValueError('Wrong paired client PLAN schema')
    idx=idx or project_index(); pairs=document.get('pairs')
    if not isinstance(pairs,list):raise ValueError('Pairs list required, can be empty')
    seen=set();rows=[];audited_count=0
    for pair in pairs:
        if not isinstance(pair,dict) or not isinstance(pair.get('id'),str) or not pair['id'] or pair['id'] in seen:
            raise ValueError('Unique pair ID required')
        seen.add(pair['id']);b=pair.get('before');a=pair.get('after')
        validate_observation(b,'before');validate_observation(a,'after')
        if (b['team'],b['market'],b['period'])!=(a['team'],a['market'],a['period']):
            raise ValueError('Team/market/period must match; no inter-year fact attribution')
        ids=pair.get('new_project_ids')
        if not isinstance(ids,list) or any(type(i) is not int or i not in idx for i in ids) or len(ids)!=len(set(ids)):
            raise ValueError('Valid unique new_project_ids required')
        flags=pair.get('controls') or {}
        # Declared by provider, never independently verified by this tool.
        declared=(flags.get('no_other_decisions_changed') is True and
                  flags.get('same_active_projects_except_new_ids') is True and
                  flags.get('read_only_evidence_collected_after_owner_authorized_preview') is True)
        f=dict(b['factors'])
        records=replay_effects(f,[(pid,eff) for pid in ids for eff in idx[pid]['effects']],COEFF)
        factor_res=[]
        for name in COEFF:
            delta_model=f[name]-b['factors'][name]
            delta_observed=a['factors'][name]-b['factors'][name]
            factor_res.append({'factor':name,'predicted_delta_if_all_other_inputs_constant':round(delta_model,8),
                               'observed_plan_display_delta':round(delta_observed,8),
                               'difference_observed_minus_partial':round(delta_observed-delta_model,8)})
        predicted=computed_index_from_factors(f)['total_index_from_displayed_factors']
        before_idx=computed_index_from_factors(b['factors'])['total_index_from_displayed_factors']
        after_idx=computed_index_from_factors(a['factors'])['total_index_from_displayed_factors']
        unknown=[rec for rec in records if not rec['mapped'] or rec.get('uncertain_due_to_saturation')]
        if declared:audited_count+=1
        rows.append({'id':pair['id'],'team':b['team'],'market':b['market'],'period':b['period'],
                     'provenance_before':b['source_evidence_id'],'provenance_after':a['source_evidence_id'],
                     'declared_other_decisions_held_fixed_not_independently_verified':declared,
                     'new_project_ids':ids,
                     'conditional_direct_factor_delta_index':round(predicted-before_idx,8),
                     'observed_plan_displayed_index_delta':round(a['displayed_index']-b['displayed_index'],8),
                     'observed_plan_factors_aggregate_delta':round(after_idx-before_idx,8),
                     'factor_discrepancies':factor_res,
                     'unmapped_or_saturated_card_effects':unknown,
                     'complete_game_score_reproduced':None,
                     'actual_future_transition_calibrated':False,
                     'causal_project_effect_isolated':False,
                     'reason':'Project-induced business state / nonlinear policy / rounding may be unobserved; only a conditional partial client-factor replay.'})
    return {'schema':'ECOSIM_R147_PAIRED_CLIENT_PLAN_CALIBRATION_V1','pair_count':len(rows),
            'pairs_with_operator_control_declarations':audited_count,
            'forecast_accuracy_validated':False,
            'realized_annual_state_transition_validated':False,
            'independent_control_verification_available':False,
            'no_observation_means_accuracy_unknown':True,
            'game_writes':0,'gameplay_gate':'STOP','pairs':rows}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',default=str(ROOT/'inputs/paired_plan.template.json'));ap.add_argument('--out',default=str(ROOT/'results/R147_PAIRED_CALIBRATION.json'));ns=ap.parse_args()
    doc=read_json(ns.input);out=measure_pairs(doc)
    p=Path(ns.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print('R147_PAIRED_CALIBRATION=PASS; observations='+str(len(out['pairs']))+'; realized_accuracy=UNKNOWN; writes=0')
if __name__=='__main__':main()
