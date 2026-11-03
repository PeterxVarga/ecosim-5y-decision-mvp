#!/usr/bin/env python3
"""Compare the exact eight R232 4/year paths under real P0 facts vs P1 preview.

Reuses R145/R148 policy replay and R162 factor index; no new optimizer or
hypothetical approved policy. Model deltas are not actual city forecasts.
"""
from __future__ import annotations
import argparse,csv,io,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"team-handoff/r228-excel-city-policy-join"),
             str(ROOT/"ECOSIM_R162_INTEGRITY_REVIEW_RC/tools")]
from source_join_r228 import parse_excel,digest,need
from json_integrity_r162 import read_json
from observation_bundle_r152 import compile_bundle
from r142_proxy_reference import COEFF, WEIGHTS
from city_bridge import computed_index_from_factors
from policy_tracks import load_tracks,replay_policy_joint
from portfolio_5y import project_index

SCHEMA="ECOSIM_R233_P0_FACT_VS_P1_PLAN_FOUR_CAP_SOURCE_COMPARISON_V1"

def read_plan_csv(p):
    with Path(p).open(encoding="utf8",newline="") as f:
        lines=list(csv.DictReader(f))
    need(len(lines)==30 and all(set(v)=={"metric","value"} for v in lines),
         "P1_SOURCE_FACTOR_CSV_SHAPE")
    keys=[v["metric"] for v in lines]
    need(len(set(keys))==30 and set(keys)==set(COEFF)|{"Okosváros index"},
         "P1_EXACT_29_AND_INDEX")
    data={v["metric"]:float(v["value"]) for v in lines}
    need(all(math.isfinite(v) and 0<=v<=100 for v in data.values()),
         "P1_INVALID_FACTOR_VALUE")
    return {k:v for k,v in data.items() if k!="Okosváros index"},data["Okosváros index"]

def compute(xlsx,p1_csv,summary_txt,r217_path,manifest,r232_path,track_path,dest):
    dest=Path(dest).resolve()
    need(dest.parent.is_dir() and not dest.parent.is_symlink()
         and not dest.exists() and not dest.is_relative_to(ROOT.resolve()),
         "NEW_PRIVATE_OUTPUT_REQUIRED")
    for path in (xlsx,p1_csv,summary_txt,r217_path,manifest,r232_path,track_path):
        need(Path(path).is_file() and not Path(path).is_symlink(),
             "PRIVATE_SOURCE_REQUIRED")
    x=parse_excel(xlsx)
    source=read_json(r217_path)
    r232=read_json(r232_path)
    need(source.get("schema")=="ECOSIM_R217_CURRENT_BROWSER_VISIBLE_PARTIAL_ADMISSION_V1"
         and source.get("round")=="Selejtező" and source.get("market")=="I"
         and source.get("period")==1 and source.get("team")=="Jutalom a nap végén"
         and source.get("newly_selected_ids")==[]
         and source.get("factor_count")==29
         and source.get("r191_current_qualification")=="HOLD_CAP_UNKNOWN_OR_ASSUMED"
         and source.get("index_p0")==51.96 and source.get("index_p1_plan")==52.48
         and source.get("r156_immutable_manifest_sha256")==digest(manifest)
         and source.get("source_text_sha256",{}).get("summary")==digest(summary_txt)
         and source.get("game_writes")==0
         and source.get("gameplay_gate")=="STOP",
         "R217_SOURCE_LINK_P1_PLAN_NOT_FACT")
    need(r232.get("schema")==
         "ECOSIM_R232_ORGANIZER_FOUR_ABSOLUTE_PER_YEAR_BOUNDED_SCENARIOS_V1"
         and r232.get("scenario_count")==8
         and r232.get("video_evidence",{}).get("base_max_new_projects_per_virtual_year")==4
         and r232.get("source_sha256",{}).get("R156_manifest")==digest(manifest)
         and r232.get("current_game_server_project_cap") is None
         and r232.get("actual_permitted_game_decision") is None
         and r232.get("game_writes")==0 and r232.get("gameplay_gate")=="STOP",
         "R232_OPTIONAL_4_CAP_AND_GAME_STOP")
    _,state,_=compile_bundle(manifest)
    need(state["provenance"]["team"]==source["team"]
         and state["provenance"]["market"]==source["market"]
         and state["provenance"]["current_period"]==source["period"]
         and state["market"]["maxProjectPerTurn"] is None
         and state["team"]["already_selected_new_project_ids_current_period"]==[],
         "CURRENT_P1_NO_NEW_PROJECT_SOURCE")
    observed_p1,display_p1=read_plan_csv(p1_csv)
    need(Path(p1_csv).read_bytes()==(Path(manifest).parent/"factors.csv").read_bytes(),
         "P1_CSV_MUST_BE_ORIGINAL_R156_FACTOR_SOURCE")
    original_p1=state["team"]["baseline_smartcity_factors"]
    need(observed_p1==original_p1 and display_p1==source["index_p1_plan"],
         "R232_BASELINE_ALREADY_P1_PLAN_NOT_P0_FACT")
    facts=[r for r in x["rows"].values()
           if r["section"]=="Összefoglaló" and r["label"] in COEFF]
    need(len(facts)==29 and len({r["label"] for r in facts})==29
         and all(r["own_p0"] is not None for r in facts),
         "P0_29_FACTS_IN_ORIGINAL_XLSX")
    p0={r["label"]:r["own_p0"] for r in facts}
    excel_idx=[r["own_p0"] for r in x["rows"].values()
              if r["section"]=="Összefoglaló" and r["label"]=="Okosváros index"]
    need(excel_idx==[source["index_p0"]],
         "P0_EXCEL_AND_UI_DISPLAY_MATCH")
    row_idx=[r for r in x["rows"].values()
             if r["section"]=="Összefoglaló" and r["label"]=="Okosváros index"]
    need(len(row_idx)==1 and len(row_idx[0]["teams_values"])==7
         and all(float(n)==source["index_p0"] for n in row_idx[0]["teams_values"]),
         "ALL_SEVEN_TEAMS_INITIAL_P0_INDEX_PARITY")
    weights=state["market"]["smartcity_total_weights"]
    need(set(weights)==set(WEIGHTS) and abs(sum(weights.values())-1)<1e-9,
         "P1_MARKET_WEIGHT_SOURCE")
    score_p0=computed_index_from_factors(p0,weights)["total_index_from_displayed_factors"]
    score_p1=computed_index_from_factors(original_p1,weights)["total_index_from_displayed_factors"]
    # Displayed factors are rounded; never assert exact equality with UI
    # two-decimal scores, especially the 51.96 vs 51.96551667 P0 mismatch.
    need(abs(score_p0-source["index_p0"])<0.011 and
         abs(score_p1-display_p1)<0.011 and score_p1>score_p0,
         "P0_P1_PARTIAL_DISPLAY_FACTOR_INDEX_PARITY")
    changed={k:{"p0_fact":p0[k],"p1_plan":observed_p1[k],
                 "p1_minus_p0":round(observed_p1[k]-p0[k],8)}
             for k in sorted(p0) if p0[k]!=observed_p1[k]}
    tracks=load_tracks(track_path)
    need(len(tracks)==1 and len(tracks[0]["actions"])==23*5,
         "R145_23_UNVERIFIED_POLICY_EFFECTS")
    idx=project_index()
    w={k:v[0] for k,v in WEIGHTS.items()}
    out=[]
    for record in r232["scenarios"]:
        starts=record["yearly_project_starts"]
        need(len(starts)==5 and all(isinstance(y,list) and len(y)<=4 for y in starts)
             and sum(map(len,starts))<=20 and
             record["p1_project_ids"]==starts[0]
             and record["gameplay_gate"]=="STOP"
             and record["source_rule_eligibility_independently_server_verified"] is False,
             "R232_FOUR_YEARLY_STARTS")
        plan={"start_by_year":[{"start_project_ids":y} for y in starts]}
        p0_years=replay_policy_joint(plan,tracks[0],p0,idx,w,1)
        p1_years=replay_policy_joint(plan,tracks[0],observed_p1,idx,w,1)
        need(len(p0_years)==len(p1_years)==5 and all(
             (yr["actual_index_forecast"] is None and
              yr["actual_cashflow_forecast"] is None and
              len(yr["policy_unmapped_actions"])==23 and
              yr["policy_cash_delta_assumption"]["complete"] is False)
             for yr in p0_years+p1_years),
             "R145_R148_UNKNOWN_NOT_ZERO")
        y0=round(p0_years[-1]["joint_mapped_factor_counterfactual_index"],6)
        y1=round(p1_years[-1]["joint_mapped_factor_counterfactual_index"],6)
        need(y1==record["conditional_year5_project_only_mapped_index_NOT_CITY_FORECAST"],
             "R232_ALREADY_USES_P1_PLAN_FACTORS")
        out.append({
           "hypothetical_annual_card_budget_ecu_NOT_SPENDABLE":
              record["hypothetical_annual_cash_budget_ecu_NOT_SPENDABLE"],
           "objective":record["objective"],
           "first_year_new_project_ids":record["p1_project_ids"],
           "annual_project_starts":record["annual_start_counts"],
           "year5_project_only_conditional_from_P0_fact_NOT_FORECAST":y0,
           "year5_project_only_conditional_from_P1_plan_NOT_FORECAST":y1,
           "baseline_difference_project_sensitivity_index_points":round(y1-y0,6),
           "original_r232_p1_baseline_reproduced":True,
           "current_p1_policy_effects_verified":False,
           "later_year_peer_actions_verified":False,
           "official_five_year_score":None,
           "actual_game_permitted":None,
        })
    need(len(out)==8,"EIGHT_R232_BASELINE_COMPARISONS")
    receipt={
       "schema":SCHEMA,
       "status":"PASS_SOURCE_P0_P1_PROVENANCE_RECONCILED_R232_ALREADY_P1",
       "team":source["team"],"market":"I","round":"Selejtező","period":1,
       "P0_fact_reported_smartcity_index":source["index_p0"],
       "P1_plan_reported_smartcity_index":source["index_p1_plan"],
       "P0_fact_reconstructed_from_displayed_factors":round(score_p0,9),
       "P1_plan_reconstructed_from_displayed_factors":round(score_p1,9),
       "display_factor_quantization_difference_not_assumed_error":True,
       "baseline_for_existing_R232_project_search":"ALREADY_P1_PLAN_NOT_P0",
       "P1_is_forecast_not_released_game_fact":True,
       "league_P0_equal_initial_index_teams":7,
       "league_other_teams_P1_and_future_actions_observed":False,
       "league_P0_common_display_index":source["index_p0"],
       "p0_p1_factor_changes":changed,
       "changed_factor_count":len(changed),
       "scenario_count":8,
       "baseline_sensitivity_scenarios":out,
       "R232_five_year_project_proxy_is_not_game_forecast":True,
       "R191_current_market_cap_server_attested":False,
       "cash_spendable_verified":False,
       "policy_current_and_future_effects_verified":False,
       "source_sha256":{
         "original_Selejtezo_Excel":digest(xlsx),
         "R217_original_receipt":digest(r217_path),
         "R217_original_P1_factor_csv":digest(p1_csv),
         "R217_original_readonly_summary":digest(summary_txt),
         "R156_current_manifest":digest(manifest),
         "R232_source_and_candidate_receipt":digest(r232_path),
         "R145_unknown_test_only_track":digest(track_path),
       },
       "gameplay_gate":"STOP","game_writes":0,
    }
    dest.mkdir(mode=0o700)
    (dest/"R233_RECEIPT.json").write_text(json.dumps(receipt,ensure_ascii=False,
         sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf8")
    lines=[
      "# R233 — a P0 tény és a P1 terv alapján számolt ötéves projektérzékenység",
      "",
      "**Kulcsfontosságú: az R232 modell már P1 tervtényezőket használt.** "
      "Nem építettünk fölöslegesen egy második keresőt.",
      f"- A megjelenített P0 összindex: {source['index_p0']:.2f}; "
      f"29 két tizedes ténytényezőből visszaszámolva: {score_p0:.6f}.",
      f"- A megjelenített P1 tervösszindex: {source['index_p1_plan']:.2f}; "
      f"29 tervtényezőből visszaszámolva: {score_p1:.6f}.",
      f"- Tényezőváltozások P0→P1: {len(changed)}/29.",
      "- A selejtezős Excelben a 7 csapat P0 kezdő összindexe "
      "mind 51,96; ebből jövőbeli helyezés nem vezethető le.",
      "A P0 és a P1 közt látható eltérés nem tekinthető kizárólag "
      "játékos döntések okozta, oksági hatásnak.",
      "",
      "| Hipotetikus évi ECU | Cél | P1 projektek | Ötödik év P0-faktor bázison | Ötödik év P1-terv bázison | Bázisérzékenység |",
      "|---:|---|---|---:|---:|---:|",
    ]
    for item in out:
        lines.append(f"| {item['hypothetical_annual_card_budget_ecu_NOT_SPENDABLE']:,.0f} | "
         f"{item['objective']} | "+(", ".join(map(str,item["first_year_new_project_ids"])) or "nincs")+" | "
         f"{item['year5_project_only_conditional_from_P0_fact_NOT_FORECAST']:.6f} | "
         f"{item['year5_project_only_conditional_from_P1_plan_NOT_FORECAST']:.6f} | "
         f"{item['baseline_difference_project_sensitivity_index_points']:+.6f} |")
    lines+=["","**Egyik ötödikéves érték sem hivatalos előrejelzés.** "
      "Az elsőéves P1 egy terv, az R232 évenkénti keretei feltételezések; "
      "a 23 szakpolitikai tényező és pénzhatás ismeretlen.",
      "A szervezői 4/év szabályt használó R232 20-as korlátja változatlan; "
      "a különleges kliens projekt1-kivétel továbbra sem engedélyezett.",
      "GAME_ACTION_GATE=STOP; játékírás 0; NO_MERGE; NO_DEPLOY.",""]
    (dest/"R233_HU.md").write_text("\n".join(lines),encoding="utf8")
    print(json.dumps({"status":receipt["status"],"changed_factors":len(changed),
       "source_p1_plan":source["index_p1_plan"],
       "source_p1_model_index":round(score_p1,6),
       "source_p0_model_index":round(score_p0,6),
       "scenarios":len(out),"actual_eligible":None,"game_writes":0},ensure_ascii=False))
    return receipt

def main():
    p=argparse.ArgumentParser()
    for key in ("xlsx","p1-csv","summary","r217","manifest","r232","track","out-dir"):
        p.add_argument("--"+key,type=Path,required=True)
    a=p.parse_args()
    compute(a.xlsx,a.p1_csv,a.summary,a.r217,a.manifest,a.r232,a.track,a.out_dir)

if __name__=="__main__":main()
