#!/usr/bin/env python3
"""R214 source-pinned operator export -> R156 -> R207 read-only advisory.

Original validators and search only. Does not access EcoSim UI/server.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"ECOSIM_R162_INTEGRITY_REVIEW_RC/tools"),
 str(ROOT/"team-handoff/r207-first-round"),
 str(ROOT/"team-handoff/r213-city-excel")]
from json_integrity_r162 import read_json
from readonly_intake_r156 import create_bundle
from observation_bundle_r152 import compile_bundle
from first_round import run_cli as original_r207_cli
from city_excel_r213 import load_xlsx,diff_candidate_baseline
from strategy_5y import write_json

SCHEMA="ECOSIM_R214_READONLY_CURRENT_INTAKE_TO_ADVISORY_V1"
BASELINE_SHA="c6cd0681a28872beb556652b584674f442c5105c379f365027ee9dbd3efe69bc"
class Hold(ValueError):pass
def require(ok,why):
    if not ok:raise Hold("HOLD_"+why)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def source_class(packet,qualification=False):
    require(isinstance(packet,dict) and packet.get("schema")=="ECOSIM_R156_LOCAL_OPERATOR_EXPORT_V1" and
            packet.get("capture_mode")=="CURRENT_READONLY" and packet.get("kind")=="PLAN",
            "R156_CURRENT_PLAN_REQUIRED")
    field=packet.get("field_sources",{})
    values=[str(packet.get(k,"")) for k in ("team","market","round","source_evidence_id")]
    values += [str(x) for x in field.values()] if isinstance(field,dict) else []
    suspect=any(any(word in v.casefold() for word in
               ("historical","synthetic","mock","tesztfordul","example","fixture")) for v in values)
    if qualification:
        require(suspect and str(packet.get("source_evidence_id","")).startswith("R210_MOCK"),
                "EXPLICIT_R210_MOCK_REQUIRED")
        return "MOCK_ONLY_NOT_REAL_CURRENT"
    require(not suspect,"FAKE_OR_HISTORICAL_CURRENT_SOURCE")
    return "OPERATOR_DECLARED_NOT_SERVER_ATTESTED"

def build(export,finance,catalog,budget,out,*,allow_drift=False,qualification=False,
          historical_workbook=None,current_workbook=None):
    dest=Path(out).resolve()
    require(not dest.exists() and not dest.is_relative_to(ROOT.resolve()),"PRIVATE_NEW_OUTPUT")
    require(dest.parent.is_dir() and not dest.parent.is_symlink(),"PRIVATE_EXISTING_PARENT")
    require(type(budget) is int and 0<=budget<=10**12,"EXPLICIT_NONNEGATIVE_BUDGET")
    require((historical_workbook is None)==(current_workbook is None),"BOTH_CITY_WORKBOOKS_REQUIRED")
    require(all(Path(p).is_file() and not Path(p).is_symlink()
                for p in (export,finance,catalog)),"READONLY_SOURCE_FILES")
    packet=read_json(export)
    classification=source_class(packet,qualification)
    require(type(packet.get("period")) is int and 1<=packet["period"]<=5,"PERIOD")
    diff=None
    if historical_workbook is not None:
        require(sha(historical_workbook)==BASELINE_SHA,"HISTORICAL_WORKBOOK_SHA")
        diff=diff_candidate_baseline(load_xlsx(historical_workbook),
             load_xlsx(current_workbook),source_claim="CURRENT_UNVERIFIED_OPERATOR_EXPORT")
        require(diff["new_source_is_cryptographically_verified_game_server"] is False,
                "FALSE_SERVER_ATTESTATION")
        require(diff["changed_count"]>0 or diff["candidate_missing_not_zero"],
                "CURRENT_EXCEL_HAS_NO_OBSERVED_CHANGE_OR_IS_BINARY_DUPLICATE")
    dest.mkdir(mode=0o700)
    incomplete=dest/"INCOMPLETE_HOLD"
    incomplete.write_text("R214 validation pending, no gameplay writes\n",encoding="utf-8")
    # Original immutable R156 compilation; no new capture parser.
    bundle,receipt=create_bundle(packet,dest/"r156_immutable")
    require(receipt["gameplay_gate"]=="STOP" and receipt["has_live_ecosim_session"] is False,
            "R156_STOP_GATE")
    _,state,_=compile_bundle(bundle/"manifest.json")
    state_file=dest/"r156_state.json"
    write_json(state_file,state)
    require(state["provenance"]["current_period"]==packet["period"],"SOURCE_PERIOD")
    # Original R207 validates current R191 finance, 35 R192/R212 card definitions,
    # searches with R162/R157 and audits with original R160.
    argv=["first_round.py","--repo-root",str(ROOT),"--state",str(state_file),
          "--r156-bundle",str(bundle),"--year1-finance",str(finance),
          "--current-card-catalog",str(catalog),"--year1-budget",str(budget),
          "--out-dir",str(dest/"advisory")]
    if allow_drift:argv.append("--allow-source-adapted-current-catalog")
    previous=sys.argv
    try:
        sys.argv=argv
        original_r207_cli()
    finally:sys.argv=previous
    advisory=read_json(dest/"advisory/R207.json")
    require(advisory.get("gameplay_gate")=="STOP" and advisory.get("game_writes")==0 and
            advisory.get("current_server_authenticated") is False and
            advisory.get("finance_server_approved") is False and
            advisory.get("selected_count",0)>0,"R207_NOT_APPROVED_ADVISORY")
    require(advisory.get("period")==packet["period"] and
            advisory.get("market")==packet["market"],"R207_IDENTITY")
    require(advisory["input_hashes"]["state_sha256"]==sha(state_file) and
            advisory["input_hashes"]["finance_sha256"]==sha(finance),"R207_SOURCE_HASH")
    require(advisory.get("requested_illustrative_year1_card_budget_ecu")==budget,
            "R207_BUDGET_JOIN")
    if diff is not None:
        (dest/"R214_CITY_DIFF_PRIVATE.json").write_text(
          json.dumps(diff,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    data={
      "schema":SCHEMA,"status":"PASS_OPERATOR_READONLY_CHAIN_NOT_LIVE_ATTESTED",
      "source_class":classification,"team":packet["team"],"market":packet["market"],
      "period":packet["period"],"gameplay_gate":"STOP","game_writes":0,
      "server_authenticated":False,"financing_approved":False,
      "score_forecast_validated":False,
      "selected_count":advisory["selected_count"],
      "card_drift_ids":advisory.get("source_adapted_card_drift_ids",[]),
      "card_source_schema":advisory.get("project_catalog_source_schema"),
      "city_workbook_diff_count":diff["changed_count"] if diff else None,
      "city_workbook_not_substituted_for_r156":True,
      "source_sha256":{
        "operator_r156":sha(export),"operator_year1_finance":sha(finance),
        "operator_current_cards":sha(catalog),
        "historical_excel":sha(historical_workbook) if historical_workbook is not None else None,
        "candidate_city_excel":sha(current_workbook) if current_workbook is not None else None},
      "output_sha256":{
        "r156_manifest":sha(bundle/"manifest.json"),
        "r156_normalized_state":sha(state_file),
        "r207_advisory":sha(dest/"advisory/R207.json"),
        "r207_hungarian":sha(dest/"advisory/R207_HU.md")},
      "next_action":"OWNER_REVIEW_ONLY_NO_GAME_ACTION"
    }
    (dest/"R214_RECEIPT.json").write_text(
        json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n",
        encoding="utf-8")
    lines=["# R214 – ellenőrzött aktuális adatút; csak olvasás","",
       "Szerverhitelesítés: NEM. Pénzügyi jóváhagyás: NEM. GAME_ACTION_GATE=STOP.","",
       "Adatbesorolás: "+classification,
       "Csapat: "+packet["team"]+"; piac: "+packet["market"]+
       "; periódus: "+str(packet["period"])+".",
       "Auditált elsőéves alternatívák száma: "+str(data["selected_count"])+".",
       "Kártyaeltérések: "+str(data["card_drift_ids"])+".",
       "Városi Excel-soreltérések: "+str(data["city_workbook_diff_count"])+".","",
       "Eredeti R207 részletes döntési jelentés: advisory/R207_HU.md",
       "Az opcionális Excel-diff nem igazolja a szerveradatok eredetét.",
       "Éles játékművelet csak külön tulajdonosi engedéllyel.",""]
    (dest/"R214_HU.md").write_text("\n".join(lines),encoding="utf-8")
    incomplete.unlink()
    return data

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--r156-export",type=Path,required=True)
    p.add_argument("--year1-finance",type=Path,required=True)
    p.add_argument("--current-card-catalog",type=Path,required=True)
    p.add_argument("--year1-budget",type=int,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    p.add_argument("--allow-source-adapted-current-catalog",action="store_true")
    p.add_argument("--historical-workbook",type=Path)
    p.add_argument("--current-workbook",type=Path)
    p.add_argument("--qualification-mock",action="store_true",
                   help="Only R210 synthetic fixture test mode; never current game.")
    a=p.parse_args()
    r=build(a.r156_export,a.year1_finance,a.current_card_catalog,
            a.year1_budget,a.out_dir,
            allow_drift=a.allow_source_adapted_current_catalog,
            qualification=a.qualification_mock,
            historical_workbook=a.historical_workbook,current_workbook=a.current_workbook)
    print(json.dumps({"status":r["status"],"source_class":r["source_class"],
                      "options":r["selected_count"],"game_writes":0,
                      "private_result":str(a.out_dir)},ensure_ascii=False))
if __name__=="__main__":main()
