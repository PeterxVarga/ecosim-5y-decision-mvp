#!/usr/bin/env python3
"""R205: join pre-existing read-only Library CSV evidence with R202/R204. No EcoSim access."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

FILES=("income.csv","loans.csv","rules.csv","observations.csv","source_index.csv")
COUNTS={"income.csv":49,"loans.csv":7,"rules.csv":5,"observations.csv":24,"source_index.csv":15}
SCHEMA="ECOSIM_R205_HISTORICAL_LIBRARY_SOURCE_RECONCILIATION_V1"

def hold(value,reason):
    if not value: raise ValueError("HOLD_"+reason)

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load_csv(path):
    with Path(path).open(encoding="utf-8-sig",newline="") as stream:
        reader=csv.DictReader(stream)
        hold(bool(reader.fieldnames) and len(reader.fieldnames)==len(set(reader.fieldnames)),"CSV_DUPLICATE_HEADERS")
        rows=list(reader)
    hold(all(None not in row and all(value is not None for value in row.values()) for row in rows),"CSV_SHAPE")
    return rows

def money(value):
    value=float(value)
    hold(math.isfinite(value),"NONFINITE")
    return value

def index_rows(rows,key):
    values={}
    for row in rows:
        token=row.get(key)
        hold(bool(token) and token not in values,"DUPLICATE_"+key.upper())
        values[token]=row
    return values

def validate(source_dir,profile,r202,r204,manifest):
    hold(manifest.get("schema")=="ECOSIM_R205_NORMALIZED_LIBRARY_SOURCE_MANIFEST_V1" and
         manifest.get("representation")=="LIBRARY_PARSED_NORMALIZED_CSV_NOT_ORIGINAL_BYTES" and
         set(manifest.get("sources",{}))==set(FILES),"LIBRARY_MANIFEST")
    for name in FILES:
        item=manifest["sources"][name]
        hold(str(item.get("file_id","")).startswith("file_") and
             item.get("normalized_sha256")==sha(source_dir/name),"LIBRARY_SOURCE_HASH_"+name)
    hold(profile["schema"]=="ECOSIM_R200_INPUT_PROFILE_V1" and profile["mode"]=="historical-test" and profile["gameplay_gate"]=="STOP","R200_MODE")
    hold(r202["schema"]=="ECOSIM_R202_TEST_REVENUE_AND_INSTITUTION_CALIBRATION_GATE_V1" and
         r202["status"]=="PASS_SOURCE_DIAGNOSTIC_HOLD_GLOBAL_CALIBRATION" and
         r202["gameplay_gate"]=="STOP" and r202["game_writes"]==0,"R202_NO_LIVE")
    hold(r204["schema"]=="ECOSIM_UNIFIED_HISTORICAL_DECISION_PACKET_V1" and
         r204["status"]=="PASS_PARTIAL_HISTORICAL_DECISION_SUPPORT_LIVE_HOLD" and
         r204["mode"]=="historical-test" and r204["gameplay_gate"]=="STOP" and r204["game_writes"]==0 and
         r204["decision"]["live"]=="HOLD","R204_NO_LIVE")
    hold(r204["source_hashes"]["finance"]==r202["source_hashes"]["finance"] and
         r204["source_hashes"]["institutions"]==r202["source_hashes"]["institutions"],"MODEL_SOURCE_HASH")
    rows={}
    for name in FILES:
        path=source_dir/name
        hold(path.is_file() and not path.is_symlink(),"MISSING_"+name)
        rows[name]=load_csv(path)
        hold(len(rows[name])==COUNTS[name],"ROW_COUNT_"+name)
    income=index_rows(rows["income.csv"],"row_id")
    loans=index_rows(rows["loans.csv"],"row_id")
    rules=index_rows(rows["rules.csv"],"heading")
    observed=index_rows(rows["observations.csv"],"observation_id")
    sources=index_rows(rows["source_index.csv"],"source_id")
    identity=profile["identity"]
    for name in ("income.csv","loans.csv","observations.csv"):
        for row in rows[name]:
            hold(row.get("team")==identity["team"] and row.get("market")==identity["market"] and
                 row.get("period")==str(identity["period"])+"/"+str(identity["period"]),"IDENTITY_"+name)
    for row in sources.values():
        scope=json.loads(row["scope"])
        hold(scope["team"]==identity["team"] and scope["market"]==identity["market"] and
             scope["period"]=="1/1" and identity["round"] in scope["competition"],"SOURCE_SCOPE")
    for row in observed.values():
        key=row["source_id"]
        hold(key in sources and row["source_url"]==sources[key]["url"],"OBSERVATION_SOURCE_ID")
    for row in rows["rules.csv"]:
        hold(row["source_url"] in {v["url"] for v in sources.values()},"RULE_SOURCE_URL")
    matched=[]
    for category,view in (("four_tax_channels","taxes"),("six_fee_channels","service_fees")):
        group=r202["observed_channel_groups"][category]
        hold(len(group)==(4 if category=="four_tax_channels" else 6),"R202_GROUP")
        for source in group:
            label=source["source_label"]
            # A single explicitly verified label variant: passenger transport income
            if category=="six_fee_channels" and source["channel"]=="transport":
                hold(label=="Tömegközlekedés","TRANSPORT_ALIAS_SOURCE")
                label="Személyszállítás"
            candidates=[row for row in income.values() if row["view"]==view and row["table_index"]=="0" and row["label"]==label]
            hold(len(candidates)==1,"CROSSWALK_"+str(source["channel"]))
            row=candidates[0]
            hold(abs(money(row["p0_number"])-money(source["p0_actual_raw"]))<1e-6 and
                 abs(money(row["p1_number"])-money(source["p1_target_raw"]))<1e-6,"R202_RECONCILIATION_"+str(source["channel"]))
            matched.append({"category":category,"model_channel":source["channel"],"source_row_id":row["row_id"],
                            "reused_r202_source_row_id":source["source_row_id"]})
    hold(len(matched)==10,"INCOME_R202_TEN")
    loan_rates={}
    for typ,source_id in (("long_term","S08"),("short_term","S09")):
        matching=[row for row in loans.values() if row["view"]==typ and row["label"]=="Kamat, %"]
        hold(len(matching)==1,"OBSERVED_LOAN_RATE_"+typ)
        rate=money(matching[0]["p0_number"])
        hold(rate==money(matching[0]["p1_number"]) and 0<rate<=100,"OBSERVED_LOAN_RATE_"+typ)
        witness=[row for row in observed.values() if row["source_id"]==source_id and
                 "Kamat" in row.get("source_location","")]
        hold(len(witness)==1,"LOAN_RATE_WITNESS_"+typ)
        cells=witness[0]["original_text"].split("\t")
        hold(len(cells)==3 and cells[0]=="Kamat, %" and
             rate==money(cells[1])==money(cells[2]),"LOAN_RATE_WITNESS_"+typ)
        loan_rates[typ]=rate
    hold(loan_rates["short_term"]>loan_rates["long_term"],"SHORT_RATE_NOT_HIGHER")
    long_rules=[row for row in rows["rules.csv"] if row["view"]=="long_term"]
    short_rules=[row for row in rows["rules.csv"] if row["view"]=="short_term"]
    hold(len(long_rules)==len(short_rules)==1 and
         "csak felvenni, vagy visszafizetni" in long_rules[0]["text_raw"] and
         "Automatikus" in short_rules[0]["text_raw"],"LOAN_RULE_TERMS")
    grant_rows={row["label"]:row for row in income.values() if row["view"]=="state_laws" and row["table_title"]=="Támogatások"}
    hold(set(grant_rows)=={"Fejlesztési célú állami támogatás","Vállalatoktól érkező fejlesztési támogatás"},"GRANT_RECORDED")
    result={
      "schema":SCHEMA,"mode":"historical-test","status":"PASS_PREVIOUSLY_UPLOADED_EVIDENCE_RECONCILED_LIVE_HOLD",
      "gameplay_gate":"STOP","game_writes":0,
      "ingest_representation":"LIBRARY_PARSED_NORMALIZED_CSV_NOT_BYTE_IDENTICAL_TO_ORIGINAL",
      "source_files":{name:{"normalized_sha256":sha(source_dir/name),"rows":len(rows[name])} for name in FILES},
      "source_count":len(sources),"observations_count":len(observed),"rules_count":len(rules),
      "income_rows":len(income),"loan_rows":len(loans),
      "r202_finance_channel_crosschecks":matched,
      "observed_long_term_loan_interest_pct":loan_rates["long_term"],
      "observed_short_term_loan_interest_pct":loan_rates["short_term"],
      "observed_finance_terms":{"long_term_borrow_or_repay_per_period":"DOCUMENTED",
          "short_term_automatic_if_negative":"DOCUMENTED",
          "loan_ceiling":"UNKNOWN","settlement_timing":"UNKNOWN"},
      "observed_development_grants":{"state_p0_raw":money(grant_rows["Fejlesztési célú állami támogatás"]["p0_number"]),
         "company_p0_raw":money(grant_rows["Vállalatoktól érkező fejlesztési támogatás"]["p0_number"]),
         "actually_spendable":"UNVERIFIED","timing":"UNKNOWN"},
      "coverage_updates":{
         "income":"HISTORICAL_INCOME_CSV_49_ROWS_10_R202_CHANNELS_RECONCILED",
         "loans":"HISTORICAL_LOAN_CSV_7_ROWS_RATES_OBSERVED_CEILINGS_UNKNOWN",
         "rules":"HISTORICAL_5_UI_RULES_DOCUMENTED",
         "observations":"HISTORICAL_24_PROVENANCE_LINKS_VERIFIED"},
      "unresolved":["Actual project-card to ledger monetary settlement","Current market loan ceilings",
         "Actual finance/admission budget and grant timing","Missing transport/population/business/other institution views",
         "Two consecutive closed FACT years","Server score and dynamic city model"],
      "live_city_model_validated":False,"verified_spendable_cash":False,"game_actions_permitted":False
    }
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-dir",type=Path,required=True)
    ap.add_argument("--profile",type=Path,required=True)
    ap.add_argument("--manifest",type=Path,required=True)
    ap.add_argument("--r202",type=Path,required=True)
    ap.add_argument("--r204",type=Path,required=True)
    ap.add_argument("--out-dir",type=Path,required=True)
    a=ap.parse_args()
    src=a.source_dir.resolve()
    hold(not src.is_relative_to(Path(__file__).resolve().parents[2]),"PRIVATE_SOURCES_INSIDE_PUBLIC_REPO")
    profile=json.loads(a.profile.read_text())
    r202=json.loads(a.r202.read_text())
    r204=json.loads(a.r204.read_text())
    hold(r204["report_hashes"]["R202"]==sha(a.r202),"R202_REPORT_IDENTITY")
    manifest=json.loads(a.manifest.read_text())
    result=validate(src,profile,r202,r204,manifest)
    hold(not a.out_dir.exists(),"OUTPUT_ALREADY_EXISTS")
    a.out_dir.mkdir(parents=True,mode=0o700)
    (a.out_dir/"R205.json").write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
    lines=["# EcoSim R205 – korábban feltöltött források tényleges visszaintegrálása",
           "","**Történeti forrásegyeztetés PASS; LIVE HOLD; GAME_ACTION_GATE=STOP.**",
           "","- 5 privát, normalizált CSV, összesen 100 forrássor",
           "- 15 forrásazonosító és 24 megfigyelés kapcsolatának ellenőrzése",
           "- 10 bevételi csatorna teljes p0/p1 egyezése az R202 számításaival",
           "- Hosszú hitel: "+str(result["observed_long_term_loan_interest_pct"])+"%; rövid hitel: "+str(result["observed_short_term_loan_interest_pct"])+"% (forrásból visszaegyeztetve)",
           "- Az R204 bizonyított forrás SHA és R202-jelentés azonossága megtartva",
           "","A hitelplafon, támogatás folyósítása, tényleges projektkeret, szerver pontozás",
           "és az évről évre változó városi állapot továbbra sem igazolt.",
           "A normalizált CSV nem bájtazonos az eredeti feltöltött CSV-vel.",
           "A 17 terv feltételes rangsora nem engedélyez éles műveletet.",
           "","GAME_ACTION_GATE=STOP; game_writes=0."]
    (a.out_dir/"R205_HU.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"status":result["status"],"r202_crosschecks":len(result["r202_finance_channel_crosschecks"]),"game_writes":0,"out":str(a.out_dir)}))
if __name__=="__main__":main()
