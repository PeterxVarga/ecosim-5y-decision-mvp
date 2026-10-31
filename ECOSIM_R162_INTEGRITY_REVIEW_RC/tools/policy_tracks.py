#!/usr/bin/env python3
"""R145 bounded operations-policy scenario inputs. Does not infer unknown EcoSim responses.

A policy track is a user-declared counterfactual path, NOT a policy simulator.
Only explicitly supplied factor effects and cash deltas are replayed; nulls stay unknown.
"""
from __future__ import annotations
from json_integrity_r162 import read_json
from pathlib import Path
import json, math
from city_bridge import computed_index_from_factors
from r142_proxy_reference import COEFF

CATEGORIES={'tax','service_fee','institution_capacity','staffing_payroll','transport','environment','social','other'}
DURATIONS={'ONE_YEAR','PERSISTENT_FROM_START'}
MODES={'SYNTHETIC_TEST_ONLY','USER_HYPOTHESIS','DOCUMENTED_OBSERVATION_ONLY'}

def finite(v):return type(v) in (int,float) and math.isfinite(v)

def load_tracks(path):
    o=read_json(path)
    if not isinstance(o,dict) or o.get('schema')!='ECOSIM_R145_POLICY_TRACKS_V1' or not isinstance(o.get('tracks'),list) or not o['tracks']:
        raise ValueError('Wrong policy tracks schema or empty collection')
    ids=set(); tracks=[]
    for t in o['tracks']:
        if not isinstance(t,dict):raise ValueError('Bad track')
        tid=t.get('track_id')
        if not isinstance(tid,str) or not tid or tid in ids:raise ValueError('Track ID empty/duplicate')
        ids.add(tid)
        if t.get('mode') not in MODES or not isinstance(t.get('assumption_note'),str) or not t['assumption_note'].strip():raise ValueError('Policy track must disclose mode and note')
        acts=t.get('actions')
        if not isinstance(acts,list):raise ValueError('Actions must be a list')
        keys=set()
        for a in acts:
            if not isinstance(a,dict) or type(a.get('year')) is not int or not 1<=a['year']<=5:raise ValueError('Action year 1..5 required')
            if a.get('category') not in CATEGORIES:raise ValueError('Unknown policy category')
            key=a.get('decision_key')
            if not isinstance(key,str) or not key or (a['year'],key) in keys:raise ValueError('Duplicate or invalid action key in year')
            keys.add((a['year'],key))
            if a.get('duration') not in DURATIONS:raise ValueError('Specify duration')
            eff=a.get('factor_relative_percent')
            if eff is not None:
                if not isinstance(eff,dict) or not eff or any(k not in COEFF or not finite(v) or v<=-100 for k,v in eff.items()):raise ValueError('Empty/unknown factor or nonfinite or invalid relative pct')
            money=a.get('annual_cash_delta_ecu')
            if money is not None and not finite(money):raise ValueError('Annual cash delta must be numeric or null')
            if a.get('duration')=='PERSISTENT_FROM_START' and a.get('factor_relative_percent') is None:
                # Supports action with unknown effect; never assume it does nothing.
                pass
            if not isinstance(a.get('assumption_note'),str) or not a['assumption_note'].strip():raise ValueError('Action needs note')
            if t['mode']=='DOCUMENTED_OBSERVATION_ONLY' and not isinstance(a.get('source_evidence_id'),str):raise ValueError('Documented observations require evidence ID')
        tracks.append(t)
    if len(tracks)>12:raise ValueError('At most 12 policy tracks per offline comparison')
    return tracks

def applicable(a, year):
    return (a['year']<=year) if a['duration']=='PERSISTENT_FROM_START' else a['year']==year

def cost_reservation_for_year(track,year):
    """Conservatively reserve only explicitly negative policy cash deltas.
    Positive hypothetical cash never expands project buying power.
    """
    return round(sum(max(0,-a['annual_cash_delta_ecu']) for a in track['actions']
                     if applicable(a,year) and a.get('annual_cash_delta_ecu') is not None),6)

def policy_factor_replay(baseline, track, year, start_year, scale=1.):
    factors=dict(baseline); unknown=[]; applied=[]
    for a in track['actions']:
        if a['year']<start_year:continue # prior actions embedded in supplied current baseline
        if not applicable(a,year):continue
        eff=a.get('factor_relative_percent')
        if eff is None:
            unknown.append({'year':year,'decision_key':a['decision_key'],'reason':'NO_CALIBRATED_FACTOR_RESPONSE'})
        else:
            for metric,pct in eff.items():
                factors[metric] *= 1+scale*pct/100
                applied.append({'decision_key':a['decision_key'],'metric':metric,'relative_percent':pct,'duration':a['duration']})
    return factors,applied,unknown

def policy_money_replay(track,year,start_year):
    """Unknown if any contributing active action has undisclosed cash effect."""
    known=0;unknown=[]
    for a in track['actions']:
        if a['year']<start_year or not applicable(a,year):continue
        v=a.get('annual_cash_delta_ecu')
        if v is None:unknown.append(a['decision_key'])
        else:known+=v
    return {'disclosed_policy_cash_delta_ecu':round(known,2),
            'undisclosed_policy_cash_decisions':unknown,
            'complete':not unknown,
            'cashflow_source':'EXPLICIT_POLICY_TRACK_ASSUMPTION_NOT_GAME_SETTLEMENT'}

def replay_policy_joint(plan, track, baseline, idx, weights, start_year):
    """Single post-aggregation clamp for joint PROJECT and hypothetical POLICY effects.

    R147 first clamped project effects and multiplied policy afterwards. That
    could exceed the EcoSim factor caps. R148 unifies both paths, labels any
    saturated latent inputs and excludes the unmodeled impact from confidence.
    """
    from annual_transition_r148 import combined_factor_replay
    starts=[x['start_project_ids'] for x in plan['start_by_year']]
    base_score=computed_index_from_factors(baseline,weights)['total_index_from_displayed_factors']
    rows=[]
    for j,ids in enumerate(starts):
        y=start_year+j
        pairs=[(i,e) for year_ids in starts[:j+1] for i in year_ids for e in idx[i]['effects']]
        policyf,applied,unknown=policy_factor_replay({k:1.0 for k in baseline},track,y,start_year)
        mixed=combined_factor_replay(baseline,pairs,policyf,weights=weights)
        money=policy_money_replay(track,y,start_year)
        rows.append({'year':y,'joint_mapped_factor_counterfactual_index':round(mixed['mapped_conditional_index'],6),
                     'joint_mapped_delta_from_input_baseline':round(mixed['mapped_conditional_index']-base_score,6),
                     'project_unmapped_effect_count':len(mixed['unmapped_project_effects']),
                     'saturated_latent_factor_ambiguity':mixed['ambiguous_saturated_factors'],
                     'conditional_saturation_only_index_interval':mixed['mapped_index_if_only_saturation_uncertain'],
                     'policy_unmapped_actions':unknown,
                     'disclosed_policy_factor_effects':applied,
                     'policy_cash_delta_assumption':money,
                     'scenario_cash_budget_reserved_ecu':cost_reservation_for_year(track,y),
                     'project_policy_clamp_order':'COMBINE_MULTIPLIERS_THEN_CLAMP_ONCE',
                     'actual_index_forecast':None,'actual_cashflow_forecast':None})
    return rows
