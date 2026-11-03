#!/usr/bin/env python3
"""R196: fail-closed cross-tab evidence review for an existing R195 result.

This is NOT a second optimizer and cannot authorize gameplay. Its purpose is to
prevent a project-only plan being misrepresented as an optimized city policy.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlsplit

SCHEMA = 'ECOSIM_R196_CITY_CROSS_TAB_REVIEW_V1'
EVIDENCE_SCHEMA = 'ECOSIM_R196_OPERATOR_CITY_VIEWS_V1'
TRADEOFF_SCHEMA = 'ECOSIM_R195_TWO_ENVELOPE_TRADEOFF_V1'
TABS = {
    'summary': ('Összefoglalás', 'index, csapat, forduló', 'BASELINE_PARTIAL'),
    'projects': ('Projektek', '35 kártya, kiválasztás, előfeltételek, limit', 'DIRECT_R195'),
    'institutions': ('Városi intézmények', 'létszám, bérek, anyagköltség', 'R155_PARTIAL_NOT_R195'),
    'transport': ('Közösségi közlekedés', 'díjak, járatok, kapacitás, utasszám', 'R155_PARTIAL_NOT_R195'),
    'income': ('Bevételek', 'adók, díjak, időzítés és adóalap', 'R153_R155_PARTIAL_NOT_R195'),
    'population': ('Lakossági adatok', 'népesség és szociális változások', 'BASELINE_ONLY'),
    'corporations': ('Vállalkozások', 'adóalap, cégek, késleltetett hatások', 'BASELINE_ONLY'),
    'loans': ('Hitelek', 'hitelkeret, kamat, törlesztés', 'HYPOTHETICAL_BRIDGE_ONLY'),
    'finance': ('Pénzügyek', 'cash flow, mérleg, szabad keret és kötelezettség', 'YEAR1_GATE_ONLY'),
    'analysis': ('Elemzés', '29 tényező, 6 súly és indexérték', 'BASELINE_PARTIAL'),
}
REQUIRED_TOPICS = {
    'summary': ('period_and_team', 'smartcity_index'),
    'projects': ('35_cards', 'running_and_selected', 'project_cap'),
    'institutions': ('staffing', 'wages_and_materials'),
    'transport': ('fares', 'fleet_or_routes', 'ridership'),
    'income': ('taxes', 'service_fees', 'revenue'),
    'population': ('population', 'social_and_housing'),
    'corporations': ('company_counts', 'business_tax_base'),
    'loans': ('short_long_terms', 'rates_and_constraints'),
    'finance': ('cash_flow', 'balance_sheet', 'spendable_and_committed', 'monetary_unit'),
    'analysis': ('29_factors', 'six_index_weights'),
}

class CityHold(ValueError):
    pass


def _pairs(items):
    ret = {}
    for key, val in items:
        if key in ret:
            raise CityHold('DUPLICATE_JSON_KEY')
        ret[key] = val
    return ret


def _float(s):
    v = float(s)
    if not math.isfinite(v):
        raise CityHold('NONFINITE_JSON_NUMBER')
    return v


def read_json(p):
    b = Path(p).read_bytes()
    if len(b) > 10_000_000:
        raise CityHold('OVERSIZED_INPUT')
    try:
        d = json.loads(b.decode('utf-8'), object_pairs_hook=_pairs, parse_float=_float,
                       parse_constant=lambda _: (_ for _ in ()).throw(CityHold('NONFINITE_JSON_NUMBER')))
    except (UnicodeError, json.JSONDecodeError) as e:
        raise CityHold('INVALID_JSON') from e
    return d, hashlib.sha256(b).hexdigest()


def _timestamp(s):
    try:
        d = datetime.fromisoformat(s.replace('Z', '+00:00'))
        if d.tzinfo is None:
            raise ValueError()
        return d.astimezone(timezone.utc)
    except (ValueError, TypeError, AttributeError):
        raise CityHold('INVALID_TIME_WITH_TIMEZONE_REQUIRED') from None


def validate_result(result):
    if not isinstance(result, dict) or result.get('schema') != TRADEOFF_SCHEMA:
        raise CityHold('R195_RESULT_REQUIRED')
    if result.get('gameplay_gate') != 'STOP' or result.get('financing_approved') is not False or result.get('live_outcome_predicted') is not False:
        raise CityHold('UNSAFE_R195_CLAIMS')
    if result.get('mode') not in ('historical-test', 'current-readonly'):
        raise CityHold('BAD_R195_MODE')
    if any(not isinstance(result.get(key), str) or not re.fullmatch('[0-9a-f]{64}', result[key])
           for key in ('input_state_sha256', 'catalog_sha256')):
        raise CityHold('SOURCE_HASH_MISSING')
    if not isinstance(result.get('annual_comparison'), list) or not 1 <= len(result['annual_comparison']) <= 5:
        raise CityHold('R195_CALENDAR_MISSING')
    if any(type(result.get(k)) not in (int,float) or not math.isfinite(result[k])
           for k in ('max_model_score','reserve_model_score')):
        raise CityHold('INVALID_R195_SCORE')
    return result


def review(result, result_hash, evidence=None, *, now=None):
    result = validate_result(result)
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise CityHold('CLOCK_WITH_TIMEZONE_REQUIRED')
    entries = []
    if evidence is not None:
        if not isinstance(evidence, dict) or evidence.get('schema') != EVIDENCE_SCHEMA:
            raise CityHold('R196_EVIDENCE_SCHEMA_REQUIRED')
        if evidence.get('mode') != result['mode'] or evidence.get('tradeoff_sha256') != result_hash:
            raise CityHold('EVIDENCE_WRONG_RUN_OR_MODE')
        if evidence.get('input_state_sha256') != result['input_state_sha256'] or evidence.get('catalog_sha256') != result['catalog_sha256']:
            raise CityHold('EVIDENCE_WRONG_STATE_OR_CATALOG')
        if not isinstance(evidence.get('tabs'), dict) or set(evidence['tabs']) != set(TABS):
            raise CityHold('EXACTLY_TEN_VIEWS_REQUIRED')
    for key, (label, subject, model_scope) in TABS.items():
        raw = None if evidence is None else evidence['tabs'][key]
        if raw is not None and not isinstance(raw, dict):
            raise CityHold('MALFORMED_VIEW_' + key)
        if raw is None or raw.get('status') == 'MISSING':
            if raw is not None and set(raw) != {'status'}:
                raise CityHold('MISSING_VIEW_CANNOT_CLAIM_EVIDENCE_' + key)
            status, source = 'MISSING', None
            confirmed = []
        else:
            if raw.get('status') != 'OPERATOR_OBSERVED':
                raise CityHold('INVALID_VIEW_STATUS_' + key)
            source = raw.get('source_evidence_id')
            if not isinstance(source, str) or not source.strip() or len(source) > 512:
                raise CityHold('EVIDENCE_SOURCE_MISSING_' + key)
            uri = raw.get('source_view')
            if not isinstance(uri,str):
                raise CityHold('SOURCE_VIEW_INVALID_' + key)
            u = urlsplit(uri)
            expected_path = '/simulation/' + key
            # A view attribution is only trusted for its exact documented
            # page. Reject prefix spoofing and accidental login tokens.
            if (u.scheme != 'https' or u.netloc != 'edu.ecosim.hu'
                or u.query or u.fragment or u.path.rstrip('/') != expected_path):
                raise CityHold('SOURCE_VIEW_INVALID_' + key)
            age = now.astimezone(timezone.utc) - _timestamp(raw.get('captured_at_local'))
            if result['mode'] == 'current-readonly' and not -timedelta(minutes=5) <= age <= timedelta(hours=48):
                raise CityHold('CURRENT_EVIDENCE_STALE_' + key)
            confirmed = raw.get('observed_topics')
            if not isinstance(confirmed, list) or len(confirmed) != len(set(map(str, confirmed))) or any(
                not isinstance(v, str) for v in confirmed):
                raise CityHold('OBSERVED_TOPICS_INVALID_' + key)
            if set(confirmed) - set(REQUIRED_TOPICS[key]):
                raise CityHold('UNKNOWN_OBSERVATION_TOPIC_' + key)
            status = 'OPERATOR_REPORTED_COMPLETE' if set(confirmed) == set(REQUIRED_TOPICS[key]) else 'OPERATOR_REPORTED_PARTIAL'
        entries.append({'key': key, 'view': label, 'needed': subject, 'model_scope':model_scope,
                        'observation_status':status, 'source_evidence_id':source,
                        'missing_topics':[k for k in REQUIRED_TOPICS[key] if k not in confirmed]})
    missing = [r['key'] for r in entries if r['observation_status'] != 'OPERATOR_REPORTED_COMPLETE']
    # Even complete operator-reported coverage CANNOT certify complete city optimization.
    status = ('HISTORICAL_PROJECT_MODEL_ONLY' if result['mode'] == 'historical-test'
              else 'HOLD_INCOMPLETE_CITY_COVERAGE' if missing else 'HOLD_CITY_EFFECTS_NOT_JOINTLY_VALIDATED')
    return {'schema':SCHEMA,'mode':result['mode'],'r195_result_sha256':result_hash,
            'r195_input_state_sha256':result['input_state_sha256'],
            'r195_catalog_sha256':result['catalog_sha256'],
            'status':status,'view_count':len(entries),'complete_operator_observed_views':len(entries)-len(missing),
            'missing_or_partial_views':missing, 'views':entries,
            'r195_scores_only_evaluate_project_model':True,
            'r153_r155_partial_models_exist_but_not_run_in_r195':True,
            'actual_citywide_optimized':False,'financing_approved':False,
            'live_score_prediction_validated':False,'gameplay_gate':'STOP'}


def render_hu(d):
    lines = ['# EcoSim – R196 teljes városi döntési lefedettség','',
        '**A sikeres R195 kétterves futás kizárólag projektmodellt bizonyít; ez nem teljes városi optimális döntéssor.**','',
        f'**Ellenőrzés:** `{d["status"]}` · **{d["complete_operator_observed_views"]}/10** fülről teljesnek jelölt operátori megfigyelés.','',
        '| Fül | Megfigyelés | A jelenlegi R195-ben való szerep | Még ellenőrizendő |',
        '|---|---|---|---|']
    for r in d['views']:
        missing=', '.join(r['missing_topics']) or '—'
        lines.append(f'| {r["view"]} | {r["observation_status"]} | `{r["model_scope"]}` | {missing} |')
    lines += ['', '## Miért nem lehet még egyetlen legjobb városi tervet állítani?',
      'Az R153–R155 adó-, díj- és intézményi részmodellek léteznek az eredeti R162 forrásában, **de az R195 nem futtatja őket a két projektterv összehasonlításakor**.',
      'A hitelek, adóalap, népesség-/vállalkozásváltozás, közlekedési kapacitás és teljes cash flow jövőbeli kölcsönhatásai nem hitelesített teljes állapotátmenetek.',
      'A közölt R195 pontértékeket ezért nem szabad a teljes városi politika pontértékeként rangsorolni. A projektköltségkeret nem teljes szabad városi pénzegyenleg.','',
      '## Következő döntési feladat',
      'A hiányzó aktuális fülek megfigyelése és a már létező R149–R159 policy-/tax-/operating modulok ugyanazon csapat- és periódusazonosságú bemenethez kötése. Eltérő vagy hiányzó forrásnál maradjon HOLD.', '',
      '**Szerver által jóváhagyott éles döntés: NEM. Játékbeli művelet: 0. `GAME_ACTION_GATE=STOP`.**','']
    return '\n'.join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tradeoff',type=Path,required=True)
    p.add_argument('--city-evidence',type=Path)
    p.add_argument('--out-json',type=Path,required=True)
    p.add_argument('--out-md',type=Path,required=True)
    args = p.parse_args(argv)
    paths=[x.resolve() for x in (args.tradeoff,args.out_json,args.out_md,*([args.city_evidence] if args.city_evidence else []))]
    if len(paths)!=len(set(paths)) or args.out_json.exists() or args.out_md.exists():
        p.error('HOLD: FILE_COLLISION')
    try:
        r, dig = read_json(args.tradeoff)
        ev = read_json(args.city_evidence)[0] if args.city_evidence else None
        out = review(r,dig,ev)
        txt = render_hu(out)
    except (CityHold,ValueError,TypeError,KeyError,OSError) as e:
        p.error('HOLD: '+str(e))
    args.out_json.parent.mkdir(parents=True,exist_ok=True)
    args.out_md.parent.mkdir(parents=True,exist_ok=True)
    with args.out_json.open('x',encoding='utf-8') as f:
        json.dump(out,f,ensure_ascii=False,indent=2,allow_nan=False)
        f.write('\n')
    with args.out_md.open('x',encoding='utf-8') as f:
        f.write(txt)
    print('R196_CITY_REVIEW='+out['status']+' GAME_ACTION_GATE=STOP')
    print('CITY_REPORT='+str(args.out_md))

if __name__ == '__main__':main()
