#!/usr/bin/env python3
"""One verifiable, PRIVATE P1 observed source bundle. ZERO optimization."""
from __future__ import annotations
import argparse,csv,hashlib,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"team-handoff/r228-excel-city-policy-join"))
from source_join_r228 import parse_excel

SCHEMA="ECOSIM_R238_UNIFIED_OBSERVED_P1_PRIVATE_NOT_STRATEGY_V1"
PIN_ORIGINAL_35_CARDS="0438d35a1ea04fa4ee71a02a2205c652ea80a2ca8a61d2c99b8c30953ef3e944"
PIN_R156_FACTORS="32713ad30fbb2eed6eb007a87928d19659a149e7d164ab23d2e9f2f61782b61d"
PIN_R156_STATES="07a67443a2e4ecfe10c4d7a0b28902a49b92981b79252add581f3ae2c67f3082"
MAP={"summary":"summary","projects":"projects",
     "institutions":"institutions_education","transport":"transport_ice_bus",
     "income":"income_service_fees","population":"population",
     "corporations":"corporations","loans":"loans",
     "finance":"finance","analysis":"analysis"}
EXTRA={"summary","projects","population","corporations",
       "loans","finance","analysis"}
MARKET="I";PERIOD=1;ROUND="Selejtező"

def hold(expr,name):
    if not expr:raise ValueError("HOLD_"+name)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding="utf8"))
def incsv(path):
    with Path(path).open(encoding="utf8",newline="") as f:
        return list(csv.DictReader(f))
def load(inputs,base,out):
    out=Path(out).resolve()
    hold(out.parent.is_dir() and not out.exists() and
         not out.is_relative_to(ROOT.resolve()),"OUTSIDE_REPO_NEW_PRIVATE_DIR")
    hold(all(Path(p).is_file() and not Path(p).is_symlink() for p in inputs.values()),
         "ALL_REQUIRED_INPUTS_PRESENT")
    r236=read(inputs["r236"]);r226=read(inputs["r226"]);r222=read(inputs["r222"])
    r228=read(inputs["r228"]);r234=read(inputs["r234"])
    r233=read(inputs["r233"]);r217=read(inputs["r217"])
    r224=read(inputs["r224"]);r235=read(inputs["r235"])
    hold(r236["schema"]=="ECOSIM_R236_PERIOD_SOURCE_COLLECTION_GATE_V1" and
         r236["data_frozen_for_final_optimization"] is False and
         r236["run_optimizer"] is False,"R236_COLLECTION_ONLY")
    for k,v in (("r226",r226),("r222",r222),("r228",r228),("r234",r234),("r233",r233),("r217",r217)):
        hold((v["market"],v["period"],v["round"])==(MARKET,PERIOD,ROUND)
             and v.get("gameplay_gate")=="STOP" and v.get("game_writes")==0,
             "SOURCE_MARKET_PERIOD_STOP_"+k)
    for k in ("r236","r226","r222","r228","r234","r233","r217","r224","r235","income_browser"):
        if k in r236["source_snapshots_sha256"]:
            hold(sha(inputs[k])==r236["source_snapshots_sha256"][k],
                 "R236_SOURCE_PIN_"+k)
    hold(sha(inputs["projects"])==PIN_ORIGINAL_35_CARDS
         and sha(inputs["p1_factors"])==PIN_R156_FACTORS
         and sha(inputs["p1_project_states"])==PIN_R156_STATES,
         "ORIGINAL_CARD_AND_R156_ROW_BYTES")
    excel=parse_excel(inputs["xlsx"])
    hold(excel["labelled"]==374 and excel["own_numeric"]==324 and
         len(excel["seven_teams"])==7 and r228["excel_rows"]==374,
         "EXCEL_374_324_7")
    projects_source=read(inputs["projects"])
    projs=projects_source["projects"]
    hold(len(projs)==35 and sorted(p["id"] for p in projs)==list(range(1,36)) and
         r222["observed_card_count"]==35 and
         r222["all_35_source_fields_match_pinned_r162"] is True and
         r222["r192_time_admission"]=="HOLD_CATALOG_NOT_SAME_PERIOD_CAPTURE_WINDOW",
         "EXACT_SOURCE_35_CARDS_STALE")
    all_factor_rows=incsv(inputs["p1_factors"])
    states=incsv(inputs["p1_project_states"])
    index_rows=[r for r in all_factor_rows if r["metric"]=="Okosváros index"]
    hold(len(index_rows)==1 and abs(float(index_rows[0]["value"])-52.48)<1e-8,
         "R156_EXPLICIT_P1_INDEX_ROW")
    factors=[r for r in all_factor_rows if r["metric"]!="Okosváros index"]
    hold(len(factors)==29 and len(states)==35 and r217["factor_count"]==29,
         "R156_FACTORS_AND_STATUS")
    factnames=[x["metric"] for x in factors]
    hold(len(set(factnames))==29,"UNIQUE_FACTOR_NAMES")
    transitions=r233["p0_p1_factor_changes"]
    hold(len(transitions)==24 and set(transitions)<=set(factnames)
         and r233["changed_factor_count"]==24 and
         r233["P0_fact_reported_smartcity_index"]==51.96 and
         r233["P1_plan_reported_smartcity_index"]==52.48,
         "P0_P1_FACTOR_RECONCILE")
    normalized=[]
    for item in factors:
        n=item["metric"];p1=float(item["value"])
        p0=transitions[n]["p0_fact"] if n in transitions else p1
        if n in transitions:
            hold(abs(p1-float(transitions[n]["p1_plan"]))<1e-8,
                 "FACTOR_P1_PLAN_"+n)
        normalized.append({"metric":n,"p0_fact_display":p0,
                           "p1_plan_display":p1,
                           "is_p1_fact":False,
                           "p0_source":"R233_P0_P1_RECONCILED_AND_R156",
                           "p1_source":"SHA_PINNED_R156_FACTORS"})
    hold({int(v["project_id"]) for v in states}==set(range(1,36)) and
         not any(v["selected_new"]=="true" for v in states),
         "R156_35_UNCHANGED_PROJECTS")
    state_lookup={int(v["project_id"]):v for v in states}
    for p in projs:
        status=state_lookup[p["id"]]
        hold((p["status_p0"]=="Fut")== (status["previous_running"]=="true"),
             "PINNED_PROJECT_RUNNING_"+str(p["id"]))
    pages=[]
    for route in r226["routes"]:
        name=route["route"]
        hold(name in MAP,"TEN_KNOWN_ROUTES")
        path=(base/("ecosim-r226-full-menu-visible-20261102/" +name+".txt")) if name in EXTRA else (
           base/("ecosim-r225-periodic-current-20261102/"+MAP[name]+".txt"))
        hold(path.is_file() and sha(path)==route["source_sha256"],
             "R226_SHA_SOURCE_VIEW_"+name)
        text=path.read_text(encoding="utf8")
        hold("Piac: I" in text and "Periódus: 1/5" in text and
             "Jutalom a nap végén" in text,
             "RAW_PAGE_TEAM_MARKET_PERIOD_"+name)
        pages.append({"route":name,"active_subview_only":True,
            "observed_at_operator_file_mtime":route["local_file_time_utc"],
            "known_subview_selector_labels":route["selector_labels_visible"],
            "content_readonly_snapshot":text,"source_sha256":sha(path),
            "full_alternate_subviews_collected":False})
    hold(len(pages)==10 and
         sum(len(r["known_subview_selector_labels"]) for r in pages)==27,
         "TEN_OBSERVED_VIEWS_27_SELECTOR_LABELS")
    hold(r235["school_client_lower_bound_count"]==4 and
         r235["original_r234_current_verified_full_minmax_pairs"]==0,
         "R235_ONLY_PARTIAL_CLIENT_BOUNDS")
    browser=read(inputs["income_browser"])
    hold(browser.get("kind")=="text" and isinstance(browser.get("text"),str)
         and "Piac: I" in browser["text"]
         and "Periódus: 1/5" in browser["text"]
         and "Jutalom a nap végén" in browser["text"]
         and "Iparűzési adó" in browser["text"],
         "RECENT_BROWSER_READ_ONLY_INCOME_CONTEXT")
    matrix=r234["matrix"]
    hold(len(matrix)==23 and len({v["control_id"] for v in matrix})==23 and
         r234["current_numeric_minmax_pairs_verified"]==0 and
         r234["calibrated_causal_factor_and_cash_effect_pairs_verified"]==0,
         "R234_NO_FALSE_POLICY_BOUNDS")
    crosswalk={v["control_id"]:v for v in r228["exact_links"]}
    hold(len(crosswalk)==19 and len(r228["unmatched_controls"])==4,
         "R228_EXACT_19_UNMATCHED_4")
    normalized_controls=[]
    for v in matrix:
        key=v["control_id"]
        item=dict(v)
        item["source_exact_excel_row"]=crosswalk[key]["excel_row"] if key in crosswalk else None
        item["p1_saved_decision_observed"]=False
        item["complete_allowed_range_observed"]=False
        normalized_controls.append(item)
    sortedrows=[excel["rows"][i] for i in sorted(excel["rows"])]
    hold(len(sortedrows)==374 and
         all(len(x["teams_values"])==7 for x in sortedrows),
         "EXCEL_SEVEN_TEAM_ROWS_ALL")
    finance=r224["cashflow"]
    hold(finance["scenario_funds_are_approved"] is False and
         r224["current_R191_real_cap"] is None and
         r228["current_spendable_project_cash_verified"] is None,
         "NO_AUTHORIZED_BUDGET")
    bundle={"schema":SCHEMA,"status":"PARTIAL_DATA_UNIFIED_NOT_COMPLETE",
      "round":ROUND,"market":MARKET,"period":PERIOD,"team":r236["team"],
      "source_file_sha256":{k:sha(v) for k,v in inputs.items()},
      "pages":pages,"excel":{"seven_teams":excel["seven_teams"],
        "all_374_labelled_p0_rows":sortedrows,"own_numeric_p0_count":324},
      "projects":{"source_card_count":35,
        "original_card_capture_span_minutes":r222["capture_span_minutes"],
        "same_hour_server_current_catalog":False,
        "observed_visible_cards_original":projs,
        "p1_current_partial_project_states":states,
        "provenance":"CARD_CATALOG_HISTORICAL_R162_VALIDATED_R222_TIMING_HOLD"},
      "city_factors":{"rows":normalized,"p0_index_ui":51.96,
                      "p1_plan_index_ui":52.48,"p1_is_observed_fact":False},
      "more_recent_open_income_tax_source":{
           "readonly_browser_markup":browser["text"],
           "source_class":"CURRENT_OPEN_TAB_STATIC_DOM_NOT_SAVED_REACT_VALUES",
           "effective_saved_p1_tax_rates_verified":False,
           "other_income_subview_contents_currently_collected":False},
      "institution_client_partial_lower_bounds":{
           "previous_school_count_client_min_only":r235["school_change_client_lower_bounds"],
           "education_training_development_symbolic_bounds":r235["institution_annual_training_development_symbolic_bounds"],
           "verified_full_allowed_ranges":0},
      "controls":{"rows":normalized_controls,"exact_excel_p0_matches":19,
                  "unmatched_excel_controls":4,"verified_full_minmax":0,
                  "approved_p1_actions":0,"calibrated_policy_effects":0},
      "finance":{"observed_p0_p1_values":finance["source_values_p0_p1_ecu"],
                 "hypothetical_annual_budget_ecu_not_spendable":
                     finance["hypothetical_annual_budget_ecu"],
                 "spendable_budget_ecu_verified":None,
                 "grant_earmarking_verified":False,
                 "project_cost_interactions_reforecasted":False},
      "data_gates":{"r236_data_collection_complete":False,
                    "project_same_hour_capture":False,
                    "all_subview_contents":False,
                    "policy_bounds_complete":False,
                    "market_config_complete":False,
                    "budget_authority_complete":False,
                    "future_year_actuals_currently_observable":False,
                    "ready_for_final_optimization":False,
                    "ready_for_gameplay":False},
      "run_optimizer":False,"game_writes":0,"gameplay_gate":"STOP",
      "provenance_type":"MIXED_PREVIOUS_SOURCE_SNAPSHOTS_NOT_SERVER_ATTESTED"
    }
    out.mkdir(mode=0o700)
    target=out/"ECOSIM_P1_OBSERVED_PRIVATE.json"
    target.write_text(json.dumps(bundle,ensure_ascii=False,sort_keys=True,
                        indent=2)+"\n",encoding="utf8")
    receipt={"schema":SCHEMA,"status":bundle["status"],
             "bundle_sha256":sha(target),
             "main_views_observed":len(pages),
             "selector_labels_incomplete":27,
             "source_excel_rows":len(sortedrows),
             "source_projects":len(projs),"source_factor_pairs":len(normalized),
             "source_controls":len(normalized_controls),
             "verified_policy_ranges":0,"game_writes":0,
             "ready_for_final_optimization":False,
             "source_file_sha256":bundle["source_file_sha256"]}
    (out/"R238_RECEIPT.json").write_text(
        json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
        encoding="utf8")
    print(json.dumps({k:v for k,v in receipt.items() if k not in (
        "source_file_sha256","bundle_sha256")},ensure_ascii=False))
    return receipt

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for k in ("r236","r226","r222","r228","r234","r233","r217",
              "r224","r235","income-browser","xlsx","projects","p1-factors","p1-project-states",
              "base","out-dir"):
        p.add_argument("--"+k,type=Path,required=True)
    a=p.parse_args()
    kw=vars(a);base=kw.pop("base");out=kw.pop("out_dir")
    load(kw,base,out)
