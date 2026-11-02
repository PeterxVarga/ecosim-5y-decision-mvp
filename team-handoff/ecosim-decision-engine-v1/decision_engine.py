#!/usr/bin/env python3
"""Source-locked unified historical decision packet. Offline and NO_SEND."""
import argparse, hashlib, json
from pathlib import Path

EXPECTED={
 "R201":("ECOSIM_R201_HISTORICAL_ROBUST_DECISION_BOOK_V1","PASS_SOURCE_PINNED_TEST_TRIAGE_NOT_LIVE_CITY_OPTIMUM"),
 "R202":("ECOSIM_R202_TEST_REVENUE_AND_INSTITUTION_CALIBRATION_GATE_V1","PASS_SOURCE_DIAGNOSTIC_HOLD_GLOBAL_CALIBRATION"),
 "R203":("ECOSIM_R203_FACT_PLAN_SAFE_PARTIAL_ANNUAL_SENSITIVITY_V1","PASS_CONDITIONAL_R148_REPLAY_HOLD_UNIDENTIFIED_CITY_TRANSITIONS"),
}
def check(value,why):
 if not value: raise ValueError("HOLD_"+why)
def load(path):
 def pairs(seq):
  out={}
  for k,v in seq:
   check(k not in out,"DUPLICATE_JSON_KEY");out[k]=v
  return out
 def reject(_):raise ValueError("HOLD_NONFINITE_JSON")
 return json.loads(Path(path).read_text(),object_pairs_hook=pairs,parse_constant=reject)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def assemble(paths):
 docs={k:load(p) for k,p in paths.items()}
 for k,v in docs.items():
  schema,status=EXPECTED[k]
  check(v.get("schema")==schema,k+"_SCHEMA")
  check(v.get("status")==status,k+"_STATUS")
  check(v.get("mode")=="historical-test",k+"_MODE")
  check(v.get("gameplay_gate")=="STOP" and v.get("game_writes")==0,k+"_NO_GAME_WRITE")
 a,b,c=(docs[k] for k in EXPECTED)
 h=c["source_sha256"]
 for src,ref in [("baseline_source_sha256","r200_profile_source_state"),("finance_source_sha256","finance"),("institutions_source_sha256","institutions"),("r149_source_sha256","r149"),("r199_source_sha256","r199")]:
  check(a[src]==h[ref],"CROSS_SOURCE_"+ref)
 check(b["source_hashes"]["finance"]==h["finance"] and b["source_hashes"]["institutions"]==h["institutions"],"CALIBRATION_SOURCE_IDENTITY")
 robust=a["scenario_robustness"]
 check(robust["candidate_count"]==17 and robust["scenario_count"]==51 and c["r201_financial_candidate_scenarios"]==51,"SCENARIO_COVERAGE")
 check(c["r202_observed_source_model_pairs"]==18 and c["tab_count"]==10 and len(c["ten_tab_coverage"])==10,"OBSERVATION_COVERAGE")
 check(c["model_input_is_p1_plan_not_p0_fact"] is True,"FACT_PLAN_SEPARATION")
 check(a["calibrated_five_year_live_prediction"] is False and a["simulator_score_formula_proven"] is False,"R201_OVERCLAIM")
 check(b["live_prediction_calibrated"] is False and b["global_city_optimum_certified"] is False,"R202_OVERCLAIM")
 check(c["real_simulator_forecast_validated"] is False and c["global_city_optimum_certified"] is False and c["actual_cash_authorized"] is False,"R203_OVERCLAIM")
 return {
  "schema":"ECOSIM_UNIFIED_HISTORICAL_DECISION_PACKET_V1",
  "status":"PASS_PARTIAL_HISTORICAL_DECISION_SUPPORT_LIVE_HOLD",
  "mode":"historical-test","gameplay_gate":"STOP","game_writes":0,
  "report_hashes":{k:sha(v) for k,v in sorted(paths.items())},
  "source_hashes":dict(sorted(h.items())),
  "candidate_count":17,"scenario_count":51,"finance_pairs":18,"tab_accounting_count":10,
  "scenario_robustness":robust,
  "annual_transition_diagnostics":c["partial_project_transition_diagnostics"],
  "tab_coverage":c["ten_tab_coverage"],
  "financial_qualifications":{"model_identifiability":b["model_identifiability"],"units_and_bases":b["units_and_bases"],"research_priority":b["research_priority"]},
  "decision":{"historical_triage":"CONDITIONAL_ONLY","current_city_optimum":"NOT_PROVEN","live":"HOLD","game_actions":"STOP"},
  "unknowns":["money units","spendable funds","loans and grants","city dynamics","missing tab observations","server score formula","two closed FACT years"]
 }
def main():
 p=argparse.ArgumentParser()
 for k in EXPECTED:p.add_argument("--"+k.lower(),type=Path,required=True)
 p.add_argument("--out-dir",type=Path,required=True)
 args=p.parse_args();packet=assemble({k:getattr(args,k.lower()) for k in EXPECTED})
 out=args.out_dir;check(not out.exists(),"OUTPUT_EXISTS")
 out.mkdir(parents=True,mode=0o700)
 (out/"DECISION_PACKET.json").write_text(json.dumps(packet,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
 lines=["# EcoSim – egységes történeti döntési csomag","",
 "**PASS: reprodukálható részmodell; LIVE HOLD; GAME_ACTION_GATE=STOP.**","",
 "17 ötéves terv; 51 feltételes projekt–működés eset; 18 pénzügyi megfeleltetés; 10 fül bizonyítéklefedettségi mátrixa.","",
 "A p1 terv nem második lezárt tényév. A pénzegység, tényleges költhető keret, hitel/támogatás,",
 "közvetett városdinamika és szerveres pontozás nincs igazolva.",
 "A rangsor csak részmodell-alapú, nem éles játékbeli optimum.","",
 "Játékbeli művelet: 0. A privát forrásadatok nem kerülnek a GitHubra."]
 (out/"DECISION_PACKET_HU.md").write_text("\n".join(lines)+"\n")
 print(json.dumps({"status":packet["status"],"result":str(out),"game_writes":0}))
if __name__=="__main__":main()
