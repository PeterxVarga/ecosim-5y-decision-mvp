#!/usr/bin/env python3
"""R207: operator-observed CURRENT_READONLY -> three diverse first-year advisory options.

This module reuses original R156/R191/R192/R160/R162 validators/search. It never
contacts EcoSim and must never infer current reality from test-round history.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

SCHEMA = "ECOSIM_R207_CURRENT_ROUND_ADVISORY_V1"


def need(ok, reason):
    if not ok:
        raise ValueError("HOLD_" + reason)


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def first_year_options(state, capture, finance, catalog, searches, *, requested_budget):
    """Extract diverse, independently audited first actions; no server approval.

    `searches` is a sequence of (scenario_name, objective, envelope, result),
    where result MUST be the original R162 strategy_5y.search output.
    """
    p = state.get("provenance", {})
    market = state.get("market", {})
    team = state.get("team", {})
    need(isinstance(p, dict) and isinstance(market, dict) and isinstance(team, dict), "STATE_SECTIONS")
    source = " ".join(str(p.get(k) or "") for k in ("source", "round", "source_evidence_id"))
    need(p.get("current_period") in range(1, 6) and type(p.get("current_period")) is int, "PERIOD")
    need(not any(v in source.casefold() for v in ("historical", "tesztfordul", "test_round", "r94_test", "r141_test")), "HISTORICAL_NOT_LIVE")
    need(capture.get("schema") == "ECOSIM_R191_LIVE_CAPTURE_ADMISSION_V1" and
         capture.get("status") == "PASS_OPERATOR_CAPTURE_CONSISTENCY_ONLY" and
         capture.get("gameplay_gate") == "STOP" and
         capture.get("current_source_is_server_authenticated") is False, "R156_R191_CAPTURE")
    need(finance.get("schema") == "ECOSIM_R191_YEAR1_FINANCE_V1" and
         finance.get("status") == "PASS_OPERATOR_DECLARED_YEAR1_ENVELOPE_ONLY" and
         finance.get("actual_server_financing_approved") is False and
         finance.get("gameplay_gate") == "STOP", "YEAR1_FINANCE_GATE")
    need(isinstance(catalog, dict) and catalog.get("schema") == "ECOSIM_R192_CATALOG_PARITY_V1" and
         catalog.get("status") == "PASS_OPERATOR_REPORTED_35_CARD_DEFINITION_PARITY_ONLY" and
         catalog.get("observed_card_count") == 35 and catalog.get("server_attested") is False and
         catalog.get("gameplay_gate") == "STOP", "R192_CATALOG_GATE")
    # The original R192 validator is invoked by the CLI, not bypassed here.
    need(finite(requested_budget) and requested_budget >= 0, "ILLUSTRATIVE_BUDGET")
    need(finite(finance.get("current_year_budget_ceiling_ecu")) and
         requested_budget <= finance["current_year_budget_ceiling_ecu"] + 1e-7 and
         abs(requested_budget - finance.get("tested_first_year_scenario_ecu", float("nan"))) <= 1e-7,
         "BUDGET_EVIDENCE_MISMATCH")
    current_cap = market.get("maxProjectPerTurn")
    project1 = team.get("project1_active_previous_period")
    selected = team.get("already_selected_new_project_ids_current_period")
    need(type(current_cap) is int and 0 <= current_cap <= 20 and type(project1) is bool, "CAP_SOURCE")
    need(isinstance(selected, list) and all(type(x) is int and 1 <= x <= 35 for x in selected)
         and len(selected) == len(set(selected)), "SELECTED_PROJECTS")
    need(len(selected) <= current_cap + int(project1), "CAP_OVERFLOW")
    need(isinstance(searches, list) and 1 <= len(searches) <= 6, "SEARCH_RUNS")

    candidates = {}
    rejected = {"hard_rule": 0, "conditional_eligibility": 0, "other": 0}
    for name, objective, ceiling, result in searches:
        need(isinstance(name, str) and len(name) <= 80 and name and objective in ("nominal", "scenario_min"), "SCENARIO_LABEL")
        need(finite(ceiling) and 0 <= ceiling <= requested_budget + 1e-7, "SCENARIO_FINANCE")
        need(isinstance(result, dict) and result.get("schema") == "ECOSIM_R148_SOURCE_BOUNDED_OFFLINE_STRATEGY_V1"
             and result.get("final_gameplay_decision") == "STOP"
             and result.get("game_write_actions") == 0 and result.get("network_actions") == 0
             and result.get("actual_five_year_score_forecast_validated") is False
             and result.get("start_year") == p["current_period"]
             and result.get("r157_search_objective") == objective, "R162_OUTPUT_IDENTITY")
        assumptions = result.get("assumptions", {})
        need(assumptions.get("annual_project_limit") == current_cap and
             assumptions.get("annual_limit_source") == "USER_MARKET_INPUT_OPERATOR_DECLARED_NOT_SERVER_VERIFIED" and
             assumptions.get("budget_source") == "EXPLICIT_ILLUSTRATIVE_CLI_SCENARIO_NOT_SPENDABLE_CASH" and
             assumptions.get("official_cash_envelopes_or_illustrative_scenario") == [ceiling] * (6 - p["current_period"]),
             "SEARCH_ASSUMPTIONS")
        need(isinstance(result.get("top_plans"), list), "PLAN_LIST")
        for ordinal, plan in enumerate(result["top_plans"], 1):
            years = plan.get("start_by_year", [])
            need(len(years) == 6 - p["current_period"] and
                 [row.get("year") for row in years] == list(range(p["current_period"], 6)), "YEAR_SEQUENCE")
            first = years[0]
            ids = first.get("start_project_ids")
            need(isinstance(ids, list) and all(type(i) is int and 1 <= i <= 35 for i in ids)
                 and len(ids) == len(set(ids)) and set(selected).issubset(ids), "FIRST_ACTION_IDS")
            cost = first.get("conservative_card_cash_requirement_ecu")
            need(finite(cost) and 0 <= cost <= ceiling + 1e-6, "FIRST_YEAR_CARD_COST")
            audit = plan.get("r160_independent_constraint_replay", {})
            need(audit.get("schema") == "ECOSIM_R160_INDEPENDENT_PLAN_AUDIT_V1"
                 and audit.get("gameplay_gate") == "STOP"
                 and audit.get("actual_game_eligibility") is None
                 and audit.get("actual_funding_approval") is None, "R160_INDEPENDENT_AUDIT")
            need(len(audit.get("years", [])) == len(years), "R160_YEAR_COVERAGE")
            need(all(audit_row.get("year") == year_row["year"] and
                     audit_row.get("new_project_ids") == year_row.get("start_project_ids") and
                     abs(audit_row["independently_replayed_conservative_cash_need_ecu"] - year_row["conservative_card_cash_requirement_ecu"]) < 1e-5
                     for audit_row, year_row in zip(audit["years"], years)), "R160_FULL_COST_REPLAY")
            if audit.get("hard_rule_violations"):
                rejected["hard_rule"] += 1
                continue
            if audit.get("conditional_eligibility_items") or audit.get("status") != "PASS_DISPLAY_RULES_ONLY_NOT_SERVER_APPROVAL":
                rejected["conditional_eligibility"] += 1
                continue
            key = tuple(sorted(ids))
            entry = {"first_year_new_project_ids": list(key),
                     "first_year_conservative_card_need_ecu": cost,
                     "conditional_five_year_proxy_delta": plan.get("terminal_mapped_proxy_delta"),
                     "illustrative_half_effect_delta": plan.get("illustrative_half_effect_sensitivity", [{}])[-1].get("mapped_proxy_delta"),
                     "excluded_unknown_effect_count": len(plan.get("excluded_unknown_effects", [])),
                     "conditional_display_eligibility_count": 0,
                     "example_future_project_starts": [y["start_project_ids"] for y in years[1:]],
                     "sources": []}
            need(finite(entry["conditional_five_year_proxy_delta"]) and
                 finite(entry["illustrative_half_effect_delta"]), "NONFINITE_PROXY")
            if key not in candidates:
                candidates[key] = entry
            old = candidates[key]
            old["sources"].append({"scenario": name, "search_objective": objective, "rank_within_search": ordinal})
            # Same action seen under different scenarios: retain least conservative
            # (smallest) cash estimate for presentation only if source agrees.
            need(abs(old["first_year_conservative_card_need_ecu"] - cost) <= 1e-5, "FIRST_ACTION_COST_DRIFT")

    ordered = sorted(candidates.values(), key=lambda x: (
        -len({z["scenario"] for z in x["sources"]}),
        -x["illustrative_half_effect_delta"], x["first_year_conservative_card_need_ecu"], x["first_year_new_project_ids"]))
    chosen = ordered[:3]
    return {"schema": SCHEMA, "status": "ADVISORY_ONLY_OPERATOR_DECLARED_LIVE_HOLD",
            "mode": "current-readonly", "gameplay_gate": "STOP", "game_writes": 0,
            "current_server_authenticated": False, "finance_server_approved": False,
            "market": p.get("market"), "period": p["current_period"],
            "requested_illustrative_year1_card_budget_ecu": requested_budget,
            "selected_options": chosen, "selected_count": len(chosen),
            "distinct_possible_first_actions": len(candidates), "audit_rejections": rejected,
            "live_game_recommendation": "NO_ACTION_WITHOUT_OWNER_APPROVAL_AND_SERVER_VALIDATION",
            "limitations": ["Operator-captured source is not independently server-attested",
                            "Future four-year card envelopes are hypothetical",
                            "Observed year-one cash is not server-financing approval",
                            "No full-city dynamics / validated score forecast",
                            "Current card catalog must match the original 35-card solver or HOLD"]}


def explain(packet):
    lines = ["# EcoSim – éles forduló előtti, csak olvasható döntési alternatívák", "",
             "**Játékmódosítás: STOP. A források kezelői megfigyelések, nem szerverhitelesítettek.**", "",
             "Az aktuális fordulóhoz egyeztetett, R160-auditált elsőéves alternatívák:", ""]
    for i, item in enumerate(packet["selected_options"], 1):
        ids = ", ".join(str(v) for v in item["first_year_new_project_ids"]) or "Nincs új projekt"
        lines.extend([f"## {i}. alternatíva – {ids}",
                      f"- Elsőéves konzervatív kártyateher: {item['first_year_conservative_card_need_ecu']:,.0f} ECU",
                      f"- Ötéves közvetlen proxyváltozás: {item['conditional_five_year_proxy_delta']:+.4f} (nem jósolt pontszám)",
                      f"- Nem modellezett projekthatások: {item['excluded_unknown_effect_count']}",
                      f"- Összevetési szcenáriók száma: {len(item['sources'])}", ""])
    if not packet["selected_options"]:
        lines.append("Nincs a szigorú, feltétel nélküli R160-kapun átjutó jelölt. HOLD.")
    lines.extend(["A jövő évekre alkalmazott borítékok kizárólag feltételezések; a hitel, támogatás és teljes városreakció ismeretlen.",
                  "**Közvetlen EcoSim-művelet: 0. A döntés emberi ellenőrzést és jóváhagyást igényel.**", ""])
    return "\n".join(lines)


def run_cli():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", type=Path, required=True)
    ap.add_argument("--state", type=Path, required=True)
    ap.add_argument("--r156-bundle", type=Path, required=True)
    ap.add_argument("--year1-finance", type=Path, required=True)
    ap.add_argument("--current-card-catalog", type=Path, required=True)
    ap.add_argument("--year1-budget", type=int, required=True, help="Explicit illustrative project-card ceiling; NOT approved funds")
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    root = args.repo_root.resolve()
    tools = root / "ECOSIM_R162_INTEGRITY_REVIEW_RC" / "tools"
    r191tools = root / "team-handoff/r191-live-admission/tools"
    need(tools.is_dir() and r191tools.is_dir(), "ORIGINAL_MODULE_LAYOUT")
    sys.path[:0] = [str(r191tools), str(tools)]
    from json_integrity_r162 import read_json
    from admission_r191 import validate_state, validate_r156_bundle, year1_finance
    from catalog_gate_r192 import validate_catalog
    from strategy_5y import search

    state = read_json(args.state)
    validate_state(state, mode="current")
    capture = validate_r156_bundle(state, args.r156_bundle)
    finance = year1_finance(read_json(args.year1_finance), state,
                            illustrative_first_year_budget=args.year1_budget)
    catalog = validate_catalog(read_json(args.current_card_catalog), state,
                               read_json(root / "ECOSIM_R162_INTEGRITY_REVIEW_RC/data/ecosim_projects_20261030.json"))
    need(not args.out_dir.exists() and not args.out_dir.resolve().is_relative_to(root), "PRIVATE_NEW_OUTPUT_ONLY")
    current_cap = state["market"]["maxProjectPerTurn"]
    p = state["provenance"]["current_period"]
    # Bounded scenario exploration; no cash approval and no game interaction.
    specs = [("CONSERVATIVE_50PCT", "scenario_min", args.year1_budget // 2),
             ("BALANCED_80PCT", "scenario_min", args.year1_budget * 4 // 5),
             ("FULL_OPERATOR_CEILING", "nominal", args.year1_budget)]
    searches=[]; scenario_holds=[]
    for name, objective, budget in specs:
        try:
            res=search(state, start_year=p, budget_override=[budget]*(6-p),
                       cap_override=None, beam_width=4, shortlist=12,
                       allow_same_year=False, objective=objective)
        except ValueError as exc:
            # An explicitly infeasible illustrative envelope does not silently
            # override a valid higher-envelope search or become an approval.
            if not str(exc).startswith("No feasible actions under assumptions at year "):
                raise
            scenario_holds.append({"scenario":name,"reason":"NO_FEASIBLE_SCHEDULE_UNDER_ASSUMPTIONS"})
            continue
        searches.append((name, objective, budget, res))
    need(bool(searches),"NO_FEASIBLE_HYPOTHETICAL_ENVELOPE")
    result=first_year_options(state, capture, finance, catalog, searches,
                              requested_budget=args.year1_budget)
    result["scenario_holds"]=scenario_holds
    result["input_hashes"]={"state_sha256": hashlib.sha256(args.state.read_bytes()).hexdigest(),
                            "finance_sha256": hashlib.sha256(args.year1_finance.read_bytes()).hexdigest()}
    args.out_dir.mkdir(parents=True, mode=0o700)
    (args.out_dir / "R207.json").write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+"\n")
    (args.out_dir / "R207_HU.md").write_text(explain(result))
    print(json.dumps({"status": result["status"], "alternatives": result["selected_count"],
                      "game_writes": 0, "out_dir": str(args.out_dir)}))


if __name__ == "__main__":
    run_cli()
