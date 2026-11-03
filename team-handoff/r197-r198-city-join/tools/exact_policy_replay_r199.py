#!/usr/bin/env python3
"""R199: replay exact R195 schedules with ORIGINAL R153/R154/R155/R159 models.
Historical synthetic analysis only; never authorizes EcoSim operations.
"""
from __future__ import annotations
import argparse, hashlib, json, math, sys
from pathlib import Path

REPO=Path(__file__).resolve().parents[3]
SOURCE=REPO/'ECOSIM_R162_INTEGRITY_REVIEW_RC'
sys.path[:0]=[str(Path(__file__).resolve().parent),
              str(REPO/'team-handoff/r191-live-admission/tools'),
              str(SOURCE/'tools')]
from bridge_r197 import assemble,load
from compare_r195 import compare
from strategy_5y import evaluate_proxy
from portfolio_5y import project_index
from tax_response_r153 import read_document,evaluate as tax_evaluate
from tax_revenue_r154 import validate as fiscal_validate,evaluate_counterfactual
from operating_cash_r155 import validate as operating_validate,evaluate as operating_evaluate
from temporal_cash_r158 import build_timing_bridge
from r142_proxy_reference import WEIGHTS

SCHEMA='ECOSIM_R199_EXACT_R195_PROJECT_POLICY_REPLAY_V1'
TAX='r153_source_backed_tax_sensitivity'
FISCAL='r154_source_four_tax_fiscal_tradeoffs'
OPERATING='r155_source_operating_cash_tradeoffs'
DOCS={'tax_scenarios':'inputs/tax_counterfactual_r153.synthetic.json',
      'tax_revenue_scenarios':'inputs/tax_revenue_r154.synthetic.json',
      'operating_scenarios':'inputs/operating_r155.synthetic.json'}

def need(v,why):
    if not v: raise ValueError('HOLD_'+why)

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def source_docs(desk):
    vals={}
    for name,relative in DOCS.items():
        p=SOURCE/relative
        r=desk['inputs'].get(name,{})
        need(p.is_file() and r.get('sha256')==digest(p) and
             r.get('filename')==p.name,'MODEL_SOURCE_SHA_'+name)
        vals[name]=p
    tax,_=read_document(vals['tax_scenarios'])
    fiscal=fiscal_validate(json.loads(vals['tax_revenue_scenarios'].read_text()))
    operating=operating_validate(json.loads(vals['operating_scenarios'].read_text()))
    need(tax['source_class']==fiscal['source_class']==operating['source_class']=='SYNTHETIC_TEST_ONLY',
         'ONLY_HISTORICAL_SYNTHETIC')
    need({p['id'] for p in tax['paths']}=={p['id'] for p in operating['paths']},
         'TAX_OPERATING_PATH_IDENTITY')
    return tax,fiscal,operating

def make_candidates(tradeoff,state,weights):
    rows=tradeoff['annual_comparison'];idx=project_index()
    need(isinstance(rows,list) and len(rows)==5 and
         [r.get('year') for r in rows]==[1,2,3,4,5],'YEAR_CALENDAR')
    result=[]
    for role in ('max','reserve'):
        starts=[r[role+'_project_ids'] for r in rows]
        costs=[r[role+'_cost_ecu'] for r in rows]
        need(all(isinstance(ids,list) and len(ids)==len(set(ids)) and
                 all(type(i) is int and i in idx for i in ids) for ids in starts),'BAD_IDS')
        need(len(set(i for yy in starts for i in yy))==sum(map(len,starts)),'REPEATED_PROJECT')
        need(all(type(x) in (int,float) and math.isfinite(x) and x>=0 for x in costs),
             'BAD_COSTS')
        proxy,unknown,_=evaluate_proxy(idx,{i for yy in starts for i in yy},
                                        state['team']['baseline_smartcity_factors'],weights)
        need(math.isfinite(proxy),'NONFINITE_PROJECT_PROXY')
        result.append({'candidate_id':'R195-'+role,'project_ids_by_year':starts,
          'conservative_project_need_ecu_by_year':costs,
          'five_year_conservative_project_need_ecu':round(sum(costs),6),
          'mapped_terminal_proxy_delta':round(proxy,6),
          'unmapped_or_uncertain_project_effect_occurrences':unknown})
    return result

def replay(tradeoff,t_sha,maxr,resr,desk,d_sha,state,state_sha):
    need(tradeoff.get('mode')=='historical-test','CURRENT_NOT_VALIDATED')
    need(state_sha==tradeoff.get('input_state_sha256')==
         desk.get('inputs',{}).get('state',{}).get('sha256'),'STATE_SOURCE_SHA')
    need(compare(maxr,resr)==tradeoff,'R195_RECEIPTS_DIFFER_FROM_REPORT')
    proof=assemble(tradeoff,t_sha,desk,d_sha)
    need(proof['same_initial_state_verified'] and proof['source_class']=='SYNTHETIC_TEST_ONLY',
         'R197_PROVENANCE')
    need(desk['run_mode']=='HISTORICAL_ILLUSTRATION' and desk['start_year']==1,
         'R149_PERIOD_MODE')
    tax,fiscal,operating=source_docs(desk)
    weights={k:entry[0] for k,entry in WEIGHTS.items()}
    idx=project_index()
    old=desk['candidate_comparison']
    need(isinstance(old,list) and bool(old),'R149_CONTROL_CANDIDATES')
    # Replay the original R149 model as an independent negative control.
    for c in old:
        proxy,_,_=evaluate_proxy(idx,{i for yy in c['project_ids_by_year'] for i in yy},
                                  state['team']['baseline_smartcity_factors'],weights)
        need(abs(round(proxy,6)-c['mapped_terminal_proxy_delta'])<1e-6,
             'R149_PROJECT_REPLAY_DRIFT')
    need(tax_evaluate(tax,old,1,weights)['paths']==desk[TAX]['paths'],
         'R153_CONTROL_REPLAY_DRIFT')
    for t in tax['paths']:
        v=next((r['fiscal_comparison'] for r in desk[FISCAL]['path_counterfactuals']
                if r['tax_path_id']==t['id']),None)
        need(v==evaluate_counterfactual(fiscal,tax['baseline']['decisions'],
                                       t['decisions_by_year'],start_year=1),
             'R154_CONTROL_REPLAY_DRIFT')
    for op in operating['paths']:
        v=next((r for r in desk[OPERATING]['path_counterfactuals']
                if r['path_id']==op['id']),None)
        need(v==operating_evaluate(operating,op,1),'R155_CONTROL_REPLAY_DRIFT')
    plans=make_candidates(tradeoff,state,weights)
    response=tax_evaluate(tax,plans,1,weights)
    cash=build_timing_bridge(plans,desk[FISCAL],desk[OPERATING],response,1)
    need(cash['gameplay_gate']=='STOP' and
         cash['true_cash_availability_or_financing_proven'] is False,'UNSAFE_CASH')
    expected={(p['candidate_id'],t['id']) for p in plans for t in tax['paths']}
    received={(c['candidate_id'],c['path_id']) for c in cash['combinations']}
    need(received==expected and len(cash['combinations'])==len(expected),
         'MISSING_OR_DUPLICATE_EXACT_PAIR')
    records=[]
    for plan in plans:
        matched=[]
        for t in sorted((v for v in cash['combinations']
                         if v['candidate_id']==plan['candidate_id']),
                        key=lambda v:v['path_id']):
            need(t['gameplay_gate']=='STOP' and t['affordability_authorized'] is False
                 and t['actual_spendable_cash_ecu'] is None and
                 t['true_funding_gap_ecu'] is None,'FAKE_FINANCE_APPROVAL')
            need([r['projects_started_ids'] for r in t['annual_rows']]==
                 plan['project_ids_by_year'],'PROJECT_YEAR_REPLAY_DRIFT')
            need(all(abs(r['project_card_need_ecu']-c)<1e-4 for r,c in zip(
                 t['annual_rows'],plan['conservative_project_need_ecu_by_year'])),
                 'PROJECT_COST_REPLAY_DRIFT')
            matched.append({'path_id':t['path_id'],
              'mapped_project_plus_tax_partial_delta':t['conditional_terminal_mapped_proxy_delta'],
              'partial_five_year_net_after_cards_ecu':t['five_year_partial_net_after_card_cost_ecu'],
              'peak_immediate_shortfall_zero_opening_ecu':
                  t['hypothetical_peak_zero_opening_cash_shortfall_immediate_ecu'],
              'peak_deferred_shortfall_zero_opening_ecu':
                  t['hypothetical_peak_zero_opening_cash_shortfall_positive_receipts_deferred_ecu'],
              'annual_rows':t['annual_rows']})
        records.append({'plan':plan['candidate_id'],'project_ids_by_year':plan['project_ids_by_year'],
          'project_cost_ecu_by_year':plan['conservative_project_need_ecu_by_year'],
          'mapped_static_project_proxy_delta':plan['mapped_terminal_proxy_delta'],
          'unmapped_or_uncertain_project_effect_occurrences':
              plan['unmapped_or_uncertain_project_effect_occurrences'],
          'policy_paths':matched})
    return {'schema':SCHEMA,
      'status':'PASS_EXACT_R195_PLANS_CONDITIONAL_POLICY_REPLAY_HISTORICAL_ONLY',
      'mode':'historical-test','r195_sha256':t_sha,'r149_sha256':d_sha,
      'source_state_sha256':state_sha,'source_pin':tradeoff['source_pin'],
      'input_model_sha256':{name:digest(SOURCE/rel) for name,rel in DOCS.items()},
      'r149_old_candidates_replayed':len(old),
      'exact_project_plans':len(records),'project_policy_pairs':len(received),
      'policy_paths':sorted({x['id'] for x in tax['paths']}),'plans':records,
      'score_definitions_not_additive':True,
      'model_city_bases_synthetic':True,'actual_cash_approved':False,
      'full_city_transition_known':False,'global_optimum_certified':False,
      'game_writes':0,'gameplay_gate':'STOP'}

def markdown(v):
    lines=['# R199 – R195 pontos projekttervek és az R153–R159 városi részmodellek',
      '','TÖRTÉNETI ÉS SZINTETIKUS PÉLDA, NEM JÁTÉKBELI JAVASLAT.',
      '','Az eredeti R195 projektütemezéseket közvetlenül újraértékeltük '
      'az R153, R154, R155 és R159 meglévő függvényeivel.',
      '','Ellenőrzött projekttervek: '+str(v['exact_project_plans'])+
      '; projekt/működési párok: '+str(v['project_policy_pairs'])+'.']
    for x in v['plans']:
        lines+=['','## '+('Pontszámorientált' if x['plan']=='R195-max' else 'Tartalékos'),
                'A külön projekt-indexproxy változás: '+str(x['mapped_static_project_proxy_delta']),
                '','| Szintetikus pálya | R153 részleges indexproxy delta | '
                'Ötéves részleges nettó kártya után ECU | Azonnali 0 nyitó csúcshiány ECU | '
                'Késleltetett bevétel csúcshiány ECU |',
                '|---|---:|---:|---:|---:|']
        for p in x['policy_paths']:
            lines.append('| '+p['path_id']+' | '+str(p['mapped_project_plus_tax_partial_delta'])+
              ' | '+str(round(p['partial_five_year_net_after_cards_ecu'],2))+
              ' | '+str(round(p['peak_immediate_shortfall_zero_opening_ecu'],2))+
              ' | '+str(round(p['peak_deferred_shortfall_zero_opening_ecu'],2))+' |')
    lines+=['','Az R195 abszolút robusztus pontszám NEM adható hozzá az R153 részindex-deltához.',
       'A részleges nettó nem felhasználható városi pénzegyenleg; '
       'a népesség-, vállalkozás-, hitel-, támogatás- és intézményi visszacsatolás nem teljes.',
       'A bevételkésleltetés stresszhipotézis, nem a játék igazolt szabálya.',
       '','Finanszírozási jóváhagyás: NINCS. EcoSim-írás: 0. GAME_ACTION_GATE=STOP.','']
    return '\n'.join(lines)

def main():
    p=argparse.ArgumentParser()
    for key in ('tradeoff','max-receipt','reserve-receipt','decision-desk'):
        p.add_argument('--'+key,required=True,type=Path)
    p.add_argument('--state',type=Path,default=REPO/'team-handoff/r191-live-admission/examples/historical_test_state.json')
    p.add_argument('--out-dir',type=Path,required=True)
    a=p.parse_args()
    if a.out_dir.exists():p.error('HOLD_OUTPUT_EXISTS')
    inputs=(a.tradeoff,a.max_receipt,a.reserve_receipt,a.decision_desk,a.state)
    if len({i.resolve() for i in inputs})!=len(inputs):p.error('HOLD_DUPLICATE_INPUT')
    try:
        t,ts=load(a.tradeoff);mx,_=load(a.max_receipt);rv,_=load(a.reserve_receipt)
        d,ds=load(a.decision_desk);s,ss=load(a.state)
        result=replay(t,ts,mx,rv,d,ds,s,ss)
    except (ValueError,TypeError,KeyError,OSError,UnicodeError) as e:
        p.error(str(e))
    a.out_dir.mkdir(parents=True)
    (a.out_dir/'R199.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    (a.out_dir/'R199_HU.md').write_text(markdown(result),encoding='utf-8')
    print('R199='+result['status']+' GAME_ACTION_GATE=STOP')
    print('REPORT='+str(a.out_dir/'R199_HU.md'))

if __name__=='__main__':main()
