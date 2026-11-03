#!/usr/bin/env python3
"""R212: audited current 35-card catalog drift admission; original R162 reuse.

Pure operator-declared, read-only source adapter. DOES NOT authenticate the
EcoSim server and never changes the R162 historical catalog on disk.
"""
from __future__ import annotations
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
from hashlib import sha256
import json
from math import isfinite

SCHEMA = "ECOSIM_R212_SOURCE_ADAPTED_CATALOG_V1"
STATUS = "PASS_OPERATOR_CAPTURE_COMPLETE_WITH_CATALOG_DRIFT_NOT_SERVER_ATTESTED"

class AdapterHold(ValueError): pass

def need(condition, code):
    if not condition: raise AdapterHold("HOLD_"+code)

def prepare(capture, state, historical, *, now=None, catalog_hash=None):
    # Import the ORIGINAL R192 card parser to preserve existing card-money,
    # dependency, uniqueness and metric-validation contracts.
    from catalog_gate_r192 import _card, _time
    need(isinstance(capture,dict) and capture.get("schema")=="ECOSIM_R192_CURRENT_CARD_CATALOG_V1"
         and capture.get("capture_mode")=="CURRENT_READONLY","ORIGINAL_R192_SCHEMA")
    need(isinstance(state,dict) and isinstance(state.get("provenance"),dict),"STATE")
    prov=state["provenance"]
    for key in ("team","market","round"):
        need(type(capture.get(key)) is str and capture[key] == prov.get(key),"SOURCE_"+key.upper())
    need(type(capture.get("period")) is int and capture["period"]==prov.get("current_period"),
         "PERIOD")
    evidence=capture.get("source_evidence_id")
    view=capture.get("source_view")
    need(type(evidence) is str and 0<len(evidence.strip())<=256 and
         type(view) is str and 0<len(view.strip())<=256, "SOURCE_EVIDENCE")
    forbidden=("historical","tesztfordul","test_round","placeholder","example","synthetic")
    need(not any(x in (evidence+" "+view).casefold() for x in forbidden),"HISTORICAL_AS_CURRENT")
    try:
        when=_time(capture.get("captured_at_local"))
        same=_time(prov.get("captured_at_local"))
    except ValueError as err:raise AdapterHold("HOLD_TIMESTAMP_INVALID") from err
    now=(now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    need(abs((when-same).total_seconds())<=3600,"CAPTURE_WINDOW")
    need(-timedelta(minutes=5)<=now-when<=timedelta(hours=48),"STALE_OR_FUTURE")
    need(isinstance(historical,dict) and isinstance(historical.get("projects"),list) and
         isinstance(capture.get("projects"),list) and
         len(historical["projects"])==len(capture["projects"])==35,"EXACT_35")
    def scan(rows,tag):
        result={};normalized={}
        for c in rows:
            try: v=_card(c,tag)
            except (ValueError,TypeError,KeyError) as exc:raise AdapterHold("HOLD_INVALID_CARD_"+tag) from exc
            i=v["id"]
            need(i not in result,"DUPLICATE_CARD_"+tag)
            result[i]=dict(c)
            normalized[i]=v
        need(set(result)==set(range(1,36)),"CARD_IDENTITY_"+tag)
        return result,normalized
    current,c_norm=scan(capture["projects"],"CURRENT")
    original,h_norm=scan(historical["projects"],"PINNED_HISTORICAL")
    drift=[i for i in range(1,36) if c_norm[i]!=h_norm[i]]
    need(bool(drift),"PARITY_USE_R192_DEFAULT")
    # No placeholder or hidden test status is copied into the active index.
    index={i:{key:value for key,value in current[i].items()
              if key in ("id","name","category","startup_cost","maintenance_cost",
                         "investment","partner_support","project_conditions","effects")}
           for i in range(1,36)}
    severe=[i for i in drift if c_norm[i]["name"]!=h_norm[i]["name"]
            or c_norm[i]["conditions"]!=h_norm[i]["conditions"]
            or c_norm[i]["effects"]!=h_norm[i]["effects"]]
    return {
        "receipt":{
          "schema":SCHEMA,"status":STATUS,"observed_card_count":35,
          "source_evidence_id":evidence,
          "current_catalog_sha256":catalog_hash,
          "current_card_definition_drift_ids":drift,
          "semantic_or_dependency_drift_ids":severe,
          "original_r162_model_source_unchanged":True,
          "source_basis":"OPERATOR_DECLARED_CURRENT_CARDS_NOT_SERVER_ATTESTED",
          "server_attested":False,"gameplay_gate":"STOP",
          "true_cash_approved":False,"official_scoring_validated":False},
        "index":index
    }

@contextmanager
def original_search_with_current_index(strategy_module,index):
    """Temporarily bind the original R162 search's input provider, never rewrite it.

    R162's R160 independent audit receives exactly this index; finally restores
    the original provider even when a candidate or audit fails.
    """
    need(isinstance(index,dict) and set(index)==set(range(1,36)),"INDEX_REQUIRED")
    original=strategy_module.project_index
    need(callable(original),"ORIGINAL_PROVIDER_REQUIRED")
    try:
        strategy_module.project_index=lambda: index
        yield
    finally:
        strategy_module.project_index=original
