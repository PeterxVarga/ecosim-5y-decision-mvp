#!/usr/bin/env python3
"""R226: actual, read-only ten-menu EcoSim P1 default-subview census.

Makes the existing R225 18-field source-ledger reusable with the 1 actually
observed long-loan field. The 27 selectors are navigation options (some nested);
NEVER treat them as 27 complete decision screens or assume their data.
No gameplay, session token, server API, programmatic browser click or guessing.
"""
from __future__ import annotations
import argparse,csv,hashlib,html,io,json,math,re,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"team-handoff/r225-periodic-control-intake"),
             str(ROOT/"ECOSIM_R162_INTEGRITY_REVIEW_RC/tools")]
from intake_r225 import parse_source,GROUPS as R225_GROUPS,SCHEMA as R225_SCHEMA
from json_integrity_r162 import read_json
from policy_tracks import load_tracks,policy_factor_replay,policy_money_replay
from observation_bundle_r152 import compile_bundle

SCHEMA="ECOSIM_R226_REAL_CURRENT_TEN_TOP_LEVEL_PAGES_VISIBLE_CONTROL_CENSUS_V1"
ROUTES=("summary","projects","institutions","transport","income","population",
        "corporations","loans","finance","analysis")
EXPECTED_NAV={
 "summary":(),
 "projects":("Gazdaságfejlesztés","Sport és Kultúra","Közlekedés","Környezet"),
 "institutions":("Oktatás","Művelődés és sport","Egészségügy","Szolgáltató",
                 "Városi hivatal","Szociális intézmények"),
 "transport":("Járművek","Közlekedési személyzet",
              "Belsőégésű motoros buszok","Elektromos buszok"),
 "income":("Szolgáltatások díjai","Adók","Állami törvények"),
 "population":("Lakosság száma","Foglalkozás, kereset","Egyéb adatok"),
 "corporations":("Kisvállalkozások","Közepes méretű vállalkozások",
                 "Nagyvállalkozások"),
 "loans":("Hosszú távú hitelek","Rövidlejáratú hitelek"),
 "finance":("Cash flow","Vagyoni kimutatás"),
 "analysis":(),
}
EXPECT_INPUTS={"summary":0,"projects":0,"institutions":7,"transport":5,
               "income":6,"population":0,"corporations":0,"loans":1,
               "finance":0,"analysis":0}
PRIVATE_STEMS={
 "institutions":"institutions_education",
 "transport":"transport_ice_bus",
 "income":"income_service_fees"}
NAV_RE=re.compile(r'<a href="https://edu.ecosim.hu/simulation/([^"]+)">')
BUTTON_RE=re.compile(r'<button title="([^"]+)"[^>]*>[^<]*</button>')
INPUT_RE=re.compile(r'<input\s+type="text"\s+value="([^"]*)"\s*/>')
TR_RE=re.compile(r'<tr>(.*?)</tr>',re.S)
TD_RE=re.compile(r'<td>(.*?)</td>',re.S)
def need(v,label):
    if not v:raise ValueError("HOLD_"+label)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def source_file(route,primary,previous):
    if route in PRIVATE_STEMS:
        return Path(previous)/(PRIVATE_STEMS[route]+".txt")
    return Path(primary)/(route+".txt")
def parse_page(route,primary,previous):
    path=source_file(route,primary,previous)
    need(path.is_file() and not path.is_symlink(),"SOURCE_FILE_"+route)
    raw=path.read_text(encoding="utf-8")
    head=raw[:600]
    need(raw.startswith("# SOURCE_URL=https://edu.ecosim.hu/simulation/"+route+"\n")
         and "# SOURCE_KIND=CONNECTED_BROWSER_VISIBLE_READONLY_NOT_SERVER_ATTESTED" in head,
         "SOURCE_URL_OR_KIND_"+route)
    need(all(t in raw for t in ("X-Challenge 2026 Selejtező","Piac: I",
        "Jutalom a nap végén","Periódus: 1/5")),"REAL_CURRENT_TEAM_PERIOD_"+route)
    body=raw.split("Periódus: 1/5",1)[1]
    actual=[x for x in NAV_RE.findall(raw) if x in ROUTES]
    need(set(actual)==set(ROUTES)-{route} and len(actual)==9,
         "TEN_MAIN_NAV_ROUTES_"+route)
    titles=[]
    for val in BUTTON_RE.findall(body):
        if val not in ("Nézet","Exportálás","Mentés","Start") and val not in titles:
            titles.append(val)
    need(tuple(titles)==EXPECTED_NAV[route],"CURRENT_SELECTOR_TOPOLOGY_"+route)
    all_input_count=raw.count("<input")
    text_inputs=INPUT_RE.findall(raw)
    need(len(text_inputs)==all_input_count==EXPECT_INPUTS[route],
         "DEFAULT_VIEW_EDITABLE_CELL_COUNT_"+route)
    # Critical: project Start buttons are separate game-write actions and NOT
    # allowed to enter the periodic editable text-input inventory.
    project_writes=raw.count('<button title="Start">') if route=="projects" else 0
    need(project_writes==0 or route=="projects","PROJECT_START_NOT_A_PERIODIC_TEXT_FIELD")
    return {
       "route":route,"view_class":"VISIBLE_ACTIVE_SUBVIEW_ONLY_NOT_ALL_SUBTABS",
       "url":"https://edu.ecosim.hu/simulation/"+route,
       "local_file_time_utc":datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat(),
       "source_sha256":sha(path),
       "selector_labels_visible":titles,
       "known_selector_labels_count":len(titles),
       "text_inputs_visible":len(text_inputs),
       "project_start_buttons_not_counted_as_periodic_inputs":project_writes,
       "unobserved_selector_contents_are_unknown":True},raw
def loan_control(raw):
    # Fail closed on changed or multiple loan input labels. No assumption
    # about the unseen short-term-loan selector or unknown loan cap.
    body=raw.split("Periódus: 1/5",1)[1]
    need("\nHosszú távú hitelek\n" in body and
         '<button title="Rövidlejáratú hitelek"></button>' in body,
         "ACTIVE_LONG_LOAN_VIEW")
    tables=re.findall(r"<table>(.*?)</table>",body,re.S)
    need(len(tables)==1,"LONG_LOAN_TABLE_COUNT")
    selected=[]
    for row in TR_RE.findall(tables[0]):
        cells=TD_RE.findall(row)
        need(row.count("<td>")==len(cells) and row.count("</td>")==len(cells),
             "LOAN_TABLE_WELL_FORMED")
        if len(cells)<3:continue
        inputs=INPUT_RE.findall(cells[2])
        need(len(inputs)<=1,"LONG_LOAN_ROW_INPUT_AMBIGUITY")
        if not inputs:
            need("<input" not in cells[2],"UNSUPPORTED_LOAN_INPUT_TYPE")
            continue
        need(len(cells)==3,"LOAN_EDITABLE_ROW_CELLS")
        value=html.unescape(cells[1]).strip()
        need(value=="0","LOAN_BASELINE_DRIFT")
        selected.append({"label":html.unescape(cells[0]).strip(),
                         "p0_visible_number":0.0,"p1_raw_input":html.unescape(inputs[0])})
    need(selected==[{"label":"Felvétel / Visszafizetés (+/-)",
                     "p0_visible_number":0.0,"p1_raw_input":""}],
         "EXACT_ONE_LONG_LOAN_EDIT_FIELD")
    return {
       "decision_key":"loans.long_term.delta_1",
       "domain":"loans","active_subview":"Hosszú távú hitelek",
       "section":"Hitelek/Hosszú távú hitelek",
       "label":selected[0]["label"],
       "p0_visible_number":0.0,"p0_raw":"0",
       "p1_visible_input_raw":selected[0]["p1_raw_input"],
       "p1_current_decision_value":None,
       "actual_allowed_min":None,"actual_allowed_max":None,
       "limit_source":"UNKNOWN_DYNAMIC_UI_CONSTRAINT",
       "factor_response":None,"cash_response_ecu":None,
       "recommended_value":None,"game_write_authorized":False,
       "policy_category":"other"
    }
def build(primary,previous,r225,r156,out):
    dest=Path(out).resolve()
    need(not dest.exists() and dest.parent.is_dir() and
         not dest.is_relative_to(ROOT.resolve()),"PRIVATE_NEW_OUTPUT")
    previous_receipt=read_json(Path(r225)/"R225_RECEIPT.json")
    need(previous_receipt.get("schema")==R225_SCHEMA and
         previous_receipt.get("observed_editable_controls")==18 and
         previous_receipt.get("R145_unknown_factor_effects_propagated")==18 and
         previous_receipt.get("R145_unknown_cash_impacts_propagated")==18 and
         previous_receipt.get("gameplay_gate")=="STOP" and previous_receipt.get("game_writes")==0,
         "ORIGINAL_R225_CURRENT_OBSERVED_18_CONTROLS_REQUIRED")
    original=read_json(Path(r156)/"R217_RECEIPT.json")
    _,state,_=compile_bundle(Path(r156)/"r156_immutable/manifest.json")
    need(original["round"]=="Selejtező" and original["market"]=="I" and
         original["team"]=="Jutalom a nap végén" and original["period"]==1 and
         original["r191_current_qualification"]=="HOLD_CAP_UNKNOWN_OR_ASSUMED" and
         original["game_writes"]==0 and state["market"]["maxProjectPerTurn"] is None,
         "CURRENT_ROUND_CAP_STILL_HOLD")
    state_time=datetime.fromisoformat(state["provenance"]["captured_at_local"]).astimezone(timezone.utc)
    census=[];loan=None
    for route in ROUTES:
        row,raw=parse_page(route,primary,previous)
        observed=datetime.fromisoformat(row["local_file_time_utc"])
        need(abs((observed-state_time).total_seconds())<=3600,
             "OUTSIDE_CURRENT_R156_60_MIN_WINDOW_"+route)
        census.append(row)
        if route in PRIVATE_STEMS:
            stem=PRIVATE_STEMS[route]
            need(row["source_sha256"]==
                 previous_receipt["sha256"]["periodic_page_sources"][stem],
                 "REUSE_REAL_R225_SOURCE_HASH_"+route)
            controls,hash_=parse_source(source_file(route,primary,previous),stem)
            need(hash_==row["source_sha256"] and len(controls)==EXPECT_INPUTS[route],
                 "R225_PARSE_REAL_INPUTS_"+route)
        if route=="loans":
            loan=loan_control(raw)
    controls=previous_receipt["controls"]+[loan]
    need(loan is not None and len(controls)==19 and
         len({x["decision_key"] for x in controls})==19,
         "EXACT_19_REAL_OBSERVED_INPUTS")
    need(sum(x["text_inputs_visible"] for x in census)==19 and
         len(census)==10,"ALL_TEN_TOP_LEVEL_MENUS_COVERED")
    need(sum(x["known_selector_labels_count"] for x in census)==27,
         "NAVIGATION_27_SELECTOR_TOPOLOGY")
    # The original R145 is reused as an UNKNOWN-propagation type contract
    # and never declares these editable controls as actual user choices.
    track={
      "schema":"ECOSIM_R145_POLICY_TRACKS_V1",
      "tracks":[{
        "track_id":"R226_UNKNOWN_EFFECT_SCHEMA_CONTRACT_NOT_ACTUAL_GAMEPLAY",
        "mode":"DOCUMENTED_OBSERVATION_ONLY",
        "assumption_note":"Read-only UI field existence; no selected current P1 action or calibrated policy impact",
        "actions":[{
            "year":1,"category":c["policy_category"],
            "decision_key":c["decision_key"],"duration":"ONE_YEAR",
            "factor_relative_percent":None,"annual_cash_delta_ecu":None,
            "source_evidence_id":"R226_CURRENT_VISIBLE_MENU_"+c["domain"],
            "assumption_note":"Read-only observed input, not authorized user action"
        } for c in controls]}]}
    dest.mkdir(mode=0o700)
    fi=dest/"R226_R145_UNKNOWN_TEST_ONLY.json"
    fi.write_text(json.dumps(track,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    parsed=load_tracks(fi)
    _,applied,unknown=policy_factor_replay(
        state["team"]["baseline_smartcity_factors"],parsed[0],1,1)
    cash=policy_money_replay(parsed[0],1,1)
    need(len(unknown)==19 and not applied and not cash["complete"] and
         len(cash["undisclosed_policy_cash_decisions"])==19,
         "R145_19_UNKNOWN_NONZERO_POLICY_EFFECTS")
    page_times=[datetime.fromisoformat(z["local_file_time_utc"]) for z in census]
    status={
      "schema":SCHEMA,
      "status":"PASS_TEN_CURRENT_VISIBLE_TOP_LEVEL_DEFAULT_VIEWS_NINETEEN_EDIT_FIELDS",
      "round":"Selejtező","market":"I","team":"Jutalom a nap végén","period":1,
      "source_class":"AUTHORIZED_CONNECTED_BROWSER_VISIBLE_NOT_SERVER_ATTESTED",
      "top_level_route_count":10,
      "observed_default_or_selected_subview_count":10,
      "distinct_selector_button_labels":27,
      "selector_buttons_are_nested_or_alternate_not_complete_decision_views":True,
      "all_selector_subview_contents_observed":False,
      "observed_editable_text_inputs":19,
      "original_R225_reused_input_count":18,
      "additional_long_loan_observed_input_count":1,
      "unknown_minmax_count":19,
      "unknown_p1_approved_decisions_count":19,
      "unknown_factor_effect_count":19,
      "unknown_cash_response_count":19,
      "original_R145_unknown_factor_effects_propagated":len(unknown),
      "original_R145_unknown_cash_effects_propagated":len(cash["undisclosed_policy_cash_decisions"]),
      "original_R145_cashflow_complete":cash["complete"],
      "actual_market_cap":None,"actual_spendable_project_cash":None,
      "actual_P1_policy_recommendation":None,
      "r191_actual_market_admission":"HOLD_CAP_UNKNOWN_OR_ASSUMED",
      "five_year_joint_policy_city_score_forecast":None,
      "gameplay_gate":"STOP","game_writes":0,
      "source_sha256":{"original_r225":sha(Path(r225)/"R225_RECEIPT.json"),
          "original_r156":sha(Path(r156)/"R217_RECEIPT.json"),
          "original_r156_manifest":sha(Path(r156)/"r156_immutable/manifest.json")},
      "earliest_operator_local_snapshot_utc":min(page_times).isoformat(),
      "latest_operator_local_snapshot_utc":max(page_times).isoformat(),
      "operator_local_observation_span_minutes":
          round((max(page_times)-min(page_times)).total_seconds()/60,3),
      "operator_local_time_is_not_server_attestation":True,
      "all_captured_default_views_within_60_min_of_R156":True,
      "r156_state_capture_time_utc":state_time.isoformat(),
      "routes":census,"controls":controls
    }
    (dest/"R226_RECEIPT.json").write_text(
        json.dumps(status,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n")
    buf=io.StringIO(newline="")
    writer=csv.writer(buf,lineterminator="\n")
    writer.writerow(["menu","editable_text_inputs_in_current_visible_view",
                     "selector_buttons","current_visible_source_sha256",
                     "other_subviews_fully_observed","source_is_server_attested"])
    for row in census:
        writer.writerow([row["route"],row["text_inputs_visible"],
          " | ".join(row["selector_labels_visible"]),row["source_sha256"],
          "NO","NO"])
    (dest/"R226_TEN_MENU_COVERAGE.csv").write_text(buf.getvalue())
    report=[
      "# R226 – 10 fő EcoSim-nézet, periódikus döntési tér felmérése","",
      "**Mind a tíz főmenü aktuálisan látható alap-/kiválasztott nézetét megfigyeltük.**",
      "**19 szerkeszthető szöveges mező látható**, ebből 18 a korábbi R225 része,",
      "egy az új hosszú távú hitel felvétel/visszafizetés mező.",
      "A 27 megjelenített alnézetválasztó gomb között lehetnek egymásba ágyazott",
      "és egymást kizáró nézetek; NEM jelent 27 teljesen feldolgozott döntési oldalt.",
      "Az összes mögöttes alnézet és teljes válaszfüggvény lefedettsége UNKNOWN.","",
      "| Főmenü | Jelenleg látható szöveges szerkesztőmezők | Nézetválasztó címkék száma |",
      "|---|---:|---:|"]
    for row in census:
        report.append(f"| {row['route']} | {row['text_inputs_visible']} | {row['known_selector_labels_count']} |")
    report += ["","A Projektek oldalon megjelenő Start gombok nem periódikus szövegmezők.",
      "P1 engedélyezett értékek: UNKNOWN (19/19); numerikus korlátok: UNKNOWN;",
      "valódi szakpolitikai tényezőhatások és cash-response: UNKNOWN.",
      "R145 19/19 ismeretlen hatást megtart; ez nem policy-optimalizálás.",
      "Legközelebbi kritikus megfigyelendő nézet: Bevételek → Adók.",
      "GAME_ACTION_GATE=STOP, játékírás 0.",""]
    (dest/"R226_HU.md").write_text("\n".join(report))
    print(json.dumps({"status":status["status"],"top_menus":10,
       "visible_inputs":19,"selectors":27,
       "unknown_factor_effects":len(unknown),"unknown_cash_effects":len(cash["undisclosed_policy_cash_decisions"]),
       "source_timing_minutes":status["operator_local_observation_span_minutes"],
       "game_writes":0,"private_output":str(dest)},ensure_ascii=False))
    return status
def main():
    a=argparse.ArgumentParser()
    a.add_argument("--primary-pages",required=True,type=Path)
    a.add_argument("--r225-pages",required=True,type=Path)
    a.add_argument("--r225-receipt",required=True,type=Path)
    a.add_argument("--r156-dir",required=True,type=Path)
    a.add_argument("--out-dir",required=True,type=Path)
    p=a.parse_args()
    build(p.primary_pages,p.r225_pages,p.r225_receipt,p.r156_dir,p.out_dir)
if __name__=="__main__":main()
