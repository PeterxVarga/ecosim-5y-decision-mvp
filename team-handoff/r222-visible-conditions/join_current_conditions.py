#!/usr/bin/env python3
"""Audit R221 what-if plans against R222 *actually displayed* prerequisites.

Pure read-only verification; explicitly does NOT upgrade R191/R192/R214.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from conditions_r222 import SCHEMA as R222_SCHEMA
from json_integrity_r162 import read_json

SCHEMA="ECOSIM_R222_DISPLAYED_DEPENDENCY_TO_R221_SCENARIO_JOIN_V1"
def need(x,msg):
    if not x:raise ValueError("HOLD_"+msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify(r221,r222,*,r221_source_hash=None):
    need(r221.get("schema")=="ECOSIM_R221_REAL_SOURCE_SCENARIO_FRONTIER_NO_LIVE_CAP_OR_CASH_V1" and
         r221.get("status")=="PASS_ACTUAL_SOURCE_HYPOTHETICAL_SCENARIO_SEARCH_ONLY" and
         r221.get("gameplay_gate")=="STOP" and r221.get("game_writes")==0 and
         r221.get("searched_scenario_count")==24 and len(r221.get("scenarios",[]))==24 and
         not r221.get("live_advisory_authorized"),
         "R221_IS_HYPOTHETICAL_NOT_LIVE")
    need(r222.get("schema")==R222_SCHEMA and
         r222.get("status")=="PASS_35_DISPLAYED_CONDITION_FIELDS_MATCH_ORIGINAL_R192_TIME_HOLD" and
         r222.get("r192_time_admission")=="HOLD_CATALOG_NOT_SAME_PERIOD_CAPTURE_WINDOW" and
         r222.get("displayed_condition_sections")==2 and
         r222.get("no_condition_section_displayed_cards")==33 and
         not r222.get("r214_live_advisory_authorized") and
         r222.get("gameplay_gate")=="STOP" and r222.get("game_writes")==0,
         "R222_CONDITIONS_AND_TIME_HOLD")
    for name in ("r217","r220"):
        need(r221["source_sha256"][name]==r222["source_sha256"][name.upper()],
             "R221_R222_COMMON_SOURCE_"+name)
    # Explicit UI observations; not a historical catalog substitution.
    raw=r222["observed_explicit_condition_rules"]
    need(raw=={"30":["Bicikliútfejlesztés — Fut"],
               "31":["Vasútfejlesztés — Fut"]},"ACTUAL_TWO_DISPLAYED_CONDITIONS")
    ids_by_name={"Bicikliútfejlesztés":29,"Vasútfejlesztés":27}
    required={int(i):ids_by_name[values[0].split(" — ",1)[0]] for i,values in raw.items()}
    need(required=={30:29,31:27},"EXACT_CURRENT_DEPENDENCIES")
    counts={30:0,31:0};all_years=0
    for row in r221["scenarios"]:
        cap=row["hypothetical_cap"]
        budget=row["hypothetical_annual_budget_ecu"]
        need(cap in (1,2,3) and budget in (0,25000,50000,150000)
             and row["gameplay_gate"]=="STOP" and
             row["validated_by_original_r160"] and not row["financing_authorized"],
             "ORIGINAL_R160_AND_SCENARIO_LIMITS")
        years=row["full_five_year_illustrative_starts"]
        need(len(years)==5 and years[0]==row["initial_project_ids"],
             "FIVE_YEAR_PLAN_IDENTITY")
        previous=set([14,22,23,24,34,35]);started=set()
        for year,started_now in enumerate(years,1):
            need(isinstance(started_now,list) and all(type(i) is int and i in range(1,36) for i in started_now)
                 and len(set(started_now))==len(started_now) and
                 not (set(started_now)&(started|previous)),
                 "DUPLICATE_OR_PREVIOUSLY_RUNNING_PROJECT")
            allowed=cap+int(1 in previous)
            need(len(started_now)<=allowed,"HYPOTHETICAL_CAP_OR_PRIOR_PROJECT1_BONUS")
            for project,pre in required.items():
                if project in started_now:
                    need(pre in previous,
                         "DISPLAYED_CURRENT_PREREQUISITE_"+str(project)+"_MISSING_YEAR_"+str(year))
                    counts[project]+=1
            started.update(started_now)
            previous.update(started_now)
            all_years+=1
    need(all(n>0 for n in counts.values()),"DEPENDENCIES_NOT_EXERCISED_IN_SCENARIOS")
    return {
      "schema":SCHEMA,"status":"PASS_24_FIVE_YEAR_SCENARIOS_RESPECT_CURRENT_DISPLAYED_DEPENDENCIES",
      "actual_current_source":"R222_FOUR_CLIENT_PAGE_SNAPSHOTS_NOT_SERVER_ATTESTED",
      "r221_source_sha256":r221_source_hash,
      "source_aligned_r217_r220":True,
      "validated_24_scenario_count":len(r221["scenarios"]),
      "audited_virtual_year_rows":all_years,
      "current_ui_dependency_rules":{"30":29,"31":27},
      "scenarios_containing_dependency_starts":{str(k):v for k,v in counts.items()},
      "uses_original_r160_audited_hypothetical_search":True,
      "r192_time_gate_still_hold":True,
      "r191_project_limit_still_unknown":True,
      "r214_current_spendable_cash_still_unknown":True,
      "current_server_conditions_cryptographically_authenticated":False,
      "gameplay_gate":"STOP","game_writes":0,
      "actual_gameplay_recommendation_authorized":False}
def main():
    a=argparse.ArgumentParser()
    a.add_argument("--r221",required=True,type=Path)
    a.add_argument("--r222",required=True,type=Path)
    a.add_argument("--out-dir",required=True,type=Path)
    args=a.parse_args()
    out=args.out_dir.resolve()
    need(not out.exists() and out.parent.is_dir(),"NEW_PRIVATE_OUTPUT")
    result=verify(read_json(args.r221),read_json(args.r222),r221_source_hash=sha(args.r221))
    out.mkdir(mode=0o700)
    (out/"R222_DEPENDENCY_JOIN.json").write_text(
         json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"status":result["status"],"years":result["audited_virtual_year_rows"],
       "scenario_count":result["validated_24_scenario_count"],
       "dependent_starts":result["scenarios_containing_dependency_starts"],
       "game_writes":0},ensure_ascii=False))
if __name__=="__main__":main()
