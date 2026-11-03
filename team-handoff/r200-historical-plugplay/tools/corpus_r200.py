#!/usr/bin/env python3
"""R200: audit all available historical EcoSim inputs and an interchangeable source profile.
Existing R199 model only; no EcoSim access, game writes, or unverified city optimization.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,re,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"ECOSIM_R162_INTEGRITY_REVIEW_RC/tools"))
PROFILE_SCHEMA="ECOSIM_R200_INPUT_PROFILE_V1"
OUTPUT_SCHEMA="ECOSIM_R200_TEST_CORPUS_AUDIT_V1"
ASSETS={
 "project_cards":"ECOSIM_R162_INTEGRITY_REVIEW_RC/data/ecosim_projects_20261030.json",
 "factor_capture":"ECOSIM_R162_INTEGRITY_REVIEW_RC/capture/R156_HISTORICAL_TEST_EXPORT.json",
 "baseline_state":"team-handoff/r191-live-admission/examples/historical_test_state.json",
 "finance":"ECOSIM_R162_INTEGRITY_REVIEW_RC/data/finance_R94_test_snapshot.csv",
 "institutions":"team-handoff/r200-historical-plugplay/fixtures/institutions_R94_readonly.json",
 "institution_numbers":"team-handoff/r200-historical-plugplay/fixtures/institutions_R94_numeric_catalog.json",
 "institution_analysis":"team-handoff/r200-historical-plugplay/fixtures/institutions_R94_reanalysis.json",
 "taxonomy":"team-handoff/r200-historical-plugplay/fixtures/R175B_factor_crosswalk.csv",
 "taxonomy_qualification":"team-handoff/r200-historical-plugplay/fixtures/R175B_QUALIFICATION.json",
 "r195":"team-handoff/r200-historical-plugplay/fixtures/R195_TWO_PROJECT_PLANS.json",
 "r199":"team-handoff/r200-historical-plugplay/fixtures/R199_EXACT_PROJECT_POLICY_REPLAY.json",
 "r149":"team-handoff/r200-historical-plugplay/fixtures/R149_COMPLETE_HISTORICAL_DECISION_DESK.json",
 "tax":"ECOSIM_R162_INTEGRITY_REVIEW_RC/inputs/tax_counterfactual_r153.synthetic.json",
 "tax_revenue":"ECOSIM_R162_INTEGRITY_REVIEW_RC/inputs/tax_revenue_r154.synthetic.json",
 "operating":"ECOSIM_R162_INTEGRITY_REVIEW_RC/inputs/operating_r155.synthetic.json",
 "passive":"ECOSIM_R162_INTEGRITY_REVIEW_RC/inputs/historical_passive_summary_20261030.json"
}
MODELS={"tax","tax_revenue","operating"}
TABS={
 "summary":("Összefoglalás","PARTIAL","R156 indexek, csapat és periódus"),
 "projects":("Projektek","HISTORICAL_FULL_CATALOG","35 megfigyelt kártya"),
 "institutions":("Intézmények","PARTIAL_ONE_SUBVIEW","Oktatás: egy megfigyelt oldal"),
 "transport":("Közlekedés","INDIRECT","Cash flow és díjrészmodell, nincs teljes fül"),
 "income":("Bevételek","INDIRECT","Pénzügyi bevételsorok, nincs teljes fül"),
 "population":("Lakosság","NOT_DIRECTLY_CAPTURED","Indexfaktor nem egyenlő lakossági modellel"),
 "corporations":("Vállalkozások","NOT_DIRECTLY_CAPTURED","Cégindex és hipotetikus adóalap"),
 "loans":("Hitelek","TERMS_UNKNOWN","Történeti nullás tételek, hitelkeret nem ismert"),
 "finance":("Pénzügyek","PARTIAL_UNITS_UNKNOWN","R94 cash-flow és vagyoni sorok"),
 "analysis":("Elemzés","HISTORICAL_FACTORS","29 faktor, 6 súly, nem szerverformula")
}
def check(ok,why):
 if not ok:raise ValueError("HOLD_"+why)
def sha(data):return hashlib.sha256(data).hexdigest()
def pairs(seq):
 obj={}
 for k,v in seq:
  check(k not in obj,"DUPLICATE_JSON")
  obj[k]=v
 return obj
def parse_json(raw):
 def parse_float(x):
  v=float(x);check(math.isfinite(v),"NONFINITE_JSON");return v
 return json.loads(raw.decode("utf-8-sig"),object_pairs_hook=pairs,
                   parse_float=parse_float,
                   parse_constant=lambda _:(_ for _ in ()).throw(ValueError("HOLD_NONFINITE_JSON")))
def csvdata(raw):return list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
def num(v):
 try:
  x=float(str(v).replace(" ","").replace("\u00a0","").replace(",","."))
  return x if math.isfinite(x) else None
 except (ValueError,TypeError):return None
def create_historical():
 out={}
 for role,path in ASSETS.items():
  out[role]={"scope":"repo","path":path,
             "sha256":sha((ROOT/path).read_bytes()),
             "source_class":"SYNTHETIC_TEST_ONLY" if role in MODELS else "HISTORICAL_READONLY"}
 return {"schema":PROFILE_SCHEMA,"mode":"historical-test",
         "identity":{"team":"Jutalom a nap végén","market":"Z","round":"Tesztforduló","period":1},
         "sources":out,"gameplay_gate":"STOP"}
def validate_profile(p):
 check(p.get("schema")==PROFILE_SCHEMA,"PROFILE_SCHEMA")
 check(p.get("mode") in ("historical-test","current-readonly"),"PROFILE_MODE")
 check(p.get("gameplay_gate")=="STOP","GAMEPLAY_GATE")
 ident=p.get("identity",{})
 check(all(isinstance(ident.get(k),str) and ident[k] for k in ("team","market","round")) and
       type(ident.get("period")) is int and 1<=ident["period"]<=5,"IDENTITY")
 sources=p.get("sources",{})
 check(isinstance(sources,dict) and set(sources)<=set(ASSETS),"SOURCE_ROLES")
 if p["mode"]=="historical-test":
  check(set(sources)==set(ASSETS),"HISTORICAL_SOURCE_COMPLETENESS")
 else:
  check(all(x.get("source_class")=="OPERATOR_DECLARED_READONLY" for x in sources.values()),
        "NO_HISTORICAL_FALLBACK_IN_CURRENT")
 return sources
def resolve(role,p,profile_path):
 spec=p["sources"][role]
 scope=spec.get("scope")
 check(scope in ("repo","profile"),"SOURCE_SCOPE")
 base=ROOT if scope=="repo" else profile_path.resolve().parent
 dst=(base/spec["path"]).resolve()
 check(dst.is_relative_to(base.resolve()) and dst.is_file(),"SOURCE_OUT_OF_SCOPE_"+role)
 raw=dst.read_bytes()
 check(len(raw)<=10_000_000,"SOURCE_TOO_LARGE_"+role)
 check(re.fullmatch("[0-9a-f]{64}",str(spec.get("sha256"))) and
       sha(raw)==spec["sha256"],"SOURCE_SHA_"+role)
 return raw

def inspect(profile,profile_path):
 validate_profile(profile)
 sources={role:resolve(role,profile,profile_path) for role in profile["sources"]}
 if profile["mode"]=="current-readonly":
  for role,raw in sources.items():
   spec=profile["sources"][role]
   check(spec.get("scope")=="profile","CURRENT_REQUIRES_OWN_EVIDENCE_DIRECTORY")
   check(sha(raw)!=sha((ROOT/ASSETS[role]).read_bytes()),
         "CURRENT_IDENTICAL_TO_ARCHIVED_TEST_"+role)
  return {"schema":OUTPUT_SCHEMA,"mode":"current-readonly",
          "status":"HOLD_CURRENT_SOURCE_INTAKE_ONLY",
          "sha_verified_roles_only":sorted(sources),
          "missing_roles":sorted(set(ASSETS)-set(sources)),
          "model_replay_validated":False,"financing_verified":False,
          "citywide_optimum_certified":False,"gameplay_gate":"STOP"}
 docs={role:parse_json(data) for role,data in sources.items()
       if role not in ("finance","taxonomy")}
 projects=docs["project_cards"];cap=docs["factor_capture"];state=docs["baseline_state"]
 ident=profile["identity"];meta=projects["metadata"];origin=state["provenance"]
 check(all(item["team"]==ident["team"] and item["market"]==ident["market"]
           for item in (meta,cap,origin)),"CROSS_SOURCE_TEAM_MARKET")
 check(meta["round"]==ident["round"] and cap["round"]==meta["simulation"] and
       origin["current_period"]==cap["period"]==ident["period"],"CROSS_SOURCE_PERIOD")
 card_ids=[v["id"] for v in projects["projects"]]
 check(len(card_ids)==35 and sorted(card_ids)==list(range(1,36)),"PROJECT_CATALOG")
 f=csvdata(cap["factors_csv"].encode());pr=csvdata(cap["projects_csv"].encode())
 check(len(f)==30 and len(pr)==35 and sum(x["metric"]=="Okosváros index" for x in f)==1,"FACTORS_PROJECTS_COVERAGE")
 check(set(state["team"]["baseline_smartcity_factors"])=={x["metric"] for x in f if x["metric"]!="Okosváros index"},
       "R156_R191_FACTORS")
 weights=cap["parameters"]["market"]["smartcity_total_weights"]
 check(len(weights)==6 and abs(sum(weights.values())-1)<1e-9,"INDEX_WEIGHTS")
 historical_summaries=docs["passive"]["snapshots"]
 check(len(historical_summaries)==2 and
       [(x["period"],x["kind"]) for x in historical_summaries]==[(0,"FACT"),(1,"PLAN")],
       "P0_FACT_P1_PLAN_NOT_ANNUAL_TRANSITION")
 check(all(x["team"]==ident["team"] and x["market"]==ident["market"]
           for x in historical_summaries),"PASSIVE_SNAPSHOT_IDENTITY")
 p0_fact,p1_plan=historical_summaries
 check(abs(p1_plan["displayed_total_index"]-
      next(num(x["value"]) for x in f if x["metric"]=="Okosváros index"))<0.001,
       "R156_P1_PLAN_TOTAL_INDEX")
 running=sorted(int(x["project_id"]) for x in pr if x["previous_running"]=="true")
 check(len(running)==6 and running==sorted(state["team"]["initially_active_project_ids"]),
       "RUNNING_PROJECTS")
 finance=csvdata(sources["finance"])
 check(len(finance)==len({x["row_id"] for x in finance}) and
       all(x["team"]==ident["team"] and x["market"]==ident["market"] and
           x["source_url"]=="https://edu.ecosim.hu/simulation/finance" for x in finance),
       "FINANCE_IDENTITY")
 def finrow(title,label):
  v=[x for x in finance if x["table_title"]==title and x["label"]==label]
  check(len(v)==1,"FINANCE_TOTAL_"+label)
  return {"p0":num(v[0]["p0_number"]),"p1":num(v[0]["p1_number"])}
 totals={
  "reported_reserve_transfer":finrow("Kiadások","Tartalékképzésre"),
  "reported_cash_balance":finrow("Vagyoni kimutatás","Pénzállomány"),
  "expenses_total":finrow("Kiadások","Kiadások összesen"),
  "revenues_total":finrow("Bevételek","Bevételek összesen"),
  "expenses_without_loans_and_reserve":
    finrow("Kiadások","Kiadások összesen hitel & tartalék nélkül")
 }
 check(totals["revenues_total"]["p0"]==p0_fact["revenue_ecu"] and
       totals["expenses_total"]["p0"]==p0_fact["expense_ecu"] and
       totals["revenues_total"]["p1"]==p1_plan["revenue_ecu"] and
       totals["expenses_without_loans_and_reserve"]["p1"]==p1_plan["expense_ecu"],
       "R94_SUMMARY_CASHFLOW_CONTRADICTION")
 planned_excess=(totals["revenues_total"]["p1"]-
                 totals["expenses_without_loans_and_reserve"]["p1"])
 check(planned_excess==totals["reported_reserve_transfer"]["p1"]==
       totals["reported_cash_balance"]["p1"],"R94_RESERVE_RECONCILIATION")
 ins=docs["institutions"];catalog=docs["institution_numbers"];ia=docs["institution_analysis"]
 check(ins["read_only"] is True and len(ins["pages"])==1 and
       ins["pages"][0]["path"]=="/simulation/institutions","INSTITUTIONS_SCOPE")
 page=ins["pages"][0]
 row_count=sum(len(z["rows"]) for z in page["tables"])
 check(row_count==ia["row_count"] and len(page["tables"])==ia["table_count"] and
       ia["snapshot_sha256"]==sha(sources["institutions"]),"INSTITUTIONS_EVIDENCE")
 check(len(catalog["numeric_observations"])==catalog["numeric_count"] and
       len(catalog["editable_fields"])==catalog["editable_count"],"INSTITUTION_NUMERIC_COVERAGE")
 taxonomy=csvdata(sources["taxonomy"])
 r195=docs["r195"];r199=docs["r199"];desk=docs["r149"]
 check(r195["mode"]==r199["mode"]=="historical-test" and r199["gameplay_gate"]=="STOP"
       and r199["actual_cash_approved"] is False,"R199_NOT_HISTORICAL")
 check(r195["input_state_sha256"]==r199["source_state_sha256"]==
       sha(sources["baseline_state"]),"PROJECT_MODEL_SOURCE_DRIFT")
 check(r199["r149_sha256"]==sha(sources["r149"]) and
       desk["inputs"]["state"]["sha256"]==sha(sources["baseline_state"]) and
       desk["run_mode"]=="HISTORICAL_ILLUSTRATION" and
       desk["gameplay_gate"]=="STOP" and desk["game_writes"]==0,
       "R149_R199_PROVENANCE_OR_GAME_GATE")
 check(all(desk["inputs"][label]["sha256"]==sha(sources[role])
       for label,role in (("tax_scenarios","tax"),
                          ("tax_revenue_scenarios","tax_revenue"),
                          ("operating_scenarios","operating"))),
       "R149_SYNTHETIC_MODEL_SOURCE_HASH")
 check(r195["source_pin"]==r199["source_pin"] and
       len(r199["plans"])==2 and r199["project_policy_pairs"]==6,"R199_COVERAGE")
 for plan in r199["plans"]:
  role=plan["plan"].removeprefix("R195-")
  check(role in ("max","reserve"),"R199_PROJECT_ROLE")
  check(plan["project_ids_by_year"]==[v[role+"_project_ids"] for v in r195["annual_comparison"]]
        and plan["project_cost_ecu_by_year"]==[v[role+"_cost_ecu"] for v in r195["annual_comparison"]],
        "EXACT_YEAR_COST_MATCH")
  check(len(plan["policy_paths"])==3 and all(
       len(x["annual_rows"])==5 and
       [y["projects_started_ids"] for y in x["annual_rows"]]==plan["project_ids_by_year"]
       for x in plan["policy_paths"]),"SIX_POLICY_PAIRS")
 check({docs[k]["source_class"] for k in MODELS}=={"SYNTHETIC_TEST_ONLY"},
       "SYNTHETIC_MODEL_INTEGRITY")
 # Falsify the synthetic fiscal/moving bases against observed same-test-date
 # aggregates, WITHOUT assuming a monetary unit or treating partial income as cash.
 from tax_response_r153 import read_document
 from tax_revenue_r154 import evaluate_counterfactual
 from operating_cash_r155 import evaluate as evaluate_operating
 tax_doc,_=read_document(ROOT/ASSETS["tax"])
 tax_path=tax_doc["paths"][0]
 tax_sample=evaluate_counterfactual(docs["tax_revenue"],
     tax_doc["baseline"]["decisions"],tax_path["decisions_by_year"],start_year=1)
 op_sample=evaluate_operating(docs["operating"],docs["operating"]["paths"][0],1)
 income=[z for z in finance if z["table_title"]=="Bevételek" and z["view"]=="cash_flow"]
 tax_ids={"8","9","10","11"}
 fee_ids={"21","22","23","24","25","26"}
 def rawsum(rows,period):
  return sum(num(z[period+"_number"]) for z in rows)
 tax_observed=[z for z in income if z["row_index"] in tax_ids]
 fee_observed=[z for z in income if z["row_index"] in fee_ids]
 check(len(tax_observed)==4 and len(fee_observed)==6,"FOUR_TAX_SIX_FEE_ROWS")
 six_total=[z for z in income if z["row_index"]=="27"]
 check(len(six_total)==1 and six_total[0]["label"]=="Szolgáltatások díjai",
       "FEE_TOTAL_IDENTITY")
 measured_vs_model={
   "observed_four_taxes_p0_raw":rawsum(tax_observed,"p0"),
   "observed_four_taxes_p1_raw":rawsum(tax_observed,"p1"),
   "observed_six_fees_p0_components_raw":rawsum(fee_observed,"p0"),
   "observed_six_fees_p1_components_raw":rawsum(fee_observed,"p1"),
   "reported_six_fees_p0_raw":num(six_total[0]["p0_number"]),
   "reported_six_fees_p1_raw":num(six_total[0]["p1_number"]),
   "synthetic_r154_first_year_four_taxes_ecu":
     tax_sample["yearly"][0]["baseline_four_tax_income_ecu"],
   "synthetic_r155_first_year_six_fees_ecu":
     op_sample["annual_rows"][0]["six_fee_baseline_ecu"],
   "same_monetary_scale_verified":False,
   "synthetic_bases_calibrated_to_R94_finance":False,
   "actual_project_budget_approved":False}
 measured_vs_model["fee_component_rounding_residual_p0_raw"]=round(
    measured_vs_model["observed_six_fees_p0_components_raw"]-
    measured_vs_model["reported_six_fees_p0_raw"],6)
 measured_vs_model["fee_component_rounding_residual_p1_raw"]=round(
    measured_vs_model["observed_six_fees_p1_components_raw"]-
    measured_vs_model["reported_six_fees_p1_raw"],6)
 candidates=[]
 for path in r199["policy_paths"]:
  choices=[(p["plan"],next(x for x in p["policy_paths"] if x["path_id"]==path))
           for p in r199["plans"]]
  for role,row in choices:
   a=(row["mapped_project_plus_tax_partial_delta"],
      row["partial_five_year_net_after_cards_ecu"],
      -row["peak_deferred_shortfall_zero_opening_ecu"])
   dominated=False
   for other,b in choices:
    if role==other:continue
    v=(b["mapped_project_plus_tax_partial_delta"],
       b["partial_five_year_net_after_cards_ecu"],
       -b["peak_deferred_shortfall_zero_opening_ecu"])
    dominated=dominated or (all(x>=y for x,y in zip(v,a)) and any(x>y for x,y in zip(v,a)))
   candidates.append({"policy":path,"plan":role,"partial_index":a[0],
       "partial_net_ecu":a[1],"hypothetical_cash_stress_ecu":-a[2],
       "dominated_in_this_two_candidate_sample":dominated})
 # Highest evidence-backed comparison: union the original 15 R149 schedules
 # with the 2 newly replayed exact R195 schedules. This is a BOUNDED sample,
 # NOT 17 novel optimized plans or the 5-year city optimum.
 old_candidates=desk["candidate_comparison"]
 old_pairs=desk["r158_annual_partial_cash_timing"]["combinations"]
 check(len(old_candidates)==15 and len(old_pairs)==45,"R149_15_X_3")
 candidate_lookup={q["candidate_id"]:q for q in old_candidates}
 check(len(candidate_lookup)==15,"R149_DUPLICATE_CANDIDATES")
 r199_ids={x["plan"] for x in r199["plans"]}
 check(not (set(candidate_lookup)&r199_ids),"R149_R195_CANDIDATE_ID_COLLISION")
 all_pairs=[]
 for entry in old_pairs:
  cid=entry["candidate_id"];p=candidate_lookup.get(cid)
  check(p is not None,"R149_UNKNOWN_CANDIDATE")
  check([x["projects_started_ids"] for x in entry["annual_rows"]]==p["project_ids_by_year"] and
        [x["project_card_need_ecu"] for x in entry["annual_rows"]]==p["conservative_project_need_ecu_by_year"],
        "R149_YEAR_COST_MISMATCH")
  all_pairs.append({"policy":entry["path_id"],"plan":cid,
   "partial_index":entry["conditional_terminal_mapped_proxy_delta"],
   "partial_net_ecu":entry["five_year_partial_net_after_card_cost_ecu"],
   "hypothetical_cash_stress_ecu":
     entry["hypothetical_peak_zero_opening_cash_shortfall_positive_receipts_deferred_ecu"]})
 all_pairs.extend({k:x[k] for k in ("policy","plan","partial_index","partial_net_ecu",
                 "hypothetical_cash_stress_ecu")} for x in candidates)
 paths=sorted({p["policy"] for p in candidates})
 check(len(paths)==3 and len(all_pairs)==51 and
       all(len([a for a in all_pairs if a["policy"]==path])==17 for path in paths),
       "R149_R199_51_PAIR_UNION")
 front=[]
 for path in paths:
  group=[v for v in all_pairs if v["policy"]==path]
  survivors=[]
  for a in group:
   v=(a["partial_index"],a["partial_net_ecu"],-a["hypothetical_cash_stress_ecu"])
   check(all(type(z) in (float,int) and math.isfinite(z) for z in v),
         "NONFINITE_CONDITIONAL_MODEL_OBJECTIVE")
   dominated=any(
     all(x>=y-1e-7 for x,y in zip(
       (b["partial_index"],b["partial_net_ecu"],-b["hypothetical_cash_stress_ecu"]),v))
     and any(x>y+1e-7 for x,y in zip(
       (b["partial_index"],b["partial_net_ecu"],-b["hypothetical_cash_stress_ecu"]),v))
       for b in group if b is not a)
   if not dominated:survivors.append(a["plan"])
  front.append({"policy":path,"candidates":len(group),
                "nondominated_sample_ids":sorted(survivors),
                "not_global_optimum":True})
 return {"schema":OUTPUT_SCHEMA,"mode":"historical-test",
  "status":"PASS_ALL_AVAILABLE_TEST_SOURCE_ACCOUNTING_NO_CITY_OPTIMUM",
  "identity":ident,
  "sources":{name:{"sha256":sha(raw),"bytes":len(raw)} for name,raw in sources.items()},
  "observations":{"project_cards":len(card_ids),"running_ids":running,
    "smartcity_factors":len(f)-1,"observed_displayed_total_index":next(num(x["value"]) for x in f if x["metric"]=="Okosváros index"),"index_weights":len(weights),
    "observed_p0_fact_index":p0_fact["displayed_total_index"],
    "observed_p1_plan_index":p1_plan["displayed_total_index"],
    "observed_p1_revenues_less_nonreserve_expenses_raw":planned_excess,
    "p0_and_p1_are_NOT_consecutive_facts":True,
    "finance_rows":len(finance),
    "finance_cashflow":sum(x["view"]=="cash_flow" for x in finance),
    "finance_wealth":sum(x["view"]=="wealth" for x in finance),
    "finance_fact_plan_changes":sum(x["p0_raw"]!=x["p1_raw"] for x in finance),
    "finance_money_unit_verified":all(x["monetary_unit"] for x in finance),
    "financial_displayed_totals_raw_scale":totals,
    "institutions_observed_pages":len(ins["pages"]),
    "institutions_tables":len(page["tables"]),"institutions_rows":row_count,
    "institutions_numeric_observations":len(catalog["numeric_observations"]),
    "institutions_editable_fields":len(catalog["editable_fields"]),
    "taxonomy_crosswalk_rows":len(taxonomy)},
  "ten_tab_evidence":{key:{"label":v[0],"status":v[1],"evidence":v[2]}
                      for key,v in TABS.items()},
  "r199_exact_test_scenarios":candidates,
  "conditional_candidate_union":{"r149_old_candidates":15,"r195_exact_candidates":2,
    "candidate_count":17,"scenario_pairs":len(all_pairs),
    "bounded_sample_front_by_policy":front,
    "not_server_scored_or_global_optimum":True},
  "observed_vs_synthetic_fiscal_reconciliation":measured_vs_model,
  "model_constraints":{"r195_budget_source":"HYPOTHESIS_NOT_APPROVED_CASH",
     "future_city_bases":"SYNTHETIC_EXOGENOUS",
     "r155_institution_operating":"PARTIAL",
     "loans_grants_terms":"UNKNOWN",
     "money_units":"UNKNOWN",
     "public_taxonomy_identity":"NOT_SERVER_VERIFIED",
     "R199_abs_score_plus_R153_delta":"NON_ADDITIVE"},
  "all_ten_tabs_directly_observed":False,"actual_cash_verified":False,
  "citywide_optimum_certified":False,"game_writes":0,"gameplay_gate":"STOP"}

def markdown(v):
 o=v["observations"];t=o["financial_displayed_totals_raw_scale"]
 lines=["# EcoSim R200 – tesztadat-alapú teljes városi bizonyítékdosszié","",
  "**Történeti, részben szintetikus, kizárólag read-only; nem éles döntési utasítás.**","",
  "Státusz: "+v["status"],"",
  "## Beolvasott, ténylegesen megfigyelt tesztadatok",
  "- "+str(o["project_cards"])+" eredeti projekt, "+str(len(o["running_ids"]))+" már futó.",
  "- "+str(o["smartcity_factors"])+" városmutató, "+str(o["index_weights"])+" indexsúly. A kijelzett p0 tény index "+str(o["observed_p0_fact_index"])+", p1 terv index "+str(o["observed_p1_plan_index"])+". A kettő NEM két egymást követő lezárt év.",
  "- "+str(o["finance_rows"])+" pénzügyi sor ("+str(o["finance_cashflow"])+" cash flow, "+
      str(o["finance_wealth"])+" vagyon), "+str(o["finance_fact_plan_changes"])+" tény/terv eltérés.",
  "- Intézményi snapshot: "+str(o["institutions_tables"])+" tábla, "+str(o["institutions_rows"])+
      " sor, "+str(o["institutions_numeric_observations"])+" szám, "+str(o["institutions_editable_fields"])+
      " szerkeszthető mező; csak az oktatási fül egy nézete.",
  "- "+str(o["taxonomy_crosswalk_rows"])+" taxonómiai keresztwalk-sor, szerverformula még nem igazolt.","",
  "## Fülenkénti lefedettség","",
  "| Fül | Státusz | Bizonyíték |","|---|---|---|"]
 for z in v["ten_tab_evidence"].values():
  lines.append("| "+z["label"]+" | "+z["status"]+" | "+z["evidence"]+" |")
 lines+=["","## Pénzügyi kiindulás (eredeti nyers skála; pénzegység nem igazolt)","",
   "| Megfigyelt sor | p0 (tény) | p1 (terv) |","|---|---:|---:|"]
 for name,x in t.items():lines.append("| "+name+" | "+str(x["p0"])+" | "+str(x["p1"])+" |")
 lines+=["","**A p1 (terv) bevétel mínusz tartalék nélküli kiadás = "+str(o["observed_p1_revenues_less_nonreserve_expenses_raw"])+
   " nyers egység, amely megegyezik a tervben szereplő tartalékátvezetéssel. Ez nem igazoltan szabadon költhető projektkeret.**","",
   "## R94 tényadatok és R154–R155 szintetikus bázisok falszifikációja","",
   "**A két forrás pénzegysége / skálája nincs egyeztetve. A táblázat csak anomáliát jelez, nem kalibrációt.**","",
   "| Mutató | Nyers tesztadat / szintetikus modellérték |","|---|---:|"]
 m=v["observed_vs_synthetic_fiscal_reconciliation"]
 for name in ("observed_four_taxes_p0_raw","observed_four_taxes_p1_raw",
  "observed_six_fees_p0_components_raw","reported_six_fees_p0_raw",
  "fee_component_rounding_residual_p0_raw","fee_component_rounding_residual_p1_raw",
  "synthetic_r154_first_year_four_taxes_ecu","synthetic_r155_first_year_six_fees_ecu"):
  lines.append("| "+name+" | "+str(m[name])+" |")
 lines+=["",
   "A szintetikus négyadó- és hatdíj-alap **nem egyezik automatikusan** az R94-ben megfigyelt részösszegekkel. "
   "A 29-es taxonómiai crosswalk és az R94 pénzügyi sorok ezért bizonyítékként szerepelnek, "
   "de a különböző pénzügyi skálák nem kerülnek összeadásra.","",
   "## Az R195 két pontos ütemezésének R199 részmodellje","",
   "| Feltételezett pálya | Projektterv | Részindex Δ | Ötéves részleges nettó (ECU) | "
   "0 nyitós stresszcsúcs (ECU) | Kétterves mintában dominált? |",
   "|---|---|---:|---:|---:|---|"]
 for x in v["r199_exact_test_scenarios"]:
  lines.append("| "+x["policy"]+" | "+x["plan"]+" | "+str(x["partial_index"])+
       " | "+str(x["partial_net_ecu"])+" | "+str(x["hypothetical_cash_stress_ecu"])+
       " | "+str(x["dominated_in_this_two_candidate_sample"])+" |")
 u=v["conditional_candidate_union"]
 lines+=["","## Az összes már meglévő projektjelölt közös, feltételes döntési halmaza","",
   "**R149 15 korábbi ötéves jelölt + R195 2 pontos terv = 17 külön jelölt, "+
   str(u["scenario_pairs"])+" részmodell-párosítás. Ez újrafelhasználás, nem új optimalizáló.**","",
   "| Szintetikus adó- és működési pálya | Vizsgált tervek | Mintabeli, háromtengelyes Pareto-jelöltek |",
   "|---|---:|---|"]
 for row in u["bounded_sample_front_by_policy"]:
  lines.append("| "+row["policy"]+" | "+str(row["candidates"])+" | "+
     ", ".join(row["nondominated_sample_ids"])+" |")
 lines+=["","A Pareto csak a meglévő 17 projekttervre és a rögzített három részmodell-"
   "pályára vonatkozik: nem bizonyít globális optimumot vagy tényleges pénzügyi megvalósíthatóságot.","",
   "## Fennmaradó modellhatárok",""]
 for a,b in v["model_constraints"].items():lines.append("- "+a+": "+b)
 lines+=["","## Plug-and-play adatcsere",
   "Az egységes profil minden bemenethez forrásosztályt, SHA-256-ot és szerepet rendel. "
   "Új current-readonly profilban kizárólag operátor által ellenőrzött adatok szerepelhetnek; "
   "az adatbevitel kompatibilis, de a current R199 közös modellfuttatás és szerverkalibráció "
   "külön jóváhagyása hiányában a rendszer HOLD.", "",
   "**Játékbeli művelet: 0. GAME_ACTION_GATE=STOP.**",""]
 return "\n".join(lines)

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--create-historical-profile",type=Path)
 p.add_argument("--profile",type=Path);p.add_argument("--out-dir",type=Path)
 a=p.parse_args()
 if a.create_historical_profile:
  dest=a.create_historical_profile
  if dest.exists():p.error("HOLD_OUTPUT_EXISTS")
  dest.parent.mkdir(parents=True,exist_ok=True)
  dest.write_text(json.dumps(create_historical(),indent=2,ensure_ascii=False)+"\n",encoding="utf8")
  print("R200_PROFILE="+str(dest));return
 if not a.profile or not a.out_dir:p.error("Provide --profile and --out-dir")
 if a.out_dir.exists():p.error("HOLD_OUTPUT_EXISTS")
 try:
  profile=parse_json(a.profile.read_bytes())
  result=inspect(profile,a.profile)
 except (ValueError,KeyError,TypeError,IndexError,OSError) as e:p.error(str(e))
 a.out_dir.mkdir(parents=True)
 (a.out_dir/"R200.json").write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+"\n")
 (a.out_dir/"R200_HU.md").write_text(markdown(result) if result["mode"]=="historical-test"
                                   else json.dumps(result,indent=2,ensure_ascii=False))
 print("R200="+result["status"]+" GAME_ACTION_GATE=STOP")
 print("REPORT="+str(a.out_dir/"R200_HU.md"))
if __name__=="__main__":main()
