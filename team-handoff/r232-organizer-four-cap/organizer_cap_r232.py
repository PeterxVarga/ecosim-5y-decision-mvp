#!/usr/bin/env python3
"""2026 organizer-announced absolute 4/year, distinct from unverified game-server config.

Reuse R162 search, R160 independent audit and R145/R148 policy UNKNOWN replay.
All real test-round source receipts and outputs stay private on operator host.
No game reads/writes, no privilege elevations, no fake R191 admission.
"""
from __future__ import annotations
import argparse
import json
import math
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"ECOSIM_R162_INTEGRITY_REVIEW_RC/tools"),
             str(ROOT/"team-handoff/r221-conditional-live-scenario"),
             str(ROOT/"team-handoff/r228-excel-city-policy-join")]
from json_integrity_r162 import read_json
from observation_bundle_r152 import compile_bundle
from strategy_5y import search
from conditional_r221 import _choose
from source_join_r228 import digest
from policy_tracks import load_tracks,replay_policy_joint
from portfolio_5y import project_index
from r142_proxy_reference import WEIGHTS

SCHEMA="ECOSIM_R232_ORGANIZER_FOUR_ABSOLUTE_PER_YEAR_BOUNDED_SCENARIOS_V1"
VIDEO_ID="3GNCkvECOdk"
VIDEO_SECONDS=21*60+8
CAP=4
BUDGETS=(0,168621,337243,674486)
OBJECTIVES=("nominal","scenario_min")

def need(v,why):
    if not v:raise ValueError("HOLD_"+why)

def compute(manifest,r224,r228,r231,track_path,dest):
    dest=Path(dest).resolve()
    need(dest.parent.is_dir() and not dest.parent.is_symlink()
         and not dest.exists() and not dest.is_relative_to(ROOT.resolve()),
         "NEW_PRIVATE_DIRECTORY")
    for p in (manifest,r224,r228,r231,track_path):
        p=Path(p)
        need(p.is_file() and not p.is_symlink(),"REGULAR_PRIOR_SOURCE_ONLY")
    a,b,c=(read_json(p) for p in (r224,r228,r231))
    need(a["source_sha256"]["current_r156_manifest"]==digest(manifest)
         and b["source_sha256"]["r224_receipt"]==digest(r224)
         and b["source_sha256"]["r156_manifest"]==digest(manifest)
         and c["source_sha256"]["R228"]==digest(r228)
         and c["source_sha256"]["R224"]==digest(r224)
         and c["source_sha256"]["R156_manifest"]==digest(manifest),
         "ORIGINAL_R224_R229_R231_SHA_CHAIN")
    need(a.get("scenario_count")==24 and a.get("hypothetical_market_project_caps")==[1,2,3]
         and a.get("gameplay_gate")=="STOP" and a.get("game_writes")==0
         and a.get("current_R191_real_cap") is None
         and a.get("current_R191_actual_spendable_cash") is None
         and a.get("current_R192_full_admission") is False
         and a.get("current_R214_live_advice_authorized") is False
         and a["cashflow"]["scenario_funds_are_approved"] is False
         and a["cashflow"]["hypothetical_annual_budget_ecu"]==list(BUDGETS),
         "R224_SCENARIO_ONLY_FINANCE")
    need(b.get("observed_total_controls")==23
         and b.get("r148_original_joint_scenario_count")==24
         and b.get("gameplay_gate")=="STOP"
         and b.get("game_writes")==0
         and b.get("actual_five_year_winning_plan") is None,
         "R228_UNCHANGED_POLICY_UNKNOWN")
    need(c.get("original_R191_current_state_admission")=="HOLD_CAP_UNKNOWN_OR_ASSUMED"
         and c.get("original_R192_catalog_admission")==
             "HOLD_CATALOG_NOT_SAME_PERIOD_CAPTURE_WINDOW"
         and c.get("source_backed_financing_semantics_R231",{}).
              get("game_can_auto_borrow_to_balance_shortfall") is True
         and c.get("gameplay_gate")=="STOP" and c.get("game_writes")==0,
         "R231_ORIGINAL_LIVE_ADMISSION_STILL_HOLD")
    _,state,_=compile_bundle(manifest)
    need(state["provenance"]["round"]=="Selejtező"
         and state["provenance"]["market"]=="I"
         and state["provenance"]["current_period"]==1
         and state["team"]["initially_active_project_ids"]==[14,22,23,24,34,35]
         and state["team"]["project1_active_previous_period"] is False
         and state["market"]["maxProjectPerTurn"] is None
         and a["team"]==b["team"]==c["team"]==state["provenance"]["team"],
         "CURRENT_SELEJTEZO_I_SOURCE_AND_NO_FORGED_CAP")
    tracks=load_tracks(track_path)
    need(len(tracks)==1 and len(tracks[0]["actions"])==23*5,
         "ORIGINAL_23_UNKNOWN_POLICY_TRACK")
    track=tracks[0]
    weights={k:v[0] for k,v in WEIGHTS.items()}
    idx=project_index()
    out=[]
    for annual_budget in BUDGETS:
        for objective in OBJECTIVES:
            model=search(state,start_year=1,cap_override=CAP,
                        announced_absolute_cap=CAP,
                        budget_override=[annual_budget]*5,beam_width=8,
                        shortlist=25,allow_same_year=False,objective=objective)
            need(model["assumptions"]["organizer_announced_absolute_limit_not_server_verified"]==CAP,
                 "R162_ABSOLUTE_CAP_NOT_APPLIED")
            chosen=_choose(model,CAP,annual_budget,objective)
            starts=chosen["full_five_year_illustrative_starts"]
            need(len(starts)==5 and
                 all(isinstance(y,list) and len(y)<=CAP for y in starts) and
                 sum(len(y) for y in starts)<=CAP*5 and
                 chosen["validated_by_original_r160"] and
                 chosen["financing_authorized"] is False and
                 chosen["gameplay_gate"]=="STOP",
                 "ANNUAL_ORGANIZER_FOUR_OR_R160_VIOLATION")
            plan={"start_by_year":[{"start_project_ids":y} for y in starts]}
            years=replay_policy_joint(plan,track,state["team"]["baseline_smartcity_factors"],
                                      idx,weights,1)
            need(len(years)==5 and all(
                 v["actual_index_forecast"] is None and
                 v["actual_cashflow_forecast"] is None and
                 len(v["policy_unmapped_actions"])==23 and
                 v["policy_cash_delta_assumption"]["complete"] is False
                 for v in years),"R148_JOINT_POLICY_UNKNOWN_PROPAGATION")
            out.append({
                "annual_project_cap_organizer_announced":CAP,
                "hypothetical_annual_cash_budget_ecu_NOT_SPENDABLE":annual_budget,
                "objective":objective,
                "p1_project_ids":starts[0],
                "p1_source_card_cash_requirement_ecu":chosen["first_year_conservative_requirement_ecu"],
                "yearly_project_starts":starts,
                "annual_start_counts":[len(y) for y in starts],
                "total_five_year_project_starts":sum(len(y) for y in starts),
                "conditional_year5_project_only_mapped_index_NOT_CITY_FORECAST":
                     round(years[-1]["joint_mapped_factor_counterfactual_index"],6),
                "policy_unknown_cash_each_year":[
                    len(v["policy_cash_delta_assumption"]["undisclosed_policy_cash_decisions"])
                    for v in years],
                "policy_unknown_factor_each_year":[
                    len(v["policy_unmapped_actions"]) for v in years],
                "project_1_client_extra_slot_not_used":True,
                "source_rule_eligibility_independently_server_verified":False,
                "actual_game_winning_strategy":None,
                "gameplay_gate":"STOP",
            })
    need(len(out)==8 and all(x["total_five_year_project_starts"]<=20 for x in out),
         "COMPLETE_EIGHT_ANNOUNCED_CAP_FIVE_YEAR_CASES")
    receipt={
        "schema":SCHEMA,
        "status":"PASS_4_PER_YEAR_8_SCENARIOS_40_YEAR_ROWS_NO_SERVER_CAP_ATTESTATION",
        "video_evidence":{
            "video_url":"https://www.youtube.com/watch?v="+VIDEO_ID,
            "video_id":VIDEO_ID,
            "spoken_at_seconds":VIDEO_SECONDS,
            "end_seconds":21*60+25,
            "speaker_role":"ECOSIM_DIRECTOR_EXPLAINS_2026_X_CHALLENGE",
            "evidence_kind":"OFFICIAL_ORGANIZER_PUBLIC_VIDEO_CAPTIONS_NOT_SERVER_CONFIG",
            "base_max_new_projects_per_virtual_year":CAP,
            "five_year_base_max_new_projects":20,
            "bonus_project1_client_code_possibility_unresolved":True,
            "do_not_promote_to_current_R191_live_cap":True,
        },
        "team":a["team"],"market":"I","period":1,
        "original_R191_current_admission":"HOLD_CAP_UNKNOWN_OR_ASSUMED",
        "original_R192_catalog_time_admission":"HOLD_CATALOG_NOT_SAME_PERIOD_CAPTURE_WINDOW",
        "original_R214_admission":"HOLD_CURRENT_OPERATOR_BUDGETS_AND_CATALOG",
        "source_sha256":{"R156_manifest":digest(manifest),"R224":digest(r224),
                         "R228":digest(r228),"R231":digest(r231),
                         "R145_policy_track":digest(track_path)},
        "current_game_server_project_cap":None,
        "actual_spendable_ecu":None,
        "actual_permitted_game_decision":None,
        "official_five_year_score":None,
        "scenarios":out,"scenario_count":len(out),
        "sampled_not_global_optimum":True,
        "gameplay_gate":"STOP","game_writes":0,
    }
    dest.mkdir(mode=0o700)
    (dest/"R232_RECEIPT.json").write_text(json.dumps(
        receipt,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf8")
    lines=["# R232 – X-Challenge 2026 szervezői projektlimit: legfeljebb 4/év","",
       "2026-os EcoSim szervezői tájékoztató: "+receipt["video_evidence"]["video_url"]+
         "&t=1268s (21:08–21:25). Alaplimit: 4 új projekt / virtuális év, az öt éves alapkeret 20.",
       "A kliens projekt-1 kivételszabályának éles szerveres alkalmazása nem bizonyított.",
       "R191/R192/R214 továbbra is HOLD. Az alábbi keresés R160-ellenőrzött, de feltételes.",
       "A 0/168 621/337 243/674 486 ECU keretek hipotetikusak, nem elkölthető keretek.",
       "A 23 szakpolitikai döntés hatása minden évben UNKNOWN; így a mutató NEM a teljes város előrejelzése.","",
       "| Hipotetikus évi ECU | Cél | Elsőéves projektek | P1 kártyateher ECU | Indítások évenként | Összes indítás | Ötödik év projektindex (feltételes) |",
       "|---:|---|---|---:|---|---:|---:|"]
    for row in out:
        lines.append(f"| {row['hypothetical_annual_cash_budget_ecu_NOT_SPENDABLE']:,.0f} | "+
         f"{row['objective']} | "+(", ".join(map(str,row['p1_project_ids'])) or "nincs")+" | "+
         f"{row['p1_source_card_cash_requirement_ecu']:,.0f} | "+
         "/".join(map(str,row['annual_start_counts']))+" | "+
         str(row['total_five_year_project_starts'])+" | "+
         f"{row['conditional_year5_project_only_mapped_index_NOT_CITY_FORECAST']:.6f} |")
    lines+=["","Az ötödik év végi versenyhelyezés számít, de a fenti index nem hivatalos pontszám.",
       "GAME_ACTION_GATE=STOP; 0 játékbeli módosítás; NO_MERGE; NO_DEPLOY."]
    (dest/"R232_HU.md").write_text("\n".join(lines)+"\n",encoding="utf8")
    print(json.dumps({"status":receipt["status"],"scenario_count":len(out),
        "max_starts":max(x["total_five_year_project_starts"] for x in out),
        "max_per_year":max(max(x["annual_start_counts"]) for x in out),
        "gameplay_gate":"STOP","private_out":str(dest)},ensure_ascii=False))
    return receipt

def main():
    p=argparse.ArgumentParser()
    for k in ("manifest","r224","r228","r231","track","out-dir"):
        p.add_argument("--"+k,type=Path,required=True)
    a=p.parse_args()
    compute(a.manifest,a.r224,a.r228,a.r231,a.track,a.out_dir)

if __name__=="__main__":main()
