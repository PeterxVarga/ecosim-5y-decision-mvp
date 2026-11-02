#!/usr/bin/env python3
"""R223 current-period read-only coherent-card intake.

Uses original R156/R152/R192 and R217/R220/R222 parsers. File mtimes are
operator-local capture metadata, not independently signed EcoSim timestamps.
Never starts/saves projects; never infers a real cap or spendable budget.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from datetime import datetime,timezone,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[
 str(ROOT/"team-handoff/r217-current-visible-admission"),
 str(ROOT/"team-handoff/r222-visible-conditions"),
 str(ROOT/"team-handoff/r191-live-admission/tools"),
 str(ROOT/"ECOSIM_R162_INTEGRITY_REVIEW_RC/tools")]
from qualify_all_views_r220 import CASES,view_page
from conditions_r222 import parse_conditions,segments
from prepare_visible_r217 import parse_project_cards,parse_summary,R162
from json_integrity_r162 import read_json
from catalog_gate_r192 import validate_catalog,_card,CatalogHold
from observation_bundle_r152 import compile_bundle

SCHEMA="ECOSIM_R223_FRESH_FOUR_CATEGORY_R192_INTAKE_V1"
EXPECTED_RUNNING=[14,22,23,24,34,35]
class Hold(ValueError):pass
def need(cond,reason):
    if not cond:raise Hold("HOLD_"+reason)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def at(path):
    return datetime.fromtimestamp(Path(path).stat().st_mtime,timezone.utc)
def capture(pages,r156,out):
    pages=Path(pages);r156=Path(r156);out=Path(out).resolve()
    need(out.parent.is_dir() and not out.exists() and
         not out.is_relative_to(ROOT.resolve()),"PRIVATE_NEW_RESULT_DIR")
    prior=read_json(r156/"R217_RECEIPT.json")
    need(prior.get("schema")=="ECOSIM_R217_CURRENT_BROWSER_VISIBLE_PARTIAL_ADMISSION_V1"
         and prior.get("status")=="PASS_PARTIAL_CURRENT_R156_BUNDLE_R191_HOLD_CAP_AND_FINANCE"
         and prior.get("r191_current_qualification")=="HOLD_CAP_UNKNOWN_OR_ASSUMED"
         and prior.get("game_writes")==0 and
         prior.get("source_page_count")==5 and
         prior.get("observed_project_statuses")==35 and
         prior.get("running_ids")==EXPECTED_RUNNING,
         "CURRENT_R156_35_PROJECT_CAPTURE_REQUIRED")
    original=read_json(R162/"data/ecosim_projects_20261030.json")
    _,state,_=compile_bundle(r156/"r156_immutable/manifest.json")
    p=state["provenance"]
    need((p["team"],p["market"],p["round"],p["current_period"])==
         ("Jutalom a nap végén","I","Selejtező",1) and
         state["market"]["maxProjectPerTurn"] is None and
         state["team"]["initially_active_project_ids"]==EXPECTED_RUNNING and
         state["team"]["already_selected_new_project_ids_current_period"]==[],
         "R156_TEAM_PERIOD_OR_CAP_FABRICATED")
    state_time=datetime.fromisoformat(p["captured_at_local"]).astimezone(timezone.utc)
    now=datetime.now(timezone.utc)
    need(-timedelta(minutes=5)<=now-state_time<=timedelta(hours=48),
         "R156_CURRENT_STATE_EXPIRED_OR_FUTURE")
    for stem,expected_sha in prior["source_text_sha256"].items():
        source=pages/(stem+".txt")
        need(source.is_file() and not source.is_symlink() and sha(source)==expected_sha,
             "FRESH_R156_SOURCE_HASH_"+stem)
        need(abs((at(source)-state_time).total_seconds())<=3600,
             "R156_FIVE_SOURCE_CAPTURE_TIME_"+stem)
    # The original R156 Summary is the authoritative view for 35 statuses.
    summary_text=(pages/"summary.txt").read_text(encoding="utf-8")
    summary=parse_summary(summary_text,original)
    need(summary["observed_running_project_ids"]==EXPECTED_RUNNING and
         summary["observed_new_selected_ids"]==[],
         "SUMMARY_CURRENT_PROJECT_STATUS_DRIFT")
    listed=[];candidate=[];source_times={};source_hashes={}
    missing=[]
    for stem,category,first,last in CASES:
        path=pages/(stem+".txt")
        if not path.exists():
            missing.append({"view":category,"ids":list(range(first,last+1))})
            continue
        raw,pfile=view_page(pages,stem,category)
        # A different page inside the wrong tab must never be admitted.
        parsed=parse_project_cards(raw,original,expected_ids=range(first,last+1))
        parts=segments(raw)
        need(set(parts)==set(range(first,last+1)),"EXACT_CARD_SEGMENTS_"+stem)
        for c in parsed["captured_cards"]:
            idx=c["id"]
            need((c["displayed_status"]=="Fut")==(idx in EXPECTED_RUNNING),
                 "R156_VS_CARD_STATUS_"+str(idx))
            conditions,condition_kind=parse_conditions(parts[idx],idx)
            card={"id":idx,"name":c["name"],**c["observed_money"],
                  "project_conditions":conditions,"effects":c["observed_effects"]}
            before=next(x for x in original["projects"] if x["id"]==idx)
            need(_card(card,"CURRENT")==_card(before,"ORIGINAL"),
                 "CURRENT_CARD_DEFINITION_DRIFT_"+str(idx))
            candidate.append(card)
            listed.append({"id":idx,"condition_status":condition_kind})
        source_times[stem]=at(pfile)
        source_hashes[stem]=sha(pfile)
    receipt={
      "schema":SCHEMA,"source_class":"OPERATOR_BROWSER_VISIBLE_NOT_SERVER_ATTESTED",
      "round":p["round"],"market":p["market"],"team":p["team"],
      "period":p["current_period"],"r156_receipt_sha256":sha(r156/"R217_RECEIPT.json"),
      "r156_manifest_sha256":sha(r156/"r156_immutable/manifest.json"),
      "state_capture_time_utc":state_time.isoformat(),
      "project_source_sha256":source_hashes,
      "observed_visible_cards":len(candidate),
      "missing_current_category_views":missing,
      "observed_condition_sections":sum(x["condition_status"]=="DISPLAYED_EXPLICIT_CONDITION" for x in listed),
      "actual_numeric_market_cap":None,"actual_spendable_ecu":None,
      "r191_current_admission":"HOLD_CAP_UNKNOWN_OR_ASSUMED",
      "r214_live_advisory_authorized":False,"gameplay_gate":"STOP","game_writes":0,
      "client_page_timestamp_is_not_server_attestation":True
    }
    out.mkdir(mode=0o700)
    if missing:
        receipt["status"]="HOLD_MISSING_CURRENT_CATEGORY_VIEWS"
        receipt["r192_catalog_admission"]="NOT_ATTEMPTED_INCOMPLETE"
    else:
        need(len(candidate)==35 and [x["id"] for x in candidate]==list(range(1,36)),
             "EXACT_35_VISIBLE_CARD_IDS")
        stamps=list(source_times.values())+[state_time]
        gap=(max(stamps)-min(stamps)).total_seconds()
        receipt["source_capture_span_minutes"]=round(gap/60,3)
        if gap>3600 or any(stamp>now+timedelta(minutes=5) for stamp in stamps):
            receipt["status"]="HOLD_NOT_SAME_HOUR_OR_FUTURE_SOURCE"
            receipt["r192_catalog_admission"]="NOT_ATTEMPTED_OUTSIDE_TIME_WINDOW"
        else:
            # Source-derived current card values, never copy historical card data
            # to the candidate. Actual latest view time is passed to R192.
            original_capture={
              "schema":"ECOSIM_R192_CURRENT_CARD_CATALOG_V1",
              "capture_mode":"CURRENT_READONLY",
              "team":p["team"],"market":p["market"],"round":p["round"],"period":p["current_period"],
              "source_evidence_id":"R223_CURRENT_FOUR_CATEGORY_OPERATOR_READONLY",
              "source_view":"https://edu.ecosim.hu/simulation/projects",
              "captured_at_local":max(source_times.values()).isoformat(),
              "projects":candidate}
            try:admission=validate_catalog(original_capture,state,original)
            except CatalogHold as exc:
                receipt["status"]="HOLD_ORIGINAL_R192_"+str(exc)
                receipt["r192_catalog_admission"]="HOLD_"+str(exc)
            else:
                need(admission["status"]=="PASS_OPERATOR_REPORTED_35_CARD_DEFINITION_PARITY_ONLY"
                     and admission["server_attested"] is False and
                     admission["gameplay_gate"]=="STOP","ORIGINAL_R192_REVIEW_ONLY")
                receipt["status"]="PASS_R192_OPERATOR_CURRENT_CATALOG_TIME_PARITY_ONLY"
                receipt["r192_catalog_admission"]=admission["status"]
                receipt["source_catalog_sha256"]=hashlib.sha256(json.dumps(
                   original_capture,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
                (out/"R223_R192_CURRENT_CATALOG_PRIVATE.json").write_text(
                    json.dumps(original_capture,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    (out/"R223_RECEIPT.json").write_text(
        json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":receipt["status"],"observed_cards":receipt["observed_visible_cards"],
          "missing_categories":[m["view"] for m in missing],
          "r192":receipt["r192_catalog_admission"],"game_writes":0,
          "private_output":str(out)},ensure_ascii=False))
    return receipt

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--pages-dir",required=True,type=Path)
    parser.add_argument("--r156-dir",required=True,type=Path)
    parser.add_argument("--out-dir",required=True,type=Path)
    x=parser.parse_args();capture(x.pages_dir,x.r156_dir,x.out_dir)
if __name__=="__main__":main()
