#!/usr/bin/env python3
"""R198: strict year-by-year R195↔R149 candidate ↔ R158 path identity join.

Read-only, source-locked, not an optimizer. Fail closed on tampered or partially
matched candidates; NEVER add cash to project budgets or claim city optimality.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bridge_r197 import assemble as bridge, load as strict_load

SCHEMA = 'ECOSIM_R198_PAIRED_CANDIDATE_POLICY_REVIEW_V1'
TIMING = 'r158_annual_partial_cash_timing'


def _sha(val):
    return isinstance(val, str) and len(val) == 64 and all(c in '0123456789abcdef' for c in val)


def _money(v):
    return type(v) in (float, int) and math.isfinite(v) and v >= 0


def _schedule_years(rows, key):
    if not isinstance(rows, list) or not 1 <= len(rows) <= 5:
        raise ValueError('INVALID_R195_YEARS')
    years = []
    ids = []
    costs = []
    for r in rows:
        if not isinstance(r, dict):
            raise ValueError('INVALID_R195_ROW')
        year = r.get('year')
        p = r.get(key + '_project_ids')
        cost = r.get(key + '_cost_ecu')
        if type(year) is not int or not 1 <= year <= 5 or not isinstance(p, list) or any(type(v) is not int or not 1 <= v <= 35 for v in p) or len(p) != len(set(p)) or not _money(cost):
            raise ValueError('INVALID_R195_ROW_' + key)
        years.append(year)
        ids.append(tuple(sorted(p)))
        costs.append(float(cost))
    if years != list(range(years[0], 6)):
        raise ValueError('NONCONTIGUOUS_R195_YEARS')
    if len(set(x for ys in ids for x in ys)) != sum(map(len, ids)):
        raise ValueError('DUPLICATE_R195_PROJECT_ACROSS_YEARS')
    return tuple(ids), costs


def _candidate(candidate, start, length):
    if not isinstance(candidate, dict):
        raise ValueError('INVALID_R149_CANDIDATE')
    c_id = candidate.get('candidate_id')
    p = candidate.get('project_ids_by_year')
    costs = candidate.get('conservative_project_need_ecu_by_year')
    if not isinstance(c_id, str) or not c_id or not isinstance(p, list) or len(p) != length or not isinstance(costs, list) or len(costs) != length:
        raise ValueError('INVALID_R149_CANDIDATE_SHAPE')
    schedule = []
    for ys, cost in zip(p, costs):
        if not isinstance(ys, list) or any(type(v) is not int or not 1 <= v <= 35 for v in ys) or len(ys) != len(set(ys)) or not _money(cost):
            raise ValueError('INVALID_R149_CANDIDATE_VALUES')
        schedule.append(tuple(sorted(ys)))
    if len(set(x for ys in schedule for x in ys)) != sum(map(len, schedule)):
        raise ValueError('DUPLICATE_R149_PROJECT_ACROSS_YEARS')
    return c_id, tuple(schedule), [float(c) for c in costs]


def _timing(t, expected, schedule, costs, start):
    if t.get('gameplay_gate') != 'STOP' or t.get('affordability_authorized') is not False or t.get('actual_spendable_cash_ecu') is not None or t.get('true_funding_gap_ecu') is not None:
        raise ValueError('TIMING_CLAIMS_APPROVAL')
    if t.get('candidate_id') != expected:
        raise ValueError('TIMING_CANDIDATE_DRIFT')
    rows = t.get('annual_rows')
    if not isinstance(rows, list) or len(rows) != len(schedule):
        raise ValueError('TIMING_CALENDAR_DRIFT')
    for offset, (r, ps, cost) in enumerate(zip(rows, schedule, costs)):
        if not isinstance(r, dict) or r.get('year') != start + offset:
            raise ValueError('TIMING_PERIOD_DRIFT')
        if not isinstance(r.get('projects_started_ids'), list) or tuple(sorted(r['projects_started_ids'])) != ps:
            raise ValueError('TIMING_PROJECT_DRIFT')
        if not _money(r.get('project_card_need_ecu')) or abs(r['project_card_need_ecu']-cost) > 1e-4:
            raise ValueError('TIMING_PROJECT_COST_DRIFT')
    # Only read values produced by the existing R159 stress calculation, no recomputation.
    return {
        'path_id': t['path_id'],
        'conditional_partial_net_after_card_cost_ecu': t.get('five_year_partial_net_after_card_cost_ecu'),
        'hypothetical_zero_opening_immediate_shortfall_ecu': t.get('hypothetical_peak_zero_opening_cash_shortfall_immediate_ecu'),
        'hypothetical_zero_opening_deferred_shortfall_ecu': t.get('hypothetical_peak_zero_opening_cash_shortfall_positive_receipts_deferred_ecu'),
        'conditional_terminal_partial_index_delta': t.get('conditional_terminal_mapped_proxy_delta'),
        'finance_approval': False,
    }


def join(tradeoff, tradeoff_sha, desk, desk_sha, city=None, city_sha=None):
    provenance = bridge(tradeoff, tradeoff_sha, desk, desk_sha, city, city_sha)
    if not _sha(tradeoff_sha) or not _sha(desk_sha):
        raise ValueError('MISSING_DOCUMENT_SHA')
    rows = tradeoff.get('annual_comparison')
    choices = {key: _schedule_years(rows, key) for key in ('max', 'reserve')}
    # Strict candidate corpus: candidate identity means complete schedule, not just first year.
    candidates = desk.get('candidate_comparison')
    if not isinstance(candidates, list) or not candidates:
        raise ValueError('R149_CANDIDATE_CORPUS_MISSING')
    parsed = {}
    for candidate in candidates:
        cid, sched, costs = _candidate(candidate, rows[0]['year'], len(rows))
        if cid in parsed:
            raise ValueError('DUPLICATE_R149_CANDIDATE_ID')
        parsed[cid] = (sched, costs)
    timing = desk.get(TIMING)
    if not isinstance(timing, dict) or timing.get('gameplay_gate') != 'STOP' or timing.get('true_cash_availability_or_financing_proven') is not False:
        raise ValueError('R159_TIMING_GATE_MISSING')
    combinations = timing.get('combinations')
    if not isinstance(combinations, list) or not combinations:
        raise ValueError('R159_COMBINATIONS_MISSING')
    sources = {}
    for name in ('r153_source_backed_tax_sensitivity','r154_source_four_tax_fiscal_tradeoffs','r155_source_operating_cash_tradeoffs',TIMING):
        mod = desk[name]
        if mod.get('source_class') != provenance['source_class']:
            raise ValueError('POLICY_SOURCE_CLASS_DRIFT')
        sources[name] = mod['source_class']
    allowed_paths = {x.get('path_id') for x in desk['r155_source_operating_cash_tradeoffs'].get('path_counterfactuals',[]) if isinstance(x, dict)}
    if not allowed_paths or None in allowed_paths:
        raise ValueError('INVALID_R155_PATHS')
    by_candidate = {}
    seen = set()
    for item in combinations:
        if not isinstance(item, dict) or not isinstance(item.get('path_id'), str) or item['path_id'] not in allowed_paths:
            raise ValueError('UNKNOWN_R159_PATH')
        cid = item.get('candidate_id')
        if cid not in parsed:
            raise ValueError('UNKNOWN_R159_CANDIDATE')
        pair = (cid, item['path_id'])
        if pair in seen:
            raise ValueError('DUPLICATE_R159_PAIR')
        seen.add(pair)
        sched, cost = parsed[cid]
        record = _timing(item, cid, sched, cost, rows[0]['year'])
        for name in ('conditional_partial_net_after_card_cost_ecu','hypothetical_zero_opening_immediate_shortfall_ecu','hypothetical_zero_opening_deferred_shortfall_ecu'):
            if type(record[name]) not in (int,float) or not math.isfinite(record[name]):
                raise ValueError('INVALID_R159_PARTIAL_METRIC')
        if record['conditional_terminal_partial_index_delta'] is not None and (type(record['conditional_terminal_partial_index_delta']) not in (int,float) or not math.isfinite(record['conditional_terminal_partial_index_delta'])):
            raise ValueError('INVALID_R159_INDEX_METRIC')
        by_candidate.setdefault(cid, []).append(record)
    findings = []
    for name,(sched, costs) in choices.items():
        first = [cid for cid,(seq,_) in parsed.items() if seq[0] == sched[0]]
        matched = [(cid,cc) for cid,(seq,cc) in parsed.items() if seq == sched]
        if len(matched) > 1:
            raise ValueError('DUPLICATE_COMPLETE_SCHEDULE')
        if not matched:
            findings.append({'plan':name,'status':'HOLD_NO_EXACT_PROJECT_SCHEDULE_MATCH',
                             'first_year_only_matches':len(first),'exact_candidate_id':None,
                             'costs_align':None,'paired_paths':[], 'r195_costs':costs})
            continue
        cid,cc = matched[0]
        aligned = all(abs(x-y) <= 1e-4 for x,y in zip(cc,costs))
        if not aligned:
            findings.append({'plan':name,'status':'HOLD_EXACT_PROJECTS_BUT_COSTS_DIFFER',
                             'first_year_only_matches':len(first),'exact_candidate_id':cid,
                             'costs_align':False,'paired_paths':[], 'r195_costs':costs, 'r149_costs':cc})
            continue
        paths = sorted(by_candidate.get(cid, []),key=lambda q:q['path_id'])
        findings.append({'plan':name,'status':'PAIRED_HYPOTHETICAL_PARTIAL_EFFECTS_ONLY' if paths else 'HOLD_NO_R159_PATHS',
                         'first_year_only_matches':len(first),'exact_candidate_id':cid,
                         'costs_align':True,'paired_paths':paths,'r195_costs':costs})
    any_match = any(x['status']=='PAIRED_HYPOTHETICAL_PARTIAL_EFFECTS_ONLY' for x in findings)
    return {'schema':SCHEMA,'status':'PARTIAL_IDENTICAL_CANDIDATE_POLICY_EVIDENCE_NO_GAME_AUTHORITY' if any_match else 'HOLD_R195_R149_CANDIDATE_MISMATCH',
            'mode':tradeoff['mode'],'r197_source_proof':{'same_initial_state':provenance['same_initial_state_verified'],'r195_sha256':tradeoff_sha,'r149_sha256':desk_sha,'r196_sha256':city_sha},
            'r149_candidate_count':len(parsed),'r159_tested_pairs':len(seen),'r159_policy_paths':sorted(allowed_paths),
            'findings':findings,'policy_source_class':provenance['source_class'],
            'complete_city_optimization':False,'full_city_cashflow_verified':False,
            'citywide_score_comparable_with_r195':False,'funds_authorized':False,
            'automatic_game_actions':0,'gameplay_gate':'STOP'}


def render_hu(r):
    text = ['# EcoSim R198 – projekt és várospolitikai pálya szigorú összevezetése','',
            '**Csak részleges, feltételes modell. Nem szerverhitelesített városi pénzügy vagy nyerő stratégia.**','',
            f'**Státusz:** `{r["status"]}` · R149 jelöltek: {r["r149_candidate_count"]}, R159 párok: {r["r159_tested_pairs"]}.','']
    for f in r['findings']:
        text.extend([f'## {"Pontszámorientált" if f["plan"]=="max" else "Tartalékos"} terv',
            f'**Egyezés:** `{f["status"]}`. Elsőéves egyező jelöltek: {f["first_year_only_matches"]}.',
            f'Teljes ötéves R149 jelölt: `{f["exact_candidate_id"] or "NINCS"}`.'])
        if f['paired_paths']:
            text.extend(['','| R159 pálya | Feltételes ötéves részleges nettó (ECU) | Azonnali 0 nyitó pénzes csúcshiány (ECU) | +1 év bevételkésleltetéses csúcshiány (ECU) |',
                         '|---|---:|---:|---:|'])
            for p in f['paired_paths']:
                text.append(f'| `{p["path_id"]}` | {p["conditional_partial_net_after_card_cost_ecu"]:,.0f} | {p["hypothetical_zero_opening_immediate_shortfall_ecu"]:,.0f} | {p["hypothetical_zero_opening_deferred_shortfall_ecu"]:,.0f} |')
        text.append('')
    text.extend(['A táblázat csak teljes év szerinti projektegyezés és kártyaköltség-egyezés esetén jelenhet meg. Az egyező első év önmagában nem jogosít összekapcsolásra.',
                 'A számított pénzáramok részleges, adott esetben szintetikus, *fix külső állapotú* ellenpéldák. Nem tartalmazzák bizonyítottan az összes intézményi, hitel-, támogatási és lakossági visszacsatolást.',
                 'A projektkeret nem növelhető ezekkel az összegekkel; a R195 modellpontszámokhoz nem adhatók hozzá.',
                 '', '**Nem történt EcoSim-módosítás. `GAME_ACTION_GATE=STOP`.**',''])
    return '\n'.join(text)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tradeoff',type=Path,required=True)
    p.add_argument('--decision-desk',type=Path,required=True)
    p.add_argument('--city-review',type=Path)
    p.add_argument('--out-json',type=Path,required=True)
    p.add_argument('--out-md',type=Path,required=True)
    args=p.parse_args()
    all_paths=[args.tradeoff,args.decision_desk,args.out_json,args.out_md] + ([args.city_review] if args.city_review else [])
    if len({v.resolve() for v in all_paths})!=len(all_paths) or args.out_json.exists() or args.out_md.exists():
        p.error('HOLD_OUTPUT_COLLISION')
    try:
        tradeoff, a = strict_load(args.tradeoff)
        desk, b = strict_load(args.decision_desk)
        city, c = strict_load(args.city_review) if args.city_review else (None,None)
        result=join(tradeoff,a,desk,b,city,c)
    except (ValueError,TypeError,KeyError,UnicodeError,OSError) as ex:
        p.error('HOLD: '+str(ex))
    args.out_json.parent.mkdir(parents=True,exist_ok=True)
    args.out_md.parent.mkdir(parents=True,exist_ok=True)
    with args.out_json.open('x',encoding='utf-8') as f:
        json.dump(result,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    with args.out_md.open('x',encoding='utf-8') as f:f.write(render_hu(result))
    print('R198_PAIR_REVIEW='+result['status']+' GAME_ACTION_GATE=STOP')

if __name__=='__main__':main()
