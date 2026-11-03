#!/usr/bin/env python3
"""Strictly provenance-linked client formulas; no current server admission."""
from pathlib import Path
import argparse,json,re,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/"team-handoff/r228-excel-city-policy-join"),
             str(R/"ECOSIM_R162_INTEGRITY_REVIEW_RC/tools")]
from source_join_r228 import need,digest
from json_integrity_r162 import read_json
from observation_bundle_r152 import compile_bundle

SCHEMA="ECOSIM_R235_STATIC_FORMULAS_PARTIAL_POLICY_BOUNDS_NOT_AUTHORIZED_V1"
JS_PIN="5a56f45f6ecf56d444af6e1066f05f586c7230fefe0bff98d20dff4547d37a08"
SCHOOL=[
 ("Középiskolák","middleSchool","institutions_education.table_2.field_1",7),
 ("Általános iskolák","elementarySchool","institutions_education.table_3.field_1",13),
 ("Óvodák","kindergarten","institutions_education.table_4.field_1",16),
 ("Bölcsődék","nursery","institutions_education.table_5.field_1",10),
]
def build(jsfile,source_page,r225_file,r226_file,r234_file,manifest,out):
    out=Path(out).resolve()
    need(out.parent.is_dir() and not out.exists() and
         not out.is_relative_to(R.resolve()),"NEW_PRIVATE_RESULT")
    for f in (jsfile,source_page,r225_file,r226_file,r234_file,manifest):
        need(Path(f).is_file() and not Path(f).is_symlink(),"EXISTING_SOURCE_REQUIRED")
    need(digest(jsfile)==JS_PIN,"HISTORICAL_CLIENT_EXACT_SHA")
    old=read_json(r234_file);r225=read_json(r225_file);r226=read_json(r226_file)
    need(old.get("schema")==
         "ECOSIM_R234_ACTUAL_23_P1_CONTROL_BOUNDS_SOURCE_GATES_V1"
         and old.get("gameplay_gate")=="STOP"
         and old.get("game_writes")==0
         and old.get("current_numeric_minmax_pairs_verified")==0
         and len(old.get("matrix",[]))==23
         and old["source_sha256"]["R225"]==digest(r225_file)
         and old["source_sha256"]["R226"]==digest(r226_file),
         "ORIGINAL_R234_SOURCE_AND_STOP")
    need(r225["sha256"]["periodic_page_sources"]["institutions_education"]==
         digest(source_page)
         and r226["source_sha256"]["original_r225"]==digest(r225_file),
         "R225_R226_PAGE_SOURCE_CHAIN")
    _,state,_=compile_bundle(manifest)
    need(state["provenance"]["market"]=="I"
         and state["provenance"]["round"]=="Selejtező"
         and state["provenance"]["current_period"]==1
         and state["team"]["already_selected_new_project_ids_current_period"]==[]
         and state["market"].get("institutions") is None,
         "CURRENT_PARTIAL_MARKET_NO_CONFIG")
    source=Path(jsfile).read_text(encoding="utf8")
    page=Path(source_page).read_text(encoding="utf8")
    need("qs=(0,R.ci)((e,t,a)=>t<=0?e.market.institutions[a].startCount:" in source,
         "SCHOOL_COUNT_PREVIOUS_PERIOD_SOURCE")
    mapping={item["control_id"]:item for item in old["matrix"]}
    derived=[]
    for label,jsid,key,expected in SCHOOL:
        anchor='(0,R.H1)("institutions.education.".concat(t,".change"),e=>({min:1-qs(e,e.period-1,E.'+jsid+')}))'
        need(anchor in source,"SCHOOL_MINIMUM_FORMULA_"+jsid)
        ix=page.index(label)
        piece=page[ix:ix+770]
        match=re.search(r'<td>Szám</td><td>\s*([0-9 ]+)\s*</td>',piece)
        need(match is not None,"SCHOOL_P0_AMOUNT_ROW_"+jsid)
        count=int(match.group(1).replace(" ",""))
        need(count==expected and key in mapping and
             mapping[key]["p0_ui_observed"]==0 and
             mapping[key]["numeric_min_verified"] is None,
             "P0_SCHOOL_COUNT_AND_R234_CONTROL")
        derived.append({
          "control_id":key,"school":label,"current_period":1,
          "previous_period_school_count":count,
          "historical_client_formula":"MIN_CHANGE = 1 - PREVIOUS_SCHOOL_COUNT",
          "derived_client_min_change":1-count,
          "client_max_change":None,
          "server_attested_current_min":None,
          "server_attested_current_max":None,
          "complete_allowed_range":False,
          "usable_as_approved_game_action":False,
          "provenance":"PINNED_HISTORICAL_JS_PLUS_SHA_MATCHED_P0_VISIBLE_ROW",
        })
    # Explicit formula holds, but no market institution settings exported.
    extra=[]
    for typ,key,prior in [
       ("training","institutions_education.table_1.field_2",12000),
       ("development","institutions_education.table_1.field_3",50000)]:
        anchor='e.market.institutions[t].decisions.'+typ+'.min[e.period]'
        anchor_max='e.market.institutions[t].decisions.'+typ+'.max[e.period]'
        need(anchor in source and anchor_max in source,
             "EDUCATION_MARKET_MULTIPLIER_FORMULA_"+typ)
        need(mapping[key]["p0_ui_observed"]==prior,"EDUCATION_P0_BUDGET_"+typ)
        extra.append({
          "control_id":key,"previous_value_p0":prior,
          "client_min_formula":"PREV_VALUE * MARKET.INSTITUTIONS.EDUCATION.DECISIONS."+typ.upper()+".MIN[PERIOD]",
          "client_max_formula":"PREV_VALUE * MARKET.INSTITUTIONS.EDUCATION.DECISIONS."+typ.upper()+".MAX[PERIOD]",
          "current_market_multiplier_min":None,
          "current_market_multiplier_max":None,
          "current_client_min_amount":None,
          "current_client_max_amount":None,
          "server_attested_current_bounds":None,
          "universal_plus_minus_20_percent":False,
        })
    # Four tax fields intentionally carry no explicit per-field callback in
    # this table definition, but shared input constraints may still apply.
    four='tl=e=>({title:e,body:[(0,R.H1)("income.taxes.business"),(0,R.H1)("income.taxes.vehicle"),(0,R.H1)("income.taxes.communal"),(0,R.H1)("income.taxes.building")]})'
    need(four in source,"TAX_COMPONENT_FOUR_NO_LOCAL_BOUND_ARGUMENT")
    taxkeys=['tax.business','tax.vehicle','tax.communal','tax.building']
    need(all(k in mapping and mapping[k]["numeric_min_verified"] is None
             and mapping[k]["numeric_max_verified"] is None for k in taxkeys),
         "TAX_FOUR_R234_UNVERIFIED")
    doc={
       "schema":SCHEMA,"status":"PASS_FOUR_DERIVED_CLIENT_LOWER_BOUNDS_TWO_SYMBOLIC_MARKET_RANGES",
       "round":"Selejtező","market":"I","period":1,
       "origin":"PREVIOUS_HISTORICAL_JS_AND_OPERATOR_VISIBLE_P0_NOT_LIVE_SERVER_ATTESTATION",
       "school_change_client_lower_bounds":derived,
       "school_client_lower_bound_count":len(derived),
       "institution_annual_training_development_symbolic_bounds":extra,
       "symbolic_range_count":len(extra),
       "four_tax_client_table_has_no_explicit_limit_callback":True,
       "tax_server_legal_ceiling_unknown":True,
       "tax_current_effective_saved_p1_unknown":True,
       "rendered_p1_may_differ_from_HTML_VALUE_ATTRIBUTE":True,
       "screenshot_seen_in_chat_not_source_attested_by_this_local_runner":True,
       "current_r156_market_institution_multipliers_observed":False,
       "client_partial_bound_does_not_promote_R234_numeric_pair_count":True,
       "original_r234_current_verified_full_minmax_pairs":0,
       "real_accepted_policy_actions":None,
       "policy_cash_and_factor_effects":None,
       "source_sha256":{"client_historical_840_js":digest(jsfile),
                        "visible_institutions_text":digest(source_page),
                        "R225":digest(r225_file),"R226":digest(r226_file),
                        "R234":digest(r234_file),"R156_manifest":digest(manifest)},
       "next_evidence":"READ_ONLY_CURRENT_MARKET_INSTITUTIONS_MULTIPLIERS_AND_TAX_UPPER_BOUNDS",
       "gameplay_gate":"STOP","game_writes":0,
    }
    out.mkdir(mode=0o700)
    (out/"R235_RECEIPT.json").write_text(
         json.dumps(doc,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf8")
    lines=[
      "# R235 – ellenőrzött kliensoldali részleges döntési korlátok",
      "",
      "A korábbi R234 szerint 0/23 teljes aktuális, hitelesített numerikus "
      "min–max pár ismert. Ez továbbra is 0: itt csak **négy részleges "
      "kliensoldali minimum** ismert és két szimbolikus képlet.",
      "A szerver oldali érvényesítés és az aktuális market-config UNKNOWN.",
      "",
      "| Oktatási döntés | P0 darab | Kliensképlet szerinti min. zárás/nyitás | Maximum |",
      "|---|---:|---:|---|",
    ]
    for v in derived:
        lines.append(f"| {v['school']} | {v['previous_period_school_count']} | "
                     f"{v['derived_client_min_change']:+d} | UNKNOWN |")
    lines+=["",
       "Oktatás / Képzés: 12 000 × market.institutions.education.decisions.training.min[1] "
       "és max[1]. Szorzók: UNKNOWN.",
       "Oktatás / Fejlesztés: 50 000 × market.institutions.education.decisions.development.min[1] "
       "és max[1]. Szorzók: UNKNOWN.",
       "Adók: a régi kliens tábladefiníciója négy H1 mezőt jelenít meg explicit "
       "korlát-callback nélkül. A shared input és a szerver ettől még "
       "alkalmazhat határt; adómaximum: UNKNOWN.",
       "A felhasználói képernyőképen a P1 adómezőkben a P0-hoz hasonló "
       "alapértékek **látszanak**, de ebből nem bizonyított, hogy az "
       "értékek külön, szerverre mentett döntések. A HTML value-attribútum "
       "hiányos képet adhat a megjelenített inputértékről.",
       "Nincs valós játékbeli módosítás vagy engedélyezett döntés. "
       "R191/R192/R214 és GAME_ACTION_GATE: STOP.",
    ]
    (out/"R235_HU.md").write_text("\n".join(lines)+"\n",encoding="utf8")
    print(json.dumps({"status":doc["status"],
         "four_client_minima":[x["derived_client_min_change"] for x in derived],
         "symbolic_ranges":2,"fully_admitted_numeric_ranges":0,
         "game_writes":0},ensure_ascii=False))
    return doc

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for name in ("jsfile","source-page","r225","r226","r234","manifest","out-dir"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args()
    build(a.jsfile,a.source_page,a.r225,a.r226,a.r234,a.manifest,a.out_dir)
