#!/usr/bin/env python3
"""Source-first P1 evidence collection ledger. Never runs an optimizer or game write."""
import argparse, hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path

SCHEMA="ECOSIM_R236_PERIOD_SOURCE_COLLECTION_GATE_V1"

def read(path):
    return json.loads(Path(path).read_text(encoding="utf8"))

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def require(condition,label):
    if not condition:
        raise ValueError("HOLD_"+label)

def collect(paths,output,at_utc=None):
    output=Path(output)
    require(output.parent.is_dir() and not output.exists(),"NEW_PRIVATE_OUTPUT")
    require(all(Path(v).is_file() and not Path(v).is_symlink()
                for v in paths.values()),"READONLY_EXISTING_FILES")
    j={k:read(paths[k]) for k in ("r217","r222","r224","r226","r228",
                                  "r232","r233","r234","r235")}
    first=j["r217"]
    ident=(first["round"],first["market"],first["period"],first["team"])
    require(ident[0]=="Selejtező" and ident[1]=="I" and ident[2]==1,
            "EXPECTED_CURRENT_PERIOD")
    for name,item in j.items():
        require(tuple(item.get(k,ident[i]) for i,k in enumerate(("round","market","period")))
             ==ident[:3] and (item.get("team",ident[3])==ident[3]),
             "SAME_MARKET_TEAM_PERIOD_"+name)
        require(item.get("gameplay_gate")=="STOP"
                and item.get("game_writes")==0,
                "NO_GAME_ACTION_"+name)
    r222,r226,r228,r234,r235=j["r222"],j["r226"],j["r228"],j["r234"],j["r235"]
    require(r222["observed_card_count"]==35
            and r222["observed_card_cost_effect_parity"]==35
            and r222["r192_time_admission"]=="HOLD_CATALOG_NOT_SAME_PERIOD_CAPTURE_WINDOW"
            and r222["capture_span_minutes"]>60,"CARD_CAPTURE_TIME_WINDOW")
    require(r226["top_level_route_count"]==10
            and r226["observed_default_or_selected_subview_count"]==10
            and r226["all_selector_subview_contents_observed"] is False
            and r226["all_captured_default_views_within_60_min_of_R156"] is True,
            "PARTIAL_SUBVIEW_COVERAGE")
    selectors=[{"route":row["route"],
                "visible_selector_labels":row["selector_labels_visible"],
                "observed_default_or_selected_view":True,
                "alternate_subviews_complete":False}
               for row in r226["routes"]]
    selector_labels=sum(len(x["visible_selector_labels"]) for x in selectors)
    require(selector_labels==r226["distinct_selector_button_labels"]==27,
            "EXACT_ROUTE_SELECTOR_LABELS")
    require(r228["excel_rows"]==374
            and r228["own_numeric_excel_rows"]==324
            and r228["observed_total_controls"]==23
            and r228["exact_xlsx_vs_ui_p0_matches"]==19,
            "SOURCE_P0_AND_CONTROL_COVERAGE")
    require(j["r233"]["changed_factor_count"]==24
            and j["r233"]["P1_plan_reported_smartcity_index"]==52.48
            and j["r233"]["P0_fact_reported_smartcity_index"]==51.96,
            "SOURCE_P0_P1_FACTOR_PAIR")
    require(r234["observed_ui_controls"]==23
            and len(r234["matrix"])==23
            and r234["current_numeric_minmax_pairs_verified"]==0
            and r234["current_P1_effective_selected_values_verified"]==0
            and r234["calibrated_causal_factor_and_cash_effect_pairs_verified"]==0,
            "POLICY_DATA_STILL_INCOMPLETE")
    require(r235["school_client_lower_bound_count"]==4
            and r235["symbolic_range_count"]==2
            and r235["original_r234_current_verified_full_minmax_pairs"]==0,
            "PARTIAL_CLIENT_RULE_NOT_FULL_ADMISSION")
    require(j["r232"]["video_evidence"]["base_max_new_projects_per_virtual_year"]==4
            and j["r232"]["current_game_server_project_cap"] is None,
            "ANNOUNCED_FOUR_NOT_SERVER_CAP")
    require(j["r224"]["current_R191_real_cap"] is None
            and j["r224"]["current_R191_actual_spendable_cash"] is None
            and j["r224"]["cashflow"]["scenario_funds_are_approved"] is False,
            "NO_UNVERIFIED_SPENDABLE_FUNDS")
    browser_payload=json.loads(Path(paths["income_browser"]).read_text(encoding="utf8"))
    require(browser_payload.get("kind")=="text" and isinstance(browser_payload.get("text"),str),"READONLY_BROWSER_SOURCE_WRAPPER")
    html=browser_payload["text"]
    require(re.search(r"\bPiac:\s*I\b",html) and
            re.search(r"\bPeriódus:\s*1/5\b",html)
            and "Iparűzési adó" in html and "Gépjármű adó" in html
            and "<input type=\"text\" value=\"\"/>" in html,
            "CURRENT_BROWSER_CONTEXT_READONLY_NOT_RENDERED_VALUE")
    times={
      "project_cards_span_minutes":r222["capture_span_minutes"],
      "project_cards_coherent_one_hour_capture":False,
      "10_menu_default_views_span_minutes":
          r226["operator_local_observation_span_minutes"],
      "10_menu_default_views_within_60min_of_R156":
          r226["all_captured_default_views_within_60_min_of_R156"],
      "r156_state_capture_time_utc":r226["r156_state_capture_time_utc"]
    }
    categories=[
      ("market_period_and_identity","OBSERVED_OPERATOR_UI","market I, P1, named team"),
      ("original_excel","COVERED_PRIOR_SOURCE","374 rows, 324 own numeric P0 rows"),
      ("project_card_catalog","COVERED_BUT_TIME_GATE_FAIL","35/35 source-matched, 103+ minute span"),
      ("p0_and_p1_factor_values","COVERED_PLAN_NOT_FACT","29 P0, 29 P1 planned values"),
      ("top_level_visible_pages","COVERED_ACTIVE_VIEW_ONLY","10/10 initial/active views"),
      ("all_alternate_subviews","INCOMPLETE","27 selector labels, not 27 verified full views"),
      ("policy_input_controls","OBSERVED_BUT_NOT_ADMITTED","23 P1 input surfaces, 19 exact P0 joins"),
      ("policy_allowed_numeric_minmax","UNKNOWN","0/23 complete admitted numeric ranges"),
      ("policy_p1_saved_decisions","UNKNOWN","0/23 source-approved values"),
      ("policy_cash_and_factor_causal_effects","UNKNOWN","0/23 calibrated responses"),
      ("current_server_project_cap","UNKNOWN","official spoken 4/year is NOT R191 server config"),
      ("real_project_funds_and_commitments","UNKNOWN","P1 plan cash-flow is not spendable budget"),
      ("institution_current_market_multipliers","UNKNOWN","historical client formulas only"),
      ("real_tax_legal_maxima","UNKNOWN","generic input shows no local numeric limit"),
      ("peer_p1_and_future_actions","UNKNOWN","7 teams had same P0 index; plans not all observed"),
      ("year_2_to_5_actuals","NOT_YET_OBSERVABLE","future period facts cannot exist in P1"),
      ("server_five_year_score_or_model","UNKNOWN","conditional card proxy is not official score"),
    ]
    require(sum(x[1] in ("UNKNOWN","INCOMPLETE","NOT_YET_OBSERVABLE",
                         "COVERED_BUT_TIME_GATE_FAIL") for x in categories)>=12,
            "UNPROVEN_DATA_MUST_NOT_PASS")
    now=at_utc or datetime.now(timezone.utc).isoformat()
    result={
      "schema":SCHEMA,"status":"PARTIAL_SOURCE_COLLECTION_NO_OPTIMIZATION",
      "captured_inventory_at_utc":now,
      "round":ident[0],"market":ident[1],"period":ident[2],"team":ident[3],
      "mode":"READ_ONLY_SOURCES_DATA_COLLECTION_ONLY",
      "source_snapshots_sha256":{k:sha(v) for k,v in paths.items()},
      "source_coverages":[{"dimension":a,"status":b,"evidence":c}
                          for a,b,c in categories],
      "route_selectors":selectors,"total_selector_labels":selector_labels,
      "capture_windows":times,
      "known_period_1_source_counts":{
         "project_cards_observed":35,"city_factor_p0":29,
         "city_factor_p1_plan":29,"default_main_views":10,
         "ui_control_surfaces":23,"p0_ui_excel_exact_matches":19,
         "fully_verified_control_minmax":0,
         "verified_policy_causal_effects":0,
         "historical_client_partial_school_lower_bounds":4,
         "client_symbolic_education_ranges_missing_multipliers":2,
      },
      "data_frozen_for_final_optimization":False,
      "current_period_full_intake_complete":False,
      "five_year_future_actuals_present":False,
      "game_action_authorized":False,
      "run_optimizer":False,"gameplay_gate":"STOP","game_writes":0,
      "next_data_collection_priority":[
        "COMPLETE_ALTERNATE_SUBVIEWS_READONLY",
        "SAME_HOUR_FULL_35_CARDS_AND_CURRENT_R156_READONLY",
        "SERVER_SOURCE_MARKET_CONFIG_AND_FIELD_BOUNDS_READONLY",
        "ACTUAL_SPENDABLE_FUNDS_COMMITMENTS_AND_FINANCE_RULES",
        "PLAN_TO_FACT_AND_PEER_OUTCOMES_ON_LATER_PERIODS"
      ],
    }
    output.mkdir(mode=0o700)
    (output/"R236_PRIVATE_LEDGER.json").write_text(json.dumps(
        result,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf8")
    lines=["# EcoSim – gyűjtés előbb, optimalizálás csak adatkapu után","",
       f"Forrásleltár időpontja: {now}",
       "I. piac / 1. periódus. **Jelenleg nincs teljes adat-felvételi PASS.**",
       "Az eddigi projekttervek mind feltételesek; nem futtattunk optimalizálót.",
       "",
       "| Adatkör | Státusz | Indok |","|---|---|---|"]
    for a,b,c in categories:lines.append(f"| {a} | {b} | {c} |")
    lines+=["","## Nyitott alnézetválasztók"]
    for item in selectors:
        lines.append(f"- {item['route']}: "+(", ".join(item["visible_selector_labels"]) or
                     "nincs további látható választó")+
                     " – csak az eredetileg kiválasztott tartalom garantált.")
    lines+=["","## Időbeli és bizonyítékszintű korlátok",
       f"- A 35 kártya felvételi időtartama: {times['project_cards_span_minutes']:.1f} perc; R192 HOLD.",
       f"- A 10 főmenü alapnézete {times['10_menu_default_views_span_minutes']:.1f} perces felvétel; R156-tal 60 percen belül.",
       "- A friss Adók HTML-szöveg csak attribútumot mutat; nem hiteles React input property / mentett döntés.",
       "- A 4/év szervezői szabály nem egyenlő szerverkonfigurációs adattal.",
       "- P2–P5 tényadatokat P1 alatt nem lehet előre begyűjteni.",
       "",
       "## Beérkezés után ellenőrzendő",
       "A következő felvételnek eredeti időpontot, piacot, periódust, csapatot, "
       "forrás-hash-t és külön P0 tény / P1 terv jelölést kell tartalmaznia.",
       "A számítási STOP csak az adott döntéshez szükséges hiteles adatok "
       "megléte esetén oldható fel, soha nem automatizáltan éles játékírásra.",
       "NO_GAME_WRITES, NO_MERGE, NO_DEPLOY."]
    (output/"R236_DATA_COVERAGE_HU.md").write_text(
        "\n".join(lines)+"\n",encoding="utf8")
    print(json.dumps({"status":result["status"],
        "source_count":len(paths),"main_views":10,"selector_labels":selector_labels,
        "unknown_full_ranges":23,"game_writes":0},ensure_ascii=False))
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for key in ("r217","r222","r224","r226","r228","r232","r233","r234","r235","income-browser","out-dir"):
        p.add_argument("--"+key,type=Path,required=True)
    a=p.parse_args()
    collect({k:v for k,v in vars(a).items()
             if k!="out_dir"},a.out_dir)
