#!/usr/bin/env python3
"""R143 V2.1 offline readiness. No claim of live config or qualification.
Input absence is expected: PASS/STOP is not a verified game decision.
"""
import json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

def read(rel): return json.loads((ROOT/rel).read_text(encoding='utf-8'))

def at(obj, path):
    for part in path.replace(']','').split('.'):
        if '[' in part:
            key,ix=part.split('[',1)
            obj=obj.get(key) if isinstance(obj,dict) else None
            obj=obj[int(ix)] if isinstance(obj,list) and len(obj)>int(ix) else None
        else: obj=obj.get(part) if isinstance(obj,dict) else None
    return obj

def absent(v): return v is None or v=='' or v==[]

def measured_gap(snapshot):
    p=snapshot.get('provenance',{}); ts=snapshot.get('teams',[])
    if not ts: return {'status':'UNKNOWN_NO_OFFICIAL_LEAGUE_SNAPSHOT'}
    own=snapshot.get('our_team_id')
    if not (p.get('captured_at') and p.get('market') and p.get('league_id') and p.get('round') and isinstance(p.get('period'),int) and own and snapshot.get('index_value_kind') in ('fact','plan')):
        return {'status':'INVALID_OR_INCOMPLETE_SNAPSHOT_PROVENANCE'}
    if len({x.get('team_id') for x in ts})!=len(ts):return {'status':'INVALID_DUPLICATE_TEAMS'}
    if any(not isinstance(x.get('team_id'),str) or not x['team_id'] or type(x.get('smartcity_index')) not in (int,float) or not math.isfinite(x['smartcity_index']) for x in ts):
        return {'status':'INVALID_TEAM_SCORE'}
    scores=sorted((float(x['smartcity_index']) for x in ts),reverse=True)
    ownrow=[float(x['smartcity_index']) for x in ts if x['team_id']==own]
    if len(ownrow)!=1:return {'status':'INVALID_OWN_TEAM_NOT_UNIQUE'}
    if len(scores)<2:return {'status':'INSUFFICIENT_PEERS'}
    ownscore=ownrow[0]
    second_order=scores[1]; second_distinct=next((s for s in scores if s<scores[0]),None)
    is_complete=snapshot.get('league_snapshot_complete') is True
    result={'status':'OBSERVED_COMPLETE_LEAGUE' if is_complete else 'OBSERVED_PARTIAL_SAMPLE_NOT_CERTIFIED_RANK',
            'team_count_observed':len(ts),'own_index':ownscore,'index_value_kind':snapshot['index_value_kind'],
            'best_tied_rank_in_observed_sample':1+sum(s>ownscore for s in scores),
            'second_order_statistic_index':second_order,
            'second_distinct_index':second_distinct,
            'gap_to_second_order_statistic_index_points':round(ownscore-second_order,5),
            'gap_to_second_distinct_index_points':None if second_distinct is None else round(ownscore-second_distinct,5),
            'top_score_has_tie':scores[0]==scores[1],
            'organizer_third_place_gap_formula':'UNKNOWN',
            'qualification_status':'UNKNOWN_NOT_DERIVED'}
    return result

def main():
    state=read('inputs/official_state.template.json'); market=state['market']; team=state['team']
    groups={
      'passive_identification': ['provenance.captured_at_local','provenance.current_period','provenance.round','provenance.team','provenance.market','provenance.source_evidence_id'],
      'cap_calibration':['market.maxProjectPerTurn','market.cap_source','team.project1_active_previous_period',
                         'team.already_selected_new_project_ids_current_period','team.new_selection_count_source'],
      'finance_validation':['team.confirmed_spendable_cash_ecu_by_year[0]',
                            'team.confirmed_spendable_cash_source','team.committed_costs_ecu_by_year[0]',
                            'market.loan_constraints_source'],
      'optional_approved_candidate_validation':['verification.game_preview_candidate',
                                                'verification.game_preview_index','verification.game_preview_cashflow_ecu']}
    missing={g:[path for path in paths if absent(at(state,path))] for g,paths in groups.items()}
    league=measured_gap(read('inputs/league_observations.template.json'))
    cal=read('inputs/calibration_observations.template.json').get('verified_observations',[])
    accepted=[]; rejected=[]
    for row in cal:
        declared=all(row.get(k) is True for k in ['approved_by_owner','reversibility_preverified','original_state_restored_and_verified'])
        vals=all(type(row.get(k)) in (int,float) and math.isfinite(row[k]) for k in ['before_index','after_index','before_cashflow_ecu','after_cashflow_ecu'])
        if declared and len(row.get('changed_fields',[]))==1 and vals:
            accepted.append({'experiment_id':row.get('experiment_id'),'status':'SELF_REPORTED_RESTORED_NOT_INDEPENDENTLY_AUDITED',
                             'delta_index':row['after_index']-row['before_index'],
                             'delta_cashflow_ecu':row['after_cashflow_ecu']-row['before_cashflow_ecu'],
                             'causal_interpretation':'NOT_ESTABLISHED'})
        else: rejected.append({'experiment_id':row.get('experiment_id'),'reason':'Incomplete or unverified reversible observation'})
    cap=market.get('maxProjectPerTurn')
    result={'no_live_actions':True,'full_game_model_validated':False,'gameplay_decision':'STOP',
        'data_groups_missing':missing,
        'passive_data_capture_ready':len(missing['passive_identification'])==0,
        'actual_cap_fully_contextualized':len(missing['cap_calibration'])==0,
        'finance_approval_not_possible_from_client_code':True,
        'candidate_preview_optional_requires_separate_approval':True,
        'candidate_preview_independently_verified':False,
        'observed_league_only':league,
        'self_reported_observation_deltas_not_causal_proof':accepted,
        'untrusted_or_incomplete_experiments':rejected,
        'actual_market_cap':cap,'video_spoken_base_cap_hypothesis':4,
        'video_spoken_loan_rate_hypothesis':0.12,
        'video_matches_cap_if_known':None if cap is None else cap==4,
        'project1_previous_period_bonus':'client predicate numeric previous project1 == 1; cannot infer from active flag alone',
        'next_step':'Resolve passive market/team provenance first; financing approval and candidate preview are separate gates, not prerequisites to drafting a calibrated skeleton.'}
    out=ROOT/'results/R143_READINESS.json';out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print('R143_READINESS_ANALYSIS=CREATED game=STOP; no game validation performed')
if __name__=='__main__':main()
