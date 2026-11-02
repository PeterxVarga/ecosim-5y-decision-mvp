#!/usr/bin/env python3
"""R201 evidence-first institutional and finance diagnostic + bounded robust scenarios.

No new city transition model or optimizer: reuse R149/R199 results through the R200
SHA-locked profile. Never convert source raw finance values to validated ECU.
"""
from __future__ import annotations
import argparse,collections,csv,hashlib,json,math,sys
from pathlib import Path

REPO=Path(__file__).resolve().parents[3]
R200=REPO/"team-handoff/r200-historical-plugplay/tools"
sys.path.insert(0,str(R200))
from corpus_r200 import (inspect as audit_r200,parse_json,csvdata,resolve,sha,
                         PROFILE_SCHEMA,OUTPUT_SCHEMA,num)
SCHEMA="ECOSIM_R201_HISTORICAL_ROBUST_DECISION_BOOK_V1"
HYPOTHETICAL_CAPS=(50000,90000,100000,150000)
INSTITUTION_TYPES=("Middle schools","Elementary schools","Kindergartens","Nurseries")
STATUS="PASS_SOURCE_PINNED_TEST_TRIAGE_NOT_LIVE_CITY_OPTIMUM"

def hold(ok,code):
 if not ok:raise ValueError("HOLD_"+code)
def finite(v):
 return type(v) in (int,float) and math.isfinite(v)
def strictint(v):
 hold(type(v) is int and v>=0,"NONNEGATIVE_INT")
 return v

def school_rows(institutions):
 pages=institutions.get("pages")
 hold(institutions.get("read_only") is True and isinstance(pages,list) and len(pages)==1,
      "INSTITUTION_SNAPSHOT_SCOPE")
 p=pages[0]
 hold(p.get("path")=="/simulation/institutions" and len(p.get("tables",[]))==5,
      "INSTITUTION_TABLES")
 body=p.get("body_text","")
 hold(all(name in body for name in INSTITUTION_TYPES),"INSTITUTION_BODY_SECTIONS")
 offsets=[body.find(name) for name in INSTITUTION_TYPES]
 hold(offsets==sorted(offsets),"INSTITUTION_SECTION_ORDER")
 required=("Number","Average capacity","Total capacity","Utilization, %",
           "Average number of employees","Total number of employees")
 results=[]
 for name,table in zip(INSTITUTION_TYPES,p["tables"][1:]):
  rows={}
  for row in table["rows"]:
   cells=row.get("cells",[])
   if len(cells)<3:continue
   label=str(cells[0].get("text","")).strip()
   if label in rows:raise ValueError("HOLD_INSTITUTION_DUPLICATE_LABEL")
   rows[label]=cells
  hold(set(required)<=set(rows),"INSTITUTION_ROW_MISSING_"+name)
  def cell(label,which):
   c=rows[label][which]
   raw=c.get("input_value") if c.get("editable") else c.get("text")
   v=num(raw)
   hold(v is not None and math.isfinite(v),"INSTITUTION_BAD_NUMBER_"+label)
   return v
  variants={}
  for year,column in (("p0",1),("p1",2)):
   count=cell("Number",column)
   capacity_each=cell("Average capacity",column)
   total=cell("Total capacity",column)
   avg_employees=cell("Average number of employees",column)
   total_employees=cell("Total number of employees",column)
   utilization=cell("Utilization, %",column)
   hold(all(x>=0 for x in (count,capacity_each,total,avg_employees,total_employees,utilization)),
        "INSTITUTION_NEGATIVE")
   hold(abs(count*capacity_each-total)<1e-6,"CAPACITY_IDENTITY_"+name+"_"+year)
   hold(abs(count*avg_employees-total_employees)<1e-6,
        "EMPLOYEE_IDENTITY_"+name+"_"+year)
   hold(0<=utilization<=1000,"UTILIZATION_RANGE")
   # Displayed percent is rounded; no fabricated exact student count.
   low=max(0.,utilization-.5)*total/100
   high=(utilization+.5)*total/100
   variants[year]={"institutions":int(count),"capacity":int(total),
     "employees":int(total_employees),"displayed_utilization_pct":utilization,
     "approx_attendees_interval_if_rounded_to_integer":[round(low,2),round(high,2)],
     "capacity_gap_interval_if_rounded":[round(low-total,2),round(high-total,2)],
     "certainly_over_capacity_on_display":utilization>100.5,
     "official_optimal_utilization_threshold_known":False}
  results.append({"institution_type":name,"p0":variants["p0"],"p1":variants["p1"],
                  "utilization_change_displayed_pp":
                  round(variants["p1"]["displayed_utilization_pct"]-
                        variants["p0"]["displayed_utilization_pct"],2),
                  "diagnostic":"OVER_CAPACITY_REVIEW" if
                  variants["p1"]["certainly_over_capacity_on_display"]
                  else "CAPACITY_UTILIZATION_OBSERVED_NO_GAME_RECOMMENDATION"})
 return results

def expense_delta_table(finance):
 hold(isinstance(finance,list) and len(finance)>0,"FINANCE_EMPTY")
 out=[]
 for row in finance:
  a=num(row.get("p0_number"));b=num(row.get("p1_number"))
  if a is not None and b is not None and abs(b-a)>1e-9:
   out.append({"source_row_id":row["row_id"],"view":row["view"],
               "table":row["table_title"],"label":row["label"],
               "p0_raw":a,"p1_raw":b,"delta_raw":round(b-a,6),
               "may_include_subtotals_do_not_sum":True})
 out.sort(key=lambda q:(-abs(q["delta_raw"]),q["source_row_id"]))
 return out

def scenario_book(desk,r199):
 older=desk["candidate_comparison"]
 old_index={z["candidate_id"]:z for z in older}
 hold(len(old_index)==len(older)==15,"OLD_15_IDENTITY")
 pair_rows=desk["r158_annual_partial_cash_timing"]["combinations"]
 hold(len(pair_rows)==45,"OLD_45_PAIR_COUNT")
 plan_cache={}
 for cid,p in old_index.items():
  plans=p["project_ids_by_year"]
  costs=p["conservative_project_need_ecu_by_year"]
  hold(len(plans)==len(costs)==5 and all(finite(x) and x>=0 for x in costs),
       "R149_ANNUAL_SCHEDULE")
  plan_cache[cid]={"source":"R149_SAMPLED_HISTORICAL","start_by_year":plans,"costs_by_year":costs}
 for p in r199["plans"]:
  cid=p["plan"]
  hold(cid not in plan_cache and cid in ("R195-max","R195-reserve"),
       "R195_ID_COLLISION")
  plan_cache[cid]={"source":"R195_EXACT_HISTORICAL",
                   "start_by_year":p["project_ids_by_year"],
                   "costs_by_year":p["project_cost_ecu_by_year"]}
 hold(len(plan_cache)==17,"CANDIDATE_UNION_NOT_17")
 scenarios=[]
 for old in pair_rows:
  cid=old["candidate_id"]
  hold(cid in plan_cache,"R149_PAIR_UNKNOWN")
  candidate=plan_cache[cid]
  annual=old["annual_rows"]
  hold([v["projects_started_ids"] for v in annual]==candidate["start_by_year"] and
       [v["project_card_need_ecu"] for v in annual]==candidate["costs_by_year"],
       "R149_ANNUAL_PAIR_MISMATCH")
  scenarios.append((cid,old["path_id"],old["conditional_terminal_mapped_proxy_delta"],
                    old["five_year_partial_net_after_card_cost_ecu"],
                    old["hypothetical_peak_zero_opening_cash_shortfall_positive_receipts_deferred_ecu"]))
 for p in r199["plans"]:
  for v in p["policy_paths"]:
   hold([x["projects_started_ids"] for x in v["annual_rows"]]==p["project_ids_by_year"] and
        [x["project_card_need_ecu"] for x in v["annual_rows"]]==p["project_cost_ecu_by_year"],
        "R199_ANNUAL_PAIR_MISMATCH")
   scenarios.append((p["plan"],v["path_id"],
                     v["mapped_project_plus_tax_partial_delta"],
                     v["partial_five_year_net_after_cards_ecu"],
                     v["peak_deferred_shortfall_zero_opening_ecu"]))
 paths=sorted({x[1] for x in scenarios})
 hold(len(paths)==3 and len(scenarios)==51,"THREE_POLICY_51")
 seen={(v[0],v[1]) for v in scenarios}
 hold(len(seen)==51 and seen=={(cid,path) for cid in plan_cache for path in paths},
      "EXACT_POLICY_PAIR_COVERAGE")
 by_plan=collections.defaultdict(dict)
 for cid,path,ix,net,stress in scenarios:
  hold(all(finite(x) for x in (ix,net,stress)) and stress>=0,
       "NONFINITE_SCENARIO")
  by_plan[cid][path]={"index_proxy_delta":round(ix,8),
                     "partial_net_ecu":round(net,6),
                     "zero_opening_cash_stress_ecu":round(stress,6)}
 rows=[]
 for cid in sorted(by_plan):
  plan=plan_cache[cid]
  costs=plan["costs_by_year"]
  vals=by_plan[cid]
  first=tuple(sorted(plan["start_by_year"][0]))
  rows.append({"candidate_id":cid,"source":plan["source"],
     "first_year_project_ids":list(first),
     "five_year_project_cost_ecu":round(sum(costs),2),
     "max_annual_project_card_need_ecu":round(max(costs),2),
     "worst_partial_index_delta":min(v["index_proxy_delta"] for v in vals.values()),
     "best_partial_index_delta":max(v["index_proxy_delta"] for v in vals.values()),
     "worst_partial_net_ecu":min(v["partial_net_ecu"] for v in vals.values()),
     "peak_zero_opening_cash_stress_ecu":max(v["zero_opening_cash_stress_ecu"] for v in vals.values()),
     "fits_illustrative_card_cap":{str(cap):all(cost<=cap+1e-7 for cost in costs)
                                    for cap in HYPOTHETICAL_CAPS},
     "policy_paths":vals,"funding_approval":False,"gameplay_gate":"STOP"})
 def objectives(x):
  return (x["worst_partial_index_delta"],x["worst_partial_net_ecu"],
          -x["peak_zero_opening_cash_stress_ecu"])
 def dominates(a,b):
  aa,bb=objectives(a),objectives(b)
  return all(x>=y-1e-7 for x,y in zip(aa,bb)) and any(x>y+1e-7 for x,y in zip(aa,bb))
 robust_front=sorted(x["candidate_id"] for x in rows
    if not any(dominates(y,x) for y in rows if y is not x))
 cap_summary=[]
 for cap in HYPOTHETICAL_CAPS:
  eligible=[r for r in rows if r["fits_illustrative_card_cap"][str(cap)]]
  cap_summary.append({"illustrative_per_year_project_card_cap_ecu":cap,
      "fit_count_not_finance_approved":len(eligible),
      "sample_robust_pareto_ids":[x["candidate_id"] for x in eligible
         if not any(dominates(y,x) for y in eligible if y is not x)],
      "actual_spendable_cash_authorized":False})
 year1=collections.Counter(tuple(r["first_year_project_ids"]) for r in rows)
 return {"candidate_count":17,"scenario_count":51,
   "conditional_across_three_synthetic_policy_paths_only":True,
   "candidate_summaries":rows,
   "candidate_robust_front_sample_ids":robust_front,
   "illustrative_cap_filters":cap_summary,
   "distinct_first_year_project_sets":len(year1),
   "first_year_agreement":[{"ids":list(ids),"candidate_count":cnt} for ids,cnt in
        sorted(year1.items(),key=lambda x:(-x[1],x[0]))],
   "selected_or_server_approved":False,"citywide_optimum_certified":False,
   "gameplay_gate":"STOP"}

def analyze(profile,profile_path):
 r=audit_r200(profile,profile_path)
 hold(r["mode"]=="historical-test" and
      r["status"]=="PASS_ALL_AVAILABLE_TEST_SOURCE_ACCOUNTING_NO_CITY_OPTIMUM" and
      r["gameplay_gate"]=="STOP" and r["citywide_optimum_certified"] is False,
      "R200_HISTORICAL_PROOF")
 raw={k:resolve(k,profile,profile_path) for k in
      ("institutions","finance","r149","r199")}
 inst=parse_json(raw["institutions"])
 finance=csvdata(raw["finance"])
 desk=parse_json(raw["r149"])
 r199=parse_json(raw["r199"])
 hold(r199["r149_sha256"]==sha(raw["r149"]) and
      desk["game_writes"]==0 and desk["gameplay_gate"]=="STOP" and
      r199["game_writes"]==0 and r199["gameplay_gate"]=="STOP",
      "HISTORICAL_MODEL_PROVENANCE")
 schools=school_rows(inst)
 differences=expense_delta_table(finance)
 hold(len(differences)==44,"FINANCIAL_NUMERIC_DELTA_COUNT")
 scenarios=scenario_book(desk,r199)
 hold(scenarios["candidate_count"]==r["conditional_candidate_union"]["candidate_count"] and
      scenarios["scenario_count"]==r["conditional_candidate_union"]["scenario_pairs"],
      "R200_R201_PAIR_COUNT_DRIFT")
 return {"schema":SCHEMA,"status":STATUS,"mode":"historical-test",
   "baseline_source_sha256":r["sources"]["baseline_state"]["sha256"],
   "finance_source_sha256":sha(raw["finance"]),
   "institutions_source_sha256":sha(raw["institutions"]),
   "r149_source_sha256":sha(raw["r149"]),
   "r199_source_sha256":sha(raw["r199"]),
   "ten_tab_coverage":r["ten_tab_evidence"],
   "r200_source_count":len(r["sources"]),
   "institutional_capacity_diagnostics":schools,
   "finance_numeric_deltas_not_additive":differences,
   "finance_textual_changes":46,
   "finance_signed_zero_only_display_changes":2,
   "finance_p0_p1_is_actual_vs_plan_not_two_actual_years":True,
   "finance_monetary_scale_or_project_budget_verified":False,
   "six_fee_subtotal_delta_raw_r200":
       r["observed_vs_synthetic_fiscal_reconciliation"]["fee_component_rounding_residual_p0_raw"],
   "scenario_robustness":scenarios,
   "new_city_dynamic_parameters_learned":0,
   "calibrated_five_year_live_prediction":False,
   "simulator_score_formula_proven":False,
   "financial_spend_authority":False,"game_writes":0,"gameplay_gate":"STOP"}

def md(report):
 rows=report["institutional_capacity_diagnostics"]
 block=report["scenario_robustness"]
 lines=["# EcoSim R201 – tesztadatokból igazolt intézményi kapacitások és 17 terv robusztussága",
   "","**Történeti read-only modellvizsgálat, nem szerverkalibrált vagy éles optimum.**",
   "",f"Állapot: {report['status']}. Eredeti R200 inputszerepek: {report['r200_source_count']}.",
   "","## Intézmények – az egyetlen valóban rögzített oktatási nézet",
   "","| Intézménytípus | p0 kapacitás | p1 terv kapacitás | p0 kihasználtság | p1 kihasználtság | Ellenőrzés |",
   "|---|---:|---:|---:|---:|---|"]
 for r in rows:
  lines.append("| "+r["institution_type"]+" | "+str(r["p0"]["capacity"])+" | "+
               str(r["p1"]["capacity"])+" | "+str(r["p0"]["displayed_utilization_pct"])+"% | "+
               str(r["p1"]["displayed_utilization_pct"])+"% | "+r["diagnostic"]+" |")
 lines.extend(["","A teljes férőhely és dolgozói létszám soronként visszaellenőrzött. "
    "A megjelenített egész százalékokat ±0,5 százalékpontos kerekítési intervallummal értelmezzük; "
    "**ez nem hitelesített tanulólétszám vagy intézménybezárási javaslat**.",
    "","## Pénzügyi tény–terv eltérések","",
    "46 szöveges eltérés, ebből 44 numerikus változás és két 0/−0 megjelenítési különbség. A sorok tartalmaznak összesítő sorokat is, "
    "így a deltaértékek **nem összeadhatók** egyetlen hatássá.",
    "","| Pénzügyi sor | p0 nyers | p1 nyers | eltérés nyers |",
    "|---|---:|---:|---:|"])
 for v in report["finance_numeric_deltas_not_additive"][:12]:
  lines.append("| "+v["view"]+" / "+v["label"]+" | "+str(v["p0_raw"])+" | "+
               str(v["p1_raw"])+" | "+str(v["delta_raw"])+" |")
 lines.extend(["","## A 17 megfigyelt projektterv robusztussága három szintetikus pályán","",
   "A számítás az eredeti R149 és R199 motorok 51 azonos szerkezetű részmodell-kimenetét "
   "használja. **Nem generál új projektterveket, új városi hatásfüggvényeket vagy éves szerverállapotot.**",
   "","Robusztus, háromtengelyes mintabeli Pareto-jelöltek: "+
   ", ".join(block["candidate_robust_front_sample_ids"])+".",
   "","| Feltételezett éves kártyakeret ECU | A 17-ből belefér | Az adott keret mintabeli Pareto-jelöltjei |",
   "|---:|---:|---|"])
 for v in block["illustrative_cap_filters"]:
  lines.append("| "+str(v["illustrative_per_year_project_card_cap_ecu"])+" | "+
               str(v["fit_count_not_finance_approved"])+" | "+
               ", ".join(v["sample_robust_pareto_ids"])+" |")
 lines+=["","**A kártyakeret illusztratív felső korlát, nem bizonyítottan rendelkezésre álló pénz.**",
   "A minimax és Pareto-rangsor csak a három feltételezett adó-/működési pálya részindexeire, "
   "részleges nettójára és 0 nyitóval számított stresszére vonatkozik.",
   "","## Még nem megismert paraméterek","",
   "- Szerveroldali öt éves városátmenet; adóalap-változások; közlekedés és cégek visszacsatolása.",
   "- Pénzegység és projektkártya–pénzügyi sor átváltás; valóban elkölthető tartalék.",
   "- Csak egy oktatási intézményi nézet teljesen látható, a többi fül hiányos.",
   "- A p0 tény és p1 terv nem két egymást követő lezárt tényforduló.",
   "","## Plug-and-play","",
   "A számítófüggvény külön validált R200 forrásprofilt olvas. Amikor lesz új export, "
   "csak hiteles forrásosztályú bemeneteket lehet betölteni, a történeti pályák nem csúszhatnak át "
   "az éles eredménybe. Jelenleg az éles futtatás szándékosan HOLD.",
   "","**GAME_ACTION_GATE=STOP. Játékbeli írás nem történt.**",""]
 return "\n".join(lines)

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--profile",type=Path,required=True)
 p.add_argument("--out-dir",type=Path,required=True)
 a=p.parse_args()
 if a.out_dir.exists():p.error("HOLD_EXISTING_OUTPUT")
 try:
  prof=parse_json(a.profile.read_bytes())
  report=analyze(prof,a.profile)
 except (ValueError,TypeError,KeyError,OSError,IndexError) as e:p.error(str(e))
 a.out_dir.mkdir(parents=True)
 (a.out_dir/"R201.json").write_text(
   json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf8")
 (a.out_dir/"R201_HU.md").write_text(md(report)+"\n",encoding="utf8")
 print("R201="+report["status"]+" GAME_ACTION_GATE=STOP")
 print("REPORT="+str(a.out_dir/"R201_HU.md"))
if __name__=="__main__":main()
