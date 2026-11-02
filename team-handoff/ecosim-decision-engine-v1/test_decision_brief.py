#!/usr/bin/env python3
"""Synthetic, public-safe cross-stage and tamper regressions for R204."""
import copy
import importlib.util
import io
import csv
import unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location("r204_brief",Path(__file__).with_name("decision_brief.py"))
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def fixture():
    candidates=[]
    plans=[]
    for i in range(17):
        name=f"test-{i:02d}"
        scores=[50+i*.01+j*.1 for j in range(3)]
        candidates.append({
            "candidate_id":name,"first_year_project_ids":[i+1],
            "five_year_project_cost_ecu":50,"max_annual_project_card_need_ecu":10,
            "worst_partial_net_ecu":-20,
            "worst_partial_index_delta":.3,
            "policy_paths":{policy:{"partial_net_ecu":[-20,10,0][j],
                "index_proxy_delta":.3+j*.01,"zero_opening_cash_stress_ecu":20}
                for j,policy in enumerate(mod.POLICIES)},
            "fits_illustrative_card_cap":{str(k):True for k in (50000,90000,100000,150000)}
        })
        years=[{
            "year":year,"projects_started_ids":[i+1] if year==1 else [],
            "conservative_project_card_need_ecu":10,
            "actual_server_index":None,"verified_financing":False,
            "conditional_index_stress":[{
                "intensity":s,"mapped_index_conditional":scores[j],
                "unmapped_or_indirect_effect_count":2,
                "unmodeled_city_drift_has_no_bound":True}
                for j,s in enumerate(mod.INTENSITIES)]}
            for year in range(1,6)]
        plans.append({"id":name,"annual_records":years,"final_year_unmapped_effects":2})
    order=[f"test-{i:02d}" for i in range(16,-1,-1)]
    return {
       "schema":"ECOSIM_UNIFIED_HISTORICAL_DECISION_PACKET_V1",
       "mode":"historical-test","status":"PASS_PARTIAL_HISTORICAL_DECISION_SUPPORT_LIVE_HOLD",
       "gameplay_gate":"STOP","game_writes":0,
       "decision":{"live":"HOLD","current_city_optimum":"NOT_PROVEN"},
       "candidate_count":17,"scenario_count":51,"report_hashes":{},"source_hashes":{},
       "scenario_robustness":{"candidate_count":17,"scenario_count":51,
           "candidate_summaries":candidates,"candidate_robust_front_sample_ids":order[:3],
           "illustrative_cap_filters":[],"selected_or_server_approved":False,
           "citywide_optimum_certified":False},
       "annual_transition_diagnostics":{
           "plan_count":17,"annual_project_only_ledgers":85,
           "direct_factor_sensitivity_evaluations":255,
           "observed_fact_to_fact_transition_samples":0,"simulator_outcome_validation":False,
           "plans":plans,
           "rankings_by_assumed_direct_effect_intensity":[
               {"intensity":s,"all_source_partial_order":order} for s in mod.INTENSITIES]}
    }

class TestR204(unittest.TestCase):
    def setUp(self): self.p=fixture()
    def rejects(self,code):
        with self.assertRaisesRegex(ValueError,"HOLD_"+code):mod.compare(self.p)
    def test_clean_packet(self):
        x=mod.compare(self.p)
        self.assertEqual(len(x["candidates"]),17)
        self.assertEqual(x["candidates"][0]["annual_project_card_need_ecu"],[10]*5)
        self.assertEqual(x["partial_top_five_by_intensity"][0]["conditional_top_five"][0],"test-16")
        self.assertFalse(x["recommended_for_gameplay"])
        self.assertEqual(x["game_writes"],0)
    def test_csv_and_hungarian(self):
        x=mod.compare(self.p)
        rows=list(csv.DictReader(io.StringIO(mod.csv_table(x))))
        self.assertEqual(len(rows),17)
        self.assertIn("LIVE HOLD",mod.display(x))
    def test_live_claim(self):
        self.p["decision"]["live"]="GO"
        self.rejects("NO_OPTIMUM_CLAIM")
    def test_wrong_mode(self):
        self.p["mode"]="current-readonly"
        self.rejects("NO_GAME_ACTIONS")
    def test_action(self):
        self.p["game_writes"]=1
        self.rejects("NO_GAME_ACTIONS")
    def test_duplicate_candidate(self):
        self.p["scenario_robustness"]["candidate_summaries"][0]["candidate_id"]="test-01"
        self.rejects("IDENTICAL_CANDIDATES")
    def test_card_cost_mismatch(self):
        self.p["annual_transition_diagnostics"]["plans"][0]["annual_records"][2]["conservative_project_card_need_ecu"]=11
        self.rejects("ANNUAL_COST_IDENTITY")
    def test_cap_not_finance(self):
        self.p["scenario_robustness"]["candidate_summaries"][0]["fits_illustrative_card_cap"]["50000"]=False
        self.rejects("CAP_FILTER_IDENTITY")
    def test_missing_policy(self):
        self.p["scenario_robustness"]["candidate_summaries"][0]["policy_paths"].pop(mod.POLICIES[0])
        self.rejects("POLICY_PATH_COVERAGE")
    def test_actual_score_leak(self):
        self.p["annual_transition_diagnostics"]["plans"][0]["annual_records"][0]["actual_server_index"]=55.2
        self.rejects("NO_LIVE_YEAR")
    def test_rank_drift(self):
        self.p["annual_transition_diagnostics"]["rankings_by_assumed_direct_effect_intensity"][0]["all_source_partial_order"].reverse()
        self.rejects("RANKING_REPLAY")
    def test_unbounded_city_drift(self):
        self.p["annual_transition_diagnostics"]["plans"][0]["annual_records"][0]["conditional_index_stress"][1]["unmodeled_city_drift_has_no_bound"]=False
        self.rejects("UNBOUNDED_CITY_EFFECT")
if __name__=="__main__":unittest.main()
