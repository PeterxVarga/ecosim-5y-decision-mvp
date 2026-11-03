#!/usr/bin/env python3
"""R215: operator city XLSX -> candidate 29-factor + index CSV for R156 form.

This is NOT R156 CURRENT_READONLY admission and cannot create an authenticated
EcoSim PLAN snapshot. No current active-project or finance fields are invented.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"team-handoff/r213-city-excel"),
              str(ROOT/"ECOSIM_R162_INTEGRITY_REVIEW_RC/tools")]
from city_excel_r213 import load_xlsx,TEAM,GROUPS
from r142_proxy_reference import COEFF
from observation_bundle_r152 import INDEX_LABEL

SCHEMA="ECOSIM_R215_OPERATOR_EXCEL_FACTOR_PREFILL_CANDIDATE_V1"
HIST_SHA="c6cd0681a28872beb556652b584674f442c5105c379f365027ee9dbd3efe69bc"
class FactorHold(ValueError): pass
def need(ok,why):
    if not ok:raise FactorHold("HOLD_"+why)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def selected_factors(book,team):
    need(team in book["teams"],"TEAM_NOT_IN_WORKBOOK")
    col=book["teams"].index(team)
    values={}
    expected=set(COEFF)|{INDEX_LABEL}
    for row in book["rows"]:
        if row["section"]!="Összefoglaló" or row["label"] not in expected:continue
        name=row["label"]
        need(name not in values,"DUPLICATE_FACTOR_"+name)
        val=row["values"][col]
        need(type(val) in (int,float) and math.isfinite(val),"MISSING_OR_NONNUMERIC_FACTOR_"+name)
        need(0<=val<=100,"FACTOR_OUTSIDE_DISPLAY_SCALE_"+name)
        values[name]=val
    need(set(values)==expected and len(COEFF)==29 and len(values)==30,
         "EXACT_29_FACTORS_AND_INDEX")
    return values

def assemble(historical,current,team,source_id,out_dir):
    historical=Path(historical);current=Path(current);out=Path(out_dir).resolve()
    need(not out.exists() and out.parent.is_dir() and not out.parent.is_symlink(),"NEW_PRIVATE_OUTPUT")
    need(type(source_id) is str and 4<=len(source_id.strip())<=180
         and not any(x in source_id.casefold() for x in
                     ("mock","historical","test","teszt","synthetic","example","fixture","password","token")),
         "CURRENT_SOURCE_EVIDENCE_ID_REQUIRED")
    need(sha(historical)==HIST_SHA,"BASELINE_HISTORICAL_SHA")
    old=load_xlsx(historical)
    candidate=load_xlsx(current,require_legacy_team=False)
    need(candidate["sha256"]!=HIST_SHA,"HISTORICAL_FILE_REPLAY")
    need(old["rows"] and candidate["rows"] and len(old["rows"])==len(candidate["rows"])==374,
         "EXACT_374_LABELS")
    for a,b in zip(old["rows"],candidate["rows"]):
        need((a["row"],a["section"],a["label"],a["depth"])==
             (b["row"],b["section"],b["label"],b["depth"]),
             "CURRENT_XLSX_SCHEMA_DRIFT_ROW_"+str(a["row"]))
    oldteam=old["teams"].index(TEAM)
    newteam=candidate["teams"].index(team) if team in candidate["teams"] else None
    need(newteam is not None,"CURRENT_TEAM_NOT_FOUND")
    # Different XLSX bytes do NOT prove newly observed values. Look at cells.
    baseline_vals=[row["values"][oldteam] for row in old["rows"]]
    candidate_vals=[row["values"][newteam] for row in candidate["rows"]]
    changed=sum(a!=b for a,b in zip(baseline_vals,candidate_vals))
    need(changed>0,"BINARY_DIFFERENT_BUT_NO_NEW_CITY_VALUES")
    factors=selected_factors(candidate,team)
    orig=selected_factors(old,TEAM)
    changed_factors=[name for name in sorted(factors) if factors[name]!=orig[name]]
    # The current workbook may describe FACT or PLAN; no assumption that its
    # P0/initial-state observations are a P1 operator-approved decision plan.
    csvstream=io.StringIO(newline="")
    writer=csv.writer(csvstream,lineterminator="\n")
    writer.writerow(["metric","value"])
    for metric in sorted(COEFF):
        writer.writerow([metric,format(factors[metric],".12g")])
    writer.writerow([INDEX_LABEL,format(factors[INDEX_LABEL],".12g")])
    receipt={
       "schema":SCHEMA,"status":"PASS_OPERATOR_CITY_EXCEL_FACTOR_PREFILL_REVIEW_REQUIRED",
       "source_class":"OPERATOR_UNVERIFIED_WORKBOOK_NOT_A_CURRENT_PLAN",
       "current_team_label":team,
       "current_team_identity_matches_historical_verified":False,
       "source_evidence_id":source_id,
       "historical_workbook_sha256":old["sha256"],
       "candidate_workbook_sha256":candidate["sha256"],
       "strict_schema":"374_ROW_TEN_DOMAIN_FIVE_TEAM_LAYOUT",
       "full_city_rows_changed_vs_historical_reference":changed,
       "factor_count":29,"index_count":1,
       "factors_changed_against_historical_other_team_possible":changed_factors,
       "operator_must_verify_p1_plan_column_before_r156":True,
       "r156_export_created":False,"gameplay_gate":"STOP","game_writes":0,
       "server_attested":False,"financing_approved":False,
       "missing_project_statuses":"MUST_CAPTURE_SEPARATELY",
       "missing_market_weights_or_cap":"MUST_CAPTURE_SEPARATELY",
       "missing_finance":"MUST_CAPTURE_SEPARATELY",
       "notes":[
         "Copy ONLY the 30-row factors.csv into the R156 offline form after confirming these are the currently displayed PLAN values.",
         "Never treat a FACT baseline or another team's numbers as a confirmed P1 PLAN.",
         "This importer never sets game team/market/period, projects, weights, budget or loans.",
         "R214 subsequently validates the completed ORIGINAL R156/R191/R192 source documents."
       ]
    }
    out.mkdir(mode=0o700)
    (out/"R215_FACTORS_FOR_REVIEW.csv").write_text(csvstream.getvalue(),encoding="utf-8")
    (out/"R215_RECEIPT.json").write_text(
        json.dumps(receipt,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+"\n",
        encoding="utf-8")
    return receipt

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--historical-workbook",required=True,type=Path)
    p.add_argument("--new-workbook",required=True,type=Path)
    p.add_argument("--team",required=True)
    p.add_argument("--source-id",required=True)
    p.add_argument("--out-dir",required=True,type=Path)
    a=p.parse_args()
    r=assemble(a.historical_workbook,a.new_workbook,a.team,a.source_id,a.out_dir)
    print(json.dumps({"status":r["status"],"factors":r["factor_count"],
          "changed_city_rows":r["full_city_rows_changed_vs_historical_reference"],
          "p1_plan_approved":False,"game_writes":0,"output":str(a.out_dir)},ensure_ascii=False))
if __name__=="__main__":main()
