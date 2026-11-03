#!/usr/bin/env python3
"""R220: source-linked four-category UI review; never R192 full admission.

Reusable parser stays in R217. Source raw pages and this report are private.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from prepare_visible_r217 import (
    R162,TEAM,ROUND,MARKET,PERIOD,parse_summary,parse_project_cards,hold,sha)
from json_integrity_r162 import read_json

SCHEMA="ECOSIM_R220_CURRENT_ALL_35_VISIBLE_CARD_PARITY_V1"
CASES=(
    ("projects_economy","Gazdaságfejlesztés",1,14),
    ("projects_sport","Sport és Kultúra",15,24),
    ("projects_transport","Közlekedés",25,31),
    ("projects_environment","Környezet",32,35),
)
SOURCE_URL="https://edu.ecosim.hu/simulation/projects"
def view_page(folder,stem,section):
    p=Path(folder)/(stem+".txt")
    hold(p.is_file() and not p.is_symlink(),"MISSING_PRIVATE_PAGE_"+stem)
    s=p.read_text(encoding="utf-8")
    hold(s.startswith("# SOURCE_URL="+SOURCE_URL+"\n") and
         "# SOURCE_KIND=CONNECTED_BROWSER_VISIBLE_READONLY_NOT_SERVER_ATTESTED\n" in s[:400],
         "SOURCE_PROVENANCE_"+stem)
    if stem!="projects_economy":
        hold("# VIEW="+section+"\n" in s[:400],"CATEGORY_PROVENANCE_"+stem)
    hold(all(x in s for x in ("X-Challenge 2026 Selejtező","Piac: I",TEAM,
                              "Periódus: 1/5")),"MARKET_TEAM_PERIOD_"+stem)
    # The active category text occurs directly after the scenery on the page;
    # mere presence of the category's navigation button is not proof.
    section_header=s.split("Periódus: 1/5",1)[1].split(" - ",1)[0]
    hold("\n"+section+"\n" in section_header,"ACTIVE_CATEGORY_"+stem)
    return s,p

def verify(pages_dir,r217_dir,out_dir):
    pages_dir=Path(pages_dir)
    r217_dir=Path(r217_dir)
    dest=Path(out_dir)
    hold(not dest.exists() and dest.parent.is_dir(),"NEW_PRIVATE_OUTPUT_REQUIRED")
    prior=read_json(r217_dir/"R217_RECEIPT.json")
    hold(prior.get("schema")=="ECOSIM_R217_CURRENT_BROWSER_VISIBLE_PARTIAL_ADMISSION_V1"
         and prior.get("gameplay_gate")=="STOP" and prior.get("game_writes")==0
         and prior.get("r191_current_qualification")=="HOLD_CAP_UNKNOWN_OR_ASSUMED"
         and prior.get("running_ids")==[14,22,23,24,34,35]
         and prior.get("observed_project_statuses")==35,
         "ORIGINAL_R217_CAP_HOLD_SOURCE")
    for name,h in prior["source_text_sha256"].items():
        hold(sha(pages_dir/(name+".txt"))==h,"ORIGINAL_R217_INPUT_CHANGED_"+name)
    original=read_json(R162/"data/ecosim_projects_20261030.json")
    summary=(pages_dir/"summary.txt").read_text(encoding="utf-8")
    states=parse_summary(summary,original)
    items=[];checks=[];hashes={}
    for stem,section,first,last in CASES:
        visible,p=view_page(pages_dir,stem,section)
        r=parse_project_cards(visible,original,expected_ids=range(first,last+1))
        check={
           "category":section,
           "observed_ids":list(range(first,last+1)),
           "visible_card_count":r["count"],
           "visible_cost_parity":r["money_identical_to_historical_count"],
           "visible_effect_parity":r["effects_identical_to_historical_count"],
           "card_conditions_observed":False}
        hold(check["visible_cost_parity"]==r["count"] and
             check["visible_effect_parity"]==r["count"],
             "VISIBLE_CATALOG_DRIFT_"+stem)
        for card in r["captured_cards"]:
            expected_state=card["id"] in states["observed_running_project_ids"]
            hold((card["displayed_status"]=="Fut")==expected_state,
                 "SUMMARY_STATUS_DRIFT_"+str(card["id"]))
            hold(card["money_equal_to_historical"] and card["effects_equal_to_historical"],
                 "INVALID_CURRENT_CARD_"+str(card["id"]))
            hold(card["project_conditions_observed"] is False and
                 card["full_r192_current_card_validated"] is False,
                 "FALSE_CONDITION_COMPLETENESS")
            items.append({"id":card["id"],"name":card["name"],
                          "status":card["displayed_status"],
                          "costs":card["observed_money"],
                          "effects":card["observed_effects"],
                          "conditions_verified":False})
        hashes[stem]=sha(p);checks.append(check)
    hold(len(items)==35 and [x["id"] for x in items]==list(range(1,36)),
         "EXACT_35_UNIQUE_SEQUENTIAL_CARDS")
    visible_active=[x["id"] for x in items if x["status"]=="Fut"]
    hold(visible_active==states["observed_running_project_ids"]==
         [14,22,23,24,34,35],"ALL_CARD_STATUS_PARITY")
    result={
        "schema":SCHEMA,"status":"PASS_35_OF_35_VISIBLE_MONEY_EFFECTS_R192_CONDITIONS_HOLD",
        "source":"USER_CONNECTED_BROWSER_READONLY_VIEW_NOT_SERVER_ATTESTED",
        "team":TEAM,"market":MARKET,"round":ROUND,"period":PERIOD,
        "captured_category_count":4,"observed_card_count":35,
        "money_parity_count":35,"effect_parity_count":35,
        "historical_source":"ORIGINAL_R162_TEST_CARD_REFERENCE_NOT_ADMITTED_AS_CURRENT",
        "r217_receipt_sha256":sha(r217_dir/"R217_RECEIPT.json"),
        "source_sha256":hashes,
        "category_checks":checks,
        "running_ids":visible_active,
        "selected_new_project_ids":states["observed_new_selected_ids"],
        "unobserved_visible_card_ids":[],
        "project_conditions_count_verified":0,
        "complete_r192_definition_admitted":False,
        "market_project_start_cap_verified":False,
        "spendable_project_cash_verified":False,
        "r214_three_option_advice_authorized":False,
        "gameplay_gate":"STOP","game_writes":0,"cards":items}
    dest.mkdir(mode=0o700)
    (dest/"R220_RECEIPT.json").write_text(
         json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2,
                    allow_nan=False)+"\n",encoding="utf-8")
    report=[
       "# R220 — Selejtező I, mind a 35 látható projektkártya",
       "",
       "**35/35 projekt** költsége és megjelenített hatása",
       "egyezik a korábbi forráskatalógussal; a források aktuális",
       "böngészős nézetekből származnak, nem szerver által aláírt exportok.",
       "",
       "A hat futó projekt: 14, 22, 23, 24, 34, 35.",
       "Újonnan elindított projekt: 0.",
       "",
       "**Nem igazolt:** projektfeltételek, piaci projektlimit,",
       "ténylegesen szabad pénzügyi keret.",
       "Ez NEM teljes R192-kártyabefogadás; az R214 javaslat HOLD.",
       "**GAME_ACTION_GATE=STOP; játékírás 0.**",""]
    (dest/"R220_HU.md").write_text("\n".join(report),encoding="utf-8")
    return result
def main():
    a=argparse.ArgumentParser()
    a.add_argument("--pages-dir",required=True,type=Path)
    a.add_argument("--r217-dir",required=True,type=Path)
    a.add_argument("--out-dir",required=True,type=Path)
    o=a.parse_args()
    r=verify(o.pages_dir,o.r217_dir,o.out_dir)
    print(json.dumps({"status":r["status"],"observed_cards":r["observed_card_count"],
                      "money_parity":r["money_parity_count"],
                      "effect_parity":r["effect_parity_count"],
                      "r192_complete":r["complete_r192_definition_admitted"],
                      "game_writes":0},ensure_ascii=False))
if __name__=="__main__":main()
