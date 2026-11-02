#!/usr/bin/env python3
"""R206: source-gated, offline search for NEW historical project schedules.

Reuses R162 strategy_5y.search including R160 independent constraint replay.
Not a live EcoSim predictor, finance authorization, or game action.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

SCHEMA = "ECOSIM_R206_REUSED_SEARCH_HISTORICAL_CANDIDATES_V1"
STATUS = "PASS_HISTORICAL_BOUNDED_SEARCH_LIVE_HOLD"
# Every envelope/cap is explicitly hypothetical. NEVER infer from p1 PLAN cash.
SCENARIOS = (
    ("LOW_CARD_ENVELOPE", 50000, 3),
    ("MIDDLE_CARD_ENVELOPE", 90000, 4),
    ("HIGH_CARD_ENVELOPE", 150000, 4),
)

def hold(value, reason):
    if not value:
        raise ValueError("HOLD_" + reason)

def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def path_key(years):
    hold(isinstance(years, (list, tuple)) and len(years) == 5, "EXACT_FIVE_YEAR_PATH")
    result=[]
    seen=set()
    for year in years:
        hold(isinstance(year, (list, tuple)) and all(type(i) is int and 1<=i<=35 for i in year), "INVALID_PROJECT_ID")
        hold(len(year)==len(set(year)) and not (seen & set(year)), "DUPLICATE_PROJECT")
        seen.update(year)
        result.append(tuple(sorted(year)))
    return tuple(result)

def old_keys(r204):
    rows=r204["annual_transition_diagnostics"]["plans"]
    hold(len(rows)==17, "R204_SEVENTEEN_PLANS")
    out=set()
    for row in rows:
        years=row["annual_records"]
        hold(len(years)==5 and [r["year"] for r in years]==[1,2,3,4,5], "R204_ANNUAL_PATH")
        out.add(path_key([r["projects_started_ids"] for r in years]))
    hold(len(out)==17, "R204_DISTINCT_PLANS")
    return out

def validate_sources(profile, state, r204, r205, state_sha):
    hold(profile["schema"]=="ECOSIM_R200_INPUT_PROFILE_V1" and profile["mode"]=="historical-test" and profile["gameplay_gate"]=="STOP", "PROFILE_MODE")
    hold(r204["schema"]=="ECOSIM_UNIFIED_HISTORICAL_DECISION_PACKET_V1" and
         r204["status"]=="PASS_PARTIAL_HISTORICAL_DECISION_SUPPORT_LIVE_HOLD" and
         r204["mode"]=="historical-test" and r204["gameplay_gate"]=="STOP" and r204["game_writes"]==0, "R204_SOURCE_GATE")
    hold(r205["schema"]=="ECOSIM_R205_HISTORICAL_LIBRARY_SOURCE_RECONCILIATION_V1" and
         r205["status"]=="PASS_PREVIOUSLY_UPLOADED_EVIDENCE_RECONCILED_LIVE_HOLD" and
         r205["mode"]=="historical-test" and r205["gameplay_gate"]=="STOP" and r205["game_writes"]==0 and
         r205["live_city_model_validated"] is False and r205["verified_spendable_cash"] is False and
         r205["game_actions_permitted"] is False, "R205_SOURCE_GATE")
    hold(len(r205["r202_finance_channel_crosschecks"])==10 and
         sum(r["rows"] for r in r205["source_files"].values())==100, "R205_COVERAGE")
    hold(state_sha==r204["source_hashes"]["r200_profile_source_state"],"STATE_SOURCE_SHA")
    p=profile["identity"]
    origin=state["provenance"]
    hold(origin["team"]==p["team"] and origin["market"]==p["market"] and origin["current_period"]==p["period"]==1, "HISTORICAL_TEAM_PERIOD")
    hold(origin["source"].endswith("_P1_HISTORICAL_NOT_LIVE"), "STATE_NOT_LIVE")
    hold(state["team"].get("initially_active_project_ids") is not None and
         len(state["team"]["initially_active_project_ids"])==6 and
         len(state["team"]["baseline_smartcity_factors"])==29, "STATE_COVERAGE")
    hold(r204["decision"]["live"]=="HOLD" and r204["decision"]["current_city_optimum"]=="NOT_PROVEN", "LIVE_OPTIMUM_OVERCLAIM")
    return old_keys(r204)

def generate(state, historical, search_fn, *, beam_width=3, shortlist=10):
    hold(callable(search_fn), "EXISTING_SEARCH_REQUIRED")
    hold(type(beam_width) is int and 1<=beam_width<=10 and type(shortlist) is int and 1<=shortlist<=40, "SEARCH_LIMITS")
    candidates=[]
    scenario_results=[]
    current={}
    for name,envelope,cap in SCENARIOS:
        result=search_fn(state, start_year=1, budget_override=[envelope]*5,
                         cap_override=cap, beam_width=beam_width, shortlist=shortlist,
                         allow_same_year=True, objective="nominal")
        hold(result["schema"]=="ECOSIM_R148_SOURCE_BOUNDED_OFFLINE_STRATEGY_V1" and
             result["final_gameplay_decision"]=="STOP" and
             result["game_write_actions"]==0 and result["network_actions"]==0 and
             result["actual_five_year_score_forecast_validated"] is False, "ORIGINAL_R162_SEARCH_GATE")
        assumptions=result["assumptions"]
        hold(assumptions["annual_project_limit"]==cap and
             assumptions["official_cash_envelopes_or_illustrative_scenario"]==[envelope]*5 and
             assumptions["budget_source"]=="EXPLICIT_ILLUSTRATIVE_CLI_SCENARIO_NOT_SPENDABLE_CASH" and
             assumptions["annual_limit_source"]=="EXPLICIT_ILLUSTRATIVE_CLI_ASSUMPTION", "NOT_HYPOTHETICAL")
        for ordinal,p in enumerate(result["top_plans"],1):
            years=p["start_by_year"]
            hold(len(years)==5 and [v["year"] for v in years]==[1,2,3,4,5], "NEW_YEAR_PATH")
            path=path_key([r["start_project_ids"] for r in years])
            cost=[r["conservative_card_cash_requirement_ecu"] for r in years]
            hold(all(type(c) in (int,float) and math.isfinite(c) and 0<=c<=envelope+1e-6 for c in cost),"NEW_CARD_COST")
            hold(abs(sum(cost)-p["five_year_conservative_card_cost_ecu"])<1e-4, "NEW_CARD_SUM")
            audit=p["r160_independent_constraint_replay"]
            hold(audit["schema"]=="ECOSIM_R160_INDEPENDENT_PLAN_AUDIT_V1" and
                 audit["gameplay_gate"]=="STOP" and not audit["hard_rule_violations"] and
                 audit["actual_game_eligibility"] is None and audit["actual_funding_approval"] is None, "R160_AUDIT")
            hold(len(audit["years"])==5 and all(
                abs(y["independently_replayed_conservative_cash_need_ecu"]-c)<1e-5
                for y,c in zip(audit["years"],cost)), "R160_ANNUAL_REPLAY")
            identity="/".join(",".join(map(str,y)) or "-" for y in path)
            historical_match=path in historical
            if path not in current:
                entry={"plan_id":"SYN-"+hashlib.sha256(identity.encode()).hexdigest()[:12],
                       "starts_by_year":[list(x) for x in path],
                       "card_need_ecu_by_year":cost,
                       "five_year_card_need_ecu":sum(cost),
                       "conditional_terminal_proxy_delta":p["terminal_mapped_proxy_delta"],
                       "illustrative_half_effect_delta":p["illustrative_half_effect_sensitivity"][-1]["mapped_proxy_delta"],
                       "illustrative_85pct_retention_delta":p["illustrative_85pct_yearly_retention_sensitivity"][-1]["mapped_proxy_delta"],
                       "unmapped_or_indirect_effects":len(p["excluded_unknown_effects"]),
                       "conditional_eligibility_items":len(audit["conditional_eligibility_items"]),
                       "source_historical_plan_match":historical_match,
                       "hypothetical_scenarios":[],
                       "finance_approved":False,"actual_game_score":None,
                       "gameplay_gate":"STOP"}
                candidates.append(entry)
                current[path]=entry
            current[path]["hypothetical_scenarios"].append({"scenario":name,"ordinal":ordinal,"annual_project_cap_assumed":cap,"annual_card_envelope_assumed_ecu":envelope})
        scenario_results.append({"scenario":name,"annual_project_cap_assumed":cap,
                                "annual_card_envelope_assumed_ecu":envelope,
                                "generated_count":len(result["top_plans"]),
                                "search_stats":result["search_stats"],
                                "hypothetical_not_spendable_cash":True})
    hold(len(candidates)>0,"EMPTY_SEARCH")
    candidates.sort(key=lambda p:(-p["conditional_terminal_proxy_delta"],p["five_year_card_need_ecu"],p["plan_id"]))
    return {"schema":SCHEMA,"status":STATUS,"mode":"historical-test",
            "search_algorithm":"REUSED_R162_BOUNDED_BEAM_AND_R160_INDEPENDENT_AUDIT",
            "hypothetical_scenarios":scenario_results,
            "unique_candidates":len(candidates),
            "distinct_new_vs_r204":sum(not p["source_historical_plan_match"] for p in candidates),
            "candidates":candidates,"game_writes":0,"gameplay_gate":"STOP",
            "verified_city_transition":False,"verified_spendable_cash":False,
            "gameplay_recommendation":"HOLD"}

def report(result):
    lines=["# EcoSim – R206 új ötéves projektjelöltek (történeti tesztadatok)","",
           "**Nem teljes városszimuláció; LIVE HOLD; GAME_ACTION_GATE=STOP.**","",
           "A keresés az R162 beam search-t és az R160 független projektellenőrzést használja újra.",
           f"Egyedi jelöltek: {result['unique_candidates']}; az R204 17 tervétől eltérő: {result['distinct_new_vs_r204']}.",
           "","A 50k / 90k / 150k éves kártyaköltség-keretek hipotetikusak, nem elkölthető városi pénz.",
           "A 3/4/4 projektlimit szintén szcenárió; a valós market cap nem igazolt.","",
           "| Jelölt | Ötéves projektindítás | Öt év kártyaköltsége (feltételes ECU) | Közvetlen indexproxy Δ | Nem modellezett hatások | R160 feltételes tételek |",
           "|---|---|---:|---:|---:|---:|"]
    for p in result["candidates"][:20]:
        starts="; ".join(f"{y+1}:"+(",".join(map(str,ids)) or "—") for y,ids in enumerate(p["starts_by_year"]))
        lines.append(f"| {p['plan_id']} | {starts} | {p['five_year_card_need_ecu']:,.0f} | {p['conditional_terminal_proxy_delta']:+.4f} | {p['unmapped_or_indirect_effects']} | {p['conditional_eligibility_items']} |")
    lines.extend(["","## Bizonytalanságok","",
                  "A szintetikus adó/díj/üzemeltetési modellek nincsenek server-oldalról kalibrálva.",
                  "A projektekre vetített részindex nem hivatalos EcoSim végső pontszám.",
                  "A hiányzó közvetett, migrációs, finanszírozási és intézményi hatások nem számítanak nullának.",
                  "A jelölttervek nem engedélyeznek projektindítást vagy módosítást."])
    return "\n".join(lines)+"\n"

def main():
    ap=argparse.ArgumentParser()
    for name in ("profile","r204","r205"):
        ap.add_argument("--"+name,required=True,type=Path)
    ap.add_argument("--out-dir",required=True,type=Path)
    ap.add_argument("--beam",type=int,default=3)
    ap.add_argument("--shortlist",type=int,default=10)
    args=ap.parse_args()
    repo=Path(__file__).resolve().parents[2]
    sys.path[:0]=[str(repo/"team-handoff/r200-historical-plugplay/tools"),
                  str(repo/"ECOSIM_R162_INTEGRITY_REVIEW_RC/tools")]
    from corpus_r200 import resolve, parse_json, inspect
    from strategy_5y import search
    profile=parse_json(args.profile.read_bytes())
    audit=inspect(profile,args.profile)
    hold(audit["mode"]=="historical-test" and audit["gameplay_gate"]=="STOP","R200_AUDIT")
    state_raw=resolve("baseline_state",profile,args.profile)
    state=parse_json(state_raw)
    r204=json.loads(args.r204.read_text())
    r205=json.loads(args.r205.read_text())
    historical=validate_sources(profile,state,r204,r205,digest(state_raw))
    result=generate(state,historical,search,beam_width=args.beam,shortlist=args.shortlist)
    result["source_sha256"]={"r200_state":digest(state_raw),"r204_packet":digest(args.r204.read_bytes()),
                              "r205_reconciliation":digest(args.r205.read_bytes())}
    hold(not args.out_dir.exists(),"OUTPUT_EXISTS")
    args.out_dir.mkdir(parents=True,mode=0o700)
    (args.out_dir/"R206.json").write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n")
    (args.out_dir/"R206_HU.md").write_text(report(result))
    print(json.dumps({"status":result["status"],"candidates":result["unique_candidates"],
                      "new":result["distinct_new_vs_r204"],"game_writes":0,"out":str(args.out_dir)}))
if __name__=="__main__":main()
