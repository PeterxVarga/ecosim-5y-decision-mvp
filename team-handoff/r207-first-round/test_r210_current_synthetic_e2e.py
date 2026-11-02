#!/usr/bin/env python3
"""R210 full CURRENT_READONLY *synthetic-fixture* E2E through the original validators.

This is NOT a current capture, server attestation, live finance approval, or gameplay
action. It reuses historical PLAN factor values as explicitly MOCK inputs only.
"""
from __future__ import annotations
import copy, hashlib, json, os, sys, tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
R162 = ROOT / "ECOSIM_R162_INTEGRITY_REVIEW_RC"
sys.path[:0] = [str(Path(__file__).resolve().parent), str(R162 / "tools"), str(ROOT / "team-handoff/r191-live-admission/tools")]
from json_integrity_r162 import read_json
from readonly_intake_r156 import create_bundle
from observation_bundle_r152 import compile_bundle
from admission_r191 import AdmissionHold, validate_state, validate_r156_bundle, year1_finance
from catalog_gate_r192 import CatalogHold, validate_catalog
from first_round import run_cli

def check(ok,why):
    if not ok:raise AssertionError("HOLD_"+why)
def write(p,obj):
    p.write_text(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8")

def capture_fixture(now):
    # Reuse only displayed *historical* numbers, not any historical identity
    # or credentials. Never assert that this synthetic fixture is an EcoSim capture.
    e=read_json(R162/"capture/R156_HISTORICAL_TEST_EXPORT.json")
    e.update(capture_mode="CURRENT_READONLY",kind="PLAN",
             team="R210_MOCK_TEAM", market="R210_MOCK_MARKET",round="R210_MOCK_ROUND",
             captured_at_local=now,source_evidence_id="R210_MOCK_SOURCE",
             source_note="R210 strictly offline simulated current-mode contract test. Derived from historical PLAN values, not the real city.")
    e["parameters"]["market"].update(maxProjectPerTurn=4,cap_source="R210_MOCK_OBSERVATION")
    e["parameters"]["team"]={
        "project1_active_previous_period":False,
        "already_selected_new_project_ids_current_period":[]}
    e["field_sources"]={
       "factors":"R210_MOCK_FACTOR_VIEW",
       "projects":"R210_MOCK_PROJECT_VIEW",
       "market_project_cap":"R210_MOCK_CAP_VIEW",
       "market_index_weights":"R210_MOCK_WEIGHT_VIEW"}
    return e

def synthetic_sources(now):
    # Entire workflow is deliberately a temporary self-test, not a user export.
    export=capture_fixture(now)
    old=read_json(R162/"data/ecosim_projects_20261030.json")
    catalog={
        "schema":"ECOSIM_R192_CURRENT_CARD_CATALOG_V1",
        "capture_mode":"CURRENT_READONLY",
        "team":export["team"],"market":export["market"],"round":export["round"],
        "period":1,"captured_at_local":now,
        "source_evidence_id":"R210_MOCK_CATALOG",
        "source_view":"R210_MOCK_LOCAL_CARD_FIXTURE",
        "projects":old["projects"]}
    finance={
        "mode":"CURRENT_YEAR1_OPERATOR_READONLY",
        "source_evidence_id":"R210_MOCK_FINANCE",
        "captured_at_local":now,"period":1,
        "operator_observed_spendable_ecu":150000,
        "operator_observed_committed_ecu":0}
    return export,catalog,finance

def exercise():
    now=datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    export,catalog,finance=synthetic_sources(now)
    check(export["source_evidence_id"].startswith("R210_MOCK"),"NOT_SYNTHETIC")
    with tempfile.TemporaryDirectory(prefix="ecosim-r210-contract-") as td:
        base=Path(td)
        bundle,receipt=create_bundle(export,base/"mock_r156_bundle")
        check(receipt["gameplay_gate"]=="STOP" and not receipt["has_live_ecosim_session"],"R156_GATE")
        _,state,_=compile_bundle(bundle/"manifest.json")
        check(state["provenance"]["round"]=="R210_MOCK_ROUND","MOCK_PROVENANCE")
        check(state["team"]["baseline_smartcity_factors"],"FACTORS_ABSENT")
        s=validate_state(state,mode="current")
        check(s["gameplay_gate"]=="STOP" and not s["official_server_attested"],"R191_STATE_GATE")
        cap=validate_r156_bundle(state,bundle)
        check(cap["status"]=="PASS_OPERATOR_CAPTURE_CONSISTENCY_ONLY" and
              not cap["current_source_is_server_authenticated"],"R191_CAPTURE_GATE")
        fin=year1_finance(finance,state,illustrative_first_year_budget=150000)
        check(fin["status"]=="PASS_OPERATOR_DECLARED_YEAR1_ENVELOPE_ONLY" and
              not fin["actual_server_financing_approved"],"R191_FINANCE_GATE")
        cat=validate_catalog(catalog,state,read_json(R162/"data/ecosim_projects_20261030.json"))
        check(cat["observed_card_count"]==35 and not cat["server_attested"],"R192_CATALOG_GATE")
        state_path=base/"mock_state.json";finance_path=base/"mock_finance.json";catalog_path=base/"mock_catalog.json"
        write(state_path,state);write(finance_path,finance);write(catalog_path,catalog)
        # Three bounded source-identical R162 searches, actual R160 audit, R207.
        inputs=["--repo-root",str(ROOT),"--state",str(state_path),"--r156-bundle",str(bundle),
                "--year1-finance",str(finance_path),"--current-card-catalog",str(catalog_path),
                "--year1-budget","150000"]
        original=sys.argv
        try:
            for i in (1,2):
                sys.argv=["first_round.py",*inputs,"--out-dir",str(base/("output"+str(i)))]
                run_cli()
        finally:sys.argv=original
        a=(base/"output1/R207.json").read_bytes()
        b=(base/"output2/R207.json").read_bytes()
        check(a==b and (base/"output1/R207_HU.md").read_bytes()==(base/"output2/R207_HU.md").read_bytes(),"REPRODUCIBILITY")
        result=json.loads(a)
        check(result["gameplay_gate"]=="STOP" and result["game_writes"]==0,"NO_GAME_WRITES")
        check(1<=result["selected_count"]<=3,"CANDIDATE_COUNT")
        check(all(x["conditional_display_eligibility_count"]==0 for x in result["selected_options"]),"R160_RULE_AUDIT")
        # Negative checks of the actual original native validators:
        invalid=copy.deepcopy(finance); invalid["operator_observed_spendable_ecu"]=999
        invalid["operator_observed_committed_ecu"]=900
        try: year1_finance(invalid,state,illustrative_first_year_budget=150000)
        except AdmissionHold:pass
        else:raise AssertionError("HOLD_UNFUNDED_YEAR1_NOT_REJECTED")
        invalid=copy.deepcopy(catalog);invalid["projects"][0]["startup_cost"]+=1
        try:validate_catalog(invalid,state,read_json(R162/"data/ecosim_projects_20261030.json"))
        except CatalogHold:pass
        else:raise AssertionError("HOLD_CATALOG_DRIFT_NOT_REJECTED")
        historic=copy.deepcopy(state);historic["provenance"]["round"]="X-Challenge Tesztforduló"
        try:validate_state(historic,mode="current")
        except AdmissionHold:pass
        else:raise AssertionError("HOLD_HISTORICAL_AS_CURRENT_NOT_REJECTED")
        return {"schema":"ECOSIM_R210_FULL_SYNTHETIC_CURRENT_MODE_REHEARSAL_V1",
                "status":"PASS_FULL_ORIGINAL_R156_R191_R192_R162_R160_R207_MOCK_E2E",
                "input_class":"R210_MOCK_ONLY_NOT_REAL_CURRENT_DATA",
                "original_r156":True,"original_r191":True,"original_r192":True,
                "original_r162_and_r160":True,"r207_options":result["selected_count"],
                "native_repeated_byte_identical":True,
                "negative_controls":3,
                "game_writes":0,"gameplay_gate":"STOP",
                "server_attested":False,"live_ready":False}

if __name__=="__main__":
    print(json.dumps(exercise(),ensure_ascii=False,sort_keys=True))