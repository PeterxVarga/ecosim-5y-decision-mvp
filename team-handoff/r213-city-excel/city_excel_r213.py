#!/usr/bin/env python3
"""R213: exact-source historical SmartCity Excel -> 29-factor / 10-domain evidence join.

Excel parser is deliberately limited to simple, cached, read-only A:F cells
and uses only Python stdlib. No game requests, edits, spreadsheet formulas,
claims of financing, or server-authenticated present-round data.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,re,sys,zipfile
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
from xml.etree import ElementTree as ET

SCHEMA="ECOSIM_R213_HISTORICAL_CITY_SOURCE_CROSSWALK_V1"
NS="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
SECTIONS=("Összefoglaló","Intézmények","Közösségi közlekedés","Közlekedési személyzet",
          "Személyzeti költségek","Bevételek","Lakossági adatok","Vállalkozások",
          "Pénzügyek","Hitelek")
GROUPS=("Gazdaság","Környezet","Kormányzás","Életkörülmények","Mobilitás","Emberek")
TEAM="Jutalom a nap végén"
ROWKEYS={314:"historical_net_earnings",312:"historical_total_expenses",
         355:"historical_total_receipts",370:"assets_market_eligible_subtotal",
         377:"assets_restricted_subtotal",381:"assets_illiquid_subtotal",
         382:"historical_reported_total_assets",351:"prior_year_end_cash",
         328:"state_development_grant",329:"company_development_grant",
         311:"planned_reserve_line_historical_snapshot",220:"population_current",
         257:"small_business_count",261:"medium_business_count",
         265:"large_business_count",37:"displayed_smartcity_index"}
def hold(ok,reason):
    if not ok:raise ValueError("HOLD_"+reason)
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def exact_number(value,reason):
    hold(type(value) in (float,int) and math.isfinite(value),reason)
    return float(value)
def load_xlsx(path,*,require_legacy_team=True):
    path=Path(path)
    hold(path.is_file() and not path.is_symlink() and path.suffix.lower()==".xlsx","EXCEL_FILE")
    with zipfile.ZipFile(path) as z:
        filenames=set(z.namelist())
        hold("xl/worksheets/sheet1.xml" in filenames,"WORKSHEET_MISSING")
        hold(len([n for n in filenames if re.fullmatch(r"xl/worksheets/sheet[0-9]+.xml",n)])==1,
             "EXACT_ONE_WORKSHEET")
        info=z.getinfo("xl/worksheets/sheet1.xml")
        hold(info.file_size<2_000_000,"WORKSHEET_TOO_LARGE")
        shared=[]
        if "xl/sharedStrings.xml" in filenames:
            strings=ET.fromstring(z.read("xl/sharedStrings.xml"))
            shared=["".join(t.text or "" for t in si.iter(NS+"t")) for si in strings.findall(NS+"si")]
        sheet=ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    columns="ABCDEF" if require_legacy_team else "ABCDEFGH"
    cells={}
    for row in sheet.findall("./"+NS+"sheetData/"+NS+"row"):
        n=int(row.attrib["r"])
        hold(1<=n<=500 and n not in cells,"ROW_INVALID")
        values=[None]*len(columns)
        for c in row.findall(NS+"c"):
            address=c.attrib.get("r","")
            m=re.fullmatch(r"([A-Z]+)([0-9]+)",address)
            hold(bool(m),"CELL_ADDRESS")
            col,rnum=m.groups()
            if col not in columns or len(col)!=1:
                # Do not silently ignore a new team header beyond the
                # established five- or seven-team layout.
                if n==1 and (c.find(NS+"v") is not None or c.find(NS+"is") is not None):
                    hold(False,"SUPPORTED_TEAM_COLUMNS")
                continue
            hold(int(rnum)==n,"CELL_ROW")
            hold(c.find(NS+"f") is None,"FORMULA_CELL_NOT_REPRODUCIBLE")
            v=c.find(NS+"v")
            inline=c.find(NS+"is")
            raw=(v.text if v is not None else None)
            typ=c.attrib.get("t","n")
            if typ=="s":
                hold(raw is not None and 0<=int(raw)<len(shared),"SHARED_STRING")
                value=shared[int(raw)]
            elif typ in ("str","inlineStr"):
                value=(raw if typ=="str" else "".join(t.text or "" for t in inline.iter(NS+"t"))
                       if inline is not None else None)
            elif typ=="b":
                value=raw=="1"
            elif raw is None:
                value=None
            elif typ in ("n",""):
                num=float(raw)
                hold(math.isfinite(num),"FINITE_NUMBER")
                value=int(num) if num.is_integer() else num
            else:raise ValueError("HOLD_UNKNOWN_CELL_TYPE_"+typ)
            values[ord(col)-65]=value
        cells[n]=values
    hold(cells[1][0]=="Összefoglaló" and not any(any(v is not None for v in values) for row,values in cells.items() if row>384),"EXPECTED_384_ROW_SOURCE")
    teams=list(cells[1][1:])
    while teams and teams[-1] is None:teams.pop()
    hold(len(teams)==5 if require_legacy_team else len(teams) in (5,7),"SUPPORTED_TEAM_COLUMNS")
    hold(len(set(teams))==len(teams) and all(isinstance(t,str) and t.strip() for t in teams) and (not require_legacy_team or TEAM in teams),"EXPECTED_DISTINCT_TEAM_HEADERS")
    records=[];section=SECTIONS[0]
    for rownum in range(2,385):
        values=cells.get(rownum,[None]*len(columns))
        label=values[0]
        if not isinstance(label,str) or not label.strip():continue
        depth=len(label)-len(label.lstrip(" "))
        if depth==0:
            section=label.strip()
            hold(section in SECTIONS,"UNKNOWN_SECTION")
        records.append({"row":rownum,"section":section,"depth":depth,
                        "label":label.strip(),"values":values[1:1+len(teams)]})
    hold(tuple(x["label"] for x in records if x["depth"]==0)==SECTIONS[1:],
         "TOP_LEVEL_SECTIONS")
    hold(len(records)==374,"SOURCE_ROW_COUNT")
    return {"sha256":digest(path),"rows":records,"teams":teams,
            "sheet":"0","source_type":(
                "HISTORICAL_TEST_ROUND_EXPORT_NOT_CURRENT" if require_legacy_team
                else "UNVERIFIED_OPERATOR_EXCEL_NOT_CURRENT_PLAN")}
def compare_r156(readout,export):
    hold(export.get("schema")=="ECOSIM_R156_LOCAL_OPERATOR_EXPORT_V1" and
         export.get("capture_mode")=="HISTORICAL_REFERENCE" and
         export.get("kind")=="PLAN" and export.get("team")==TEAM and
         export.get("period")==1,"R156_HISTORICAL_PLAN")
    idx=readout["teams"].index(TEAM)
    overview={r["label"]:r["values"][idx] for r in readout["rows"]
              if r["section"]=="Összefoglaló"}
    factors={r["label"]:r["values"][idx] for r in readout["rows"]
             if r["section"]=="Összefoglaló" and
             r["label"] not in GROUPS and r["label"] not in ("Okosváros index","Piaci rangsor")}
    fact_rows=list(csv.DictReader(io.StringIO(export.get("factors_csv",""))))
    d={r["metric"]:float(r["value"]) for r in fact_rows}
    hold(len(factors)==29 and len(d)==30 and set(d)==set(factors)|{"Okosváros index"},
         "R156_29_FACTOR_IDENTITY")
    changes=[]
    for name in sorted(factors):
        p0=exact_number(factors[name],"FACTOR_P0")
        p1=exact_number(d[name],"FACTOR_P1")
        changes.append({"metric":name,"historical_p0_fact_or_baseline":p0,
                        "same_period_p1_plan_not_realized":p1,
                        "plan_minus_baseline":round(p1-p0,6)})
    initial=exact_number(overview["Okosváros index"],"P0_INDEX")
    plan=exact_number(d["Okosváros index"],"P1_INDEX")
    return {"matched_factor_labels":len(changes),"factor_deltas":changes,
            "p0_observed_index":initial,"p1_same_period_plan_index":plan,
            "index_plan_minus_observed":round(plan-initial,6),
            "p1_is_later_realized_fact":False,
            "source_trust":"EXCEL_P0_TO_R156_P1_PLAN_SAME_TEAM_SAME_TEST_PERIOD"}
def coverage(readout):
    selected=readout["teams"].index(TEAM)
    sec={}
    for name in SECTIONS:
        subset=[r for r in readout["rows"] if r["section"]==name and r["depth"]>0]
        sec[name]={"labelled_data_rows":len(subset),
                   "observed_numeric_or_text":sum(r["values"][selected] is not None for r in subset),
                   "null_not_zero":sum(r["values"][selected] is None for r in subset)}
    team_cov={}
    for i,team in enumerate(readout["teams"]):
        team_cov[team]={"observed_value_cells":sum(r["values"][i] is not None for r in readout["rows"]),
                        "missing_value_cells":sum(r["values"][i] is None for r in readout["rows"])}
    return {"by_section":sec,"by_team":team_cov,
            "workbook_loan_details_observed":sec["Hitelek"]["observed_numeric_or_text"]>0,
            "other_teams_finance_not_assumed_zero":all(
                 r["values"][i] is None
                 for r in readout["rows"] if r["section"]=="Pénzügyek"
                 for i,t in enumerate(readout["teams"]) if t!=TEAM)}
def finances(readout):
    idx=readout["teams"].index(TEAM)
    at={r["row"]:r["values"][idx] for r in readout["rows"]}
    keyed={k:exact_number(at[i],"FINANCE_ROW_"+str(i)) for i,k in ROWKEYS.items()}
    flow_gap=keyed["historical_total_receipts"]-keyed["historical_total_expenses"]-keyed["historical_net_earnings"]
    hold(abs(flow_gap)<=0.02,"HISTORICAL_FLOW_RECONCILIATION")
    assets_gap=sum(keyed[k] for k in
                   ("assets_market_eligible_subtotal","assets_restricted_subtotal","assets_illiquid_subtotal"))-keyed["historical_reported_total_assets"]
    return {"source_row_values":keyed,
            "flow_balance_residual_ecu":round(flow_gap,2),
            "flow_balance_check":"PASS_WITH_DISPLAY_ROUNDING_TOLERANCE",
            "assets_subtotal_disagreement_ecu":round(assets_gap,2),
            "assets_totals_reconciled":abs(assets_gap)<0.02,
            "historical_net_income_is_spendable_project_cash":False,
            "historical_grants_recognized_as_new_spendable_cash_ecu":0,
            "historical_workbook_loan_credit_limit":"UNKNOWN",
            "same_period_p1_reserve_plan_is_alternative_liquidity":False}
def link_r211(path):
    if path is None:return {"status":"NO_R211_JOIN_SUPPLIED","model_comparison_only":True}
    r=json.loads(Path(path).read_text(encoding="utf-8"))
    hold(r.get("schema")=="ECOSIM_R211_SOURCE_LINKED_INCREMENTAL_FINANCE_STRESS_V1"
         and r.get("status")=="PASS_SOURCE_LINKED_HISTORICAL_DELTA_STRESS_NOT_LIVE_FUNDING"
         and r.get("mode")=="historical-test" and r.get("gameplay_gate")=="STOP"
         and r.get("game_writes")==0 and r.get("combination_count")==36
         and r.get("incremental_stress_case_count")==108
         and r.get("actual_city_cash_balance") is None
         and r.get("verified_spendable_budget") is None
         and r.get("loan_authorization") is False
         and r.get("grant_disbursement_verified") is False
         and r.get("score_forecast_validated") is False,"R211_PARTIAL_FINANCE_GATES")
    plans=r.get("three_budget_tier_diagnostics")
    hold(isinstance(plans,list) and len(plans)==3 and
         {x.get("budget_tier") for x in plans}=={"LOW","MID","HIGH"} and
         all(x.get("not_a_real_funding_gap") is True for x in plans),"R211_DIAGNOSTICS")
    return {"status":"SOURCE_LINKED_PARTIAL_MODEL_CONTEXT_NOT_ADDITIVE_TO_P0_CASH",
            "r211_file_sha256":digest(path),"observed_p0_cash_not_ADDED_to_r211_delta":True,
            "observed_p0_income_not_REUSED_as_project_budget":True,
            "r211_historical_partial_scenarios":36,
            "r211_incremental_stress_cases":108,
            "three_model_relative_examples":plans,
            "approved_financing":False}

def diff_candidate_baseline(baseline,candidate,*,source_claim):
    """Source-identical change ledger; comparison does not authenticate 'current'."""
    hold(source_claim=="CURRENT_UNVERIFIED_OPERATOR_EXPORT","EXPLICIT_UNVERIFIED_SOURCE_LABEL")
    hold(baseline["sha256"]!=candidate["sha256"],"NEW_CANDIDATE_MUST_DIFFER_BY_SOURCE_SHA")
    hold(TEAM in baseline["teams"] and TEAM in candidate["teams"],"MATCHING_TEAM")
    before=baseline["teams"].index(TEAM)
    after=candidate["teams"].index(TEAM)
    hold(len(baseline["rows"])==len(candidate["rows"]),"SOURCE_ROW_COUNT_DRIFT")
    changed=[];missing=[];by_domain=defaultdict(int)
    for old,new in zip(baseline["rows"],candidate["rows"]):
        hold((old["row"],old["section"],old["depth"],old["label"])==
             (new["row"],new["section"],new["depth"],new["label"]),
             "CURRENT_WORKBOOK_STRUCTURE_CHANGED")
        previous=old["values"][before];observed=new["values"][after]
        if observed is None:
            if previous is not None:missing.append({"row":old["row"],"section":old["section"],"label":old["label"]})
            continue
        if previous!=observed:
            numeric=(type(previous) in (int,float) and type(observed) in (int,float))
            changed.append({"row":old["row"],"section":old["section"],"label":old["label"],
                            "historical_value":previous,"candidate_value":observed,
                            "numeric_difference_if_comparable":round(observed-previous,6) if numeric else None,
                            "server_authentication":"NOT_ATTESTED"})
            by_domain[old["section"]]+=1
    return {"status":"OPERATOR_EXPORT_DIFF_NOT_SERVER_AUTHENTICATED",
            "selected_team":TEAM,"candidate_sha256":candidate["sha256"],
            "new_source_is_cryptographically_verified_game_server":False,
            "candidate_missing_not_zero":missing,
            "changed_rows":changed,"changed_count":len(changed),
            "changed_by_domain":dict(sorted(by_domain.items())),
            "same_period_and_team_validation_must_be_done_separately":True,
            "gameplay_gate":"STOP"}

def build(readout,r156,projects,loan_csv=None,r211_path=None):
    matched=compare_r156(readout,r156);cov=coverage(readout);money=finances(readout)
    hold(len(projects.get("projects",[]))==35 and
         {p.get("id") for p in projects["projects"]}==set(range(1,36)),
         "HISTORICAL_35_CARD_CATALOG")
    running=sum(p.get("status_p1")=="Fut" for p in projects["projects"])
    hold(running==6,"SIX_HISTORICAL_RUNNING")
    rates=None
    if loan_csv:
        rr=list(csv.DictReader(io.StringIO(Path(loan_csv).read_text())))
        hold(len(rr)==7,"HISTORICAL_7_LOAN_ROWS")
        def rate(view):
            vals=[x for x in rr if x.get("view")==view and x.get("label")=="Kamat, %"]
            hold(len(vals)==1,"LOAN_RATE_"+view)
            return exact_number(float(vals[0]["p0_number"]),"HISTORICAL_LOAN_RATE")
        rates={"long_term_historical_interest_pct":rate("long_term"),
               "short_term_historical_interest_pct":rate("short_term"),
               "loan_credit_ceiling":"UNKNOWN","approved_cash_from_loans_ecu":0}
    allsections=set(SECTIONS)
    decision_input={"direct_29_factors":"HISTORICAL_P0_AVAILABLE",
                    "R156_p1_factor_delta":"AVAILABLE_AS_PLAN_NOT_CAUSAL",
                    "historical_project_cards":"35_WITH_SIX_RUNNING",
                    "institutional_capacity_and_staff":"OBSERVED_HISTORICAL_NO_DYNAMIC_EFFECT_CALIBRATION",
                    "transport_fleet_and_staff":"OBSERVED_HISTORICAL_NO_DYNAMIC_EFFECT_CALIBRATION",
                    "population_and_households":"OBSERVED_HISTORICAL_NO_DYNAMIC_EFFECT_CALIBRATION",
                    "company_counts_jobs_revenue":"OBSERVED_HISTORICAL_NO_DYNAMIC_EFFECT_CALIBRATION",
                    "finance_income_expense_assets":"OBSERVED_HISTORICAL_NOT_SPENDABLE",
                    "loans":("PARTIAL_7_ROWS_SOURCE" if rates else "WORKBOOK_NO_DETAIL"),
                    "actual_next_period_transition":"UNKNOWN_NO_TWO_CLOSED_FACTS",
                    "official_scoring":"UNKNOWN_SERVER_SIDE"}
    return {"schema":SCHEMA,"status":"PASS_HISTORICAL_FULL_CITY_CROSSWALK_LIVE_HOLD",
            "data_origin":"X-CHALLENGE_2026_TEST_ROUND_OPERATOR_EXPORTED_P0_PLUS_SAME_YEAR_P1_PLAN",
            "source_excel_sha256":readout["sha256"],
            "historical_r156_sha256":None,
            "selected_team":TEAM,"team_count":5,"labelled_rows":len(readout["rows"]),
            "top_level_sections":len(allsections),"section_coverage":cov,
            "R156_plan_bridge":matched,"finance":money,
            "historical_project_catalog":{"count":35,"active_p1":running},
            "historical_loans":rates,"R211_partial_finance_bridge":link_r211(r211_path),"domain_model_boundary":decision_input,
            "observed_history_can_replace_current_round":False,
            "actual_spendable_cash_ecu":None,"next_year_city_transition_validated":False,
            "official_score_predicted":False,"gameplay_gate":"STOP","game_writes":0}
def report(result):
    c=result["section_coverage"];finance=result["finance"];bridge=result["R156_plan_bridge"]
    lines=["# EcoSim R213 – teljes történeti városadat-egyeztetés",
           "","**TÖRTÉNETI TESZTFORDULÓ, NEM ÉLES FINANSZÍROZÁSI VAGY PONTOZÁSI BIZONYÍTÉK.**",
           "",f"Forrás SHA-256: `{result['source_excel_sha256']}`",
           f"Feldolgozott címkézett sorok: {result['labelled_rows']}; fő területek: {result['top_level_sections']}.",
           "", "| Városi felület | Címkézett alsorok | Értékek: kiválasztott csapat | Hiány |",
           "|---|---:|---:|---:|"]
    for section,item in c["by_section"].items():
        lines.append(f"| {section} | {item['labelled_data_rows']} | {item['observed_numeric_or_text']} | {item['null_not_zero']} |")
    lines.extend(["",f"29 tényező megfeleltetés R156 P1 tervvel: **{bridge['matched_factor_labels']}/29**.",
        f"SmartCity-index: P0 **{bridge['p0_observed_index']}**, ugyanazon forduló P1 **terv** **{bridge['p1_same_period_plan_index']}**.",
        f"P1−P0 indexkülönbség: **{bridge['index_plan_minus_observed']}**, **nem lezárt éves tényváltozás**.",
        "",f"Bevétel−kiadás−nettó eredmény különbség: {finance['flow_balance_residual_ecu']} ECU (kerekítési eltérés).",
        f"Vagyon-alsóösszegek és jelentett összvagyon eltérése: **{finance['assets_subtotal_disagreement_ecu']} ECU**; feloldatlan.",
        "Az üres konkurenscsapat-pénzügyi cellák **hiányzó megfigyelések**, nem nullák.",
        "A támogatási sorok és a p1 tartalékképzés **nem külön elkölthető összegek**.",
        "Nincs ismert hitelkeret; nem áll rendelkezésre két egymást követő lezárt FACT év.",
        "","## Következtetés",
        "A városi státuszadatok széles körben rendelkezésre állnak; a hiány főként a",
        "hatásmechanizmusok, a következő évi átmenetek és a tényleges pénzügyi",
        "jogosultság bizonyítása. Az eredeti projektkeresőt nem cseréljük le; ezt",
        "a tényleges forráslefedettséget mellé rendeljük. `GAME_ACTION_GATE=STOP`."
    ])
    return "\n".join(lines)+"\n"
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--workbook",type=Path,required=True)
    ap.add_argument("--r156",type=Path,required=True)
    ap.add_argument("--projects",type=Path,required=True)
    ap.add_argument("--loans-csv",type=Path)
    ap.add_argument("--r211-historical",type=Path)
    ap.add_argument("--identical-earlier-workbook",type=Path)
    ap.add_argument("--candidate-workbook",type=Path)
    ap.add_argument("--candidate-source-claim",default=None)
    ap.add_argument("--expected-workbook-sha",required=True)
    ap.add_argument("--out-dir",type=Path,required=True)
    a=ap.parse_args()
    hold(re.fullmatch("[0-9a-f]{64}",a.expected_workbook_sha) is not None,"EXPECTED_SHA")
    hold(digest(a.workbook)==a.expected_workbook_sha,"EXCEL_SOURCE_SHA_CHANGED")
    hold(not a.out_dir.exists(),"OUTPUT_MUST_BE_NEW")
    readout=load_xlsx(a.workbook)
    r156=json.loads(a.r156.read_text(encoding="utf-8"))
    cards=json.loads(a.projects.read_text(encoding="utf-8"))
    output=build(readout,r156,cards,a.loans_csv,a.r211_historical)
    if a.identical_earlier_workbook is not None:
        earlier=load_xlsx(a.identical_earlier_workbook)
        hold(earlier["teams"]==readout["teams"] and earlier["rows"]==readout["rows"],"EARLIER_WORKBOOK_ACTUAL_VALUES_DIFFER")
        output["earlier_original_excel_duplicate"]={"original_sha256":earlier["sha256"],"same_parsed_374_rows_and_five_teams":True,"different_file_bytes":earlier["sha256"]!=readout["sha256"]}
    output["historical_r156_sha256"]=digest(a.r156)
    output["historical_cards_sha256"]=digest(a.projects)
    if a.candidate_workbook is not None:
        output["candidate_source_diff"]=diff_candidate_baseline(readout,load_xlsx(a.candidate_workbook),source_claim=a.candidate_source_claim)
    a.out_dir.mkdir(mode=0o700,parents=True)
    (a.out_dir/"R213.json").write_text(json.dumps(output,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    (a.out_dir/"R213_HU.md").write_text(report(output),encoding="utf-8")
    print(json.dumps({"status":output["status"],"source_sha256":output["source_excel_sha256"],
       "rows":output["labelled_rows"],"factors":output["R156_plan_bridge"]["matched_factor_labels"],
       "asset_gap":output["finance"]["assets_subtotal_disagreement_ecu"],"game_writes":0,
       "out_dir":str(a.out_dir)},ensure_ascii=False))
if __name__=="__main__":main()
