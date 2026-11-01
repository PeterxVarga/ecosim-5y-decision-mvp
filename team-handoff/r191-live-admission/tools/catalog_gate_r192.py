#!/usr/bin/env python3
"""Read-only verification of an operator-observed current card catalog.

This is NOT server authentication: it prevents silent use of historical project
card definitions when current observations differ or are not supplied.
"""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
from math import isfinite
from pathlib import Path

class CatalogHold(ValueError):
    pass

_FIELDS=('name','startup_cost','maintenance_cost','investment','partner_support','project_conditions','effects')
_MONEY=('startup_cost','maintenance_cost','investment','partner_support')


def _time(s):
    if not isinstance(s,str):raise CatalogHold('BAD_CATALOG_CAPTURE_TIME')
    try: t=datetime.fromisoformat(s.replace('Z','+00:00'))
    except ValueError:raise CatalogHold('BAD_CATALOG_CAPTURE_TIME') from None
    if t.tzinfo is None or t.utcoffset() is None:raise CatalogHold('CATALOG_TIMEZONE_REQUIRED')
    return t.astimezone(timezone.utc)


def _card(c, label):
    if not isinstance(c,dict) or any(key not in c for key in ('id',)+_FIELDS):
        raise CatalogHold('INCOMPLETE_CATALOG_CARD_'+label)
    if type(c['id']) is not int or not 1<=c['id']<=35:
        raise CatalogHold('INVALID_CARD_ID_'+label)
    if not isinstance(c['name'],str) or not c['name'].strip():
        raise CatalogHold('INVALID_CARD_NAME_'+label)
    for k in _MONEY:
        v=c[k]
        if type(v) not in (int,float) or not isfinite(v):raise CatalogHold('INVALID_CARD_MONEY_'+label+'_'+k)
        if k in ('startup_cost','investment') and v<0:raise CatalogHold('NEGATIVE_CARD_STARTUP_'+label)
    conditions=c['project_conditions']
    if not isinstance(conditions,list) or any(not isinstance(v,str) or not v.strip() for v in conditions):
        raise CatalogHold('INVALID_CARD_CONDITIONS_'+label)
    if len(set(conditions))!=len(conditions):raise CatalogHold('DUPLICATE_CARD_CONDITION_'+label)
    effects=c['effects']
    if not isinstance(effects,list):raise CatalogHold('INVALID_CARD_EFFECTS_'+label)
    observed=[]
    for e in effects:
        if not isinstance(e,dict) or not isinstance(e.get('metric'),str) or not e['metric'].strip() or type(e.get('value_percent')) not in (int,float) or not isfinite(e['value_percent']):
            raise CatalogHold('INVALID_CARD_EFFECT_'+label)
        observed.append((e['metric'],float(e['value_percent'])))
    if len(set(m for m,_ in observed))!=len(observed):raise CatalogHold('DUPLICATE_CARD_EFFECT_'+label)
    return {'id':c['id'],'name':c['name'].strip(),**{k:float(c[k]) for k in _MONEY},
            'conditions':tuple(sorted(conditions)),'effects':tuple(sorted(observed))}


def validate_catalog(capture,state,original,*,now=None):
    """Require 35 current observed cards and exact historical optimizer parity.

    A difference blocks and requires a separate catalog/model refresh. Never
    re-label a historical test catalog as current evidence.
    """
    if not isinstance(capture,dict) or capture.get('schema')!='ECOSIM_R192_CURRENT_CARD_CATALOG_V1' or capture.get('capture_mode')!='CURRENT_READONLY':
        raise CatalogHold('CURRENT_CATALOG_EVIDENCE_REQUIRED')
    provenance=state.get('provenance') or {}
    for k in ('team','market','round'):
        if not isinstance(capture.get(k),str) or capture[k]!=provenance.get(k):
            raise CatalogHold('CATALOG_PROVENANCE_MISMATCH_'+k.upper())
    if type(capture.get('period')) is not int or capture['period']!=provenance.get('current_period'):
        raise CatalogHold('CATALOG_PERIOD_MISMATCH')
    evidence=capture.get('source_evidence_id')
    if not isinstance(evidence,str) or not evidence.strip() or len(evidence)>256:
        raise CatalogHold('CATALOG_SOURCE_PROVENANCE_MISSING')
    if any(token in (evidence+' '+str(capture.get('source_view',''))).lower() for token in ('historical','tesztfordul','test_round','placeholder','example','synthetic')):
        raise CatalogHold('HISTORICAL_CATALOG_AS_CURRENT')
    if not isinstance(capture.get('source_view'),str) or not capture['source_view'].strip() or len(capture['source_view'])>256:
        raise CatalogHold('CATALOG_SOURCE_VIEW_MISSING')
    when=_time(capture.get('captured_at_local'))
    state_time=_time(provenance.get('captured_at_local'))
    if abs((when-state_time).total_seconds())>3600:
        raise CatalogHold('CATALOG_NOT_SAME_PERIOD_CAPTURE_WINDOW')
    now=(now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if not -timedelta(minutes=5)<=now-when<=timedelta(hours=48):
        raise CatalogHold('CATALOG_OBSERVATION_STALE_OR_FUTURE')
    if not isinstance(original,dict) or not isinstance(original.get('projects'),list):
        raise CatalogHold('PINNED_HISTORICAL_CATALOG_REQUIRED')
    values=capture.get('projects')
    if not isinstance(values,list) or len(values)!=35 or len(original['projects'])!=35:
        raise CatalogHold('ALL_35_CURRENT_AND_HISTORICAL_CARDS_REQUIRED')
    cur={}
    for c in values:
        parsed=_card(c,'CURRENT')
        if parsed['id'] in cur:raise CatalogHold('DUPLICATE_CURRENT_CARD_ID')
        cur[parsed['id']]=parsed
    old={}
    for c in original['projects']:
        parsed=_card(c,'HISTORICAL')
        if parsed['id'] in old:raise CatalogHold('DUPLICATE_HISTORICAL_CARD_ID')
        old[parsed['id']]=parsed
    if set(old)!=set(range(1,36)) or set(cur)!=set(old):
        raise CatalogHold('CURRENT_CATALOG_IDENTITY_DRIFT')
    different=[i for i in sorted(cur) if cur[i]!=old[i]]
    if different:raise CatalogHold('CURRENT_CARD_DEFINITION_DRIFT_IDS_'+','.join(map(str,different[:8])))
    return {'schema':'ECOSIM_R192_CATALOG_PARITY_V1',
            'status':'PASS_OPERATOR_REPORTED_35_CARD_DEFINITION_PARITY_ONLY',
            'observed_card_count':35,'source_evidence_id':evidence,
            'server_attested':False,'independent_from_operator':False,
            'gameplay_gate':'STOP'}
