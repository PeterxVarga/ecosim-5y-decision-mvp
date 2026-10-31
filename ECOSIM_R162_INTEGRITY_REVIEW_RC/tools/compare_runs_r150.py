#!/usr/bin/env python3
"""Compare two offline R149/R150 reports, preserving observation semantics.

No game interaction or causal inference. A changed candidate set can reflect
changed inputs, assumptions, search truncation or code versions, not game effects.
"""
from __future__ import annotations
from json_integrity_r162 import loads_strict
import argparse,hashlib,json
from pathlib import Path

SCHEMA='ECOSIM_R149_OFFLINE_DECISION_DESK_RESULT_V1'

def _identity(report):
    c=report.get('source_context') or {}
    return {k:c.get(k) for k in ('team','market','period','capture_mode','observed_column_kind','round')}

def compare(before,after):
    for label,report in (('before',before),('after',after)):
        if not isinstance(report,dict) or report.get('schema')!=SCHEMA:raise ValueError(label+' must be an R149/R150 decision report')
        if report.get('gameplay_gate')!='STOP' or report.get('game_writes')!=0:raise ValueError('Only offline STOP reports supported')
    a=_identity(before);b=_identity(after)
    current=(before.get('run_mode')=='CURRENT_SNAPSHOT_REVIEW' and after.get('run_mode')=='CURRENT_SNAPSHOT_REVIEW' and a['capture_mode']=='CURRENT_READONLY' and b['capture_mode']=='CURRENT_READONLY')
    same_city=all(a[k] and a[k]==b[k] for k in ('team','market'))
    if not current:status='HISTORICAL_OR_NONCURRENT_COMPARISON_ONLY'
    elif not same_city:status='INCOMPARABLE_CITY_IDENTITY'
    elif type(a['period']) is not int or type(b['period']) is not int:status='INCOMPARABLE_PERIOD'
    elif a['period']==b['period']:status='SAME_PERIOD_DESCRIPTIVE_COMPARISON_ONLY'
    elif b['period']==a['period']+1:status='SEQUENTIAL_YEAR_DESCRIPTIVE_REPLAN_NOT_REALIZED_VALIDATION'
    else:status='NONCONSECUTIVE_OR_REVERSED_PERIODS_NO_DRIFT_INFERENCE'
    aa={r['candidate_id']:r for r in before.get('candidate_comparison') or []}
    bb={r['candidate_id']:r for r in after.get('candidate_comparison') or []}
    # Project start-year labels are absolute, so a signature from two different
    # start years is not comparable even if the hash happens to coincide.
    comparable_ids=(status=='SAME_PERIOD_DESCRIPTIVE_COMPARISON_ONLY')
    before_env={x['id']:x for x in before.get('comparison_envelopes') or []}
    after_env={x['id']:x for x in after.get('comparison_envelopes') or []}
    same_env_ids=sorted(set(before_env)&set(after_env))
    changes={key:{'old_limits_ecu':before_env[key]['limits_ecu'],
                  'new_limits_ecu':after_env[key]['limits_ecu']}
             for key in same_env_ids if before_env[key]['limits_ecu']!=after_env[key]['limits_ecu']}
    return {
      'schema':'ECOSIM_R150_OFFLINE_REPORT_COMPARISON_V1',
      'comparison_class':status,'before_source_context':a,'after_source_context':b,
      'yearly_realized_effect_claim':None,'causal_change_identified':False,
      'same_period_candidate_id_set_comparable':comparable_ids,
      'candidate_counts':{'before':len(aa),'after':len(bb)},
      'same_period_candidate_overlap':({
        'in_both':sorted(set(aa)&set(bb)), 'only_before':sorted(set(aa)-set(bb)),
        'only_after':sorted(set(bb)-set(aa))} if comparable_ids else None),
      'hypothetical_envelope_changes':changes,
      'unmatched_envelope_ids':{'only_before':sorted(set(before_env)-set(after_env)),
                                'only_after':sorted(set(after_env)-set(before_env))},
      'model_predictions_independently_validated':False,
      'permission_to_change_game':False,'gameplay_gate':'STOP',
      'interpretation':'Changes in offline plans are descriptive and may reflect changed assumptions, search or input. They are not an observed causal city transition.'
    }

def main():
    p=argparse.ArgumentParser();p.add_argument('--before',required=True);p.add_argument('--after',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    left=Path(a.before).read_bytes();right=Path(a.after).read_bytes()
    report=compare(loads_strict(left),loads_strict(right))
    report['input_sha256']={'before':hashlib.sha256(left).hexdigest(),'after':hashlib.sha256(right).hexdigest()}
    target=Path(a.out);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print('R150_COMPARE=PASS; class='+report['comparison_class']+'; gameplay=STOP')
if __name__=='__main__':main()
