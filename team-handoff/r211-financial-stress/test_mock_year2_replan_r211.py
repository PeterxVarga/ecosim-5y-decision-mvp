#!/usr/bin/env python3
"""R211 second E2E: R203 synthetic closed-FACT pair -> R162 year-2 replan.

All FACT tags are MOCK examples built from historical PLAN values; NOT observed
game FACTs, not identified transition parameters, not year-2 finance authority.
"""
from __future__ import annotations
import copy
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
R162=ROOT/"ECOSIM_R162_INTEGRITY_REVIEW_RC"
sys.path[:0]=[str(R162/"tools"),str(ROOT/"team-handoff/r203-transition-evidence/tools"),
             str(ROOT/"team-handoff/r207-first-round")]
from observation_bundle_r152 import compile_bundle
from city_bridge import computed_index_from_factors
from portfolio_5y import project_index
from strategy_5y import search
from independent_audit_r160 import audit_plan
from fact_pair_r203 import admissible

def require(ok,reason):
    if not ok:raise ValueError("HOLD_"+reason)

def make_faux_fact_pair(original,future_factors,weights):
    x=copy.deepcopy(original)
    y=copy.deepcopy(future_factors)
    def shot(period,factors):
        return {"id":"R211_MOCK_FACT_"+str(period),
                "team":"SYNTHETIC_ONLY_R211",
                "market":"SYNTHETIC_ONLY_R211_MARKET",
                "period":period,"kind":"FACT",
                "captured_at":"2026-11-02T00:00:00+01:00",
                "source_evidence_id":"R211_SYNTHETIC_NOT_A_REAL_FACT_"+str(period),
                "factors":factors,
                "displayed_total_index":computed_index_from_factors(factors,weights)["total_index_from_displayed_factors"],
                "revenue_ecu":50000.,"expense_ecu":50000.}
    return {"schema":"ECOSIM_R203_OPERATOR_DECLARED_TWO_CLOSED_FACTS_V1",
            "source_class":"OPERATOR_DECLARED_READONLY",
            "snapshots":[shot(1,x),shot(2,y)]}

def exercise():
    _,historical,_=compile_bundle(R162/"examples/R152_HISTORICAL_R94_READONLY_PACKET/manifest.json")
    require(historical["provenance"]["observed_column_kind"]=="PLAN","ORIGINAL_HISTORICAL_IS_PLAN")
    base=historical["team"]["baseline_smartcity_factors"]
    require(len(base)==29,"29_METRICS")
    weights=historical["market"]["smartcity_total_weights"]
    after=copy.deepcopy(base)
    changed=sorted(after)[0]
    after[changed]=round(after[changed]+0.5,6)
    pair=make_faux_fact_pair(base,after,weights)
    gate=admissible(pair)
    require(gate["status"]=="PASS_STRUCTURAL_ONLY_NOT_AUTHENTICATED_AND_NOT_MODEL_TRAINED" and
            not gate["evidence_authenticated_against_server"] and
            not gate["city_causality_or_transition_parameters_identified"],"R203_STRUCTURAL_GATE")
    # A fictional first-year choice. R209 source-mode YEAR1 and the real game
    # are unrelated; the following assumes that these two starts were accepted.
    assumption=[13,27]
    older=historical["team"]["initially_active_project_ids"]
    new_state=copy.deepcopy(historical)
    new_state["team"]["initially_active_project_ids"]=sorted(set(older)|set(assumption))
    new_state["team"]["already_selected_new_project_ids_current_period"]=[]
    new_state["team"]["project1_active_previous_period"]=1 in set(older)|set(assumption)
    new_state["team"]["baseline_smartcity_factors"]=after
    new_state["market"]["maxProjectPerTurn"]=4
    new_state["provenance"].update(current_period=2,round="R211_FAKE_YEAR2_NOT_OBSERVED",
                                   source_evidence_id="R211_MOCK_FACT_PAIR_YEAR2",
                                   observed_column_kind="FACT",
                                   captured_at_local="2026-11-02T00:00:00+01:00")
    idx=project_index()
    result=search(new_state,start_year=2,budget_override=[120000]*4,cap_override=4,
                  beam_width=4,shortlist=12,allow_same_year=False,objective="scenario_min")
    require(result["final_gameplay_decision"]=="STOP" and result["game_write_actions"]==0
            and not result["actual_five_year_score_forecast_validated"],"SOURCE_SEARCH_GATE")
    require(1<=len(result["top_plans"])<=4,"R162_PLANS")
    accepted=0
    for plan in result["top_plans"]:
        years=plan["start_by_year"]
        require([v["year"] for v in years]==[2,3,4,5],"REMAINING_YEAR_HORIZON")
        starts=[v["start_project_ids"] for v in years]
        audit=audit_plan(idx,start_year=2,active_ids=new_state["team"]["initially_active_project_ids"],
            fixed_first_ids=[],previous_project1_active=new_state["team"]["project1_active_previous_period"],
            base_project_cap=4,annual_budgets=[120000]*4,starts=starts,allow_same_year=False,
            advertised_costs=[x["conservative_card_cash_requirement_ecu"] for x in years],
            advertised_total=plan["five_year_conservative_card_cost_ecu"])
        require(audit==plan["r160_independent_constraint_replay"] and not audit["hard_rule_violations"],
                "R160_CROSS_YEAR_AUDIT")
        require(not (set(v for row in starts for v in row)&set(new_state["team"]["initially_active_project_ids"])),
                "DUPLICATE_PREVIOUS_PROJECT")
        accepted+=1
    negatives=0
    for bad in (lambda p:p["snapshots"][1].update(kind="PLAN"),
                lambda p:p["snapshots"][1].update(period=4),
                lambda p:p["snapshots"][1].update(team="OTHER_TEAM")):
        changed_pair=copy.deepcopy(pair);bad(changed_pair)
        try:admissible(changed_pair)
        except ValueError:negatives+=1
        else:raise ValueError("HOLD_INVALID_SYNTHETIC_FACT_PAIR_ACCEPTED")
    require(negatives==3,"NEGATIVE_CONTROLS")
    return {"schema":"ECOSIM_R211_REPLAN_MOCK_FACT_PAIR_TO_YEAR2_V1",
            "status":"PASS_SYNTHETIC_R203_FACT_PAIR_TO_R162_YEAR2_REPLAN_ONLY",
            "source_origin":"R94_P1_PLAN_RELABELED_AS_EXPLICIT_FAKE_FACT_TEST",
            "real_fact_pair_available":False,"authentic_transition_model":False,
            "initial_period":1,"new_period":2,"synthetic_changed_factor":changed,
            "synthetic_factor_step":0.5,"hypothetical_card_ceiling_per_future_year_ecu":120000,
            "original_year2_to_year5_plans_audited":accepted,
            "distinct_second_year_first_actions":len({tuple(row["start_by_year"][0]["start_project_ids"]) for row in result["top_plans"]}),
            "selected_year2_project_options":[row["start_by_year"][0]["start_project_ids"] for row in result["top_plans"]],
            "unmodeled_exogenous_city_changes":"UNKNOWN",
            "actual_gameplay_approved":False,"gameplay_gate":"STOP","game_writes":0,
            "negative_controls":negatives}
if __name__=="__main__":
    print(json.dumps(exercise(),ensure_ascii=False,sort_keys=True))
