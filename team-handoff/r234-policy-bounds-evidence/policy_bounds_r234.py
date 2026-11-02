#!/usr/bin/env python3
"""Official manual + current observed 23 control domains -> no-fabricated-bounds gate.

Reuses actual R225/R226/R228, R145 contract and R233 4-per-year scenarios.
No game access, no guessed percentages, no new policy optimizer.
"""
from __future__ import annotations
import argparse
import csv
import io
import json
import math
import sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"team-handoff/r228-excel-city-policy-join"),
             str(ROOT/"ECOSIM_R162_INTEGRITY_REVIEW_RC/tools")]
from source_join_r228 import SCHEMA as R228_SCHEMA, TAX_MAP, digest, need, parse_excel
from json_integrity_r162 import read_json
from policy_tracks import load_tracks, policy_factor_replay, policy_money_replay

SCHEMA="ECOSIM_R234_ACTUAL_23_P1_CONTROL_BOUNDS_SOURCE_GATES_V1"
MARKET="I"
ROUND="Selejtező"
TEAM="Jutalom a nap végén"
PERIOD=1

def rule_class(key):
    if key in ("institutions_education.table_1.field_2",
               "institutions_education.table_1.field_3"):
        return "HANDBOOK_PERIOD_SPECIFIC_PERCENT_EXAMPLE_NOT_NUMERIC_BOUND"
    if key=="institutions_education.table_1.field_1":
        return "LEGAL_WAGE_FLOOR_CURRENT_LAW_AND_UI_LIMIT_UNKNOWN"
    if key.startswith("tax."):
        return "STATUTORY_TAX_MAXIMUM_CURRENT_UI_VALUE_UNKNOWN"
    if key.startswith("loans."):
        return "CREDIT_AUTHORIZATION_AND_REPAYMENT_DYNAMIC_UNKNOWN"
    return "CURRENT_FIELD_RULE_UNKNOWN_FROM_READONLY_INPUT"

def bound_issue(key):
    if key.startswith("tax."):
        return "OBSERVE_CURRENT_TAX_SUBVIEW_LEGAL_MAX_AND_UNIT_SAFELY"
    if key.startswith("institutions_education.table_1."):
        return "OBSERVE_CURRENT_PERIOD_WAGE_TRAINING_DEVELOPMENT_RULE"
    if key.startswith("loans."):
        return "OBSERVE_ALLOWED_LOAN_DELTA_AND_LOAN_AUTHORIZATION"
    return "OBSERVE_ACTIVE_FIELD_MIN_MAX_OR_RULE_TOOLTIP_READONLY"

def run(r225_path,r226_path,r228_path,tax_path,r233_path,track_path,xlsx_path,
        manual_pdf,manual_text,source_js,dest):
    out=Path(dest).resolve()
    need(out.parent.is_dir() and not out.parent.is_symlink() and not out.exists()
         and not out.is_relative_to(ROOT.resolve()),"NEW_PRIVATE_OUTPUT")
    paths=(r225_path,r226_path,r228_path,tax_path,r233_path,track_path,
           xlsx_path,manual_pdf,manual_text,source_js)
    need(all(Path(p).is_file() and not Path(p).is_symlink() for p in paths),
         "IMMUTABLE_SOURCE_FILES_REQUIRED")
    r225,r226,r228,tax,r233=(read_json(p) for p in
                             (r225_path,r226_path,r228_path,tax_path,r233_path))
    excel=parse_excel(xlsx_path)
    need(r225.get("schema")=="ECOSIM_R225_ACTUAL_PERIODIC_EDITABLE_SURFACE_INVENTORY_V1"
         and r225.get("observed_editable_controls")==18
         and r225.get("p1_decision_values_verified")==0
         and r225.get("numeric_bounds_verified")==0
         and r225.get("gameplay_gate")=="STOP"
         and r225.get("game_writes")==0,
         "ORIGINAL_R225_P1_BOUNDS_UNVERIFIED")
    need(r226.get("schema")=="ECOSIM_R226_REAL_CURRENT_TEN_TOP_LEVEL_PAGES_VISIBLE_CONTROL_CENSUS_V1"
         and r226.get("observed_editable_text_inputs")==19
         and r226.get("unknown_minmax_count")==19
         and r226.get("unknown_p1_approved_decisions_count")==19
         and r226.get("unknown_factor_effect_count")==19
         and r226.get("unknown_cash_response_count")==19
         and r226.get("source_sha256",{}).get("original_r225")==digest(r225_path)
         and r226.get("gameplay_gate")=="STOP" and r226.get("game_writes")==0,
         "ORIGINAL_R226_19_INPUTS_RETAIN_UNKNOWN")
    need(r228.get("schema")==R228_SCHEMA
         and r228.get("observed_total_controls")==23
         and r228.get("exact_xlsx_vs_ui_p0_matches")==19
         and r228.get("unmapped_unique_excel_control_rows")==4
         and r228.get("current_P1_selected_actions_approved")==0
         and r228.get("source_sha256",{}).get("r226_receipt")==digest(r226_path)
         and r228.get("source_sha256",{}).get("tax_view")==digest(tax_path)
         and r228.get("source_sha256",{}).get("excel")==digest(xlsx_path)
         and r228.get("gameplay_gate")=="STOP" and r228.get("game_writes")==0,
         "R228_23_SOURCE_AND_CROSSWALK")
    need(tax.get("schema")=="ECOSIM_R228_CURRENT_TAX_ACTIVE_VIEW_READONLY_V1"
         and tax.get("active_subview")=="Adók"
         and tax.get("source_is_still_current_server_attested") is False
         and tax.get("bounds_verified") is False
         and tax.get("game_writes")==0
         and len(tax.get("controls",[]))==4,
         "ACTUAL_TAX_UI_READONLY_LIMITS_UNKNOWN")
    need(r233.get("schema")=="ECOSIM_R233_P0_FACT_VS_P1_PLAN_FOUR_CAP_SOURCE_COMPARISON_V1"
         and r233.get("scenario_count")==8
         and r233.get("changed_factor_count")==24
         and r233.get("baseline_for_existing_R232_project_search")==
              "ALREADY_P1_PLAN_NOT_P0"
         and r233.get("policy_current_and_future_effects_verified") is False
         and r233.get("cash_spendable_verified") is False
         and r233.get("gameplay_gate")=="STOP" and r233.get("game_writes")==0,
         "EXISTING_R233_EIGHT_SCENARIOS_NOT_ACTUAL_POLICY")
    for v in (r225,r226,r228,r233,tax):
        need(v.get("team")==TEAM and v.get("market")==MARKET and
             v.get("round")==ROUND and v.get("period")==PERIOD,
             "SOURCE_SAME_TEAM_MARKET_PERIOD")
    need(digest(manual_pdf)==
         "4d6b5c545bb205e5a9f8b92959b6659c4786d10cf6e1e6b2f654fa79c0168087"
         and digest(manual_text)==
         "b0c9337837f6dd661497c7de5c073d02745eae12c79c7f980fc1ae33083af581",
         "ORIGINAL_OFFICIAL_HANDBOOK_SHA")
    manual=Path(manual_text).read_text(encoding="utf8")
    need("pl.: +/- 20%" in manual
         and "szimulációbeli beállítások határozzák meg" in manual
         and "A pontos limitek a szimulációs" in manual
         and "Az állam törvényileg szabályozza az adók maximális mértékét" in manual,
         "OFFICIAL_HANDBOOK_BOUND_STATEMENTS")
    # This generic field component is not proof of a current EcoSim market
    # numeric bound or even of this table's active runtime code path.
    js=Path(source_js).read_text(encoding="utf8")
    need("a.limit(f)" in js and "a.hardMin=Math.max" in js and
         "a.hardMax=Math.min" in js,"HISTORICAL_GENERIC_DYNAMIC_BOUND_CODE")
    need(r228.get("current_R192_full_catalog_time_admitted") is False,
         "CURRENT_UI_NOT_FULL_SERVER_ADMISSION")
    tracks=load_tracks(track_path)
    need(len(tracks)==1 and len(tracks[0]["actions"])==23*5,
         "R145_EXACT_TEST_ONLY_23_X_5")
    need(tracks[0].get("mode")=="DOCUMENTED_OBSERVATION_ONLY",
         "R145_TEST_ONLY_NOT_ACTUAL_CHOSEN_POLICY")
    controls=r226["controls"]
    need(len(controls)==19,"R226_EXACT_ORIGINAL_INPUTS")
    link={v["control_id"]:v for v in r228["exact_links"]}
    unmatch={v["control_id"]:v for v in r228["unmatched_controls"]}
    need(len(link)==19 and len(unmatch)==4
         and not set(link)&set(unmatch),
         "R228_MATCH_UNIQUE_CONTROL_KEYS")
    roster=[]
    keys=set()
    for v in controls:
        k=v["decision_key"]
        need(k not in keys and (k in link or k in unmatch),
             "R226_CONTROL_MISSING_CROSSWALK")
        keys.add(k)
        need(v["p1_current_decision_value"] is None
             and v["actual_allowed_min"] is None
             and v["actual_allowed_max"] is None
             and v["cash_response_ecu"] is None
             and v["factor_response"] is None
             and v["game_write_authorized"] is False,
             "R226_NOT_AN_ADMITTED_DECISION_"+k)
        p0=v["p0_visible_number"]
        if k in link:
            need(link[k]["observed_ui_p0"]==p0
                 and link[k]["p1_selected"] is None
                 and link[k]["allowed_min"] is None
                 and link[k]["allowed_max"] is None,
                 "R228_MATCHED_P0_AND_BOUND_"+k)
            excel_row=link[k]["excel_row"]
        else:
            need(unmatch[k]["status"]=="EXCEL_UNIQUE_ROW_NOT_PROVEN",
                 "ORIGINAL_UNMATCHED_R228_EXCEL")
            excel_row=None
        roster.append((k,v["label"],p0,excel_row,v["section"],"R226_OPERATOR_VISIBLE",
                       v["policy_category"]))
    tax_map={v["label"]:v for v in tax["controls"]}
    need(set(tax_map)==set(TAX_MAP),
         "EXACT_FOUR_TAX_LABELS")
    for label,(key,row) in TAX_MAP.items():
        need(key in link and key not in keys and link[key]["excel_row"]==row,
             "R228_TAX_CROSSWALK")
        rec=tax_map[label]
        need(rec.get("p1_input")=="" and
             rec["p0"]==link[key]["observed_ui_p0"]
             and rec["p0"]==excel["rows"][row]["own_p0"],
             "R228_TAX_PERCENT_NOT_ECU")
        keys.add(key)
        roster.append((key,label,rec["p0"],row,"Bevételek/Adók",
                       "R228_TAX_OPERATOR_VISIBLE","tax"))
    need(len(roster)==len(keys)==23
         and len([r for r in roster if r[3] is not None])==19,
         "ALL_23_UI_CONTROL_SOURCE_COVERAGE")
    actionkeys=set(v["decision_key"] for v in tracks[0]["actions"])
    need(actionkeys==keys and
         all(v["factor_relative_percent"] is None and
             v["annual_cash_delta_ecu"] is None
             for v in tracks[0]["actions"]),
         "R145_23_SOURCE_KEYS_EFFECTS_UNKNOWN_NOT_ZERO")
    # Static HTML warnings and manual descriptions cannot reveal live numeric
    # min/max or user-approved decisions; reflect actual source insufficiency.
    results=[]
    for k,label,p0,excel_row,section,src,cat in roster:
        results.append({
          "control_id":k,"label":label,
          "source_active_section":section,"source_kind":src,
          "p0_ui_observed":p0,
          "excel_p0_exact_row_id_or_null":excel_row,
          "policy_category":cat,
          "handbook_non_numeric_rule_class":rule_class(k),
          "numeric_min_verified":None,"numeric_max_verified":None,
          "numeric_delta_percent_verified":None,
          "p1_effective_selected_value_verified":None,
          "annual_cash_change_ecu_calibrated":None,
          "city_factors_effect_calibrated":None,
          "is_validated_admissible_action":False,
          "source_acquisition_needed":bound_issue(k),
          "percent_hypothesis_not_accepted_as_rule":True,
        })
    need(len(results)==23,"FULL_BOUND_MATRIX")
    reports={
       "schema":SCHEMA,
       "status":"PASS_23_P0_SOURCE_MATCH_0_NUMERIC_BOUNDS_0_CALIBRATED_ACTIONS",
       "round":ROUND,"market":MARKET,"team":TEAM,"period":PERIOD,
       "observed_ui_controls":23,
       "exact_excel_p0_matches":19,"excel_unmatched_but_ui_observed":4,
       "current_numeric_minmax_pairs_verified":0,
       "current_P1_effective_selected_values_verified":0,
       "calibrated_causal_factor_and_cash_effect_pairs_verified":0,
       "original_R145_unknown_annual_action_count":23,
       "original_R145_unknown_annual_cash_effect_count":23,
       "original_R145_unknown_annual_factor_effect_count":23,
       "original_R145_test_only_5_year_rows":115,
       "R233_source_proven_4_project_per_year_8_scenario_paths":8,
       "source_rulebook_example_plus_minus_20_not_generic_bound":True,
       "tax_legal_ceiling_rule_but_numeric_rates_unknown":True,
       "client_generic_dynamic_minmax_support_not_current_rule":True,
       "current_server_attested_bound_source":None,
       "usable_joint_real_policy_project_optimization":False,
       "approved_p1_city_actions":None,
       "live_R191_R192_R214_gates":"HOLD",
       "matrix":results,
       "source_sha256":{
          "R225":digest(r225_path),"R226":digest(r226_path),
          "R228":digest(r228_path),"R228_tax_visible":digest(tax_path),
          "R233":digest(r233_path),"original_R145_TEST_ONLY":digest(track_path),
          "current_Selejtezo_excel":digest(xlsx_path),
          "original_official_handbook_pdf":digest(manual_pdf),
          "official_handbook_extracted_text":digest(manual_text),
          "historical_shared_ui_input_component":digest(source_js)},
       "next_evidence":"READ_ONLY_PERIOD_SPECIFIC_LIMIT_TOOLTIP_OR_EXPLICIT_MARKET_RULES_PLUS_CAUSAL_PLAN_FACT_NEXT_PERIOD",
       "gameplay_gate":"STOP","game_writes":0,
    }
    out.mkdir(mode=0o700)
    (out/"R234_RECEIPT.json").write_text(json.dumps(reports,
            ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n",
            encoding="utf8")
    buff=io.StringIO(newline="")
    writer=csv.writer(buff,lineterminator="\n")
    writer.writerow(["control_id","label","P0_visible","excel_row_or_empty",
                     "handbook_rule_type","numeric_P1_min","numeric_P1_max",
                     "effective_P1_selected","calibrated_factor","calibrated_cash",
                     "next_readonly_evidence"])
    for f in results:
        writer.writerow([f["control_id"],f["label"],f["p0_ui_observed"],
               f["excel_p0_exact_row_id_or_null"] or "",
               f["handbook_non_numeric_rule_class"],"UNKNOWN","UNKNOWN",
               "UNKNOWN","UNKNOWN","UNKNOWN",f["source_acquisition_needed"]])
    (out/"R234_P1_SOURCE_MATRIX_PRIVATE.csv").write_text(buff.getvalue(),encoding="utf8")
    md=[
      "# EcoSim R234 – P1 döntési korlátok forrásellenőrzése",
      "",
      "**23 valós, megfigyelt input; 19/23 pontos Excel-P0 egyezés; "
      "4/23 nem egyedileg párosítható Excel-sor.**",
      "**0/23 hitelesített aktuális numerikus min-max; 0/23 jóváhagyott P1 döntés; "
      "0/23 kalibrált tényező+pénz hatás.**",
      "",
      "A hivatalos kézikönyv ±20%-ot csak példaként említ. "
      "Képzés/fejlesztés korlátja periódusfüggő beállítás, az adókulcs "
      "felső határa jogszabályi és aktuális UI értékfüggő.",
      "A korábbi általános kliens-tablekomponens a hardMin/hardMax "
      "összevonására képes, de ez nem bizonyít konkrét EcoSim mezőkorlátot.",
      "R233 változatlanul 8 feltételes, legfeljebb 4 projekt/év ötéves pályát "
      "tartalmaz; ennek 23 szakpolitikai hatáskomponense évenként UNKNOWN.",
      "",
      "| Döntési terület | Ismert input | P1 megengedett numerikus értékek |",
      "|---|---:|---|",
    ]
    for kind,num in sorted(Counter(v["source_active_section"] for v in results).items()):
        md.append(f"| {kind} | {num} | UNKNOWN |")
    md+=["","**Következő leghasznosabb külső bizonyíték:** az aktuális "
         "mezőkhöz tartozó számszerű korlátok olvasási megfigyelése "
         "(elsősorban Adók és intézményi Képzés/Fejlesztés), valamint "
         "majd azonosított P1 TERV → következő P1 TÉNY állapotok.",
         "Játékbeli módosítás: 0. GATE=STOP. No merge/deploy."]
    (out/"R234_HU.md").write_text("\n".join(md)+"\n",encoding="utf8")
    print(json.dumps({"status":reports["status"],
        "observed":23,"excel_p0_matches":19,
        "verified_numeric_bounds":0,
        "calibrated_actions":0,"scenario_paths":8,
        "game_writes":0},ensure_ascii=False))
    return reports

def main():
    p=argparse.ArgumentParser()
    for key in ("r225","r226","r228","tax","r233","track","xlsx",
                "manual-pdf","manual-text","source-js","out-dir"):
        p.add_argument("--"+key,type=Path,required=True)
    a=p.parse_args()
    run(a.r225,a.r226,a.r228,a.tax,a.r233,a.track,a.xlsx,a.manual_pdf,
        a.manual_text,a.source_js,a.out_dir)
if __name__=="__main__":main()
