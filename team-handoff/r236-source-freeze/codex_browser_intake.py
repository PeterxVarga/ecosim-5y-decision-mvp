#!/usr/bin/env python3
"""Safely import Codex' existing-tab browser observation; never upgrade BLOCKED to observed.

No new browser access, no navigation, and no game actions are performed here.
The user must explicitly grant the browser's origin permission separately.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path

SCHEMA="ECOSIM_R236_CODEX_NATIVE_BROWSER_CURRENT_TABS_INTAKE_V1"
ALLOWED_ROUTES={"summary","projects","institutions","transport","income",
                "population","corporations","loans","finance","analysis"}
PERSONAL_DATA_HINT=re.compile(
    r"(cookie|authorization|bearer\s+|access_token|refresh_token|sessionid|set-cookie)",
    re.IGNORECASE)

def need(value,why):
    if not value:raise ValueError("HOLD_"+why)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def ingest(r236_path, codex_path, outdir):
    outdir=Path(outdir).resolve()
    need(outdir.parent.is_dir() and not outdir.exists(),"NEW_PRIVATE_OUTPUT")
    need(all(Path(p).is_file() and not Path(p).is_symlink()
             for p in (r236_path,codex_path)),"READ_ONLY_SOURCE_FILES")
    base=json.loads(Path(r236_path).read_text())
    src=json.loads(Path(codex_path).read_text())
    need(base["schema"]=="ECOSIM_R236_PERIOD_SOURCE_COLLECTION_GATE_V1"
         and base["status"]=="PARTIAL_SOURCE_COLLECTION_NO_OPTIMIZATION"
         and base["data_frozen_for_final_optimization"] is False
         and base["gameplay_gate"]=="STOP" and base["game_writes"]==0,
         "R236_ORIGINAL_STOP_GATES")
    need(src.get("source")=="codex_browser_existing_open_tabs_only"
         and src.get("browser_navigation") is False
         and src.get("game_writes")==0,
         "CODEX_NO_NAVIGATION_NO_GAME_WRITES")
    tabs=src.get("ecosim_tabs")
    need(isinstance(tabs,list)
         and type(src.get("total_visible_tabs")) is int
         and type(src.get("ecosim_tab_count")) is int
         and 0<=len(tabs)==src["ecosim_tab_count"]<=src["total_visible_tabs"]<=100,
         "CODEX_TAB_INVENTORY")
    accepted=[]
    blocked=[]
    for v in tabs:
        route=v.get("path")
        need(type(route) is str and route.startswith("/simulation/")
             and route.split("/")[2] in ALLOWED_ROUTES
             and len(route.split("/"))==3
             and v.get("read_status") in ("OBSERVED","BLOCKED"),
             "STRICT_ECOSIM_PATH_AND_STATUS")
        excerpt=v.get("observed_text_excerpt")
        need(isinstance(excerpt,str) and len(excerpt)<=6000 and
             not PERSONAL_DATA_HINT.search(excerpt),"NO_TOKENS_OR_SECRETS")
        if v["read_status"]=="BLOCKED":
            need(v.get("round") is None and v.get("market") is None
                 and v.get("period") is None and v.get("active_section") is None
                 and v.get("table_count") is None and v.get("input_count") is None
                 and v.get("table_headers")==[],
                 "BLOCKED_MUST_NOT_CONTAIN_INFERRED_DATA")
            blocked.append({"path":route,
                            "reason":"BROWSER_ORIGIN_PERMISSION_DECLINED"})
        else:
            need(v.get("round")=="Selejtező"
                 and v.get("market")=="I"
                 and v.get("period") in ("1/5",1,"1")
                 and type(v.get("table_count")) is int
                 and type(v.get("input_count")) is int
                 and len(excerpt)>30
                 and v.get("active_section") is not None,
                 "OBSERVED_CURRENT_PERIOD_SOURCE_REQUIRED")
            # Even with browser permission: DOM snapshots alone cannot prove
            # React saved P1 values, server min/max or causal policy effects.
            accepted.append({"path":route,"subview":v["active_section"],
                 "table_count":v["table_count"],
                 "input_count":v["input_count"],
                 "excerpt_text":excerpt,
                 "raw_browser_text_not_saved_decisions":True})
    output={
       "schema":SCHEMA,"status":
            "PARTIAL_NATIVE_BROWSER_AUTH_BLOCKED" if blocked else
            "PARTIAL_NATIVE_BROWSER_CURRENT_OPEN_TABS_ONLY",
       "round":base["round"],"market":base["market"],"period":base["period"],
       "origin_permission_granted_for_all_ecosim_tabs":len(blocked)==0,
       "existing_tabs_seen":src["total_visible_tabs"],
       "ecosim_existing_tabs_seen":len(tabs),
       "observed_approved_ecosim_tabs":len(accepted),
       "origin_blocked_ecosim_tabs":len(blocked),
       "observed_readonly_tabs":accepted,
       "blocked_tabs":blocked,
       "remaining_unobserved_other_subviews":True,
       "source_sha256":{"R236_original_intake":sha(r236_path),
                        "Codex_native_browser_last_message":sha(codex_path)},
       "no_user_permission_bypass_attempted":True,
       "codex_sandbox":"read-only",
       "gameplay_gate":"STOP","game_writes":0,
       "data_frozen_for_final_optimization":False,
       "current_period_complete":False,
       "run_optimizer":False,
       "requires_owner_browser_origin_permission":len(blocked)>0,
    }
    outdir.mkdir(mode=0o700)
    (outdir/"R236_CODEX_BROWSER_INTAKE_PRIVATE.json").write_text(json.dumps(
        output,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:output[k] for k in (
        "status","ecosim_existing_tabs_seen","observed_approved_ecosim_tabs",
        "origin_blocked_ecosim_tabs","requires_owner_browser_origin_permission",
        "run_optimizer","game_writes")},ensure_ascii=False))
    return output

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--r236",type=Path,required=True)
    p.add_argument("--codex-result",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    ingest(a.r236,a.codex_result,a.out_dir)
