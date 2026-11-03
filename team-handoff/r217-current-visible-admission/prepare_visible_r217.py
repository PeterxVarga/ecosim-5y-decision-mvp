#!/usr/bin/env python3
"""R217: visible current EcoSim pages -> *partial* immutable R156 capture.

Read only source from connected Browser tab text written to a private directory.
No gameplay writes, no UI controls, no substitution of historical card data as
live evidence; fail closed on identity, 30 factors, 35 statuses, or unknown cap.
"""
from __future__ import annotations
import argparse,csv,hashlib,html,io,json,re,sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[2]
R162=ROOT/"ECOSIM_R162_INTEGRITY_REVIEW_RC"
sys.path[:0]=[str(R162/"tools"),str(ROOT/"team-handoff/r191-live-admission/tools")]
from readonly_intake_r156 import create_bundle, validate_export
from observation_bundle_r152 import compile_bundle
from json_integrity_r162 import read_json
from r142_proxy_reference import COEFF
from admission_r191 import AdmissionHold,validate_state

SCHEMA="ECOSIM_R217_CURRENT_BROWSER_VISIBLE_PARTIAL_ADMISSION_V1"
SRC_URL="https://edu.ecosim.hu/simulation/"
TEAM="Jutalom a nap végén"
ROUND="Selejtező"
MARKET="I"
PERIOD=1
WEIGHTS={"Gazdaság":0.25,"Környezet":0.2,"Kormányzás":0.15,
         "Életkörülmények":0.15,"Mobilitás":0.1,"Emberek":0.15}
HEAD=re.compile(r"<tr><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td></tr>",re.S)
PROJECT=re.compile(r"(?m)^(\d{1,2}) - ([^\n]+)$")
COST_LABELS={
 "Indítási költség":"startup_cost",
 "Fenntartási költség":"maintenance_cost",
 "Beruházás":"investment",
 "Fejlesztési támogatás a partnervállalattól":"partner_support",
}
def hold(cond,why):
    if not cond:raise ValueError("HOLD_"+why)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def number(text):
    t=html.unescape(str(text))
    t=re.sub(r"[\s\u00a0,]","",t)
    if t=="-0":return 0.0
    return float(t)
def rows(text):
    return [(html.unescape(x).strip(),html.unescape(a).strip(),html.unescape(b).strip())
            for x,a,b in HEAD.findall(text)]
def readpage(folder,key):
    p=Path(folder)/(key+".txt")
    hold(p.is_file() and not p.is_symlink(),"PAGE_FILE_MISSING_"+key)
    raw=p.read_text(encoding="utf-8")
    url=SRC_URL+("projects" if key=="projects_economy" else key)
    hold(raw.startswith("# SOURCE_URL="+url+"\n") and
         "SOURCE_KIND=CONNECTED_BROWSER_VISIBLE_READONLY_NOT_SERVER_ATTESTED" in raw[:350],
         "PAGE_PROVENANCE_"+key)
    hold(all(x in raw for x in (ROUND,"Piac: "+MARKET,TEAM,"Periódus: 1/5")),
         "ROUND_IDENTITY_"+key)
    return raw,p

def csvdata(headers,rs):
    s=io.StringIO(newline="")
    w=csv.writer(s,lineterminator="\n")
    w.writerow(headers);w.writerows(rs)
    return s.getvalue()

def parse_summary(summary,historical):
    hold("Projekt táblázat" in summary and "SmartCity index" in summary,"SUMMARY_TABLES")
    metrics,projects_section=summary.split("Projekt táblázat",1)
    present=rows(metrics)
    source={label:(a,b) for label,a,b in present}
    expected=set(COEFF)|{"Okosváros index"}
    hold(expected.issubset(source) and len(COEFF)==29,"EXACT_FACTOR_NAMES")
    f=[]
    for name in sorted(COEFF):
        a,b=source[name]
        hold(b and b!="-","MISSING_CURRENT_PLAN_FACTOR_"+name)
        v=number(b)
        hold(0<=v<=100,"BAD_PLAN_FACTOR_"+name)
        f.append((name,format(v,".12g")))
    p0,p1=map(number,source["Okosváros index"])
    f.append(("Okosváros index",format(p1,".12g")))
    projectrows=[r for r in rows(projects_section) if r[0]]
    names=[p["name"] for p in historical["projects"]]
    hold(len(projectrows)==35 and len(names)==35,"ALL_35_PROJECT_STATES")
    captured=[];running=[];new=[]
    for i,(title,p0_state,p1_state) in enumerate(projectrows,1):
        hold(title==names[i-1],"HISTORICAL_CARD_NAME_ID_DRIFT_"+str(i))
        hold(p0_state in ("Fut","Nem fut") and p1_state in ("Fut","Nem fut"),
             "UNKNOWN_STATE_"+str(i))
        before=p0_state=="Fut"
        after=p1_state=="Fut"
        hold(not (before and not after),"UNEXPECTED_PROJECT_STOP_"+str(i))
        selected=after and not before
        captured.append((i,str(before).lower(),str(selected).lower()))
        if before:running.append(i)
        if selected:new.append(i)
    hold(len(running)==6,"PROJECT_RUNNING_COUNT_DRIFT")
    return {"factors_csv":csvdata(["metric","value"],f),
            "projects_csv":csvdata(["project_id","previous_running","selected_new"],captured),
            "observed_running_project_ids":running,"observed_new_selected_ids":new,
            "observed_index_p0":p0,"observed_index_p1_plan":p1,
            "index_is_approved_official_result":False,
            "observed_35_project_statuses":True}

def parse_finance(finance,loans):
    hold(finance.count("<table>")>=2,"FINANCE_TABLES")
    expenditure,receipts=finance.split("Bevételek\n",1)
    exp=rows(expenditure);income=rows(receipts)
    def find(ls,label):
        matched=[(a,b) for name,a,b in ls if name==label]
        hold(len(matched)>=1 and len(set(matched))==1,"FINANCE_ROW_"+label)
        return tuple(map(number,matched[0]))
    result={
        "observed_p0_and_p1": {
           "net_earnings":find(exp,"A periódus nettó eredményessége"),
           "total_expenses":find(exp,"Kiadások összesen"),
           "total_receipts":find(income,"Bevételek összesen"),
           "reserve_transfer":find(exp,"Tartalékképzés / átvezetés"),
           "prior_year_cash":find(income,"Előző év végi pénzállomány"),
           "state_development_grant":find(income,"Fejlesztési célú állami támogatás"),
           "company_development_grant":find(income,"Vállalatoktól érkező fejlesztési támogatás"),
           "loans_drawn":find(income,"Hitelfelvétel"),
           "project_line":find(exp,"Projekt - egyedi alapon összesen")
        },
        "observed_spendable_project_cash_ecu":None,
        "confirmed_committed_costs_ecu":None,
        "finance_is_officially_approved":False,
        "p1_reserve_is_verified_spendable":False,
        "grants_addable_to_project_budget":False,
    }
    loan_rows=rows(loans)
    interest=[(number(a),number(b)) for name,a,b in loan_rows if name=="Kamat, %"]
    hold(len(interest)==1 and interest[0]==(7.5,7.5),"LONG_INTEREST")
    result["long_loan_interest_p0_p1"]=interest[0]
    result["observed_long_loan_balance_p0_p1"]=[
        number(a) for name,a,b in loan_rows if name=="Záró hitel állomány"
    ]
    hold(len(result["observed_long_loan_balance_p0_p1"])==1,"LONG_LOAN_BALANCE")
    result["short_loan_cap_ecu"]=None
    result["long_loan_cap_ecu"]=None
    return result

def parse_project_cards(text,historical,*,expected_ids=None):
    matches=list(PROJECT.finditer(text))
    expected=list(range(1,15)) if expected_ids is None else list(expected_ids)
    hold(len(matches)==len(expected) and [int(m.group(1)) for m in matches]==expected,
         "FIRST_FOURTEEN_ECONOMY_CARDS" if expected_ids is None else "EXPECTED_CURRENT_CATEGORY_CARD_IDS")
    source={x["id"]:x for x in historical["projects"]}
    results=[];valid_money=0;valid_effects=0
    for i,m in enumerate(matches):
        id_=int(m.group(1));name=m.group(2).strip()
        seg=text[m.end():matches[i+1].start() if i+1<len(matches) else len(text)]
        hold(source[id_]["name"]==name,"CARD_NAME_DRIFT_"+str(id_))
        money={}
        for label,k in COST_LABELS.items():
            found=re.findall(r"(?m)^"+re.escape(label)+r":\s*([-\d,. ]+)\s*$",seg)
            hold(len(found)==1,"MONEY_FIELD_"+str(id_)+"_"+k)
            money[k]=number(found[0])
        money_agrees=all(money[k]==source[id_][k] for k in money)
        if money_agrees:valid_money+=1
        eff=[]
        if "Hatások\n" in seg:
            body=seg.split("Hatások\n",1)[1].split("<img",1)[0]
            for line in body.splitlines():
                match=re.fullmatch(r"([^\n:]+):\s*(-?[\d.,]+)%",line.strip())
                if match:eff.append({"metric":match.group(1),"value_percent":number(match.group(2))})
        hist_eff=source[id_]["effects"]
        eff_equal=(len(eff)==len(hist_eff) and
                   sorted((e["metric"],e["value_percent"]) for e in eff)==
                   sorted((e["metric"],float(e["value_percent"])) for e in hist_eff))
        if eff_equal:valid_effects+=1
        running='<button>Fut</button>' in seg
        results.append({"id":id_,"name":name,"displayed_status":"Fut" if running else "Start",
           "observed_money":money,"money_equal_to_historical":money_agrees,
           "observed_effects":eff,"effects_equal_to_historical":eff_equal,
           "project_conditions_observed":False,
           "full_r192_current_card_validated":False})
    return {"captured_cards":results,"count":len(results),
            "money_identical_to_historical_count":valid_money,
            "effects_identical_to_historical_count":valid_effects,
            "remaining_categories_unobserved":35-len(results),
            "full_current_catalog_ready":False}

def build(folder,dest):
    folder=Path(folder);dest=Path(dest)
    hold(not dest.exists() and dest.parent.is_dir(),"NEW_PRIVATE_OUTPUT")
    original=read_json(R162/"data/ecosim_projects_20261030.json")
    raw={}
    for name in ("summary","finance","loans","projects_economy","income"):
        raw[name],_=readpage(folder,name)
    observed=parse_summary(raw["summary"],original)
    finance=parse_finance(raw["finance"],raw["loans"])
    cards=parse_project_cards(raw["projects_economy"],original)
    hold(cards["count"]==14,"INCOMPLETE_CARD_CATEGORY")
    hold(cards["captured_cards"][13]["displayed_status"]=="Fut" and
         14 in observed["observed_running_project_ids"],"STATUS_CROSS_PAGE_14")
    # R156 permits incomplete market limits as explicit null. R191 will refuse
    # this partial admission; never silently replace a cap from prior rounds.
    template=read_json(R162/"inputs/official_state.template.json")
    market={k:None for k in template["market"]}
    market["smartcity_total_weights"]=WEIGHTS
    market["loan_rate_long"]=finance["long_loan_interest_p0_p1"][1]
    team={"project1_active_previous_period":1 in observed["observed_running_project_ids"],
          "already_selected_new_project_ids_current_period":observed["observed_new_selected_ids"]}
    now=datetime.now(ZoneInfo("Europe/Budapest")).replace(microsecond=0).isoformat()
    packet={"schema":"ECOSIM_R156_LOCAL_OPERATOR_EXPORT_V1",
            "capture_mode":"CURRENT_READONLY","kind":"PLAN",
            "team":TEAM,"market":MARKET,"round":ROUND,"period":PERIOD,
            "captured_at_local":now,
            "source_evidence_id":"R217_CONNECTED_BROWSER_VISIBLE_SUMMARY_20261102",
            "source_note":"Read-only visible EcoSim summary page, operator-declared; not authenticated score or finance approval.",
            "factors_csv":observed["factors_csv"],"projects_csv":observed["projects_csv"],
            "parameters":{"market":market,"team":team},
            "field_sources":{
                "factors":SRC_URL+"summary",
                "projects":SRC_URL+"summary",
                "market_index_weights":SRC_URL+"summary",
                "finance":SRC_URL+"finance",
                "other":SRC_URL+"loans"},
           }
    validate_export(packet)
    dest.mkdir(mode=0o700)
    (dest/"R217_R156_CURRENT_READONLY_PARTIAL.json").write_text(
        json.dumps(packet,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    immutable,receipt=create_bundle(packet,dest/"r156_immutable")
    _,state,_=compile_bundle(immutable/"manifest.json")
    hold(state["provenance"]["current_period"]==1 and
         state["team"]["initially_active_project_ids"]==observed["observed_running_project_ids"],
         "R156_35_STATUS_BUNDLE")
    r191="UNKNOWN"
    try:validate_state(state,mode="current")
    except AdmissionHold as e:r191=str(e)
    hold("CAP_UNKNOWN" in r191,"MUST_HOLD_CURRENT_CAP")
    sourcehashes={name:sha(folder/(name+".txt")) for name in raw}
    result={
        "schema":SCHEMA,
        "status":"PASS_PARTIAL_CURRENT_R156_BUNDLE_R191_HOLD_CAP_AND_FINANCE",
        "source":"CONNECTED_BROWSER_VISIBLE_CONTENT_NOT_SERVER_ATTESTED",
        "team":TEAM,"market":MARKET,"round":ROUND,"period":1,
        "source_text_sha256":sourcehashes,
        "source_page_count":len(raw),
        "source_r156_packet_sha256":sha(dest/"R217_R156_CURRENT_READONLY_PARTIAL.json"),
        "r156_immutable_manifest_sha256":sha(immutable/"manifest.json"),
        "factor_count":29,"index_p0":observed["observed_index_p0"],
        "index_p1_plan":observed["observed_index_p1_plan"],
        "observed_project_statuses":35,
        "running_ids":observed["observed_running_project_ids"],
        "newly_selected_ids":observed["observed_new_selected_ids"],
        "economy_cards":cards,"finance_snapshot":finance,
        "r191_current_qualification":"HOLD_"+r191,
        "observed_max_project_per_turn":None,
        "total_current_card_definitions_verified":False,
        "verified_spendable_cash_ecu":None,
        "owner_approved_gameplay":False,
        "gameplay_gate":"STOP","game_writes":0,
        "next_required_sources":[
             "Current verified market maxProjectPerTurn and cap_source",
             "Full 35 current project-card definitions including conditions and effects, across all four categories",
             "Current same-period operator-observed spendable project funds and commitments, separately from reserve/earnings"
        ],
    }
    (dest/"R217_RECEIPT.json").write_text(
        json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n",
        encoding="utf-8")
    (dest/"R217_PROJECT_STATUS.csv").write_text(observed["projects_csv"])
    (dest/"R217_P1_FACTORS.csv").write_text(observed["factors_csv"])
    print(json.dumps({"status":result["status"],"project_states":35,
        "active_ids":result["running_ids"],"index_plan":result["index_p1_plan"],
        "current_cards_observed":cards["count"],
        "R191":result["r191_current_qualification"],"game_writes":0,
        "private_dir":str(dest)},ensure_ascii=False))
    return result
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--browser-text-dir",required=True,type=Path)
    p.add_argument("--out-dir",required=True,type=Path)
    a=p.parse_args()
    build(a.browser_text_dir,a.out_dir)
if __name__=="__main__":main()
