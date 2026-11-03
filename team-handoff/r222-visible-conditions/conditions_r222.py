#!/usr/bin/env python3
"""R222: actual current EcoSim *displayed* project condition proof.

Preserve source time separation and original R192 same-hour gate. No browser
interaction, no game writes, no fabricated market cap or finance.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sys
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/"team-handoff/r217-current-visible-admission"),
             str(ROOT/"team-handoff/r191-live-admission/tools"),
             str(ROOT/"ECOSIM_R162_INTEGRITY_REVIEW_RC/tools")]
from prepare_visible_r217 import parse_project_cards,parse_summary,R162
from qualify_all_views_r220 import CASES,view_page,SCHEMA as R220_SCHEMA
from catalog_gate_r192 import _card,validate_catalog,CatalogHold
from json_integrity_r162 import read_json
from observation_bundle_r152 import compile_bundle

SCHEMA="ECOSIM_R222_ALL_35_VISIBLE_PROJECT_CONDITIONS_PROOF_V1"
def need(x,why):
    if not x:raise ValueError("HOLD_"+why)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def segments(raw):
    matches=list(re.finditer(r"(?m)^(\d{1,2}) - ([^\n]+)$",raw))
    return {int(m.group(1)):raw[m.end():matches[i+1].start() if i+1<len(matches) else len(raw)]
            for i,m in enumerate(matches)}
def parse_conditions(section,project_id):
    # Extract displayed conditions from a complete card, not prior R162 data.
    hits=section.count("Projekt feltételek\n")
    need(hits<=1,"DUPLICATE_CONDITION_SECTION_"+str(project_id))
    if not hits:
        need("feltételek" not in section.casefold(),"UNPARSED_CONDITION_HEADER_"+str(project_id))
        return [],"NO_CONDITION_SECTION_DISPLAYED"
    a=section.index("Projekt feltételek\n")
    b=section.find("Hatások\n",a)
    need(b>a,"CONDITION_MUST_PRECEDE_EFFECTS_"+str(project_id))
    lines=[v.strip() for v in section[a+len("Projekt feltételek\n"):b].splitlines()
           if v.strip()]
    need(0<len(lines)<=12 and len(lines)==len(set(lines)),
         "INVALID_OR_DUPLICATE_CONDITIONS_"+str(project_id))
    need(all(" — " in v and v.endswith(" — Fut") for v in lines),
         "UNSUPPORTED_DISPLAYED_CONDITION_GRAMMAR_"+str(project_id))
    return lines,"DISPLAYED_EXPLICIT_CONDITION"
def audit(pages_dir,r217_dir,r220_file,rulebook,out):
    pages_dir=Path(pages_dir);r217_dir=Path(r217_dir);r220_file=Path(r220_file)
    out=Path(out)
    need(not out.exists() and out.parent.is_dir() and
         not out.resolve().is_relative_to(ROOT.resolve()),"NEW_PRIVATE_OUTPUT")
    prior=read_json(r217_dir/"R217_RECEIPT.json")
    proof=read_json(r220_file)
    need(prior.get("schema")=="ECOSIM_R217_CURRENT_BROWSER_VISIBLE_PARTIAL_ADMISSION_V1" and
         proof.get("schema")==R220_SCHEMA and
         proof.get("r217_receipt_sha256")==sha(r217_dir/"R217_RECEIPT.json") and
         proof.get("observed_card_count")==35 and
         proof.get("money_parity_count")==35 and
         proof.get("effect_parity_count")==35 and
         proof.get("gameplay_gate")=="STOP" and proof.get("game_writes")==0,
         "PINNED_R217_R220_NO_WRITE_PROOF")
    _,state,_=compile_bundle(r217_dir/"r156_immutable/manifest.json")
    need(state["market"]["maxProjectPerTurn"] is None and
         state["provenance"]["round"]=="Selejtező" and
         state["provenance"]["market"]=="I" and
         state["team"]["initially_active_project_ids"]==[14,22,23,24,34,35],
         "ACTUAL_R156_CAP_UNVERIFIED")
    orig=read_json(R162/"data/ecosim_projects_20261030.json")
    historical={c["id"]:c for c in orig["projects"]}
    cards=[];observed_conditions={};source_mtimes={};sources={}
    for stem,category,first,last in CASES:
        raw,p=view_page(pages_dir,stem,category)
        need(sha(p)==proof["source_sha256"][stem],"R220_VERIFIED_PAGE_HASH_"+stem)
        cardfields=parse_project_cards(raw,orig,expected_ids=range(first,last+1))
        source_mtimes[stem]=datetime.fromtimestamp(p.stat().st_mtime,timezone.utc)
        sources[stem]=sha(p)
        segs=segments(raw)
        need(set(segs)==set(range(first,last+1)),"EXACT_CARD_SEGMENTS_"+stem)
        for c in cardfields["captured_cards"]:
            pid=c["id"]
            explicit,disposition=parse_conditions(segs[pid],pid)
            snapshot={
               "id":pid,"name":c["name"],
               "startup_cost":c["observed_money"]["startup_cost"],
               "maintenance_cost":c["observed_money"]["maintenance_cost"],
               "investment":c["observed_money"]["investment"],
               "partner_support":c["observed_money"]["partner_support"],
               "project_conditions":explicit,
               "effects":c["observed_effects"],
               "displayed_condition_status":disposition,
            }
            orig_card={k:historical[pid][k] for k in
                       ("id","name","startup_cost","maintenance_cost","investment",
                        "partner_support","project_conditions","effects")}
            need(_card(snapshot,str(pid))==_card(orig_card,"ORIGINAL_"+str(pid)),
                 "CURRENT_DISPLAYED_CARD_DRIFT_"+str(pid))
            observed_conditions[pid]=disposition
            cards.append(snapshot)
    cards.sort(key=lambda x:x["id"])
    need([x["id"] for x in cards]==list(range(1,36)),"EXACT_35_CARDS")
    explicitly={c["id"]:c["project_conditions"] for c in cards
                if c["project_conditions"]}
    need(explicitly=={30:["Bicikliútfejlesztés — Fut"],
                      31:["Vasútfejlesztés — Fut"]},
         "TWO_ACTUALLY_DISPLAYED_DEPENDENCIES")
    earliest=min(source_mtimes.values())
    latest=max(source_mtimes.values())
    # R192 source timestamp is the latest actual observed page timestamp.
    # NEVER replace it with state timestamp to fake a same-hour capture.
    capture={
      "schema":"ECOSIM_R192_CURRENT_CARD_CATALOG_V1",
      "capture_mode":"CURRENT_READONLY",
      "team":state["provenance"]["team"],
      "market":state["provenance"]["market"],
      "round":state["provenance"]["round"],
      "period":state["provenance"]["current_period"],
      "source_evidence_id":"R222_FOUR_UI_CATEGORY_READONLY_OBSERVED",
      "source_view":"https://edu.ecosim.hu/simulation/projects",
      "captured_at_local":latest.isoformat(),
      "projects":[{k:v for k,v in c.items() if k!="displayed_condition_status"}
                  for c in cards]
    }
    r192_status="UNKNOWN"
    try:
        r192=validate_catalog(capture,state,orig)
        r192_status=r192["status"]
    except CatalogHold as e:
        r192_status="HOLD_"+str(e)
    # Actual four categories span >1 hour. No current single-source snapshot.
    need((latest-earliest).total_seconds()>3600,"EXPECTED_ACTUAL_MULTITIME_CAPTURE")
    need(r192_status=="HOLD_CATALOG_NOT_SAME_PERIOD_CAPTURE_WINDOW",
         "R192_MUST_KEEP_SAME_CAPTURE_WINDOW")
    sourcehash=sha(rulebook)
    need(sourcehash=="4d6b5c545bb205e5a9f8b92959b6659c4786d10cf6e1e6b2f654fa79c0168087",
         "OFFICIAL_RULEBOOK_SHA_CHANGED")
    result={
       "schema":SCHEMA,
       "status":"PASS_35_DISPLAYED_CONDITION_FIELDS_MATCH_ORIGINAL_R192_TIME_HOLD",
       "source_class":"READONLY_CONNECTED_BROWSER_PAGE_SNAPSHOTS_NOT_SERVER_ATTESTED",
       "team":capture["team"],"round":capture["round"],
       "market":capture["market"],"period":capture["period"],
       "observed_card_count":35,"observed_card_cost_effect_parity":35,
       "displayed_condition_sections":2,
       "observed_condition_counts_by_project":{str(k):len(v) for k,v in explicitly.items()},
       "observed_explicit_condition_rules":{str(k):v for k,v in explicitly.items()},
       "no_condition_section_displayed_cards":33,
       "all_35_source_fields_match_pinned_r162":True,
       "client_ui_absence_not_cryptographic_proof_of_server_conditions":True,
       "r192_time_admission":r192_status,
       "original_r191_market_cap":None,
       "actual_spendable_project_cash":None,
       "r214_live_advisory_authorized":False,
       "source_sha256":{
           "R217":sha(r217_dir/"R217_RECEIPT.json"),
           "R220":sha(r220_file),
           "official_rulebook":sourcehash,
           **sources},
       "capture_time_utc_by_category":{k:v.isoformat() for k,v in source_mtimes.items()},
       "earliest_capture_utc":earliest.isoformat(),
       "latest_capture_utc":latest.isoformat(),
       "capture_span_minutes":round((latest-earliest).total_seconds()/60,3),
       "r217_state_capture_time":state["provenance"]["captured_at_local"],
       "gameplay_gate":"STOP","game_writes":0
    }
    out.mkdir(mode=0o700)
    (out/"R222_RECEIPT.json").write_text(
        json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    (out/"R222_R192_CURRENT_CATALOG_TIME_HOLD.json").write_text(
        json.dumps(capture,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    lines=["# R222 – a 35 kártya aktuálisan megjelenített projektfeltételei","",
       "**35/35 látható kártyamező egyezik az eredeti R162 forrással.**",
       "Két explicit feltétel jelenik meg:",
       "- 30. Bubi bővítés: Bicikliútfejlesztés — Fut",
       "- 31. P+R parkolók: Vasútfejlesztés — Fut",
       "A másik 33 kártyán nem jelenik meg külön feltételblokk.",
       "Az időben szétválasztott böngészős nézeteket nem tekintjük egyetlen szerverpillanatképnek.",
       f"R192 időkapu: **{r192_status}**.",
       "Az aktuális projektlimit és elkölthető pénzösszeg továbbra is UNKNOWN.",
       "**GAME_ACTION_GATE=STOP; játékírás 0.**",""]
    (out/"R222_HU.md").write_text("\n".join(lines),encoding="utf-8")
    return result
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pages-dir",required=True,type=Path)
    p.add_argument("--r217-dir",required=True,type=Path)
    p.add_argument("--r220-receipt",required=True,type=Path)
    p.add_argument("--official-rulebook",required=True,type=Path)
    p.add_argument("--out-dir",required=True,type=Path)
    a=p.parse_args()
    result=audit(a.pages_dir,a.r217_dir,a.r220_receipt,a.official_rulebook,a.out_dir)
    print(json.dumps({"status":result["status"],
      "displayed_conditions":result["observed_explicit_condition_rules"],
      "r192":result["r192_time_admission"],
      "capture_span_minutes":result["capture_span_minutes"],
      "game_writes":0},ensure_ascii=False))
if __name__=="__main__":main()
