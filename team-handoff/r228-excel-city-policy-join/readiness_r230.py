#!/usr/bin/env python3
"""Source-anchored first-year candidate thresholds and original R191/R192 HOLD gates.

This never validates official game eligibility. It never writes to the game.
All inputs are private existing receipts; only generic source is publishable.
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [
    str(HERE),
    str(ROOT / "ECOSIM_R162_INTEGRITY_REVIEW_RC/tools"),
    str(ROOT / "team-handoff/r191-live-admission/tools"),
]
from source_join_r228 import SCHEMA as R228_SCHEMA, digest, need
from json_integrity_r162 import read_json
from observation_bundle_r152 import compile_bundle
from admission_r191 import validate_state, AdmissionHold

SCHEMA = "ECOSIM_R230_SOURCE_GATED_FIRST_YEAR_THRESHOLDS_V1"
EXPECTED_R228 = "PASS_R227_EXCEL_SOURCE_JOIN_R145_R148_UNKNOWN_PRESERVED_NOT_LIVE"
EXPECTED_R224 = "ECOSIM_R224_CURRENT_P1_CASHFLOW_SCENARIOS_NO_SPENDABLE_APPROVAL_V1"
EXPECTED_R222 = "ECOSIM_R222_ALL_35_VISIBLE_PROJECT_CONDITIONS_PROOF_V1"


def build(r228_path, r224_path, r222_path, manifest_path, output, *,now=None):
    dest = Path(output).resolve()
    need(dest.parent.is_dir() and not dest.exists()
         and not dest.is_relative_to(ROOT.resolve()), "NEW_PRIVATE_OUTPUT")
    r228, r224, r222 = (read_json(x) for x in (r228_path,r224_path,r222_path))
    need(r228.get("schema") == R228_SCHEMA
         and r228.get("status") == EXPECTED_R228
         and r228.get("gameplay_gate") == "STOP"
         and r228.get("game_writes") == 0
         and r228.get("actual_first_year_eligible_recommendation") is None
         and r228.get("actual_five_year_winning_plan") is None
         and r228.get("r148_full_city_score_verified") is False
         and r228.get("source_R224_finance_and_game_authority") == "HYPOTHETICAL_ONLY",
         "R228_STRICT_SOURCE_NOT_LIVE")
    need(r224.get("schema") == EXPECTED_R224
         and r224.get("current_R191_real_cap") is None
         and r224.get("current_R191_actual_spendable_cash") is None
         and r224.get("current_R192_full_admission") is False
         and r224.get("current_R214_live_advice_authorized") is False
         and r224.get("gameplay_gate") == "STOP"
         and r224.get("game_writes") == 0,
         "R224_ADMISSION_IS_NOT_LIVE")
    cash=r224.get("cashflow",{})
    need(isinstance(cash,dict)
         and cash.get("grant_earmarking_verified") is False
         and cash.get("incremental_project_funding_observed_and_approved") is False
         and cash.get("scenario_funds_are_approved") is False
         and cash.get("project_interactions_reforecasted_in_cash_flow") is False
         and r224.get("future_year_budgets_assumed_same_not_observed") is True,
         "R224_FUNDS_NOT_APPROVED")
    need(r222.get("schema") == EXPECTED_R222
         and r222.get("market") == "I"
         and r222.get("period") == 1
         and r222.get("observed_card_count") == 35
         and r222.get("observed_card_cost_effect_parity") == 35
         and r222.get("r192_time_admission") == "HOLD_CATALOG_NOT_SAME_PERIOD_CAPTURE_WINDOW"
         and r222.get("original_r191_market_cap") is None
         and r222.get("actual_spendable_project_cash") is None
         and r222.get("gameplay_gate") == "STOP"
         and r222.get("game_writes") == 0,
         "R222_SOURCE_OBSERVATION_HOLD")
    need(r228["source_sha256"]["r224_receipt"] == digest(r224_path)
         and r228["source_sha256"]["r156_manifest"] == digest(manifest_path),
         "R229_SHA_LINK_TO_ORIGINAL_SOURCES")
    _, state, _ = compile_bundle(Path(manifest_path))
    prov=state.get("provenance",{})
    need(prov.get("market") == "I"
         and prov.get("current_period") == 1
         and prov.get("round") == "Selejtező"
         and r228.get("market") == prov.get("market")
         and r228.get("period") == prov.get("current_period")
         and r228.get("team") == prov.get("team")
         and r222.get("team") == prov.get("team")
         and r224.get("team") == prov.get("team"),
         "SAME_SOURCE_ROUND_TEAM_PERIOD_REQUIRED")
    # Actual original R191 current-state validator is authoritative in this
    # system. An expected HOLD here is a result, not admission.
    try:
        validate_state(state,mode="current",now=now)
    except AdmissionHold as exc:
        r191 = str(exc)
        need(r191 in ("CAP_UNKNOWN_OR_ASSUMED","CURRENT_SOURCE_STALE_OR_FUTURE"),
             "UNEXPECTED_R191_ISSUE_"+r191)
    else:
        # A newly admitted state must not be presented as accepted using old
        # R224/R228 sources; a full new R214 original-source run is required.
        raise ValueError("HOLD_NEW_R191_STATE_REQUIRES_FRESH_R214_INTAKE")
    samples=r224.get("scenarios")
    joined=r228.get("conditional_joint_scenarios")
    need(isinstance(samples,list) and isinstance(joined,list)
         and len(samples)==len(joined)==24
         and r228.get("r148_original_joint_annual_rows")==120,
         "EXACT_R224_R228_SCENARIOS")
    unique={}
    covered=0
    for a,b in zip(samples,joined):
        ids=a.get("initial_project_ids")
        starts=a.get("full_five_year_illustrative_starts")
        count=len(ids) if isinstance(ids,list) else -1
        need(isinstance(starts,list) and len(starts)==5
             and ids==starts[0]
             and starts==b.get("source_project_starts")
             and ids==b.get("first_year_project_ids")
             and a.get("hypothetical_cap")==b.get("hypothetical_cap")
             and a.get("hypothetical_annual_budget_ecu")==b.get("hypothetical_budget")
             and a.get("objective")==b.get("objective")
             and a.get("validated_by_original_r160") is True
             and a.get("financing_authorized") is False
             and a.get("not_an_eligible_game_action") is True
             and b.get("actual_first_year_spend_authorized") is False
             and b.get("future_year_financing_verified") is False
             and type(a.get("first_year_conservative_requirement_ecu")) in (int,float)
             and a["first_year_conservative_requirement_ecu"] ==
                  b.get("first_year_source_R224_conservative_requirement_ecu")
             and a["first_year_conservative_requirement_ecu"]<=a["hypothetical_annual_budget_ecu"]
             and b["first_year_hypothetical_budget_headroom_ecu"]==
                 a["hypothetical_annual_budget_ecu"]-a["first_year_conservative_requirement_ecu"]
             and 0<=count<=3
             and (count==0 or a["first_year_conservative_requirement_ecu"]>0),
             "SOURCE_PAIR_OR_COST_DRIFT_"+str(covered))
        covered+=1
        key=(tuple(ids),a["first_year_conservative_requirement_ecu"])
        if key not in unique:
            unique[key]={"first_year_project_ids":ids,
              "starts_requested":count,
              "source_R224_conservative_card_cost_ecu_NOT_SPENDABLE":
                  a["first_year_conservative_requirement_ecu"],
              "actual_market_cap":None,"actual_residual_cash_ecu":None,
              "actual_eligibility":None,
              "conditional_model_scenario_count":0,
              "scenario_budgets_are_hypothetical":True}
        unique[key]["conditional_model_scenario_count"]+=1
    need(covered==24 and len(unique)==13,"SAMPLED_FIRST_YEAR_VARIANT_COVERAGE")
    groups=sorted(unique.values(),key=lambda v:(
        v["starts_requested"],
        v["source_R224_conservative_card_cost_ecu_NOT_SPENDABLE"],
        v["first_year_project_ids"]))
    receipt={
      "schema":SCHEMA,
      "status":"PASS_SOURCE_GATED_THRESHOLDS_HOLD_ACTUAL_ELIGIBILITY",
      "source_class":"READONLY_PRIVATE_OPERATOR_OBSERVED_NOT_SERVER_ATTESTED",
      "round":"Selejtező","market":"I","team":r228["team"],"period":1,
      "original_R191_current_state_admission":"HOLD_"+r191,
      "original_R192_catalog_admission":r222["r192_time_admission"],
      "original_R214_current_advisory_admission":"HOLD_MISSING_REAL_CAP_SPENDABLE_AND_SAME_HOUR_CATALOG",
      "finance_source_p1_surplus_not_spendable_ecu":
         cash["p1_surplus_excluding_prior_cash_and_both_grants_ecu"],
      "actual_market_project_start_cap":None,
      "actual_spendable_cash_ecu":None,"actual_committed_cash_ecu":None,
      "real_financial_residual_ecu":None,
      "actual_eligible_first_year_actions":None,
      "actual_winning_five_year_plan":None,
      "observed_24_scenarios":covered,
      "distinct_sampled_first_year_variants":len(groups),
      "coverage_limit":"24_SAMPLED_HYPOTHETICAL_PATHS_NOT_ALL_FEASIBLE_ACTIONS",
      "candidate_thresholds":groups,
      "source_sha256":{"R228":digest(r228_path),"R224":digest(r224_path),
                        "R222":digest(r222_path),"R156_manifest":digest(manifest_path)},
      "next_evidence":["ACTUAL_MARKET_I_PROJECT_CAP_SOURCE",
                       "OPERATOR_OBSERVED_SPENDABLE_AND_COMMITTED_YEAR1_ECU",
                       "ONE_HOUR_CURRENT_35_CARD_AND_R156_STATE_CAPTURE",
                       "P1_DECISION_BOUNDS_AND_MODEL_EFFECT_UNITS"],
      "gameplay_gate":"STOP","game_writes":0,
      "merge_authorized":False,"deploy_authorized":False
    }
    dest.mkdir(mode=0o700)
    (dest/"R230_READINESS_PRIVATE.json").write_text(
        json.dumps(receipt,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+"\n",
        encoding="utf8")
    lines=[
        "# EcoSim R230 – elsőéves feltételes lehetőségek, hitelesítési kapukkal",
        "",
        "Forrás: meglévő R224 → R229, eredeti R191, R222. "
        "Az alábbi **13 egyedi elsőéves változat** 24 mintavételezett "
        "feltételes tervből származik; nem teljes döntési tér.",
        "",
        "**Egyetlen változat sem jogosult valós projektindításra.** "
        "A költség csak az eredeti R224-kártyateher; "
        "nem tartalmaz minden városi és szakpolitikai visszahatást.",
        "",
        f"- R191: HOLD_{r191}",
        f"- R192: {r222['r192_time_admission']}",
        "- R214: HOLD – piaci limit, nettó rendelkezésre álló pénz és "
        "azonos órában rögzített kártyakatalógus hiányzik.",
        "- A projektek darabszáma szükséges új indítási igény, "
        "nem bizonyított piaci cap; a játék előző időszaki kivételei külön "
        "vizsgálatot igényelnek.",
        "",
        "| Elsőéves projektek | Új indítások | R224 konzervatív kártyaköltség, ECU | Mintavételezett forgatókönyvek |",
        "|---|---:|---:|---:|",
    ]
    for g in groups:
        ids=", ".join(map(str,g["first_year_project_ids"])) or "nincs"
        lines.append(f"| {ids} | {g['starts_requested']} | "
          f"{g['source_R224_conservative_card_cost_ecu_NOT_SPENDABLE']:,.0f} | "
          f"{g['conditional_model_scenario_count']} |")
    lines.extend(["",
      "Az R229 R145/R148 ötéves projektindexei feltételesek; "
      "nincs hiteles teljes városi eredmény- vagy finanszírozási előrejelzés.",
      "Egy későbbi valós forrásfelvételt az eredeti R191/R192/R214 validátorokon "
      "kell átvezetni. A régi R224 keretből nem keletkezhet végrehajtható döntés.",
      "**NO_GAME_WRITES, NO_MERGE, NO_DEPLOY; GAME_ACTION_GATE=STOP.**",""])
    (dest/"R230_HU.md").write_text("\n".join(lines),encoding="utf8")
    print(json.dumps({"status":receipt["status"],"distinct_first_year":len(groups),
                      "scenario_count":covered,"r191":"HOLD_"+r191,
                      "r192":receipt["original_R192_catalog_admission"],
                      "actual_actions":None,"game_writes":0},
                     ensure_ascii=False))
    return receipt


def main():
    p=argparse.ArgumentParser()
    for k in ("r228","r224","r222","manifest","out-dir"):
        p.add_argument("--"+k,type=Path,required=True)
    args=p.parse_args()
    build(args.r228,args.r224,args.r222,args.manifest,args.out_dir)
if __name__=="__main__":
    main()
