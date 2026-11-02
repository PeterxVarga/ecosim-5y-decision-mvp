#!/usr/bin/env python3
"""R203: source-pinned, FACT-vs-PLAN-safe partial annual sensitivity evidence.

Reuses R148 annual_component_rollout and combined_factor_replay. No new
causal city transition model, economic calibration, money-unit inference,
game actions, actual server scores, or unobserved population predictions.
"""
from __future__ import annotations
import argparse,hashlib,json,math,sys
from pathlib import Path
from collections import Counter

REPO=Path(__file__).resolve().parents[3]
sys.path[:0]=[
 str(REPO/"team-handoff/r200-historical-plugplay/tools"),
 str(REPO/"ECOSIM_R162_INTEGRITY_REVIEW_RC/tools")]
from corpus_r200 import inspect as r200_inspect,parse_json,resolve,sha
from annual_transition_r148 import annual_component_rollout,combined_factor_replay
from portfolio_5y import project_index

SCHEMA="ECOSIM_R203_FACT_PLAN_SAFE_PARTIAL_ANNUAL_SENSITIVITY_V1"
STATUS="PASS_CONDITIONAL_R148_REPLAY_HOLD_UNIDENTIFIED_CITY_TRANSITIONS"
# User-specified *stress factors* only; cannot infer probabilities or forecast errors.
SCALES=(.5,1.0,1.5)

def hold(test,label):
 if not test:raise ValueError("HOLD_"+label)
def finite(v):return type(v) in (float,int) and math.isfinite(v)

def validate_test_fact_plan(snapshots):
 hold(isinstance(snapshots,list) and len(snapshots)==2 and
      [(x.get("period"),x.get("kind")) for x in snapshots]==
      [(0,"FACT"),(1,"PLAN")],"FACT_PLAN_NOT_TRAINING_PAIR")
 return True

def provenance(profile,profile_path,r201,r202):
 a=r200_inspect(profile,profile_path)
 hold(a["mode"]=="historical-test" and
      a["status"]=="PASS_ALL_AVAILABLE_TEST_SOURCE_ACCOUNTING_NO_CITY_OPTIMUM" and
      a["gameplay_gate"]=="STOP" and not a["citywide_optimum_certified"] and
      not a["actual_cash_verified"],"R200_SOURCE_GATE")
 raw={k:resolve(k,profile,profile_path)
      for k in ("baseline_state","passive","r149","r199","finance","institutions")}
 state=parse_json(raw["baseline_state"])
 passive=parse_json(raw["passive"])
 desk=parse_json(raw["r149"])
 exact=parse_json(raw["r199"])
 validate_test_fact_plan(passive["snapshots"])
 team=profile["identity"]
 hold(all(x.get("team")==team["team"] and x.get("market")==team["market"]
          for x in passive["snapshots"]),"SCOPE_IDENTITY")
 hold(state["provenance"]["current_period"]==1 and
      state["provenance"]["source"].endswith("_P1_HISTORICAL_NOT_LIVE"),
      "P1_BUNDLE_NOT_CONFIRMED")
 hold(desk["game_writes"]==exact["game_writes"]==0 and
      desk["gameplay_gate"]==exact["gameplay_gate"]=="STOP","NO_GAME_ACTION")
 hold(exact["r149_sha256"]==sha(raw["r149"]) and
      exact["source_state_sha256"]==sha(raw["baseline_state"]),
      "MODEL_STATE_INTEGRITY")
 hold(r201["schema"]=="ECOSIM_R201_HISTORICAL_ROBUST_DECISION_BOOK_V1" and
      r201["status"]=="PASS_SOURCE_PINNED_TEST_TRIAGE_NOT_LIVE_CITY_OPTIMUM" and
      r201["gameplay_gate"]=="STOP" and r201["game_writes"]==0 and
      r201["baseline_source_sha256"]==sha(raw["baseline_state"]) and
      r201["r149_source_sha256"]==sha(raw["r149"]) and
      r201["r199_source_sha256"]==sha(raw["r199"]) and
      r201["finance_source_sha256"]==sha(raw["finance"]) and
      r201["institutions_source_sha256"]==sha(raw["institutions"]),
      "R201_JOIN")
 hold(r202["schema"]=="ECOSIM_R202_TEST_REVENUE_AND_INSTITUTION_CALIBRATION_GATE_V1" and
      r202["status"]=="PASS_SOURCE_DIAGNOSTIC_HOLD_GLOBAL_CALIBRATION" and
      r202["game_writes"]==0 and r202["gameplay_gate"]=="STOP" and
      r202["source_hashes"]["finance"]==sha(raw["finance"]) and
      r202["source_hashes"]["institutions"]==sha(raw["institutions"]) and
      not r202["live_prediction_calibrated"],
      "R202_JOIN")
 hold(r201["scenario_robustness"]["candidate_count"]==17 and
      r201["scenario_robustness"]["scenario_count"]==51,
      "R201_PARTIAL_FINANCE_COVERAGE")
 hold(len(a["ten_tab_evidence"])==10 and len(a["sources"])==16,
      "R200_SOURCES_TABS")
 return a,raw,state,passive,desk,exact

def exact_plans(desk,exact):
 result=[]
 for p in desk["candidate_comparison"]:
  result.append({"id":p["candidate_id"],"starts":p["project_ids_by_year"],
                 "costs":p["conservative_project_need_ecu_by_year"],
                 "source":"R149_BOUNDED_HISTORICAL"})
 for p in exact["plans"]:
  result.append({"id":p["plan"],"starts":p["project_ids_by_year"],
                 "costs":p["project_cost_ecu_by_year"],
                 "source":"R195_EXACT_HISTORICAL"})
 ids=[p["id"] for p in result]
 hold(len(result)==len(set(ids))==17,"PLAN_IDENTITY_17")
 return sorted(result,key=lambda p:p["id"])

def make_years(state,desk,exact):
 idx=project_index()
 active=state["team"]["initially_active_project_ids"]
 baseline=state["team"]["baseline_smartcity_factors"]
 plans=exact_plans(desk,exact)
 rows=[]; terminal=[]
 for plan in plans:
  starts=plan["starts"];costs=plan["costs"]
  hold(len(starts)==len(costs)==5,"EXACT_FIVE_YEAR_CALENDAR")
  ledger=annual_component_rollout(idx,active,starts,baseline,start_year=1)
  records=ledger["yearly_state_records"]
  hold(len(records)==5 and ledger["actual_terminal_game_score"] is None and
       ledger["gameplay_action"]=="STOP","R148_PARTIAL_ONLY")
  cumulative=set()
  peryear=[]
  for k,rec in enumerate(records):
   year=k+1;started=starts[k];cumulative.update(started)
   hold(rec["year"]==year and rec["new_project_ids"]==sorted(started) and
        rec["actual_annual_city_state_transition"] is None and
        rec["finance_components"]["project_budget_approval"] is False and
        rec["finance_components"]["actual_cashflow_ecu"] is None and
        rec["finance_components"]["hypothetical_closing_cash_ecu"] is None,
        "NO_ACTUAL_TRANSITIONS_"+plan["id"])
   cost=rec["finance_components"]["conservative_project_funding_need_ecu"]
   hold(finite(cost) and abs(cost-costs[k])<1e-6,
        "R148_R149_R199_COST_DRIFT_"+plan["id"])
   pairs=[(i,e) for i in sorted(cumulative) for e in idx[i]["effects"]]
   simulations=[]
   for sc in SCALES:
    case=combined_factor_replay(baseline,pairs,scale=sc)
    score=case["mapped_conditional_index"]
    band=case["mapped_index_if_only_saturation_uncertain"]
    hold(finite(score) and len(band)==2 and all(finite(x) for x in band) and
         band[0]<=band[1]+1e-8,"BAD_MODEL_FACTOR_RANGE")
    hold(case["total_score_uncertainty_is_bounded"] is False and
         case["partial_score_is_full_city_or_server_forecast"] is False,
         "R148_UNBOUNDED_UNKNOWN")
    simulations.append({"intensity":sc,
      "mapped_index_conditional":round(score,9),
      "index_interval_if_only_saturation_unknown":[round(x,9) for x in band],
      "number_of_source_mapped_direct_effects":case["direct_effects_used"],
      "unmapped_or_indirect_effect_count":len(case["unmapped_project_effects"]),
      "saturation_ambiguities":len(case["ambiguous_saturated_factors"]),
      "unmodeled_city_drift_has_no_bound":True})
   annual=rec["factor_replay"]
   hold(abs(simulations[1]["mapped_index_conditional"]-
            annual["mapped_conditional_index"])<1e-8,
        "R148_BASELINE_SCALE_REPLAY_DRIFT")
   hold(simulations[1]["unmapped_or_indirect_effect_count"]==
        len(annual["unmapped_project_effects"]),"UNMAPPED_EFFECT_COUNT_DRIFT")
   peryear.append({"year":year,"projects_started_ids":sorted(started),
      "conservative_project_card_need_ecu":cost,
      "conditional_index_stress":simulations,
      "unobserved_city_change":"UNKNOWN",
      "actual_server_index":None,"verified_financing":False})
  rows.append({"id":plan["id"],"source":plan["source"],
               "annual_records":peryear,
               "terminal":peryear[-1]["conditional_index_stress"],
               "final_year_unmapped_effects":peryear[-1]["conditional_index_stress"][1]["unmapped_or_indirect_effect_count"]})
 # Ranking is calculated only within the *same* arbitrary direct-effect intensity.
 for i,sc in enumerate(SCALES):
  order=sorted(rows,key=lambda r:(-r["terminal"][i]["mapped_index_conditional"],r["id"]))
  terminal.append({"intensity":sc,
     "conditional_top_five_ids":[r["id"] for r in order[:5]],
     "all_source_partial_order":[r["id"] for r in order],
     "not_real_city_ranking":True})
 return {"plan_count":len(rows),"annual_project_only_ledgers":sum(len(r["annual_records"]) for r in rows),
    "direct_factor_sensitivity_evaluations":len(rows)*5*len(SCALES),
    "project_effect_intensity_assumptions":list(SCALES),
    "rankings_by_assumed_direct_effect_intensity":terminal,
    "plans":rows,
    "observed_fact_to_fact_transition_samples":0,
    "actual_city_transitions_inferred":0,
    "simulator_outcome_validation":False}

def run(profile,profile_path,r201,r202):
 a,raw,state,passive,desk,exact=provenance(profile,profile_path,r201,r202)
 trajectory=make_years(state,desk,exact)
 return {"schema":SCHEMA,"status":STATUS,"mode":"historical-test",
    "source_sha256":{"r200_profile_source_state":sha(raw["baseline_state"]),
       "r149":sha(raw["r149"]),"r199":sha(raw["r199"]),
       "passive":sha(raw["passive"]),"finance":sha(raw["finance"]),
       "institutions":sha(raw["institutions"])},
    "source_roles":len(a["sources"]),"tab_count":len(a["ten_tab_evidence"]),
    "observed_snapshots":[{"period":p["period"],"kind":p["kind"],
       "displayed_total_index":p["displayed_total_index"]} for p in passive["snapshots"]],
    "model_input_is_p1_plan_not_p0_fact":True,
    "baseline_state_and_model_year_semantics_not_proven_server_transition":True,
    "r201_financial_candidate_scenarios":r201["scenario_robustness"]["scenario_count"],
    "r202_observed_source_model_pairs":sum(len(v) for v in r202["observed_channel_groups"].values()),
    "ten_tab_coverage":a["ten_tab_evidence"],
    "partial_project_transition_diagnostics":trajectory,
    "operating_policy_changes_in_annual_project_replay":"NOT_MODELED_DO_NOT_ASSUME_ZERO",
    "actual_city_population_business_credit_and_transport_transitions":"UNKNOWN_UNBOUNDED",
    "synthetic_effect_intensity_is_probability_or_confidence_interval":False,
    "actual_cash_authorized":False,"global_city_optimum_certified":False,
    "real_simulator_forecast_validated":False,"game_writes":0,"gameplay_gate":"STOP"}

def markdown(result):
 x=result["partial_project_transition_diagnostics"]
 ranks=x["rankings_by_assumed_direct_effect_intensity"]
 lines=["# EcoSim R203 – évenkénti részmodell és bizonyított állapotátmenet-hiányok","",
   "**R200–R202 forrásokkal egyeztetett történeti teszt. Nem szerveres városszimulátor.**",
   "",f"Minősítés: {result['status']}.", "",
   f"Értékelt ötéves projektütemezések: {x['plan_count']}; "
   f"R148 éves résznaplók: {x['annual_project_only_ledgers']}; "
   f"közvetlen projektintenzitás-érzékenységi értékelések: {x['direct_factor_sensitivity_evaluations']}.",
   f"Kapcsolódó R201 pénzügyi részforgatókönyvek: {result['r201_financial_candidate_scenarios']}; "
   f"R202 megfigyelt–szintetikus pénzügyi csatornák: {result['r202_observed_source_model_pairs']}.",
   "","## Mit szabad és mit nem szabad az éves adatokból következtetni?","",
   "| Időszak | Forrás jelentése | Kijelzett index |",
   "|---|---|---:|"]
 for z in result["observed_snapshots"]:
  lines.append(f"| {z['period']} | {z['kind']} | {z['displayed_total_index']} |")
 lines+=["","**A p1 PLAN nem lezárt tényév. Nincs két egymást követő FACT időszak, "
         "ezért megfigyelt állapotátmeneti tanítóminta: 0.**",
         "","## Az R148 kliensoldali projekt-indexhatások érzékenysége","",
         "A 0,5× / 1,0× / 1,5× intenzitások **hipotetikus stresszek**; nem "
         "valószínűségek, kalibrált hibahatárok vagy várható városi kimenetek.",
         "","| Projekt-hatásintenzitás | Első öt feltételes részmodell-jelölt |",
         "|---:|---|"]
 for row in ranks:
  lines.append(f"| {row['intensity']}× | "+", ".join(row["conditional_top_five_ids"])+" |")
 lines+=["","## Két korábbi R195 terv: év szerinti projekt-részmodell","",
   "| Terv | Év | Feltételes R148 index (1×) | Nem leképezett hatások | "
   "Konzervatív projektkártya-igény ECU |",
   "|---|---:|---:|---:|---:|"]
 for plan in x["plans"]:
  if plan["id"] not in ("R195-max","R195-reserve"):continue
  for yy in plan["annual_records"]:
   v=yy["conditional_index_stress"][1]
   lines.append(f"| {plan['id']} | {yy['year']} | {v['mapped_index_conditional']} | "
       f"{v['unmapped_or_indirect_effect_count']} | "
       f"{yy['conservative_project_card_need_ecu']} |")
 lines+=["","**Ez a kliensoldali, közvetlen hatásokat alkalmazó részmodell, nem az EcoSim "
  "megjelenített vagy szerver által elfogadott pontszáma.** "
  "A hatásokat a p1 PLAN kiinduló faktoraira alkalmazzuk változatlan külső városállapot "
  "feltételezésével. A nem leképezett hatásoknak nincs igazolt hibakorlátja.",
  "","## Plug-and-play korlát","",
  "A közös profil és a meglévő R148 modell új adatokkal újraellenőrizhető. "
  "Éles állapotból történő tényleges többéves előrejelzéshez viszont szükségesek "
  "az időben egymást követő, lezárt tényállapotok, a teljes pénzügyi és intézményi "
  "adatsor, a szerveres átmeneti szabály és az igazolt projektkártya–pénzügyi mértékegység.",
  "","**Éles döntés: HOLD. EcoSim-módosítás: 0. GAME_ACTION_GATE=STOP.**",""]
 return "\n".join(lines)

def main():
 p=argparse.ArgumentParser()
 for name in ("profile","r201","r202","out-dir"):
  p.add_argument("--"+name,required=True,type=Path)
 args=p.parse_args()
 if args.out_dir.exists():p.error("HOLD_OUTPUT_EXISTS")
 try:
  profile=parse_json(args.profile.read_bytes())
  r201=parse_json(args.r201.read_bytes())
  r202=parse_json(args.r202.read_bytes())
  result=run(profile,args.profile,r201,r202)
 except (ValueError,TypeError,KeyError,IndexError,OSError,UnicodeError) as e:
  p.error(str(e))
 args.out_dir.mkdir(parents=True)
 (args.out_dir/"R203.json").write_text(json.dumps(result,ensure_ascii=False,
   indent=2,allow_nan=False)+"\n",encoding="utf8")
 (args.out_dir/"R203_HU.md").write_text(markdown(result)+"\n",encoding="utf8")
 print("R203="+result["status"]+" GAME_ACTION_GATE=STOP")
 print("R203_RESULT="+str(args.out_dir/"R203.json"))
 print("R203_REPORT="+str(args.out_dir/"R203_HU.md"))
if __name__=="__main__":main()
