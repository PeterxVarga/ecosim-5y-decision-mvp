#!/usr/bin/env python3
"""Historical EcoSim decision comparison. No game access, no live claims."""
import argparse
import csv
import io
import json
import math
from pathlib import Path

SCHEMA="ECOSIM_R204_HISTORICAL_DECISION_COMPARISON_V1"
POLICIES=("business_tax_increased_synthetic","business_tax_reduced_synthetic","unchanged_synthetic")
INTENSITIES=(0.5,1.0,1.5)

def need(ok,reason):
    if not ok:raise ValueError("HOLD_"+reason)
def finite(v):
    return type(v) in (int,float) and math.isfinite(v)
def compare(p):
    need(p["schema"]=="ECOSIM_UNIFIED_HISTORICAL_DECISION_PACKET_V1","PACKET_SCHEMA")
    need(p["status"]=="PASS_PARTIAL_HISTORICAL_DECISION_SUPPORT_LIVE_HOLD","HISTORICAL_ONLY")
    need(p["mode"]=="historical-test" and p["gameplay_gate"]=="STOP" and p["game_writes"]==0,"NO_GAME_ACTIONS")
    need(p["decision"]["live"]=="HOLD" and p["decision"]["current_city_optimum"]=="NOT_PROVEN","NO_OPTIMUM_CLAIM")
    r=p["scenario_robustness"]
    a=p["annual_transition_diagnostics"]
    need(r["candidate_count"]==p["candidate_count"]==a["plan_count"]==17,"CANDIDATE_COUNTS")
    need(r["scenario_count"]==p["scenario_count"]==51,"SCENARIO_COUNTS")
    need(a["annual_project_only_ledgers"]==85 and a["direct_factor_sensitivity_evaluations"]==255,"ANNUAL_REPLAY_COUNTS")
    need(a["observed_fact_to_fact_transition_samples"]==0 and not a["simulator_outcome_validation"],"NOT_ACTUAL_TRANSITION")
    rs={x["candidate_id"]:x for x in r["candidate_summaries"]}
    ann={x["id"]:x for x in a["plans"]}
    need(len(rs)==len(ann)==17 and set(rs)==set(ann),"IDENTICAL_CANDIDATES")
    need(not r["selected_or_server_approved"] and not r["citywide_optimum_certified"],"NO_SERVER_APPROVAL")
    results=[]
    for name in sorted(rs):
        x=rs[name]
        y=ann[name]
        yrs=y["annual_records"]
        need(len(yrs)==5 and [v["year"] for v in yrs]==[1,2,3,4,5],"FIVE_YEARS")
        starts=[v["projects_started_ids"] for v in yrs]
        need(starts[0]==x["first_year_project_ids"],"FIRST_YEAR_IDENTITY")
        costs=[v["conservative_project_card_need_ecu"] for v in yrs]
        need(all(finite(v) and v>=0 for v in costs),"BAD_CARD_COST")
        need(abs(sum(costs)-x["five_year_project_cost_ecu"])<1e-5 and abs(max(costs)-x["max_annual_project_card_need_ecu"])<1e-5,"ANNUAL_COST_IDENTITY")
        needs=[]
        for yr in yrs:
            need(yr["actual_server_index"] is None and yr["verified_financing"] is False,"NO_LIVE_YEAR")
            cases=yr["conditional_index_stress"]
            need(len(cases)==3 and [v["intensity"] for v in cases]==list(INTENSITIES),"SENSITIVITY_CASES")
            need(all(finite(v["mapped_index_conditional"]) and v["unmodeled_city_drift_has_no_bound"] is True for v in cases),"UNBOUNDED_CITY_EFFECT")
            needs.append(cases[1]["unmapped_or_indirect_effect_count"])
        need(needs[-1]==y["final_year_unmapped_effects"],"UNMAPPED_DRIFT")
        need(set(x["policy_paths"])==set(POLICIES),"POLICY_PATH_COVERAGE")
        for rec in x["policy_paths"].values():
            need(all(finite(rec[k]) for k in ("index_proxy_delta","partial_net_ecu","zero_opening_cash_stress_ecu")),"POLICY_FINANCE")
        need(min(rec["partial_net_ecu"] for rec in x["policy_paths"].values())>=x["worst_partial_net_ecu"]-1e-5,"NET_LOWER_BOUND_DRIFT")
        need(abs(min(rec["partial_net_ecu"] for rec in x["policy_paths"].values())-x["worst_partial_net_ecu"])<1e-5,"NET_WORST_CASE_IDENTITY")
        fit=x["fits_illustrative_card_cap"]
        need(set(fit)=={"50000","90000","100000","150000"},"CAP_COVERAGE")
        need(all(type(fit[k]) is bool and fit[k]==(max(costs)<=int(k)) for k in fit),"CAP_FILTER_IDENTITY")
        results.append({
            "id":name,"first_year_projects":starts[0],"annual_project_card_need_ecu":costs,
            "five_year_project_card_need_ecu":sum(costs),
            "peak_annual_project_card_need_ecu":max(costs),
            "conditional_direct_index_year5_by_intensity":[yr["conditional_index_stress"][i]["mapped_index_conditional"] for i in range(3) for yr in yrs if yr["year"]==5],
            "unmapped_or_indirect_effect_count_year5":needs[-1],
            "worst_partial_net_ecu":x["worst_partial_net_ecu"],
            "worst_partial_index_delta":x["worst_partial_index_delta"],
            "policy_paths":x["policy_paths"],"illustrative_cap_fit":fit,
            "sample_robust_front_member":name in r["candidate_robust_front_sample_ids"],
            "financing_approved":False,"actual_server_score":None
        })
    orders=[]
    for i,scenario in enumerate(a["rankings_by_assumed_direct_effect_intensity"]):
        need(scenario["intensity"]==INTENSITIES[i],"RANKING_INTENSITY")
        actual=sorted(results,key=lambda z:(-z["conditional_direct_index_year5_by_intensity"][i],z["id"]))
        need([x["id"] for x in actual]==scenario["all_source_partial_order"],"RANKING_REPLAY")
        orders.append({"intensity":INTENSITIES[i],"conditional_top_five":[x["id"] for x in actual[:5]]})
    return {
        "schema":SCHEMA,"mode":"historical-test","status":"PASS_17_EXACT_RECONCILED_PLANS_HOLD_LIVE",
        "gameplay_gate":"STOP","game_writes":0,
        "candidates":results,"partial_top_five_by_intensity":orders,
        "sample_robust_front_ids":sorted(r["candidate_robust_front_sample_ids"]),
        "illustrative_caps":r["illustrative_cap_filters"],
        "provenance":p["report_hashes"],"source_hashes":p["source_hashes"],
        "warnings":["No server outcome or global optimum","CAP filters are hypothetical, not spendable cash",
                    "Partial project net is not actual cash balance","Unmapped city drift has no identified bounds",
                    "p1 PLAN is not a second closed FACT year"],
        "current_admission":"HOLD","recommended_for_gameplay":False
    }

def display(result):
    def n(v):return f"{v:,.0f}".replace(","," ")
    lines=["# EcoSim – összehasonlítható ötéves döntési jelentés",
        "","**TÖRTÉNETI RÉSZMODELL PASS; LIVE HOLD; JÁTÉKBELI DÖNTÉS NINCS JÓVÁHAGYVA.**",
        "","17 egyező ötéves ütemezés, 51 feltételes politika/finanszírozás eset,",
        "85 éves résznapló és 255 feltételes indexérzékenységi vizsgálat.",
        "","A pontszámok közvetlen projekthatás-modellek, nem valódi EcoSim szerverértékek.",
        "A pénzügyi eredmények szintetikusak; az ECU-egység és a költhető keret nem igazolt.",
        "","## Feltételes rangsorok (kizárólag közvetlen projekthatás)",
       ]
    for item in result["partial_top_five_by_intensity"]:
        lines.append(f"- {item['intensity']}× feltételezett közvetlen hatás: "+", ".join(item["conditional_top_five"]))
    lines.extend(["","## 17 projektterv – ellenőrzött azonos ütemezések",
        "","| Terv | Éves projektköltség (5 év, feltételes ECU) | 5. év közvetlen indexe (1×) | Legrosszabb résznettó (ECU) | Nem modellezett hatások |",
        "|---|---|---:|---:|---:|"])
    for x in result["candidates"]:
        annual="/".join(n(v) for v in x["annual_project_card_need_ecu"])
        lines.append(f"| {x['id']} | {annual} | {x['conditional_direct_index_year5_by_intensity'][1]:.4f} | {n(x['worst_partial_net_ecu'])} | {x['unmapped_or_indirect_effect_count_year5']} |")
    lines.extend(["","## Helyes értelmezés",
        "- Az évenkénti projektköltségek 17/17 tervnél egyeznek a pénzügyi részmodelllel.",
        "- A 50k/90k/100k/150k plafonok **hipotetikus vizsgálati korlátok**, nem jóváhagyott keretek.",
        "- A negatív résznettó nem egyenlő a valódi város pénzügyi egyenlegével.",
        "- Az ismeretlen közvetett hatásokat tilos nullának tekinteni.",
        "- Nem bizonyítottak az évközi bevételi ütemezések, teljes városdinamika, hitel/támogatás és a valódi pontozó.",
        "- Az eredmény nem engedélyez semmilyen EcoSim-módosítást: GAME_ACTION_GATE=STOP.",
        ""])
    return "\n".join(lines)

def csv_table(result):
    out=io.StringIO()
    fields=["id","year1","year2","year3","year4","year5","total","peak","direct_index_0_5","direct_index_1","direct_index_1_5","worst_partial_net","unmapped_effects","sample_pareto"]
    writer=csv.DictWriter(out,fieldnames=fields,lineterminator="\n");writer.writeheader()
    for x in result["candidates"]:
        row={"id":x["id"],"total":x["five_year_project_card_need_ecu"],"peak":x["peak_annual_project_card_need_ecu"],
             "direct_index_0_5":x["conditional_direct_index_year5_by_intensity"][0],
             "direct_index_1":x["conditional_direct_index_year5_by_intensity"][1],
             "direct_index_1_5":x["conditional_direct_index_year5_by_intensity"][2],
             "worst_partial_net":x["worst_partial_net_ecu"],"unmapped_effects":x["unmapped_or_indirect_effect_count_year5"],
             "sample_pareto":x["sample_robust_front_member"]}
        row.update({f"year{i+1}":cost for i,cost in enumerate(x["annual_project_card_need_ecu"])})
        writer.writerow(row)
    return out.getvalue()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--packet",type=Path,required=True)
    ap.add_argument("--out-dir",type=Path,required=True)
    args=ap.parse_args()
    packet=json.loads(args.packet.read_text())
    result=compare(packet)
    out=args.out_dir
    if out.exists():
        need(out.is_dir() and not any((out/n).exists() for n in ("DECISION_COMPARISON.json","DECISION_COMPARISON.csv","DECISION_COMPARISON_HU.md")),"EXISTING_RESULTS")
    else:out.mkdir(parents=True,mode=0o700)
    (out/"DECISION_COMPARISON.json").write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    (out/"DECISION_COMPARISON.csv").write_text(csv_table(result))
    (out/"DECISION_COMPARISON_HU.md").write_text(display(result))
    print(json.dumps({"status":result["status"],"candidates":len(result["candidates"]),"game_writes":0}))
if __name__=="__main__":main()
