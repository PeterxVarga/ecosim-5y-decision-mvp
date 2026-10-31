from json_integrity_r162 import read_json as strict_read_json
#!/usr/bin/env python3
"""Passive evidence gateway for the integrated planner; never creates experiments."""
from pathlib import Path
import math
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from readiness import measured_gap
from r142_proxy_reference import evaluate
from portfolio_5y import project_index

def read_json(path):
    return strict_read_json(path)

ROOT=Path(__file__).resolve().parent.parent

def finite_number(x):return type(x) in (int,float) and math.isfinite(x)

def evidence_summary(state, league_file=None, calibration_file=None):
    league=read_json(league_file or ROOT/'inputs/league_observations.template.json')
    cal=read_json(calibration_file or ROOT/'inputs/calibration_observations.template.json')
    tests=[]; trusted_proxy_residuals=[]
    for row in cal.get('verified_observations',[]):
        eligible=(isinstance(row,dict) and
                  all(row.get(k) is True for k in ('approved_by_owner','reversibility_preverified','original_state_restored_and_verified')) and
                  all(finite_number(row.get(k)) for k in ('before_index','after_index','before_cashflow_ecu','after_cashflow_ecu')) and
                  isinstance(row.get('changed_fields'),list) and len(row['changed_fields'])==1)
        entry=dict(experiment_id=row.get('experiment_id') if isinstance(row,dict) else None,
                   recorded_observation_usable_for_descriptive_comparison=bool(eligible),
                   independent_causal_validation=False)
        if eligible:
            entry['observed_index_difference']=round(row['after_index']-row['before_index'],6)
            entry['observed_cashflow_difference_ecu']=round(row['after_cashflow_ecu']-row['before_cashflow_ecu'],2)
            proxy=row.get('forecast_delta_proxy')
            if finite_number(proxy):
                error=entry['observed_index_difference']-proxy
                entry['proxy_delta_error']=round(error,6)
                # only an observed difference; not independently verified; exclude from validated accuracy claims
                trusted_proxy_residuals.append(abs(error))
        tests.append(entry)
    preview=state.get('verification',{})
    # Optional comparison of a candidate in a paired baseline/preview, using
    # explicit observed before/after and normalized project IDs. This is NOT an
    # invitation to create a UI A/B experiment.
    preview_comparison={'status':'NO_PAIRED_APPROVED_RESTORED_PREVIEW_DATA','gameplay_decision':'STOP'}
    verified_flags=(preview.get('preview_reversible_and_owner_approved') is True and
                    preview.get('original_state_restored_and_verified') is True)
    before=preview.get('game_preview_baseline_index')
    after=preview.get('game_preview_index')
    ids=preview.get('game_preview_candidate')
    if verified_flags and finite_number(before) and finite_number(after) and isinstance(ids,list) and len(ids)==len(set(map(str,ids))):
        idx=project_index()
        if all(type(i) is int and i in idx for i in ids):
            factors=state.get('team',{}).get('baseline_smartcity_factors')
            if isinstance(factors,dict) and factors:
                try:
                    model_delta, unknown=evaluate([idx[i] for i in ids],factors)
                    preview_comparison=dict(status='SELF_REPORTED_COMPARISON_NOT_CAUSAL_OR_SERVER_CERTIFIED',
                                            project_ids=ids,observed_delta=round(after-before,6),
                                            proxy_delta=round(model_delta,6),
                                            proxy_residual=round((after-before)-model_delta,6),
                                            unknown_effects=len(unknown),gameplay_decision='STOP')
                except (TypeError,KeyError,ValueError):pass
    gap=measured_gap(league)
    return {'league_read_only_snapshot':gap,
            'paired_candidate_preview_comparison':preview_comparison,
            'historical_observation_differences':tests,
            'observed_proxy_residual_mae_descriptive_only':(round(sum(trusted_proxy_residuals)/len(trusted_proxy_residuals),6)
                                                            if trusted_proxy_residuals else None),
            'causal_validation_achieved':False,
            'official_eligibility_validated':False,
            'gameplay_decision':'STOP'}
