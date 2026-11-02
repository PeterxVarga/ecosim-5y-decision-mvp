#!/usr/bin/env python3
"""Source-typed EcoSim period-1 editable-control inventory, never gameplay.

R225 operates on authorized, read-only Browser-visible page text. Validates the
currently visible subviews only; unknown tab contents, P1 input values, value
bounds, score response and cash effect stay UNKNOWN. Original R145 policy
scenario loader is reused for a DRY-RUN UNKNOWN-response contract, never as
a recommended or actually selected decision.
"""
from __future__ import annotations
import argparse,csv,hashlib,html,io,json,math,re,sys
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
R162=ROOT/"ECOSIM_R162_INTEGRITY_REVIEW_RC"
sys.path.insert(0,str(R162/"tools"))
from json_integrity_r162 import read_json
from policy_tracks import load_tracks,policy_factor_replay,policy_money_replay
from observation_bundle_r152 import compile_bundle

SCHEMA="ECOSIM_R225_ACTUAL_PERIODIC_EDITABLE_SURFACE_INVENTORY_V1"
# Static expectations = UI page structure, not a claim that other tabs are covered.
GROUPS={
 "institutions_education":{
   "url":"/institutions","active_view":"Oktatás",
   "category":"staffing_payroll",
   "table_keys":("Oktatás/Döntések","Oktatás/Középiskolák",
     "Oktatás/Általános iskolák","Oktatás/Óvodák","Oktatás/Bölcsődék"),
   "expected_input_counts":(3,1,1,1,1),
   "expected_labels":(
      ("Bérek","Képzés","Fejlesztés"),
      ("Nyitás / Zárás (+/-)",),
      ("Nyitás / Zárás (+/-)",),
      ("Nyitás / Zárás (+/-)",),
      ("Nyitás / Zárás (+/-)",)),
   "other_views":("Művelődés és sport","Egészségügy",
     "Szolgáltató","Városi hivatal","Szociális intézmények")},
 "transport_ice_bus":{
   "url":"/transport","active_view":"Belsőégésű motoros buszok",
   "category":"transport",
   "table_keys":("Közlekedés/Belsőégésű buszok","Közlekedés/Infrastruktúra"),
   "expected_input_counts":(3,2),
   "expected_labels":(
      ("Busz beszerzés / eladás (+/-)","Beszerzett buszok életkora","Karbantartás"),
      ("Karbantartás","Kommunikáció")),
   "other_views":("Elektromos buszok","Közlekedési személyzet")},
 "income_service_fees":{
   "url":"/income","active_view":"Szolgáltatások díjai",
   "category":"service_fee",
   "table_keys":("Bevételek/Szolgáltatás bevételek",
       "Bevételek/Szolgáltatások díjai","Bevételek/Hatások"),
   "expected_input_counts":(0,6,0),
   "expected_labels":((),
       ("Tömegközlekedés / fő","Temetkezés / fő",
        "Parkolási díj (éves) / hely","Kommunális / fő",
        "Víz, csatorna, távhő / fő","Bérlakás díjak / fő"),()),
   "other_views":("Adók","Állami törvények")},
}
SOURCES=tuple(GROUPS)
TAB_COUNT=sum(len(c["other_views"])+1 for c in GROUPS.values()) # 6+3+3 = 12
TOTAL_CONTROLS=sum(sum(c["expected_input_counts"]) for c in GROUPS.values()) # 18
TR=re.compile(r"<tr>(.*?)</tr>",re.S)
TD=re.compile(r"<td>(.*?)</td>",re.S)
INPUT=re.compile(r'<input\s+type="text"\s+value="([^"]*)"\s*/>')
def need(ok,why):
    if not ok:raise ValueError("HOLD_"+why)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def parse_number(s):
    # Preserve raw UI string and normalized display number separately.
    s=html.unescape(s).strip()
    need(bool(re.fullmatch(r"-?[0-9][0-9 ,]*(?:\.[0-9]+)?",s)),
         "UNSUPPORTED_NUMERIC_DISPLAY")
    val=float(s.replace(" ","").replace(",",""))
    need(math.isfinite(val),"NUMERIC_FINITE")
    return val
def parse_source(path,stem):
    path=Path(path)
    config=GROUPS[stem]
    need(path.is_file() and not path.is_symlink(),"SOURCE_FILE_"+stem)
    raw=path.read_text(encoding="utf-8")
    head=raw[:550]
    need(raw.startswith("# SOURCE_URL=https://edu.ecosim.hu/simulation"+
                        config["url"]+"\n") and
         "# SOURCE_KIND=CONNECTED_BROWSER_VISIBLE_READONLY_NOT_SERVER_ATTESTED" in head and
         "# ACTIVE_VIEW="+config["active_view"]+"\n" in head,
         "SOURCE_PROVENANCE_"+stem)
    need(all(x in raw for x in ("X-Challenge 2026 Selejtező","Piac: I",
                                "Jutalom a nap végén","Periódus: 1/5")),
         "CURRENT_ROUND_IDENTITY_"+stem)
    visible=raw.split("Periódus: 1/5",1)[1]
    # Require active subview independently from navigation-button labels.
    before=visible.split("<table>",1)[0]
    need("\n"+config["active_view"]+"\n" in before,
         "ACTIVE_SUBVIEW_"+stem)
    tables=re.findall(r"<table>(.*?)</table>",visible,re.S)
    need(len(tables)==len(config["expected_input_counts"]),
         "ACTUAL_TABLE_COUNT_"+stem)
    parsed=[]
    for idx,(table,expected_labels,n_inputs,table_key) in enumerate(
       zip(tables,config["expected_labels"],config["expected_input_counts"],
           config["table_keys"])):
        found=[]
        for row in TR.findall(table):
            cols=TD.findall(row)
            need(row.count("<td>")==len(cols) and row.count("</td>")==len(cols),
                 "MALFORMED_TABLE_ROW_"+stem)
            text=html.unescape(re.sub(r"<[^>]*>","",cols[0])).strip() if cols else ""
            inputs=INPUT.findall(cols[2]) if len(cols)>=3 else []
            need(len(inputs)<=1,"MULTIPLE_INPUTS_IN_ROW_"+stem)
            if len(inputs)==0:
                # Unexpected alternate input controls must not be ignored.
                if len(cols)>=3:
                    need("<input" not in cols[2] and "<select" not in cols[2],
                         "UNSUPPORTED_EDIT_CONTROL_"+stem)
                continue
            need(len(cols)==3 and len(inputs)==1 and len(cols[1].strip())>0,
                 "EDITABLE_ROW_SHAPE_"+stem)
            need(re.fullmatch(r"[^<>]+",text) is not None,"INVALID_CONTROL_LABEL")
            p0_raw=html.unescape(re.sub(r"<[^>]*>","",cols[1])).strip()
            p1_raw=html.unescape(inputs[0]).strip()
            found.append({
               "decision_key":f"{stem}.table_{idx+1}.field_{len(found)+1}",
               "domain":stem,"active_subview":config["active_view"],
               "section":table_key,"label":text,
               "p0_raw":p0_raw,"p0_visible_number":parse_number(p0_raw),
               "p1_visible_input_raw":p1_raw,
               "p1_current_decision_value":None,
               "p1_value_source":"UNKNOWN_INPUT_BLANK_OR_DOM_NOT_ENOUGH" if not p1_raw
                                 else "VISIBLE_EDIT_FIELD_NOT_OPERATOR_APPROVED",
               "actual_allowed_min":None,"actual_allowed_max":None,
               "limit_source":"UNKNOWN_DYNAMIC_UI_WARNING_NOT_NUMERIC_RULE",
               "factor_response":None,"cash_response_ecu":None,
               "recommended_value":None,"game_write_authorized":False,
               "policy_category":("institution_capacity" if
                    stem=="institutions_education" and idx>0 else
                    "other" if stem=="institutions_education" and text in ("Képzés","Fejlesztés")
                    else config["category"])})
        need(tuple(c["label"] for c in found)==expected_labels and len(found)==n_inputs,
             "EXACT_KNOWN_CONTROL_LIST_"+stem+"_table_"+str(idx))
        parsed.extend(found)
    need(len(parsed)==sum(config["expected_input_counts"]),
         "CONTROL_COUNT_"+stem)
    return parsed,sha(path)
def build(pages,r156,result_dir):
    pages=Path(pages);r156=Path(r156);dest=Path(result_dir).resolve()
    need(not dest.exists() and dest.parent.is_dir() and
         not dest.is_relative_to(ROOT.resolve()),"NEW_PRIVATE_OUTPUT")
    receipt=read_json(r156/"R217_RECEIPT.json")
    need(receipt.get("schema")=="ECOSIM_R217_CURRENT_BROWSER_VISIBLE_PARTIAL_ADMISSION_V1"
         and receipt.get("team")=="Jutalom a nap végén"
         and receipt.get("round")=="Selejtező"
         and receipt.get("market")=="I" and receipt.get("period")==1
         and receipt.get("r191_current_qualification")=="HOLD_CAP_UNKNOWN_OR_ASSUMED"
         and receipt.get("game_writes")==0,"CURRENT_R156_UNVERIFIED_CAP_STATUS")
    _,state,_=compile_bundle(r156/"r156_immutable/manifest.json")
    need(state["market"]["maxProjectPerTurn"] is None and
         state["provenance"]["current_period"]==1 and
         state["provenance"]["round"]=="Selejtező",
         "MUST_NOT_PROMOTE_CAP_OR_PERIOD")
    controls=[];hashes={};local_capture_times={}
    state_time=datetime.fromisoformat(state["provenance"]["captured_at_local"]).astimezone(timezone.utc)
    for stem in SOURCES:
        c,h=parse_source(pages/(stem+".txt"),stem)
        controls.extend(c);hashes[stem]=h
        local_time=datetime.fromtimestamp((pages/(stem+".txt")).stat().st_mtime,timezone.utc)
        need(abs((local_time-state_time).total_seconds())<=3600,
             "NOT_WITHIN_60_MIN_OF_CURRENT_R156_"+stem)
        local_capture_times[stem]=local_time.isoformat()
    need(len(controls)==TOTAL_CONTROLS and
         len({c["decision_key"] for c in controls})==TOTAL_CONTROLS,
         "EXACT_ALL_ACTIVE_VIEW_EDIT_FIELDS")
    # Original R145 accepts documented observations only when effect/money is
    # explicitly UNKNOWN. Track is a SCHEMA/UNKNOWN propagation test, not
    # a set of actual operator decisions.
    track={
      "schema":"ECOSIM_R145_POLICY_TRACKS_V1",
      "tracks":[{
        "track_id":"R225_SCHEMA_TEST_ONLY_NO_GAMEPLAY_DECISIONS",
        "mode":"DOCUMENTED_OBSERVATION_ONLY",
        "assumption_note":"18 observed editable UI fields; actions only as UNKNOWN-impact test placeholders, NOT chosen or authorized game actions",
        "actions":[{
           "year":1,"category":c["policy_category"],
           "decision_key":c["decision_key"],
           "duration":"ONE_YEAR",
           "factor_relative_percent":None,
           "annual_cash_delta_ecu":None,
           "source_evidence_id":"R225_PRIVATE_VISIBLE_"+c["domain"],
           "assumption_note":"UI control exists, P0 observed; P1 decision and effects UNKNOWN. NOT A SELECTED ACTION",
           } for c in controls]}]}
    dest.mkdir(mode=0o700)
    skeleton=dest/"R225_R145_UNKNOWN_EFFECT_CONTRACT_TEST_ONLY.json"
    skeleton.write_text(json.dumps(track,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    tested=load_tracks(skeleton)
    need(len(tested)==1 and len(tested[0]["actions"])==TOTAL_CONTROLS,
         "REUSE_R145_SCHEMA")
    factors,applied,unmapped=policy_factor_replay(
        state["team"]["baseline_smartcity_factors"],tested[0],1,1)
    cash=policy_money_replay(tested[0],1,1)
    need(len(applied)==0 and len(unmapped)==TOTAL_CONTROLS and
         cash["complete"] is False and
         len(cash["undisclosed_policy_cash_decisions"])==TOTAL_CONTROLS,
         "R145_MUST_NOT_TREAT_UNKNOWN_AS_NO_EFFECT")
    data={
       "schema":SCHEMA,
       "status":"PASS_18_CURRENT_VISIBLE_EDIT_FIELDS_WITH_UNKNOWN_P1_LIMIT_EFFECT_AND_CASH",
       "provenance_class":"OPERATOR_BROWSER_VISIBLE_NOT_SERVER_ATTESTED",
       "round":"Selejtező","market":"I","team":"Jutalom a nap végén",
       "period":1,"source_pages":3,"observed_active_subviews":list(SOURCES),
       "observed_editable_controls":TOTAL_CONTROLS,
       "known_subview_count":TAB_COUNT,
       "known_unobserved_subviews":{stem:list(GROUPS[stem]["other_views"])
                                    for stem in SOURCES},
       "unobserved_subviews_count":TAB_COUNT-3,
       "local_capture_time_utc_by_view":local_capture_times,
       "capture_times_within_60_min_of_R156":True,
       "file_mtime_is_not_cryptographic_server_attestation":True,
       "missing_active_subview_values_are_unknown_not_zero":True,
       "p1_decision_values_verified":0,"numeric_bounds_verified":0,
       "calibrated_policy_effects_verified":0,
       "operator_authorized_changed_values":0,
       "R145_unknown_factor_effects_propagated":len(unmapped),
       "R145_unknown_cash_impacts_propagated":len(cash["undisclosed_policy_cash_decisions"]),
       "R145_cash_complete":cash["complete"],
       "R145_track_is_schema_test_only_not_user_policy":True,
       "actual_market_cap":None,"actual_project_spendable_cash":None,
       "current_R191_admission":"HOLD_CAP_UNKNOWN_OR_ASSUMED",
       "five_year_joint_policy_city_score_forecast":None,
       "live_optimized_policy_validated":False,
       "gameplay_gate":"STOP","game_writes":0,
       "sha256":{"current_r156_receipt":sha(r156/"R217_RECEIPT.json"),
                 "r156_manifest":sha(r156/"r156_immutable/manifest.json"),
                 "periodic_page_sources":hashes},
       "controls":controls}
    (dest/"R225_RECEIPT.json").write_text(
       json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n",
       encoding="utf-8")
    b=io.StringIO(newline="")
    w=csv.writer(b,lineterminator="\n")
    w.writerow(("decision_key","section","label","p0_visible_number",
                "p1_current_decision_value","limit_min","limit_max","factor_effect",
                "cash_delta","operator_approved"))
    for c in controls:
        w.writerow((c["decision_key"],c["section"],c["label"],
                    c["p0_visible_number"],"UNKNOWN","UNKNOWN","UNKNOWN",
                    "UNKNOWN","UNKNOWN","NO"))
    (dest/"R225_PERIODIC_UI_CONTROL_INVENTORY.csv").write_text(b.getvalue())
    lines=["# R225 – aktuális Selejtező I periódikus döntési mezők",
       "","**18 valóban látható módosítható mező** három aktív alnézetből:",
       "- Oktatás: 7", "- Belsőégésű buszok + infrastruktúra: 5",
       "- Szolgáltatások díjai: 6","",
       "**9 további ismert alnézet tartalma továbbra is megfigyeletlen.**",
       "A p0 értékek megfigyeltek. Az üres szerkesztőmező nem bizonyít",
       "érvényes p1 döntést. A numerikus minimum/maximum, a tényezőhatás",
       "és a pénzügyi hatás UNKNOWN; nem helyettesítjük nullával.",
       "",
       "Az eredeti R145 modellséma 18/18 UNKNOWN tényező- és 18/18 UNKNOWN",
       "pénzhatás-megőrzését ellenőriztük. Ez csak a séma integrációja;",
       "nem politikai döntés és nem öt évre kalibrált városi előrejelzés.",
       "Az R191 és R214 változatlanul HOLD.","GAME_ACTION_GATE=STOP.",""]
    (dest/"R225_HU.md").write_text("\n".join(lines))
    print(json.dumps({"status":data["status"],"fields":len(controls),
      "unobserved_subviews":data["unobserved_subviews_count"],
      "unknown_effects":len(unmapped),"unknown_cash":len(cash["undisclosed_policy_cash_decisions"]),
      "actual_cap":None,"game_writes":0,
      "private_dir":str(dest)},ensure_ascii=False))
    return data
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pages-dir",type=Path,required=True)
    p.add_argument("--r156-dir",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args();build(a.pages_dir,a.r156_dir,a.out_dir)
if __name__=="__main__":main()
