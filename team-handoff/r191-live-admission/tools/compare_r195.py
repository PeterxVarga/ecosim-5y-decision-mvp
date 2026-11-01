#!/usr/bin/env python3
"""R195: independent offline comparison of two *finished, audited* R194 receipts.

No optimization, game access, or execution authorization. Both compared candidates
must come from the same R162 pin, original input state, 35-card catalog and mode.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

PIN = '9d2d17d822bb97a210151e269454a0432a1952ae'
R191_SCHEMA = 'ECOSIM_R191_HARDENED_PINNED_SHADOW_V1'
R193_SCHEMA = 'ECOSIM_R193_HUMAN_DECISION_EXPLANATION_V1'

class ComparisonHold(ValueError):
    pass


def _valid_nonneg(v):
    return type(v) in (float, int) and math.isfinite(v) and v >= 0


def validate_receipt(raw, role):
    if not isinstance(raw,dict) or raw.get('schema') != R191_SCHEMA:
        raise ComparisonHold(role + ': R191_RECEIPT_REQUIRED')
    if raw.get('status') != 'PASS_CONDITIONAL_MODEL_SHADOW_ONLY':
        raise ComparisonHold(role + ': SHADOW_NOT_PASSED')
    if raw.get('r162_source_pin') != PIN:
        raise ComparisonHold(role + ': R162_PIN_MISMATCH')
    if raw.get('gameplay_gate') != 'STOP' or raw.get('r162_result_game_action') != 'STOP' or raw.get('actual_gameplay_approved') is not False:
        raise ComparisonHold(role + ': GAMEPLAY_STOP_REQUIRED')
    if raw.get('actual_live_score_forecast_verified') is not False or raw.get('live_ready_decision_authorization') is not False:
        raise ComparisonHold(role + ': LIVE_AUTHORIZATION_NOT_ALLOWED')
    audit=raw.get('independent_replay')
    if not isinstance(audit,dict) or audit.get('status')!='PASS_DISPLAY_RULES_ONLY_NOT_SERVER_APPROVAL' or audit.get('hard_violations') != 0 or audit.get('conditional_items') != 0:
        raise ComparisonHold(role + ': R160_AUDIT_NOT_CLEAN')
    mode=raw.get('mode'); admission=raw.get('admission')
    if mode not in ('historical-test','current-readonly') or not isinstance(admission,dict) or admission.get('gameplay_gate')!='STOP':
        raise ComparisonHold(role + ': ADMISSION_INVALID')
    if admission.get('mode') != ('historical' if mode=='historical-test' else 'current'):
        raise ComparisonHold(role + ': ADMISSION_MODE_MISMATCH')
    if mode=='current-readonly':
        for key,status in (('r156_capture','PASS_OPERATOR_CAPTURE_CONSISTENCY_ONLY'),('year1_finance','PASS_OPERATOR_DECLARED_YEAR1_ENVELOPE_ONLY'),('catalog_parity','PASS_OPERATOR_REPORTED_35_CARD_DEFINITION_PARITY_ONLY')):
            if not isinstance(admission.get(key),dict) or admission[key].get('status') != status:
                raise ComparisonHold(role+': CURRENT_EVIDENCE_MISSING_'+key)
    h=raw.get('human_explanation_hu')
    if not isinstance(h,dict) or h.get('schema')!=R193_SCHEMA or h.get('gameplay_gate')!='STOP' or h.get('mode')!=mode:
        raise ComparisonHold(role + ': R193_HUMAN_REPORT_INVALID')
    if h.get('live_financing_approved') is not False or h.get('global_optimum_claimed') is not False:
        raise ComparisonHold(role + ': UNSUPPORTED_CERTIFICATION')
    score=raw.get('final_score')
    if type(score) not in (float,int) or not math.isfinite(score):
        raise ComparisonHold(role + ': SCORE_INVALID')
    rows=h.get('years'); envelopes=raw.get('annual_envelopes'); starts=raw.get('years')
    year=admission.get('current_period')
    if type(year) is not int or not 1<=year<=5 or not isinstance(rows,list) or len(rows)!=6-year or not isinstance(envelopes,list) or len(envelopes)!=len(rows) or not isinstance(starts,list) or len(starts)!=len(rows):
        raise ComparisonHold(role + ': CALENDAR_INVALID')
    budgets=[];costs=[]
    for offset,(r,e,ids) in enumerate(zip(rows,envelopes,starts)):
        target=year+offset
        if not isinstance(r,dict) or not isinstance(e,dict) or r.get('year')!=target or e.get('year')!=target or not isinstance(ids,list) or any(type(i) is not int or not 1<=i<=35 for i in ids) or len(ids)!=len(set(ids)):
            raise ComparisonHold(role + ': ANNUAL_ROW_INVALID')
        project_ids=[p.get('id') for p in r.get('projects',[]) if isinstance(p,dict)]
        if len(project_ids)!=len(ids) or sorted(ids)!=sorted(project_ids):
            raise ComparisonHold(role + ': ANNUAL_PROJECTS_INCONSISTENT')
        ceiling=e.get('scenario_ceiling_ecu');cost=r.get('total')
        if not _valid_nonneg(ceiling) or not _valid_nonneg(cost) or not _valid_nonneg(r.get('remaining_scenario_ceiling')) or not _valid_nonneg(r.get('once')) or not _valid_nonneg(r.get('annual_positive_maintenance')):
            raise ComparisonHold(role+': ANNUAL_FINANCE_INVALID')
        if abs(cost-(r['once']+r['annual_positive_maintenance']))>1e-6 or abs((ceiling-cost)-r['remaining_scenario_ceiling'])>1e-6 or cost>ceiling+1e-7 or abs(ceiling-r.get('scenario_ceiling',-1))>1e-6:
            raise ComparisonHold(role+': FINANCIAL_REPLAY_MISMATCH')
        budgets.append(ceiling);costs.append(cost)
    if len(set(budgets))!=1:
        raise ComparisonHold(role+': NONUNIFORM_SCENARIO_BUDGET_NOT_SUPPORTED')
    for key in ('input_state_sha256','original_35_catalog_sha256'):
        s=raw.get(key)
        if not isinstance(s,str) or len(s)!=64 or any(ch not in '0123456789abcdef' for ch in s):
            raise ComparisonHold(role+': SOURCE_IDENTITY_MISSING_'+key)
    return dict(raw=raw,calendar=rows,mode=mode,year=year,budget=budgets[0],costs=costs,score=score)


def compare(maximum, reserve):
    a=validate_receipt(maximum,'max'); b=validate_receipt(reserve,'reserve')
    for key in ('r162_source_pin','input_state_sha256','original_35_catalog_sha256','mode'):
        if maximum[key]!=reserve[key]:raise ComparisonHold('DIFFERENT_SOURCE_OR_MODE_'+key)
    if a['year']!=b['year']:raise ComparisonHold('DIFFERENT_START_PERIOD')
    # Same operator-recorded baseline must not silently differ across receipts.
    for key in ('active','fixed','current_period'):
        if a['raw']['admission'].get(key)!=b['raw']['admission'].get(key):
            raise ComparisonHold('ADMISSION_DRIFT_'+key)
    if not a['budget']>b['budget']>=0:
        raise ComparisonHold('RESERVE_BUDGET_MUST_BE_STRICTLY_LOWER')
    if a['mode']=='current-readonly':
        for key in ('r156_capture','year1_finance','catalog_parity'):
            if a['raw']['admission'].get(key)!=b['raw']['admission'].get(key):
                # year1 finance compares illustrative_budget in its receipt; treat
                # budget-specific record as unshareable without deeper source proof.
                if key!='year1_finance':raise ComparisonHold('CURRENT_EVIDENCE_DRIFT_'+key)
        # Current-year finance must be independently approved by the two R191
        # runner instances; no financing claim from this comparator.
    rows=[]
    for i,(ca,cb) in enumerate(zip(a['calendar'],b['calendar'])):
        rows.append({'year':ca['year'],'max_project_ids':[p['id'] for p in ca['projects']],
          'max_project_names':[p['name'] for p in ca['projects']],
          'reserve_project_ids':[p['id'] for p in cb['projects']],
          'reserve_project_names':[p['name'] for p in cb['projects']],
          'max_cost_ecu':ca['total'],'reserve_cost_ecu':cb['total'],
          'max_free_against_common_cap_ecu':round(a['budget']-ca['total'],4),
          'reserve_free_against_common_cap_ecu':round(a['budget']-cb['total'],4),
          'reserve_free_against_its_own_cap_ecu':round(b['budget']-cb['total'],4)})
    # Historical modeled-score advantage, NOT a verified live advantage.
    delta=round(a['score']-b['score'],9)
    return {'schema':'ECOSIM_R195_TWO_ENVELOPE_TRADEOFF_V1',
        'mode':a['mode'],'base_scenario_budget_ecu':a['budget'],'reserve_scenario_budget_ecu':b['budget'],
        'source_pin':PIN,'input_state_sha256':maximum['input_state_sha256'],
        'catalog_sha256':maximum['original_35_catalog_sha256'],
        'max_model_score':a['score'],'reserve_model_score':b['score'],
        'model_score_advantage_max_minus_reserve':delta,
        'max_min_annual_free_ecu':min(r['max_free_against_common_cap_ecu'] for r in rows),
        'reserve_min_annual_free_ecu':min(r['reserve_free_against_common_cap_ecu'] for r in rows),
        'annual_comparison':rows,'global_optimum_certified':False,
        'live_outcome_predicted':False,'financing_approved':False,'gameplay_gate':'STOP'}


def render_hu(result):
    def money(v):return f'{v:,.0f}'.replace(',',' ')
    b=result['base_scenario_budget_ecu'];s=result['reserve_scenario_budget_ecu']
    historical=result['mode']=='historical-test'
    lines=['# EcoSim – két ötéves terv összehasonlítása','',
      '**TÖRTÉNETI MODELLTESZT, NEM ÉLES PROJEKTINDÍTÁSI UTASÍTÁS.**' if historical else '**Aktuális, operátor által rögzített adatokra épülő MODELLJAVASLAT; nem játékbeli engedély.**','',
      '## Melyiket válasszuk, és miért?',
      f'**Pontszámra kihegyezett jelölt:** a modell szerinti érték {result["max_model_score"]:.6f}; egy évben legfeljebb {money(b)} ECU feltételezett projektkeret.',
      f'**Nagyobb tartalékú jelölt:** a modell szerinti érték {result["reserve_model_score"]:.6f}; egy évben legfeljebb {money(s)} ECU-t engedtünk a keresőnek.',
      f'A két pontérték különbsége (első mínusz második): {result["model_score_advantage_max_minus_reserve"]:+.6f} **feltételes modell-indexpont**; nem éles versenypontszám.',
      f'A legszűkebb évben az első terv legalább {money(result["max_min_annual_free_ecu"])} ECU-t, a tartalékos terv pedig legalább {money(result["reserve_min_annual_free_ecu"])} ECU-t hagyna meg azonos, {money(b)} ECU-s összehasonlítási keret mellett.','',
      '| Év | Pontszám-orientált projektek | Költség | Maradna | Tartalékos projektek | Költség | Maradna |',
      '|---|---|---:|---:|---|---:|---:|']
    for r in result['annual_comparison']:
        def names(k):return ', '.join(f'#{i} {n}' for i,n in zip(r[k+'_project_ids'],r[k+'_project_names'])) or 'Nincs új projekt'
        lines.append(f'| {r["year"]}. | {names("max")} | {money(r["max_cost_ecu"])} | {money(r["max_free_against_common_cap_ecu"])} | {names("reserve")} | {money(r["reserve_cost_ecu"])} | {money(r["reserve_free_against_common_cap_ecu"])} |')
    if result['model_score_advantage_max_minus_reserve'] < -1e-9:
        recommendation='A tartalékos jelölt a korlátos keresésben **nagyobb modellértéket és több szabad keretet is ad**. Érdemes ezzel kezdeni a csapatos felülvizsgálatot; egyik futás sem garantált globális optimum.'
    elif result['model_score_advantage_max_minus_reserve'] > 1e-9:
        recommendation='A magasabb keretes jelölt **nagyobb feltételes modellértéket**, a tartalékos jelölt **nagyobb pénzügyi mozgásteret** ad. A csapatnak kell eldöntenie, melyik fontosabb az igazolt keret fényében.'
    else:
        recommendation='A két jelölt modellértéke a kijelzett pontosságon belül egyenlő; a nagyobb tartalékú tervet érdemes előbb megvizsgálni.'
    lines+=['','## Döntési szempont',recommendation,
       'Ezek a jelöltek **két külön, korlátos keresés** eredményei; nem garantáltan globális optimumok, és nem ugyanazt a projektkészletet tartalmazzák. A maradék összegek a projektkártyák konzervatív költségeihez képest számított *feltételezett* keretmaradékok, nem rendelkezésre álló számlaegyenlegek.',
       'A partnertámogatások folyósítását, hitelköltségeket, adókat és nem-projekt műveleteket ez nem igazolja. Az éles játékban csak külön aktuális ellenőrzés után döntsetek.',
       '', '**Játékbeli művelet nincs. `GAME_ACTION_GATE=STOP`.**','']
    return '\n'.join(lines)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--max-receipt',type=Path,required=True)
    p.add_argument('--reserve-receipt',type=Path,required=True)
    p.add_argument('--out-json',type=Path,required=True)
    p.add_argument('--out-md',type=Path,required=True)
    a=p.parse_args(argv)
    paths=[x.resolve() for x in (a.max_receipt,a.reserve_receipt,a.out_json,a.out_md)]
    if len(set(paths)) !=4 or a.out_json.exists() or a.out_md.exists():
        p.error('HOLD: INPUT_OUTPUT_OVERLAP_OR_EXISTING_OUTPUT')
    try:
        maxr=json.loads(a.max_receipt.read_text(encoding='utf-8'))
        reserver=json.loads(a.reserve_receipt.read_text(encoding='utf-8'))
        result=compare(maxr,reserver)
    except (ValueError,OSError,TypeError,KeyError) as e:
        p.error('HOLD: '+str(e))
    # First validate everything, then create files exclusively in one evidence folder.
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_md.parent.mkdir(parents=True,exist_ok=True)
    with a.out_json.open('x',encoding='utf-8') as f:
        json.dump(result,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    with a.out_md.open('x',encoding='utf-8') as f:
        f.write(render_hu(result))
    print('R195_COMPARISON=PASS_OFFLINE_MODEL_ONLY GAME_ACTION_GATE=STOP')
    print('HUMAN_REPORT='+str(a.out_md))

if __name__=='__main__':main()
