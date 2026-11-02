#!/usr/bin/env python3
"""Actual Selejtező Excel → observed UI → original R145/R148/R224 five-year join.

Read-only. Exact Excel row matches and original-source pinned data. Never
fabricate selected P1 controls, minimum/maximum constraints, model effects,
official score, or spendable money. All private source/report bytes stay off Git.
"""
from __future__ import annotations
import argparse, hashlib, json, math, re, sys, xml.etree.ElementTree as ET, zipfile
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[2]
EXCEL_SHA="a130d6606c4488112c8825d79d5fb6aaa65a65f4dca7d1e1f9e4029cdafe53f4"
SRC=ROOT/"ECOSIM_R162_INTEGRITY_REVIEW_RC"
sys.path[:0]=[str(SRC/"tools"),str(ROOT/"team-handoff/r191-live-admission/tools")]
from json_integrity_r162 import read_json
from observation_bundle_r152 import compile_bundle
from policy_tracks import load_tracks,policy_factor_replay,policy_money_replay,replay_policy_joint
from portfolio_5y import project_index
from r142_proxy_reference import WEIGHTS
from tax_response_r153 import FIELDS as R153_FIELDS
from tax_revenue_r154 import BASE_FIELDS as R154_BASE_FIELDS
SCHEMA="ECOSIM_R228_SOURCE_LINKED_EXCEL23_POLICY5Y_GATES_V1"
TEAM="Jutalom a nap végén"
TEAMS=["Bányász kódok",TEAM,"Kiwi","Kőbánya Optima",
       "Midas Nonprofit","Zéró","I7"]
SECTIONS=("Összefoglaló","Intézmények","Közösségi közlekedés",
 "Közlekedési személyzet","Személyzeti költségek","Bevételek",
 "Lakossági adatok","Vállalkozások","Pénzügyek","Hitelek")
# Exact R227 source Excel row IDs and 19 R226 control keys. None means the
# original R227 cannot safely name a unique counterpart in the Excel.
R226_ROW_MAP={
 "institutions_education.table_1.field_1":None, # School wage, no unique Excel decision row
 "institutions_education.table_1.field_2":None, # School training
 "institutions_education.table_1.field_3":None, # School development
 "institutions_education.table_2.field_1":42,
 "institutions_education.table_3.field_1":50,
 "institutions_education.table_4.field_1":58,
 "institutions_education.table_5.field_1":66,
 "transport_ice_bus.table_1.field_1":122,
 "transport_ice_bus.table_1.field_2":124,
 "transport_ice_bus.table_1.field_3":127,
 "transport_ice_bus.table_2.field_1":145,
 "transport_ice_bus.table_2.field_2":146,
 "income_service_fees.table_2.field_1":191,
 "income_service_fees.table_2.field_2":192,
 "income_service_fees.table_2.field_3":193,
 "income_service_fees.table_2.field_4":194,
 "income_service_fees.table_2.field_5":195,
 "income_service_fees.table_2.field_6":196,
 "loans.long_term.delta_1":None,
}
TAX_MAP={
 "Iparűzési adó, %":("tax.business",198),
 "Gépjármű adó, %":("tax.vehicle",199),
 "Kommunális adó, %":("tax.communal",200),
 "Építményadó, %":("tax.building",201),
}
NS={"x":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
def need(test,why):
 if not test:raise ValueError("HOLD_"+why)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def nval(v,why):
 need(type(v) in (int,float) and math.isfinite(v),why)
 return float(v)
def parse_excel(path):
 p=Path(path)
 need(p.is_file() and p.stat().st_size<2_000_000 and digest(p)==EXCEL_SHA,
      "EXCEL_ORIGINAL_PIN_MISMATCH")
 with zipfile.ZipFile(p) as zip:
  sheet=zip.read("xl/worksheets/sheet1.xml")
  need(len(sheet)<2_000_000,"EXCEL_SHEET_SIZE")
  try:
   shared=ET.fromstring(zip.read("xl/sharedStrings.xml"))
   strs=["".join(si.itertext()) for si in shared.findall("x:si",NS)]
  except KeyError:strs=[]
  doc=ET.fromstring(sheet)
 cellrows={}
 for row in doc.findall("x:sheetData/x:row",NS):
  i=int(row.attrib["r"])
  cells={}
  for c in row.findall("x:c",NS):
   col=re.match(r"[A-Z]+",c.attrib["r"]).group()
   value=c.find("x:v",NS); inline=c.find("x:is",NS)
   text="".join(inline.itertext()) if inline is not None else (
         (value.text or "") if value is not None else "")
   if c.get("t")=="s":text=strs[int(text)]
   need(c.find("x:f",NS) is None,"UNVALIDATED_EXCEL_FORMULA_"+str(i))
   cells[col]=text
  cellrows[i]=cells
 need([cellrows[1].get(chr(x),"") for x in range(66,73)]==TEAMS,
      "EXCEL_TEAM_HEADER_ORDER")
 labelled={}
 own_numeric=0
 section=cellrows[1].get('A','').strip()
 need(section=='Összefoglaló','EXCEL_FIRST_SECTION')
 for i in sorted(cellrows):
  if i==1:continue
  cells=cellrows[i];raw=cells.get("A","")
  if not raw.strip():continue
  label=raw.strip()
  if label in SECTIONS and len(raw)==len(label):section=label
  need(section in SECTIONS,"EXCEL_SECTION_FOR_"+str(i))
  value=cells.get("C","")
  own=None
  if value!="":
   own=float(value)
   need(math.isfinite(own),"NONFINITE_OWN_VALUE")
   own_numeric+=1
  labelled[i]={"row":i,"section":section,"label":label,"own_p0":own,
              "teams_values":[cells.get(chr(x),"") for x in range(66,73)]}
 need(len(labelled)==374 and own_numeric==324 and len(SECTIONS)==10,
      "EXACT_374_ROWS_324_NUMERIC")
 need(len({k for k in labelled})==374,"UNIQUE_EXCEL_ROW")
 return {"rows":labelled,"labelled":374,"own_numeric":324,"own_non_numeric":50,
         "seven_teams":TEAMS,"sha256":digest(p)}
def match(excel,control,row_id):
 need(row_id in excel["rows"],"MISSING_EXCEL_ROW_"+str(row_id))
 row=excel["rows"][row_id]
 need(row["label"]==control["label"],"LABEL_DRIFT_"+str(row_id))
 want_section=("Bevételek" if control["domain"] in ("income_service_fees","tax") else
  "Intézmények" if control["domain"]=="institutions_education" else
  "Közösségi közlekedés" if control["domain"]=="transport_ice_bus" else None)
 need(want_section==row["section"],"SECTION_DRIFT_"+str(row_id))
 n=nval(control["p0_visible_number"],"OBSERVED_P0_NONNUMERIC")
 need(row["own_p0"] is not None and math.isclose(n,row["own_p0"],rel_tol=0,abs_tol=1e-10),
      "EXCEL_UI_VALUE_DRIFT_"+str(row_id))
 return {"control_id":control["decision_key"],"excel_row":row_id,
         "source_section":row["section"],"label":row["label"],
         "excel_p0":row["own_p0"],"observed_ui_p0":n,
         "match":"EXACT_LABEL_SECTION_AND_NUMERIC_P0",
         "p1_selected":None,"allowed_min":None,"allowed_max":None,
         "calibrated_cash_response":None,"calibrated_factor_response":None,
         "game_write_authorized":False}
def tax_source(path):
 p=Path(path);s=read_json(p)
 need(s.get("schema")=="ECOSIM_R228_CURRENT_TAX_ACTIVE_VIEW_READONLY_V1"
      and s.get("source_class")=="CONNECTED_BROWSER_VISIBLE_NOT_SERVER_ATTESTED"
      and s.get("source_url")=="https://edu.ecosim.hu/simulation/income"
      and s.get("active_subview")=="Adók"
      and (s.get("round"),s.get("market"),s.get("team"),s.get("period"))==
            ("Selejtező","I",TEAM,1)
      and s.get("game_writes")==0 and s.get("bounds_verified") is False
      and s.get("source_is_still_current_server_attested") is False,
      "PRIVATE_CURRENT_TAX_PROVENANCE")
 controls=s.get("controls")
 need(type(controls) is list and len(controls)==4 and
      set(x.get("label") for x in controls)==set(TAX_MAP),"TAX_FOUR_EXACT_FIELDS")
 for c in controls:
  need(type(c.get("p0")) in (int,float) and math.isfinite(c["p0"]) and
       c.get("p1_input")=="","NO_APPROVED_TAX_P1_INPUT")
 return s
def join(excel_path,r226_path,tax_path,r156_path,r224_path,out_dir):
 dest=Path(out_dir).resolve()
 need(dest.parent.exists() and not dest.exists() and
      not dest.is_relative_to(ROOT.resolve()),"NEW_PRIVATE_RESULT_DIR")
 excel=parse_excel(excel_path)
 old=read_json(r226_path)
 need(old.get("schema")=="ECOSIM_R226_REAL_CURRENT_TEN_TOP_LEVEL_PAGES_VISIBLE_CONTROL_CENSUS_V1"
      and old.get("top_level_route_count")==10 and
      old.get("observed_editable_text_inputs")==19 and
      old.get("original_R145_unknown_factor_effects_propagated")==19 and
      old.get("original_R145_unknown_cash_effects_propagated")==19 and
      old.get("game_writes")==0 and old.get("gameplay_gate")=="STOP" and
      old.get("actual_market_cap") is None and
      old.get("actual_spendable_project_cash") is None,
      "R226_SOURCE_AND_SAFETY_HOLD")
 controls=old.get("controls")
 need(isinstance(controls,list) and len(controls)==19 and
      {c["decision_key"] for c in controls}==set(R226_ROW_MAP),
      "R226_EXACT_NINETEEN_INPUT_IDENTITIES")
 tax=tax_source(tax_path)
 _,state,_=compile_bundle(Path(r156_path)/"r156_immutable/manifest.json")
 need(state["provenance"]["current_period"]==1 and
      state["provenance"]["market"]=="I" and
      state["market"]["maxProjectPerTurn"] is None and
      len(state["team"]["baseline_smartcity_factors"])==29,
      "SOURCE_BUNDLE_NOT_REAL_P1")
 results=[];unmatched=[];ids=set()
 for c in controls:
  k=c["decision_key"];r=R226_ROW_MAP[k]
  need(c["p1_current_decision_value"] is None and
       c["actual_allowed_min"] is None and c["actual_allowed_max"] is None and
       c["cash_response_ecu"] is None and c["factor_response"] is None and
       c["game_write_authorized"] is False,
       "R226_NOT_APPROVED_CONTROL_"+k)
  if r is None:
   unmatched.append({"control_id":k,"label":c["label"],
       "status":"EXCEL_UNIQUE_ROW_NOT_PROVEN"})
  else:
   row=match(excel,c,r);results.append(row);ids.add(r)
 for c in tax["controls"]:
  key,r=TAX_MAP[c["label"]]
  row=match(excel,{"decision_key":key,"domain":"tax",
                   "label":c["label"],"p0_visible_number":c["p0"]},r)
  results.append(row);ids.add(r)
 need(len(results)==19 and len(ids)==19 and len(unmatched)==4,
      "R227_19_EXACT_AND_FOUR_UNMAPPED")
 # All 23 are observed UI controls, NOT any selected P1 policy actions.
 all_controls=controls+[{"decision_key":TAX_MAP[c["label"]][0],
                          "policy_category":"tax"}
                         for c in tax["controls"]]
 need(len({c["decision_key"] for c in all_controls})==23,
      "TWENTY_THREE_UNIQUE_CONTROLS")
 # Reuse original R145 schema AND original R148 joined project/policy replay.
 # Explicitly synthetic 23 UNKNOWN-response placeholders each of five years;
 # future-year UI control availability is NOT verified; no policy selections.
 tracks={"schema":"ECOSIM_R145_POLICY_TRACKS_V1","tracks":[{
  "track_id":"R228_ALL_P1_SOURCE_OBSERVED_CONTROLS_FUTURE_YEARS_UNKNOWN_ONLY",
  "mode":"DOCUMENTED_OBSERVATION_ONLY",
  "assumption_note":"Coverage sentinel, not selected P1 decisions; future years unobserved",
  "actions":[{
    "year":year,"category":c["policy_category"],
    "decision_key":c["decision_key"],"duration":"ONE_YEAR",
    "factor_relative_percent":None,"annual_cash_delta_ecu":None,
    "source_evidence_id":"R228_R226_OR_CURRENT_TAX_READONLY",
    "assumption_note":"Unknown potential annual policy response, NO action chosen"
  } for year in range(1,6) for c in all_controls]}]}
 dest.mkdir(mode=0o700)
 trackpath=dest/"R228_POLICY_UNKNOWN_CONTRACT_TEST_ONLY.json"
 trackpath.write_text(json.dumps(tracks,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
 track=load_tracks(trackpath)[0]
 need(len(track["actions"])==115 and track["mode"]=="DOCUMENTED_OBSERVATION_ONLY",
      "R145_FIVE_YEAR_UNKNOWN_COVERAGE")
 for year in range(1,6):
  _,applied,unknown=policy_factor_replay(
   state["team"]["baseline_smartcity_factors"],track,year,1)
  cash=policy_money_replay(track,year,1)
  need(not applied and len(unknown)==23 and not cash["complete"] and
       len(cash["undisclosed_policy_cash_decisions"])==23,
       "R145_YEAR_UNKNOWN_NOT_ZERO_"+str(year))
 prior=read_json(r224_path)
 need(prior.get("schema")=="ECOSIM_R224_CURRENT_P1_CASHFLOW_SCENARIOS_NO_SPENDABLE_APPROVAL_V1"
      and prior.get("scenario_count")==24 and prior.get("game_writes")==0
      and prior.get("current_R191_real_cap") is None and
      prior.get("current_R191_actual_spendable_cash") is None and
      prior.get("current_R214_live_advice_authorized") is False,
      "ORIGINAL_R224_CONDITIONAL_NOT_LIVE")
 idx=project_index()
 weights={k:v[0] for k,v in WEIGHTS.items()}
 replay=[]
 for scenario in prior["scenarios"]:
  starts=scenario.get("full_five_year_illustrative_starts")
  need(isinstance(starts,list) and len(starts)==5 and
       all(isinstance(y,list) for y in starts),
       "R224_SCENARIO_START_SHAPE")
  plan={"start_by_year":[{"start_project_ids":y} for y in starts]}
  years=replay_policy_joint(plan,track,state["team"]["baseline_smartcity_factors"],
                            idx,weights,1)
  need(len(years)==5 and all(y["actual_index_forecast"] is None and
       y["actual_cashflow_forecast"] is None and
       len(y["policy_unmapped_actions"])==23 and
       y["policy_cash_delta_assumption"]["complete"] is False
       for y in years),"R148_JOINT_HIDDEN_UNKNOWN_EFFECTS")
  replay.append({"hypothetical_cap":scenario["hypothetical_cap"],
    "hypothetical_budget":scenario["hypothetical_annual_budget_ecu"],
    "objective":scenario["objective"],"source_project_starts":starts,
    "annual_replay":[{"year":y["year"],
      "mapped_project_only_conditional_index_NOT_TOTAL_FORECAST":
         y["joint_mapped_factor_counterfactual_index"],
      "unknown_policy_factor_effects":len(y["policy_unmapped_actions"]),
      "unknown_policy_cash_impacts":len(y["policy_cash_delta_assumption"]["undisclosed_policy_cash_decisions"]),
      "actual_index_forecast":None,"actual_cashflow_forecast":None} for y in years]})
 need(len(replay)==24 and sum(len(x["annual_replay"]) for x in replay)==120,
      "R148_24_5_YEAR_REPLAY")
 # Real formula preconditions: only business-tax baseline percent is source
 # matched. R153/R154 need extra market coefficients and money amounts, not
 # percentages. NEVER promote percent labels to *_amount parameters.
 tax_ready={
  "original_R153_required_decision_fields":list(R153_FIELDS),
  "source_verified_business_tax_percentage":excel["rows"][198]["own_p0"],
  "services_fee_percentage":None,
  "vehicle_tax_amount":None,"building_tax_amount":None,
  "vehicle_UI_unit":"PERCENT_NOT_VERIFIED_ECU_AMOUNT",
  "building_UI_unit":"PERCENT_NOT_VERIFIED_ECU_AMOUNT",
  "communal_UI_unit":"PERCENT_NOT_VERIFIED_ECU_AMOUNT",
  "market_coefficients_and_tax_divisors":None,
  "R153_actual_tax_counterfactual_allowed":False,
  "original_R154_required_city_bases":list(R154_BASE_FIELDS),
  "R154_current_and_future_city_bases_verified":False,
  "R154_actual_tax_revenue_forecast_allowed":False,
  "do_not_convert_ui_percent_to_tax_amount_without_source":True}
 summary={"schema":SCHEMA,
  "status":"PASS_R227_EXCEL_SOURCE_JOIN_R145_R148_UNKNOWN_PRESERVED_NOT_LIVE",
  "scope":"REAL_XLSX_AND_OPERATOR_VISIBLE_P0_NOT_SERVER_ATTESTED",
  "round":"Selejtező","market":"I","team":TEAM,"period":1,
  "excel_rows":excel["labelled"],"own_numeric_excel_rows":excel["own_numeric"],
  "seven_teams":len(excel["seven_teams"]),"main_menus_source_observed":10,
  "r226_controls":19,"new_tax_view_controls":4,"observed_total_controls":23,
  "exact_xlsx_vs_ui_p0_matches":19,"unmapped_unique_excel_control_rows":4,
  "excel_rows_without_a_direct_observed_UI_input_link":355,
  "current_P1_selected_actions_approved":0,
  "current_market_cap_verified":None,"current_spendable_project_cash_verified":None,
  "current_R192_full_catalog_time_admitted":False,
  "source_sha256":{"excel":excel["sha256"],
    "r226_receipt":digest(r226_path),"tax_view":digest(tax_path),
    "r156_manifest":digest(Path(r156_path)/"r156_immutable/manifest.json"),
    "r224_receipt":digest(r224_path)},
  "original_model_reuse":["R145 POLICY TRACKS","R148 JOINT FACTOR REPLAY",
                          "R224 CONDITIONAL 5Y PROJECT SCENARIOS",
                          "R153/R154 CONTRACT FIELD READINESS"],
  "r145_policy_unknown_effects_each_year":23,
  "r145_policy_unknown_cash_each_year":23,
  "r148_original_joint_scenario_count":len(replay),
  "r148_original_joint_annual_rows":120,
  "r148_full_city_score_verified":False,
  "actual_tax_model_readiness":tax_ready,
  "exact_links":results,"unmatched_controls":unmatched,
  "conditional_joint_scenarios":replay,
  "actual_five_year_winning_plan":None,"actual_first_year_eligible_recommendation":None,
  "gameplay_gate":"STOP","game_writes":0}
 (dest/"R228_RECEIPT.json").write_text(
  json.dumps(summary,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n")
 (dest/"R228_HU.md").write_text(
  "# R228 forrásösszekötés és öt éves ellenőrzés\n\n"
  "Excel: 374/374 sor, 324 saját numerikus sor.\n"
  "R226 + Adók UI: 23 megfigyelt szerkesztőmező; Excel P0 egyedi egyezés: 19, "
  "nem párosítható: 4.\n"
  "Eredeti R145/R148: 24 feltételes 5 éves projektpályán "
  "120 éves sor; a 23/év szakpolitikai és cash hatás UNKNOWN marad.\n"
  "R153/R154: üzleti adókulcs P0 ismert, de további paraméterek/adóalapok "
  "és a pénzösszeg-% mértékegység bizonyítása hiányzik.\n"
  "Ez nem valós ötéves pontszám és nem jogosult projektindítás.\n"
  "R191/R192/R214 továbbra is HOLD. GAME_ACTION_GATE=STOP, játékírás 0.\n",
  encoding="utf-8")
 print(json.dumps({"status":summary["status"],"excel":374,"ui_controls":23,
  "matched":19,"unmapped":4,"joint_scenarios":24,"joint_years":120,
  "unknown_policy_each_year":23,"tax_live_ready":False,
  "game_writes":0,"private_output":str(dest)},ensure_ascii=False))
 return summary
def main():
 p=argparse.ArgumentParser()
 for key in ("excel","r226","tax","r156","r224","out-dir"):
  p.add_argument("--"+key,type=Path,required=True)
 a=p.parse_args();join(a.excel,a.r226,a.tax,a.r156,a.r224,a.out_dir)
if __name__=="__main__":main()
