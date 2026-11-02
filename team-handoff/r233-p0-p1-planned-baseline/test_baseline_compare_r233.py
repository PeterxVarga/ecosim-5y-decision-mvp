#!/usr/bin/env python3
"""Real current Selejtezo source replay: exact P0 fact and P1 plan attribution."""
from __future__ import annotations
import copy,json,os,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from baseline_compare_r233 import compute,SCHEMA
from json_integrity_r162 import read_json

class RealSourceP0P1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path={k:Path(os.environ["R233_"+k]) for k in
             ("XLSX","P1","SUMMARY","R217","MANIFEST","R232","TRACK","RESULT")}
        cls.r=read_json(cls.path["RESULT"]/"R233_RECEIPT.json")
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="r233-guard-")
        self.tmp=Path(self.temp.name)
    def tearDown(self):
        self.temp.cleanup()
    def newrun(self,**changes):
        p=self.path
        args={"xlsx":p["XLSX"],"p1_csv":p["P1"],"summary_txt":p["SUMMARY"],
              "r217_path":p["R217"],"manifest":p["MANIFEST"],"r232_path":p["R232"],
              "track_path":p["TRACK"],"dest":self.tmp/"fresh"}
        args.update(changes)
        return compute(**args)
    def patch(self,key,patch):
        f=self.tmp/(key+".json")
        o=copy.deepcopy(read_json(self.path[key]))
        patch(o)
        f.write_text(json.dumps(o,ensure_ascii=False))
        return f
    def test_proven_29_factors_and_observed_ui_displays(self):
        r=self.r
        self.assertEqual(r["schema"],SCHEMA)
        self.assertEqual(r["changed_factor_count"],24)
        self.assertEqual(r["P0_fact_reported_smartcity_index"],51.96)
        self.assertEqual(r["P1_plan_reported_smartcity_index"],52.48)
        self.assertAlmostEqual(r["P0_fact_reconstructed_from_displayed_factors"],51.965516667,8)
        self.assertAlmostEqual(r["P1_plan_reconstructed_from_displayed_factors"],52.483733333,8)
        self.assertTrue(r["display_factor_quantization_difference_not_assumed_error"])
        self.assertTrue(r["P1_is_forecast_not_released_game_fact"])
        self.assertEqual(r["baseline_for_existing_R232_project_search"],"ALREADY_P1_PLAN_NOT_P0")
    def test_equal_initial_seven_team_p0_not_future_competition(self):
        self.assertEqual(self.r["league_P0_equal_initial_index_teams"],7)
        self.assertEqual(self.r["league_P0_common_display_index"],51.96)
        self.assertFalse(self.r["league_other_teams_P1_and_future_actions_observed"])
    def test_all_eight_year5_plans_already_p1_and_not_forecast(self):
        r=self.r
        self.assertEqual(r["scenario_count"],8)
        self.assertEqual(len(r["baseline_sensitivity_scenarios"]),8)
        source=read_json(self.path["R232"])
        for now,old in zip(r["baseline_sensitivity_scenarios"],source["scenarios"]):
            self.assertEqual(now["year5_project_only_conditional_from_P1_plan_NOT_FORECAST"],
                old["conditional_year5_project_only_mapped_index_NOT_CITY_FORECAST"])
            self.assertTrue(now["original_r232_p1_baseline_reproduced"])
            self.assertEqual(now["annual_project_starts"],old["annual_start_counts"])
            self.assertTrue(all(x<=4 for x in now["annual_project_starts"]))
            self.assertEqual(now["first_year_new_project_ids"],old["p1_project_ids"])
            self.assertFalse(now["current_p1_policy_effects_verified"])
            self.assertFalse(now["later_year_peer_actions_verified"])
            self.assertIsNone(now["official_five_year_score"])
            self.assertIsNone(now["actual_game_permitted"])
    def test_no_real_budget_or_game_authority(self):
        r=self.r
        self.assertFalse(r["cash_spendable_verified"])
        self.assertFalse(r["R191_current_market_cap_server_attested"])
        self.assertFalse(r["policy_current_and_future_effects_verified"])
        self.assertEqual(r["game_writes"],0)
        self.assertEqual(r["gameplay_gate"],"STOP")
    def test_source_sha_links_exact_files(self):
        from source_join_r228 import digest
        paths={"original_Selejtezo_Excel":"XLSX","R217_original_receipt":"R217",
               "R217_original_P1_factor_csv":"P1",
               "R217_original_readonly_summary":"SUMMARY",
               "R156_current_manifest":"MANIFEST",
               "R232_source_and_candidate_receipt":"R232",
               "R145_unknown_test_only_track":"TRACK"}
        for label,p in paths.items():
            self.assertEqual(self.r["source_sha256"][label],digest(self.path[p]))
    def test_modified_r217_p0_p1_claim_fails_closed(self):
        f=self.patch("R217",lambda d:d.update(index_p1_plan=52.5))
        with self.assertRaisesRegex(ValueError,"HOLD_R217_SOURCE_LINK_P1_PLAN_NOT_FACT"):
            self.newrun(r217_path=f)
    def test_modified_r232_score_fails_original_replay(self):
        def corrupt(d):
            d["scenarios"][2]["conditional_year5_project_only_mapped_index_NOT_CITY_FORECAST"]=123.456
        f=self.patch("R232",corrupt)
        with self.assertRaisesRegex(ValueError,"HOLD_R232_ALREADY_USES_P1_PLAN_FACTORS"):
            self.newrun(r232_path=f)
    def test_modified_p1_factor_csv_rejected(self):
        p=self.tmp/"changed.csv"
        t=self.path["P1"].read_text()
        self.assertIn("30.17",t)
        p.write_text(t.replace("30.17","31.17",1))
        with self.assertRaisesRegex(ValueError,"HOLD_P1_CSV_MUST_BE_ORIGINAL_R156_FACTOR_SOURCE"):
            self.newrun(p1_csv=p)
    def test_modified_readonly_ui_snapshot_rejected(self):
        p=self.tmp/"changed_summary.txt"
        p.write_text(self.path["SUMMARY"].read_text()+"fake")
        with self.assertRaisesRegex(ValueError,"HOLD_R217_SOURCE_LINK_P1_PLAN_NOT_FACT"):
            self.newrun(summary_txt=p)
    def test_existing_directory_not_overwritten(self):
        with self.assertRaisesRegex(ValueError,"HOLD_NEW_PRIVATE_OUTPUT_REQUIRED"):
            self.newrun(dest=self.path["RESULT"])
    def test_deterministic_reproduction(self):
        expected=self.r
        actual=self.newrun()
        self.assertEqual(actual,expected)
        self.assertEqual((self.tmp/"fresh/R233_RECEIPT.json").read_bytes(),
                         (self.path["RESULT"]/"R233_RECEIPT.json").read_bytes())
        self.assertEqual((self.tmp/"fresh/R233_HU.md").read_bytes(),
                         (self.path["RESULT"]/"R233_HU.md").read_bytes())
if __name__=="__main__":unittest.main()
