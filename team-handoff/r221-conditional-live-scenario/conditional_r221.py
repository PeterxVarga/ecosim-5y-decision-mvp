#!/usr/bin/env python3
"""R221: current observed EcoSim factors + 35 visible cards -> WHAT-IF search grid.

Original R162/R160 engines and official handbook rule semantics are reused.
NEVER admit a fictional project cap or projected cash as official R191/R214
inputs; no login, no API/network, no gameplay actions.
"""
from __future__ import annotations
import argparse,hashlib,json,math,sys
from collections import defaultdict
from datetime import datetime,timezone,timedelta
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"ECOSIM_R162_INTEGRITY_REVIEW_RC/tools"),
              str(ROOT/"team-handoff/r217-current-visible-admission")]
from json_integrity_r162 import read_json
from observation_bundle_r152 import compile_bundle
from strategy_5y import search
from r142_proxy_reference import COEFF

SCHEMA="ECOSIM_R221_REAL_SOURCE_SCENARIO_FRONTIER_NO_LIVE_CAP_OR_CASH_V1"
CAPS=(1,2,3)
CASH=(0,25000,50000,150000)
OBJECTIVES=("nominal","scenario_min")
RULEBOOK_SHA="4d6b5c545bb205e5a9f8b92959b6659c4786d10cf6e1e6b2f654fa79c0168087"
EXPECTED_RUNNING=[14,22,23,24,34,35]
def hold(condition,reason):
    if not condition:raise ValueError("HOLD_"+reason)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def valid_data(r217,r220,rulebook,bundle):
    readout=read_json(r217)
    coverage=read_json(r220)
    hold(readout.get("schema")=="ECOSIM_R217_CURRENT_BROWSER_VISIBLE_PARTIAL_ADMISSION_V1" and
         readout.get("r191_current_qualification")=="HOLD_CAP_UNKNOWN_OR_ASSUMED" and
         readout.get("observed_project_statuses")==35 and
         readout.get("running_ids")==EXPECTED_RUNNING and
         readout.get("index_p1_plan")==52.48 and
         readout.get("game_writes")==0 and readout.get("gameplay_gate")=="STOP",
         "R217_CURRENT_PARTIAL_SOURCE_IDENTITY")
    hold(coverage.get("schema")=="ECOSIM_R220_CURRENT_ALL_35_VISIBLE_CARD_PARITY_V1" and
         coverage.get("observed_card_count")==35 and
         coverage.get("money_parity_count")==35 and
         coverage.get("effect_parity_count")==35 and
         coverage.get("project_conditions_count_verified")==0 and
         coverage.get("complete_r192_definition_admitted") is False and
         coverage.get("market_project_start_cap_verified") is False and
         coverage.get("spendable_project_cash_verified") is False and
         coverage.get("gameplay_gate")=="STOP" and
         coverage.get("running_ids")==EXPECTED_RUNNING and
         coverage.get("game_writes")==0,
         "R220_VISIBLE_CARD_NOT_FULL_ADMISSION")
    hold(coverage.get("r217_receipt_sha256")==sha(r217),
         "CURRENT_R217_R220_SHA_BINDING")
    hold(coverage.get("team")==readout.get("team") and
         coverage.get("market")==readout.get("market") and
         coverage.get("period")==readout.get("period")==1 and
         coverage.get("round")==readout.get("round")=="Selejtező",
         "R217_R220_PERIOD_TEAM_ROUND")
    hold(sha(rulebook)==RULEBOOK_SHA,"OFFICIAL_RULEBOOK_CHANGED")
    _,state,_=compile_bundle(Path(bundle)/"manifest.json")
    hold(state["provenance"]["round"]=="Selejtező" and
         state["provenance"]["team"]==readout["team"] and
         state["provenance"]["market"]==readout["market"] and
         state["provenance"]["current_period"]==1,
         "ORIGINAL_R156_CURRENT_SOURCE")
    hold(state["team"]["initially_active_project_ids"]==EXPECTED_RUNNING and
         state["team"]["already_selected_new_project_ids_current_period"]==[] and
         state["market"]["maxProjectPerTurn"] is None and
         all(v is None for v in state["team"].get("confirmed_spendable_cash_ecu_by_year",[])) and
         all(v is None for v in state["team"].get("committed_costs_ecu_by_year",[])),
         "UNVERIFIED_LIVE_CAP_OR_CASH_MUST_REMAIN_UNKNOWN")
    hold(set(state["team"]["baseline_smartcity_factors"])==set(COEFF) and
         len(state["market"].get("smartcity_total_weights") or {})==6,
         "ACTUAL_CURRENT_29_FACTORS_WEIGHTS")
    hold(coverage.get("source_sha256",{}).get("projects_environment") and
         coverage.get("source_sha256",{}).get("projects_transport"),
         "FOUR_OBSERVED_VIEWS_REQUIRED")
    return state,readout,coverage

def _choose(result,cap,budget,obj):
    hold(result.get("schema")=="ECOSIM_R148_SOURCE_BOUNDED_OFFLINE_STRATEGY_V1" and
         result.get("final_gameplay_decision")=="STOP" and
         result.get("game_write_actions")==0 and
         result.get("actual_five_year_score_forecast_validated") is False and
         isinstance(result.get("top_plans"),list) and len(result["top_plans"])>0,
         "ORIGINAL_STRATEGY_OUTPUT_SAFETY")
    assumptions=result["assumptions"]
    hold(assumptions["annual_project_limit"]==cap and
         assumptions["annual_limit_source"]=="EXPLICIT_ILLUSTRATIVE_CLI_ASSUMPTION" and
         assumptions["budget_source"]=="EXPLICIT_ILLUSTRATIVE_CLI_SCENARIO_NOT_SPENDABLE_CASH" and
         assumptions["official_cash_envelopes_or_illustrative_scenario"]==[budget]*5,
         "EXPLICIT_NOT_OFFICIAL_CAP_AND_BUDGET")
    eligible=[]
    for p in result["top_plans"]:
        audit=p["r160_independent_constraint_replay"]
        hold(audit["schema"]=="ECOSIM_R160_INDEPENDENT_PLAN_AUDIT_V1" and
             audit["gameplay_gate"]=="STOP" and
             audit["actual_game_eligibility"] is None and
             audit["actual_funding_approval"] is None,
             "ORIGINAL_R160_AUDIT_NOT_APPROVAL")
        hold(not audit["hard_rule_violations"],"R160_HARD_VIOLATIONS")
        if audit["conditional_eligibility_items"]:continue
        years=p["start_by_year"]
        hold(len(years)==5 and [x["year"] for x in years]==[1,2,3,4,5],
             "ALL_FIVE_YEARS_REQUIRED")
        first=years[0];ids=first["start_project_ids"]
        hold(len(ids)<=cap and
             first["conservative_card_cash_requirement_ecu"]<=budget+1e-7,
             "SCENARIO_BUDGET_OR_SLOT_EXCEEDED")
        eligible.append(p)
    hold(bool(eligible),"NO_R160_CONDITION_FREE_PLAN_UNDER_SCENARIO")
    best=eligible[0]
    return {
        "hypothetical_cap":cap,"hypothetical_annual_budget_ecu":budget,
        "objective":obj,"initial_project_ids":best["start_by_year"][0]["start_project_ids"],
        "first_year_conservative_requirement_ecu":best["start_by_year"][0]["conservative_card_cash_requirement_ecu"],
        "full_five_year_illustrative_starts":[x["start_project_ids"] for x in best["start_by_year"]],
        "five_year_conditional_project_proxy_delta":best["terminal_mapped_proxy_delta"],
        "sampled_worst_direct_effect_proxy_delta":best["r157_robust_sensitivity"]["scenario_min_clamp_only_mapped_delta"],
        "five_year_conservative_cash_requirements_ecu":best["five_year_conservative_card_cost_ecu"],
        "validated_by_original_r160":True,"source_history_project_conditions_current_verified":False,
        "financing_authorized":False,"gameplay_gate":"STOP",
        "run_count_of_r160_condition_free_plans":len(eligible)}

def compute(r217,r220,rulebook,bundle,output):
    out=Path(output)
    hold(not out.exists() and out.parent.is_dir() and
         not out.resolve().is_relative_to(ROOT.resolve()),
         "OUTPUT_MUST_BE_NEW_PRIVATE_DIRECTORY")
    for p in (r217,r220,rulebook):
        hold(Path(p).is_file() and not Path(p).is_symlink(),"SOURCE_FILE_REQUIRED")
    state,original,proof=valid_data(r217,r220,rulebook,bundle)
    scenarios=[]
    for cap in CAPS:
        for cash in CASH:
            for objective in OBJECTIVES:
                # IMPORTANT: never update R156 cap/funds, never write to game.
                res=search(state,start_year=1,cap_override=cap,
                           budget_override=[cash]*5,
                           beam_width=8,shortlist=25,
                           allow_same_year=False,objective=objective)
                scenarios.append(_choose(res,cap,cash,objective))
    grouped=defaultdict(list)
    for r in scenarios:
        key=tuple(r["initial_project_ids"])
        grouped[key].append({"cap":r["hypothetical_cap"],
                             "budget_ecu":r["hypothetical_annual_budget_ecu"],
                             "objective":r["objective"]})
    cross=[{
          "first_year_project_ids":list(ids),
          "scenario_support_count":len(runs),
          "scenario_sensitivity_support_only":runs,
          "not_current_market_eligibility":True} for ids,runs in grouped.items()]
    cross.sort(key=lambda x:(-x["scenario_support_count"],
                              len(x["first_year_project_ids"]),
                              x["first_year_project_ids"]))
    result={
       "schema":SCHEMA,"status":"PASS_ACTUAL_SOURCE_HYPOTHETICAL_SCENARIO_SEARCH_ONLY",
       "round":original["round"],"market":original["market"],
       "team":original["team"],"period":1,
       "source":"ACTUAL_R217_R220_CURRENT_OPERATOR_VISIBLE_NOT_SERVER_ATTESTED",
       "source_sha256":{"r217":sha(r217),"r220":sha(r220),
                        "official_rulebook":sha(rulebook),
                        "r156_manifest":sha(Path(bundle)/"manifest.json")},
       "project_card_visible_cost_effect_match":35,
       "current_statuses_observed":35,"current_project_conditions_verified":0,
       "historical_condition_count":2,
       "current_max_project_starts_per_period":None,
       "current_spendable_cash":None,
       "projected_p1_plan_reserve_not_financing_approval":True,
       "official_rulebook_budget_mechanism":"CASHFLOW_AUTO_DEBT_IF_DEFICIT",
       "official_rulebook_cap":"LIMITED_PER_PERIOD_BUT_NUMERIC_UNSPECIFIED",
       "rulebook_project_effect":"ONCE_ON_START_RELATIVE_TO_PREVIOUS_FACTOR",
       "scenario_parameters":{"caps_hypothetical":list(CAPS),
                              "annual_cash_envelopes_hypothetical_ecu":list(CASH),
                              "objectives":list(OBJECTIVES),
                              "start_year":1,
                              "future_years_all_same_scenario_assumption":True,
                              "co_start_dependencies":"PRIOR_YEAR_ONLY_CONSERVATIVE_TEST_CONDITION"},
       "searched_scenario_count":len(scenarios),"scenarios":scenarios,
       "first_year_action_sensitivity_groups":cross,
       "one_time_project_conditions_from_historical_not_current_validated":True,
       "full_causal_city_transition_predicted":False,
       "official_score_predicted":False,
       "r191_live_eligibility":"HOLD_CAP_UNKNOWN_OR_ASSUMED",
       "r192_live_catalog":"HOLD_UNVERIFIED_PROJECT_CONDITIONS",
       "r214_live_finance":"HOLD_UNKNOWN_SPENDABLE_CASH",
       "live_advisory_authorized":False,
       "gameplay_gate":"STOP","game_writes":0,
       "owner_action":"NO_GAMEPLAY_ACTION_FROM_THIS_HYPOTHETICAL_MATRIX"}
    out.mkdir(mode=0o700)
    (out/"R221.json").write_text(
        json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    lines=[
      "# R221 – az éles Selejtező I tényezőin futtatott FELTÉTELES ötéves keresés",
      "","**KIZÁRÓLAG MI LENNE, HA SZCENÁRIÓ, NEM ÉLES PROJEKTJAVASLAT.**",
      f"Aktualitás: {original['round']} / I. piac / 1. év.",
      "35/35 megfigyelt kártyaköltség és hatás; a projektfeltételek nem hitelesítettek.",
      "Hivatalos kézikönyv alapján a konkrét projektlimit nem ismert, automatikus hitel lehetséges.",
      "A hipotetikus éves pénzkeretekből semelyiket nem tekintjük igazoltan elkölthetőnek.",
      "","| Csak feltételezett limit | Csak feltételezett éves keret | Cél | Elsőéves projektek | Konzervatív kártyateher |",
      "|---:|---:|---|---|---:|"]
    for x in scenarios:
        lines.append(
           f"| {x['hypothetical_cap']} | {x['hypothetical_annual_budget_ecu']:,.0f} ECU | {x['objective']} | "+
           (", ".join(map(str,x["initial_project_ids"])) or "Nincs új projekt")+
           f" | {x['first_year_conservative_requirement_ecu']:,.0f} ECU |")
    lines += ["","## Feltételezések iránti érzékenység"]
    for group in cross:
        names=", ".join(map(str,group["first_year_project_ids"])) or "Nincs projekt"
        lines.append(f"- Első év: **{names}**, az {len(scenarios)} külön hipotetikus futásból {group['scenario_support_count']} esetben.")
    lines += ["","A feltételes közvetlenhatás-proxy nem hivatalos játékeredmény.",
              "A pénzügyi forgatókönyvek nem hagyják jóvá a projektindítást.",
              "**GAME_ACTION_GATE=STOP.**",""]
    (out/"R221_HU.md").write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps({"status":result["status"],
                      "scenario_runs":len(scenarios),"distinct_first_actions":len(cross),
                      "best_supported_first_actions":[z["first_year_project_ids"] for z in cross[:5]],
                      "live_advisory_authorized":False,"game_writes":0,
                      "private_result":str(out)},ensure_ascii=False))
    return result

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--r217-receipt",required=True,type=Path)
    a.add_argument("--r220-receipt",required=True,type=Path)
    a.add_argument("--official-rulebook",required=True,type=Path)
    a.add_argument("--r156-bundle",required=True,type=Path)
    a.add_argument("--out-dir",required=True,type=Path)
    x=a.parse_args()
    compute(x.r217_receipt,x.r220_receipt,x.official_rulebook,x.r156_bundle,x.out_dir)
if __name__=="__main__":main()
