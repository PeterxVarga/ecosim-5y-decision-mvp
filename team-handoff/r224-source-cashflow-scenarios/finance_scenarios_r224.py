#!/usr/bin/env python3
"""Actual P1 EcoSim cash-flow reconciliation -> conservative HYPOTHETICAL envelope.

No permission to spend money, start projects or borrow. Use original R162/R160.
Never confuse p1 forecast, prior cash or earmarked grants with approved cash.
"""
from __future__ import annotations
import argparse,hashlib,io,json,math,sys
from datetime import datetime,timezone,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[
 str(ROOT/"team-handoff/r217-current-visible-admission"),
 str(ROOT/"team-handoff/r221-conditional-live-scenario"),
 str(ROOT/"team-handoff/r222-visible-conditions"),
 str(ROOT/"team-handoff/r191-live-admission/tools"),
 str(ROOT/"ECOSIM_R162_INTEGRITY_REVIEW_RC/tools")]
from prepare_visible_r217 import rows,number,parse_finance
from json_integrity_r162 import read_json
from observation_bundle_r152 import compile_bundle
from strategy_5y import search
from conditional_r221 import _choose,RULEBOOK_SHA
from catalog_gate_r192 import CatalogHold,validate_catalog

SCHEMA="ECOSIM_R224_CURRENT_P1_CASHFLOW_SCENARIOS_NO_SPENDABLE_APPROVAL_V1"
CAPS=(1,2,3) # HYPOTHETICAL; Market I actual cap UNKNOWN
FRACTIONS=(0.0,0.25,0.5,1.0)
OBJECTIVES=("nominal","scenario_min")
def need(ok,reason):
    if not ok:raise ValueError("HOLD_"+reason)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def extract(finance_raw):
    need("X-Challenge 2026 Selejtező" in finance_raw and
         "Jutalom a nap végén" in finance_raw and
         "Piac: I" in finance_raw and "Periódus: 1/5" in finance_raw,
         "FINANCE_SOURCE_IDENTITY")
    need(finance_raw.startswith("# SOURCE_URL=https://edu.ecosim.hu/simulation/finance\n"),
         "FINANCE_SOURCE_URL")
    need("# SOURCE_KIND=CONNECTED_BROWSER_VISIBLE_READONLY_NOT_SERVER_ATTESTED" in finance_raw[:400],
         "FINANCE_SOURCE_KIND")
    need(finance_raw.count("Bevételek\n")==1,"FINANCE_EXPENSE_INCOME_SEPARATION")
    exp,inc=finance_raw.split("Bevételek\n",1)
    a,b=rows(exp),rows(inc)
    need(len(a)>35 and len(b)>30,"FINANCE_TABLE_COMPLETENESS")
    def pair(arr,name):
        matches=[(x,y) for label,x,y in arr if label==name]
        need(len(matches)>=1 and len(set(matches))==1,"CASHFLOW_ROW_"+name)
        try:return tuple(number(x) for x in matches[0])
        except (ValueError,TypeError):raise ValueError("HOLD_FINANCE_NON_NUMBER_"+name)
    names={
      "receipts":pair(b,"Bevételek összesen"),
      "receipts_no_loan":pair(b,"Bevételek összesen /hitelek nélkül"),
      "expense_gross":pair(a,"Kiadások összesen"),
      "expense_ex_reserve":pair(a,"Kiadások összesen hitel & tartalék nélkül"),
      "period_net_result":pair(a,"A periódus nettó eredményessége"),
      "reserve_creation":pair(a,"Tartalékképzésre"),
      "reserve_transfer":pair(a,"Tartalékképzés / átvezetés"),
      "prior_year_cash":pair(b,"Előző év végi pénzállomány"),
      "state_development_grant":pair(b,"Fejlesztési célú állami támogatás"),
      "company_development_grant":pair(b,"Vállalatoktól érkező fejlesztési támogatás"),
      "project_expense_line":pair(a,"Projekt - egyedi alapon összesen"),
      "loans_drawn":pair(b,"Hitelfelvétel"),
    }
    need(all(math.isfinite(v) for val in names.values() for v in val),
         "NONFINITE_FINANCE")
    get=lambda key:names[key][1]
    # Only P1 is a balanced planned cash-flow; P0 fact income/expenditure
    # is not booked as a balanced closing reserve in current UI.
    predicted=get("receipts_no_loan")-get("expense_ex_reserve")
    need(abs(predicted-get("period_net_result"))<=1 and
         abs(predicted-get("reserve_creation"))<=1 and
         abs(predicted-get("reserve_transfer"))<=1,
         "PLAN_RESERVE_IS_ARITHMETIC_NOT_FREE_CASH")
    need(abs(get("expense_gross")-(get("expense_ex_reserve")+get("reserve_creation")))<=1
         and abs(get("receipts")-get("expense_gross"))<=1,
         "P1_BALANCE_IDENTITY")
    need(get("loans_drawn")==0 and
         get("receipts")==get("receipts_no_loan"),
         "P1_NO_LOAN_BASELINE")
    need(get("project_expense_line")==0,"P1_BASELINE_ALREADY_HAS_PROJECT_COSTS")
    need(get("prior_year_cash")>=0 and get("state_development_grant")>=0 and
         get("company_development_grant")>=0,
         "NEGATIVE_GRANTS_OR_STARTING_CASH")
    p1_net_without_prior_cash=predicted-get("prior_year_cash")
    scenario_base=p1_net_without_prior_cash-get("state_development_grant")-get("company_development_grant")
    need(scenario_base>0,"NONPOSITIVE_CONSERVATIVE_SCENARIO_BASE")
    # Model arithmetic: opening money and grant rows subtracted ONCE.
    need(abs(scenario_base-
         (get("receipts_no_loan")-get("expense_ex_reserve")-
          get("prior_year_cash")-get("state_development_grant")-
          get("company_development_grant")))<=1e-9,
         "DOUBLE_COUNTED_PRIOR_CASH_OR_GRANTS")
    budgets=[int(math.floor(scenario_base*f)) for f in FRACTIONS]
    need(budgets[0]==0 and budgets==sorted(set(budgets)),"INVALID_SCENARIO_GRID")
    return {"source_values_p0_p1_ecu":{k:list(v) for k,v in names.items()},
      "p1_project_free_cashflow_surplus_ecu":round(predicted,2),
      "p1_surplus_excluding_prior_cash_ecu":round(p1_net_without_prior_cash,2),
      "p1_surplus_excluding_prior_cash_and_both_grants_ecu":round(scenario_base,2),
      "hypothetical_annual_budget_ecu":budgets,
      "grant_earmarking_verified":False,
      "incremental_project_funding_observed_and_approved":False,
      "scenario_funds_are_approved":False,
      "project_interactions_reforecasted_in_cash_flow":False}

def compute(current_pages,r156,r220,r222,rulebook,out):
    current_pages=Path(current_pages);r156=Path(r156)
    r220=Path(r220);r222=Path(r222);rulebook=Path(rulebook)
    out=Path(out).resolve()
    need(not out.exists() and out.parent.is_dir() and
         not out.is_relative_to(ROOT.resolve()),"PRIVATE_NEW_OUTPUT")
    for fp in (r220,r222,rulebook):
        need(fp.is_file() and not fp.is_symlink(),"PRIOR_SOURCE_REQUIRED")
    need(sha(rulebook)==RULEBOOK_SHA,"OFFICIAL_HANDBOOK_SHA_DRIFT")
    p=read_json(r156/"R217_RECEIPT.json")
    need(p["schema"]=="ECOSIM_R217_CURRENT_BROWSER_VISIBLE_PARTIAL_ADMISSION_V1"
         and p["round"]=="Selejtező" and p["market"]=="I"
         and p["period"]==1 and p["team"]=="Jutalom a nap végén"
         and p["r191_current_qualification"]=="HOLD_CAP_UNKNOWN_OR_ASSUMED"
         and p["observed_project_statuses"]==35 and p["running_ids"]==[14,22,23,24,34,35]
         and p["gameplay_gate"]=="STOP" and p["game_writes"]==0,
         "R223_ACTUAL_STATE_NOT_ADMITTED_AS_LIVE")
    source=current_pages/"finance.txt"
    need(source.is_file() and not source.is_symlink() and
         sha(source)==p["source_text_sha256"]["finance"],"CURRENT_FINANCE_HASH")
    finance_raw=source.read_text(encoding="utf-8")
    financial=extract(finance_raw)
    prior_cards=read_json(r220)
    conditions=read_json(r222)
    need(prior_cards.get("schema")=="ECOSIM_R220_CURRENT_ALL_35_VISIBLE_CARD_PARITY_V1"
         and prior_cards.get("observed_card_count")==35
         and prior_cards.get("money_parity_count")==35
         and prior_cards.get("effect_parity_count")==35
         and prior_cards.get("gameplay_gate")=="STOP"
         and prior_cards.get("game_writes")==0
         and prior_cards.get("market_project_start_cap_verified") is False,
         "ORIGINAL_35_UI_CARDS_CONDITIONAL")
    need(conditions.get("schema")=="ECOSIM_R222_ALL_35_VISIBLE_PROJECT_CONDITIONS_PROOF_V1"
         and conditions.get("r192_time_admission")=="HOLD_CATALOG_NOT_SAME_PERIOD_CAPTURE_WINDOW"
         and conditions.get("observed_explicit_condition_rules")==
           {"30":["Bicikliútfejlesztés — Fut"],"31":["Vasútfejlesztés — Fut"]}
         and conditions.get("game_writes")==0 and
         conditions.get("source_sha256",{}).get("R220")==sha(r220),
         "CURRENT_VISIBLE_CONDITIONS_BUT_STALE_R192")
    _,state,_=compile_bundle(r156/"r156_immutable/manifest.json")
    need(state["provenance"]["round"]=="Selejtező" and
         state["provenance"]["market"]=="I" and
         state["provenance"]["current_period"]==1 and
         state["market"]["maxProjectPerTurn"] is None and
         state["team"]["initially_active_project_ids"]==[14,22,23,24,34,35],
         "R156_FRESH_BUNDLE_SOURCE")
    need(p["finance_snapshot"]["observed_p0_and_p1"]["net_earnings"]==
         financial["source_values_p0_p1_ecu"]["period_net_result"],
         "FINANCE_R217_INDEPENDENT_PARSER_DRIFT")
    results=[]
    for hypothetical_cap in CAPS:
      for frac,budget in zip(FRACTIONS,financial["hypothetical_annual_budget_ecu"]):
       for objective in OBJECTIVES:
        v=search(state,start_year=1,cap_override=hypothetical_cap,
                 budget_override=[budget]*5,beam_width=8,shortlist=25,
                 allow_same_year=False,objective=objective)
        r=_choose(v,hypothetical_cap,budget,objective)
        need(r["first_year_conservative_requirement_ecu"]<=budget and
             not r["financing_authorized"] and r["gameplay_gate"]=="STOP",
             "HYPOTHETICAL_RESULTS_NOT_GAME_FINANCE")
        r["budget_basis"]="ILLUSTRATIVE_FRACTION_OF_SOURCE_DERIVED_P1_NO_PRIOR_CASH_NO_GRANTS_SURPLUS"
        r["budget_fraction"]=frac
        r["forecast_impact_on_P1_finance_NOT_verified"]=True
        r["not_an_eligible_game_action"]=True
        results.append(r)
    need(len(results)==len(CAPS)*len(FRACTIONS)*len(OBJECTIVES)==24,
         "EXACT_24_FINANCE_GROUNDED_HYPOTHESES")
    result={"schema":SCHEMA,
      "status":"PASS_SOURCE_RECONCILED_HYPOTHETICAL_FINANCE_SCENARIOS_ONLY",
      "round":"Selejtező","market":"I","team":"Jutalom a nap végén","period":1,
      "source_class":"ACTUAL_UI_P1_FINANCE_OPERATOR_VISIBLE_NOT_SERVER_ATTESTED",
      "source_sha256":{
         "current_r156_receipt":sha(r156/"R217_RECEIPT.json"),
         "current_r156_manifest":sha(r156/"r156_immutable/manifest.json"),
         "current_finance_text":sha(source),
         "prior_R220_visible_35_card_receipt":sha(r220),
         "prior_R222_conditions_receipt":sha(r222),
         "official_rulebook_pdf":sha(rulebook)},
      "cashflow":financial,
      "source_facts_only_first_period":True,
      "hypothetical_market_project_caps":list(CAPS),
      "future_year_budgets_assumed_same_not_observed":True,
      "scenarios":results,"scenario_count":24,
      "independent_original_R160_used":True,
      "current_R191_real_cap":None,
      "current_R191_actual_spendable_cash":None,
      "current_R192_full_admission":False,
      "current_R192_same_hour_card_capture":False,
      "current_R214_live_advice_authorized":False,
      "official_score_predicted":False,
      "gameplay_gate":"STOP","game_writes":0}
    out.mkdir(mode=0o700)
    (out/"R224_RECEIPT.json").write_text(
       json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    report=[
       "# R224 – Selejtező I: aktuális P1 cash-flow alapján kötött forgatókönyvek",
       "",
       "**Forrásellenőrzött pénzügyi egyezés, de kizárólag hipotetikus projektkeretek!**",
       f"- P1 bevétel: {financial['source_values_p0_p1_ecu']['receipts_no_loan'][1]:,.0f} ECU",
       f"- P1 kiadás tartalék nélkül: {financial['source_values_p0_p1_ecu']['expense_ex_reserve'][1]:,.0f} ECU",
       f"- P1 várható pénzforgalmi többlet: {financial['p1_project_free_cashflow_surplus_ecu']:,.0f} ECU",
       f"- Nyitó pénzállomány nélküli többlet: {financial['p1_surplus_excluding_prior_cash_ecu']:,.0f} ECU",
       f"- Nyitó pénz és két fejlesztési támogatás nélkül: {financial['p1_surplus_excluding_prior_cash_and_both_grants_ecu']:,.0f} ECU",
       "",
       "**FONTOS:** egyik összeg sem igazoltan szabadon elkölthető, nincsenek",
       "megfigyelt kötelezettség- és pénzügyi jogosultsági adatok; a költségtervek",
       "megvalósítása és a bevételek visszahatása ismeretlen.",
       "",
       "| Hipotetikus indítási limit | Éves szcenáriókeret | Cél | P1 javasolt projektek (csak MI LENNE HA) | Konzervatív kártyateher |",
       "|---:|---:|---|---|---:|"]
    for x in results:
        ids=", ".join(map(str,x["initial_project_ids"])) or "Nincs új projekt"
        report.append(
          f"| {x['hypothetical_cap']} | {x['hypothetical_annual_budget_ecu']:,.0f} ECU ({100*x['budget_fraction']:.0f}%)"+
          f" | {x['objective']} | {ids} | {x['first_year_conservative_requirement_ecu']:,.0f} ECU |")
    report+=["","A hipotetikus költségkeret minden következő öt évre ismétlődik a keresőben,",
       "DE a forrás csak P1 pénzügyi tervet tartalmaz; P2–P5 pénzügyi keret nem ismert.",
       "Ez nem a hivatalos pontszám előrejelzése, és nem játékbeli engedély.",
       "R191 cap=UNKNOWN, spendable=UNKNOWN; R192=same-hour HOLD; R214=HOLD.",
       "**GAME_ACTION_GATE=STOP; módosítás 0.**",""]
    (out/"R224_HU.md").write_text("\n".join(report),encoding="utf-8")
    print(json.dumps({"status":result["status"],
       "p1_cashflow_surplus_ecu":financial["p1_project_free_cashflow_surplus_ecu"],
       "ex_prior_and_grants_ecu":financial["p1_surplus_excluding_prior_cash_and_both_grants_ecu"],
       "hypothetical_budgets":financial["hypothetical_annual_budget_ecu"],
       "scenario_count":len(results),"actual_spendable":None,
       "live_advice":False,"game_writes":0,
       "private_output":str(out)},ensure_ascii=False))
    return result
def main():
    p=argparse.ArgumentParser()
    for key in ("current-pages","current-r156","r220-receipt","r222-receipt","rulebook","out-dir"):
        p.add_argument("--"+key,required=True,type=Path)
    a=p.parse_args()
    compute(a.current_pages,a.current_r156,a.r220_receipt,a.r222_receipt,a.rulebook,a.out_dir)
if __name__=="__main__":main()
