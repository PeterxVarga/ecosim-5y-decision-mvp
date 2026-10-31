#!/usr/bin/env python3
"""Source-anchored partial project effect factor replay, R147.

Source-backed *direct project multiplier* and post-multiplier clamps only.
Never a city transition, server acceptance, cash authorization or complete score.
Original 840 bundle must be verified separately against source anchor catalog.
"""
from __future__ import annotations
from math import isfinite

# Original client factor model uses `Pr` to multiply the project effect.
# Names are Hungarian project-card effect fields; only unemployment is an alias
# for a separate English source factor key, and it is source-backed.
ALIASES = {"Munkanélküliség": "Munkanélküli arány"}

# Display values are 100x the client-side fractional factor values.
# These clamps are applied AFTER the raw project multiplier in the identified
# branches of 840.41fdc8e1.chunk.js.
# A baseline AT its clamp edge may conceal an unknown uncapped base, so
# the exact resulting change is unidentifiable from displayed values alone.
BOUNDS = {
    "Vállalkozóbarátság": (None, 100.0),
    "Településfejlettség": (2.1, 95.6),
    "Közlekedési minőség": (None, 200.0),
    "Tömegközlekedők aránya, %": (None, 80.0),
}

def normalize_metric(name):
    return ALIASES.get(name, name)

def clamp(value, minimum, maximum):
    if minimum is not None:value=max(value,minimum)
    if maximum is not None:value=min(value,maximum)
    return value

def apply_effect(factors, name, pct, recognized, *, scale=1.0, project_id=None):
    """Update source-supported *conditional* direct factor replay.

    Returns audit record; on baseline at a cap and effect crossing out of it,
    value is left as a conditional proxy and `uncertain_due_to_saturation=True`.
    No float is presented as a unique, verified client output.
    """
    label=normalize_metric(name)
    rec={'project_id':project_id, 'project_metric':name,'factor':label,
         'source_direct_multiplier':name==label or name in ALIASES,
         'mapped':label in recognized,'model':'R147_CLIENT_CONDITIONAL_DIRECT_FACTOR_ONLY'}
    if label not in recognized:
        rec.update(mapped=False, reason='NO_PROVEN_DIRECT_DISPLAY_FACTOR_OR_INDIRECT_DEPENDENCY')
        return rec
    if type(pct) not in (int,float) or not isfinite(pct) or type(scale) not in (int,float) or not isfinite(scale):
        raise ValueError('Finite percentage and scenario scale required')
    mult=1+scale*pct/100.0
    if mult<=0:raise ValueError('Project effect multiplier must remain positive')
    before=factors[label]
    if type(before) not in (int,float) or not isfinite(before):raise ValueError('Finite baseline factor required')
    lo,hi=BOUNDS.get(label,(None,None))
    uncapped=before*mult
    after=clamp(uncapped,lo,hi)
    ambiguous = ((hi is not None and abs(before-hi)<1e-8 and mult<1)
                 or (lo is not None and abs(before-lo)<1e-8 and mult>1))
    factors[label]=after
    rec.update(multiplier=mult, before=before, after=after,
               clamp={'min':lo,'max':hi} if label in BOUNDS else None,
               uncertain_due_to_saturation=ambiguous,
               remains_conditional_on_unchanged_exogenous_city_state=True)
    return rec

def replay_effects(factors, pairs, recognized, *, scale=1.0):
    """Aggregate all project relative multipliers FIRST, then clamp each factor once.

    This mirrors the common source Pr product before the outer factor clamp.
    No retroactive compounding and no clamp applied once per project.
    """
    grouped={};unmapped=[]
    for pid,row in pairs:
        name=row['metric'];pct=row['value_percent'];label=normalize_metric(name)
        if label not in recognized:
            unmapped.append({'project_id':pid,'project_metric':name,'factor':label,'mapped':False,
                             'reason':'NO_PROVEN_DIRECT_DISPLAY_FACTOR_OR_INDIRECT_DEPENDENCY'})
            continue
        if type(pct) not in (int,float) or not isfinite(pct):raise ValueError('Finite project effect required')
        multiplier=1+scale*pct/100
        if multiplier<=0:raise ValueError('Nonpositive multiplier')
        group=grouped.setdefault(label,{'multiplier':1.,'ids':[],'raw_labels':[]})
        group['multiplier']*=multiplier
        group['ids'].append(pid);group['raw_labels'].append(name)
    records=[]
    for label,g in grouped.items():
        rec=apply_effect(factors,label,(g['multiplier']-1)*100,recognized)
        rec['project_ids']=g['ids'];rec['project_metric_labels']=g['raw_labels']
        rec['grouped_before_single_final_clamp']=True
        records.append(rec)
    return records+unmapped
