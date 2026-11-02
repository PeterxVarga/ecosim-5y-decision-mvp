#!/usr/bin/env python3
"""R203 future intake: 2 consecutive operator-declared FACT snapshots.

Strict structural admission only; DOES NOT authenticate EcoSim origin, infer
causality, calibrate tax/population dynamics, or permit gameplay.
"""
from __future__ import annotations
import argparse,hashlib,json,math,sys
from pathlib import Path

REPO=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(REPO/"team-handoff/r200-historical-plugplay/tools"))
from corpus_r200 import parse_json

SCHEMA="ECOSIM_R203_OPERATOR_DECLARED_TWO_CLOSED_FACTS_V1"
KEYS={"id","team","market","period","kind","captured_at","source_evidence_id",
      "factors","displayed_total_index","revenue_ecu","expense_ecu"}
def hold(condition,reason):
 if not condition:raise ValueError("HOLD_"+reason)
def numeric(v):return type(v) in (int,float) and math.isfinite(v)
def admissible(doc):
 hold(isinstance(doc,dict) and set(doc)=={"schema","source_class","snapshots"},
      "EXACT_INPUT_SCHEMA")
 hold(doc["schema"]==SCHEMA and doc["source_class"]=="OPERATOR_DECLARED_READONLY",
      "NO_HISTORICAL_AUTOMATIC_LIVE_FALLBACK")
 rows=doc["snapshots"]
 hold(isinstance(rows,list) and len(rows)==2,"EXACT_TWO_FACT_SNAPSHOTS")
 for s in rows:
  hold(isinstance(s,dict) and set(s)==KEYS,"FACT_SNAPSHOT_SCHEMA")
  hold(s["kind"]=="FACT","FACT_NOT_PLAN")
  hold(type(s["period"]) is int and 0<=s["period"]<=5,"PERIOD")
  hold(all(isinstance(s[k],str) and s[k].strip() for k in
      ("id","team","market","captured_at","source_evidence_id")),"SOURCE_IDENTITY")
  hold(isinstance(s["factors"],dict) and len(s["factors"])==29 and
       all(isinstance(k,str) and k.strip() and numeric(v) for k,v in s["factors"].items()),
       "29_NUMERIC_FACTORS")
  hold(all(numeric(s[k]) for k in ("displayed_total_index","revenue_ecu","expense_ecu")),
       "FACT_FINANCIAL_AND_SCORE_NUMERICS")
  hold(s["revenue_ecu"]>=0 and s["expense_ecu"]>=0,"NONNEGATIVE_FINANCE")
 a,b=rows
 hold(b["period"]==a["period"]+1,"CONSECUTIVE_CLOSED_PERIODS")
 hold(a["team"]==b["team"] and a["market"]==b["market"],"TEAM_MARKET_IDENTITY")
 hold(a["source_evidence_id"]!=b["source_evidence_id"] and a["id"]!=b["id"],
      "INDEPENDENT_FACT_RECORD_IDS")
 hold(set(a["factors"])==set(b["factors"]),"FACTOR_NAME_IDENTITY")
 return {"schema":"ECOSIM_R203_OPERATOR_FACT_PAIR_VALIDATION_V1",
   "status":"PASS_STRUCTURAL_ONLY_NOT_AUTHENTICATED_AND_NOT_MODEL_TRAINED",
   "periods":[a["period"],b["period"]],"team":a["team"],"market":a["market"],
   "factor_count":29,
   "observed_factors_difference_raw":{k:round(b["factors"][k]-a["factors"][k],8) for k in sorted(a["factors"])},
   "observed_displayed_index_difference_raw":
      round(b["displayed_total_index"]-a["displayed_total_index"],8),
   "observed_revenue_difference_raw":round(b["revenue_ecu"]-a["revenue_ecu"],8),
   "observed_expenses_difference_raw":round(b["expense_ecu"]-a["expense_ecu"],8),
   "observed_transition_pair_admitted_for_descriptive_analysis":1,
   "evidence_authenticated_against_server":False,
   "city_causality_or_transition_parameters_identified":False,
   "financial_units_independently_verified":False,
   "game_writes":0,"gameplay_gate":"STOP"}
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--input",type=Path,required=True)
 p.add_argument("--out-dir",type=Path,required=True)
 a=p.parse_args()
 if a.out_dir.exists():p.error("HOLD_EXISTING_OUTPUT")
 try:
  raw=a.input.read_bytes()
  hold(len(raw)<=2_000_000,"OVERSIZE")
  result=admissible(parse_json(raw))
  result["input_sha256"]=hashlib.sha256(raw).hexdigest()
 except (ValueError,TypeError,KeyError,OSError,IndexError,UnicodeError) as e:p.error(str(e))
 a.out_dir.mkdir(parents=True)
 (a.out_dir/"FACT_PAIR_R203.json").write_text(
    json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf8")
 print("R203_FACT_PAIR="+result["status"]+" GAME_ACTION_GATE=STOP")
if __name__=="__main__":main()
