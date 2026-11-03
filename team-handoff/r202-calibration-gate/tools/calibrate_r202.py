#!/usr/bin/env python3
"""R202: observed-source-to-client-model consistency and identifiability gate.

Does NOT fit invented coefficients, convert currency, assume p1 is an observed
later year, or approve a project.  Reuses R200, R154 and R155 without reimplementing
their client-side revenue/wage formulas.  Private data remains on owner's Fedora.
"""
from __future__ import annotations
import argparse,json,math,sys
from pathlib import Path

REPO=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(REPO/"team-handoff/r200-historical-plugplay/tools"),
              str(REPO/"ECOSIM_R162_INTEGRITY_REVIEW_RC/tools")]
from corpus_r200 import inspect as r200_inspect,parse_json,csvdata,resolve,num,sha
from tax_revenue_r154 import tax_revenue,validate as validate_tax_revenue
from operating_cash_r155 import service_fees,staff_expenses,validate as validate_operating

SCHEMA="ECOSIM_R202_TEST_REVENUE_AND_INSTITUTION_CALIBRATION_GATE_V1"
STATUS="PASS_SOURCE_DIAGNOSTIC_HOLD_GLOBAL_CALIBRATION"

# Each source row is identified by TAB + TABLE + row index + label: names repeat
# in other contexts, including transport expenses vs transport service fees.
TAX_ROWS=[
 ("business","8","Iparűzési adó"),
 ("vehicle","9","Gépjárműadó"),
 ("communal","10","Kommunális adó"),
 ("building","11","Építményadó")
]
FEE_ROWS=[
 ("burial","21","Temetkezés"),
 ("parking","22","Parkolásüzemeltetés"),
 ("communal","23","Kommunális"),
 ("services","24","Víz, csatorna, távhő"),
 ("rental","25","Bérlakás díjak"),
 ("transport","26","Tömegközlekedés")
]
WAGE_ROWS=[
 ("education","1","Okt. intézmények"),
 ("sport","2","Sport intézmények"),
 ("culture","3","Műv. intézmények"),
 ("health","4","Eü. intézmények"),
 ("social","5","Szoc. intézmények"),
 ("services","6","Szolgáltató"),
 ("transport","7","Tömegközlekedés"),
 ("bureau","8","Városi hivatal")
]
def hold(test,code):
 if not test:raise ValueError("HOLD_"+code)
def isfinite(v):
 return type(v) in (float,int) and math.isfinite(v)
def exact_ledger_row(rows,view,table,idx,label):
 matches=[r for r in rows if (r.get("view"),r.get("table_title"),
          str(r.get("row_index")),r.get("label"))==(view,table,idx,label)]
 hold(len(matches)==1,"LEDGER_ROW_IDENTITY_"+idx)
 r=matches[0]
 a,b=num(r.get("p0_number")),num(r.get("p1_number"))
 hold(isfinite(a) and isfinite(b) and a>=0 and b>=0,
      "LEDGER_NUMERIC_"+idx)
 return {"source_row_id":r["row_id"],"p0_actual_raw":a,
         "p1_target_raw":b,"source_label":label}

def channels(rows,view,table,specs,model_channels):
 hold(set(model_channels)=={key for key,_,_ in specs},"CHANNEL_SET")
 output=[]
 for key,index,label in specs:
  observed=exact_ledger_row(rows,view,table,index,label)
  model=model_channels[key]
  hold(isfinite(model) and model>=0,"MODEL_CHANNEL_NONFINITE")
  # A ratio is a dimensionless *diagnostic* only, NOT an exchange rate.
  ratio=(observed["p0_actual_raw"]/model if model>0 else None)
  output.append(dict(channel=key,synthetic_baseline_ecu=model,
    observed_to_model_ratio_unqualified=round(ratio,8) if ratio is not None else None,
    source_class="ACTUAL_P0_VS_SYNTHETIC_EXOGENOUS_MODEL",
    **observed))
 return output

def ratio_diagnostic(groups):
 all_channels=[x for gr in groups.values() for x in gr]
 positives=[x["observed_to_model_ratio_unqualified"] for x in all_channels
            if x["observed_to_model_ratio_unqualified"] is not None and
               x["observed_to_model_ratio_unqualified"]>0]
 hold(len(positives)>=4,"INSUFFICIENT_SCALE_PAIRS")
 spread=max(positives)/min(positives)
 hold(math.isfinite(spread),"RATIO_SPREAD_NONFINITE")
 # If a *single common scale* exactly explained a fixed synthetic baseline,
 # the nonzero ratios would be equal up to display rounding. Disagreement
 # does NOT falsify the source formulas; unknown base values can cause it.
 exact_common=all(abs(v-positives[0])<1e-6 for v in positives[1:])
 return {"compared_positive_channel_count":len(positives),
   "ratio_min":round(min(positives),8),"ratio_max":round(max(positives),8),
   "ratio_max_div_min":round(spread,8),
   "exact_universal_baseline_scale_supported":exact_common,
   "universal_currency_conversion_identified":False,
   "underlying_exogenous_city_bases_identified":False,
   "channel_ratios_are_not_safe_conversion_factors":True}

def build(profile,profile_path):
 prior=r200_inspect(profile,profile_path)
 hold(prior.get("mode")=="historical-test" and
      prior.get("status")=="PASS_ALL_AVAILABLE_TEST_SOURCE_ACCOUNTING_NO_CITY_OPTIMUM" and
      prior.get("gameplay_gate")=="STOP" and
      prior.get("actual_cash_verified") is False and
      prior.get("citywide_optimum_certified") is False,
      "R200_HISTORICAL_PROVENANCE")
 raw={role:resolve(role,profile,profile_path)
      for role in ("finance","institutions","tax","tax_revenue","operating")}
 rows=csvdata(raw["finance"])
 taxdoc=parse_json(raw["tax"])
 fiscal=parse_json(raw["tax_revenue"])
 operating=parse_json(raw["operating"])
 hold(taxdoc["source_class"]==fiscal["source_class"]==
      operating["source_class"]=="SYNTHETIC_TEST_ONLY","SOURCE_CLASS")
 validate_tax_revenue(fiscal);validate_operating(operating)
 year1=fiscal["annual_city_bases"][0]
 baseline=taxdoc["baseline"]["decisions"]
 tax_model=tax_revenue(
     fiscal["market"],
     {k:year1[k] for k in ("business_taxable_base_ecu",
       "car_count_index","population","housing_unit_count")},
     baseline,communal_tax_amount=year1["communal_tax_amount"])
 fbase=operating["annual_city_bases"][0]
 fee_model=service_fees(operating["market"],1,fbase,operating["baseline_fees"])
 wage_model=staff_expenses(fbase,fbase["staff"])
 groups={
   "four_tax_channels":channels(rows,"cash_flow","Bevételek",
                       TAX_ROWS,tax_model["channels_ecu"]),
   "six_fee_channels":channels(rows,"cash_flow","Bevételek",
                       FEE_ROWS,fee_model["channels_ecu"]),
   "eight_wage_channels":channels(rows,"cash_flow","Kiadások",
                       WAGE_ROWS,wage_model["wage_components_ecu"])
 }
 totals={}
 for key,items in groups.items():
  totals[key]={"p0_actual_components_raw":round(sum(x["p0_actual_raw"] for x in items),8),
     "p1_target_components_raw":round(sum(x["p1_target_raw"] for x in items),8),
     "first_year_synthetic_baseline_ecu":
         round(sum(x["synthetic_baseline_ecu"] for x in items),8),
     "same_source_currency_scale_verified":False}
 # The observed sums must also match the independent R200 read-only audit.
 old=prior["observed_vs_synthetic_fiscal_reconciliation"]
 hold(abs(totals["four_tax_channels"]["p0_actual_components_raw"]-
          old["observed_four_taxes_p0_raw"])<1e-6,
      "FOUR_TAX_R200_RECONCILIATION")
 hold(abs(totals["six_fee_channels"]["p0_actual_components_raw"]-
          old["observed_six_fees_p0_components_raw"])<1e-6,
      "SIX_FEE_R200_RECONCILIATION")
 wage_subtotal=exact_ledger_row(rows,"cash_flow","Kiadások","9",
                                 "Bérek (közterhekkel) összesen")
 hold(abs(totals["eight_wage_channels"]["p0_actual_components_raw"]-
          wage_subtotal["p0_actual_raw"])<1e-6 and
      abs(totals["eight_wage_channels"]["p1_target_components_raw"]-
          wage_subtotal["p1_target_raw"])<1e-6,
      "WAGE_TOTAL_RECONCILIATION")
 fees_subtotal=exact_ledger_row(rows,"cash_flow","Bevételek","27",
                                 "Szolgáltatások díjai")
 fee_residuals={
  "p0_actual_raw":round(totals["six_fee_channels"]["p0_actual_components_raw"]-
                         fees_subtotal["p0_actual_raw"],6),
  "p1_target_raw":round(totals["six_fee_channels"]["p1_target_components_raw"]-
                         fees_subtotal["p1_target_raw"],6)
 }
 hold(fee_residuals["p0_actual_raw"]==
      old["fee_component_rounding_residual_p0_raw"] and
      fee_residuals["p1_target_raw"]==
      old["fee_component_rounding_residual_p1_raw"],
      "FEE_TOTAL_R200_RECONCILIATION")
 observed_institutions=parse_json(raw["institutions"])
 observed_pages=observed_institutions["pages"]
 hold(len(observed_pages)==1 and observed_pages[0]["path"]=="/simulation/institutions",
      "INSTITUTION_PARTIAL_ONLY")
 # The UI's education wage decision is not one-to-one with any R155 city-base
 # field; R155's edu wage rate is synthetic and absolute payroll units diverge.
 education_wage=exact_ledger_row(rows,"cash_flow","Kiadások","1","Okt. intézmények")
 ratios=ratio_diagnostic(groups)
 # A future better-aligned corpus may legitimately pass the common-scale
 # diagnostic; do not turn successful calibration into a safety failure.
 return {"schema":SCHEMA,"status":STATUS,"mode":"historical-test",
   "source_hashes":{k:sha(v) for k,v in raw.items()},
   "source_roles_total":len(prior["sources"]),
   "p0_is_actual_and_p1_is_plan":True,"p1_not_a_following_actual_year":True,
   "model_source":"R154_R155_REUSED_CLIENT_COMPONENTS_STATIC_EXOGENOUS",
   "observed_channel_groups":groups,
   "ledger_vs_model_totals":totals,
   "observed_fee_component_minus_reported_total_raw":fee_residuals,
   "observed_education_wage_row":education_wage,
   "synthetic_edu_wage_component_ecu":wage_model["wage_components_ecu"]["education"],
   "units_and_bases":ratios,
   "model_identifiability":{
      "can_reconcile_observed_p0_subtotals_with_components":True,
      "can_reconcile_observed_p1_target_subtotals_with_components":True,
      "can_infer_one_common_unit_multiplier_only":False,
      "can_calibrate_multi_year_transitions_from_two_actual_years":False,
      "future_city_bases_verified":False,
      "true_four_tax_parameters_identified":False,
      "true_six_fee_parameters_identified":False,
      "institutional_coverage_is_partial":True,
      "actual_available_project_cash_verified":False,
      "server_score_formula_verified":False},
   "research_priority":[
     "Obtain documented cash-vs-project-card unit relationship",
     "Observe p0 tax/fee decision inputs and independent city bases, not only resulting income",
     "Capture all institution and transport subtabs in read-only mode",
     "Capture consecutive closed FACT periods for calibrated transitions",
     "Check 26 public vs 29 client factor mapping and server-calculated score"],
   "global_city_optimum_certified":False,"live_prediction_calibrated":False,
   "game_writes":0,"gameplay_gate":"STOP"}

def report_md(r):
 lines=["# EcoSim R202 – pénzügyi és intézményi modellkalibrációs kapu",
   "","**Történeti R94 megfigyelés × R154/R155 szintetikus bemenet: NEM éles optimalizálás.**",
   "",f"Állapot: {r['status']}. SHA-256-tal egyeztetett forrásszerepek: {r['source_roles_total']}.",
   "","## Csatornánkénti összevetés","",
   "A szintetikus ECU és az UI nyers pénzügyi sora közötti **mértékegység-kapcsolat nem igazolt**. "
   "A hányados kizárólag eltérésdiagnosztika; nem átváltási tényező, és a képlet helyességét sem bizonyítja.",
   "","| Terület | Csatorna | Megfigyelt p0 | Tervezett p1 | R154/R155 szintetikus első év | Nyers / modell hányados |",
   "|---|---|---:|---:|---:|---:|"]
 for name,chs in r["observed_channel_groups"].items():
  for ch in chs:
   lines.append("| "+name+" | "+ch["channel"]+" | "+str(ch["p0_actual_raw"])+" | "+
                str(ch["p1_target_raw"])+" | "+str(ch["synthetic_baseline_ecu"])+" | "+
                str(ch["observed_to_model_ratio_unqualified"])+" |")
 vals=r["units_and_bases"]
 lines+=["","## Azonosíthatóság","",
   f"Pozitív csatornák: {vals['compared_positive_channel_count']}; "
   f"legkisebb megfigyelt/modell hányados {vals['ratio_min']}, "
   f"legnagyobb {vals['ratio_max']} (szélsőérték-arány {vals['ratio_max_div_min']}).",
   "A közös skálaszorzó a jelenlegi szintetikus bázisokat nem illeszti egyszerre. "
   "Ez **nem igazolja**, hogy eltérő pénznemek, vagy hogy hibás képletek lennének: "
   "a nem megfigyelt adóalapok, intézményi létszámok és díjérzékenységi paraméterek is eltérhetnek.",
   "","## Könyvelési egyeztetés","",
   "| Részösszeg | p0 megfigyelt (nyers) | p1 terv (nyers) | Szintetikus modell (ECU) |",
   "|---|---:|---:|---:|"]
 for label,v in r["ledger_vs_model_totals"].items():
  lines.append("| "+label+" | "+str(v["p0_actual_components_raw"])+" | "+
               str(v["p1_target_components_raw"])+" | "+
               str(v["first_year_synthetic_baseline_ecu"])+" |")
 fee=r["observed_fee_component_minus_reported_total_raw"]
 lines+=["","A hat szolgáltatási bevételi sor és a kijelzett összeg eltérése: "
         f"p0: {fee['p0_actual_raw']}, p1: {fee['p1_target_raw']} nyers egység.",
   "A nyolc bérkategória összege egyezik az UI megjelenített bérösszegével, "
   "de ez nem jelenti az R155 teljes költségmodelljének kalibrálását.",
   "","## Éles futtatást továbbra is tiltó bizonytalanságok",""]
 for key,val in r["model_identifiability"].items():
  lines.append("- "+key+": "+str(val))
 lines+=["","## Legnagyobb értékű új információk",""]
 lines+=["- "+p for p in r["research_priority"]]
 lines+=["","**Nincs igazolt globális optimum, nincs finanszírozási engedély, "
         "nincs játékon belüli írás. GAME_ACTION_GATE=STOP.**",""]
 return "\n".join(lines)

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--profile",required=True,type=Path)
 ap.add_argument("--out-dir",required=True,type=Path)
 args=ap.parse_args()
 if args.out_dir.exists():ap.error("HOLD_OUT_DIR_EXISTS")
 try:
  profile=parse_json(args.profile.read_bytes())
  out=build(profile,args.profile)
 except (OSError,KeyError,IndexError,TypeError,ValueError,UnicodeError) as e:
  ap.error(str(e))
 args.out_dir.mkdir(parents=True)
 (args.out_dir/"R202.json").write_text(
    json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
 (args.out_dir/"R202_HU.md").write_text(report_md(out)+"\n",encoding="utf-8")
 print("R202="+out["status"]+" GAME_ACTION_GATE=STOP")
 print("R202_REPORT="+str(args.out_dir/"R202_HU.md"))
if __name__=="__main__":main()
