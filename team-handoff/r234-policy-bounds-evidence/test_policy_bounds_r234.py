#!/usr/bin/env python3
"""Real-source / changed-source fail-closed validation of 23 UI P1 controls."""
from __future__ import annotations
import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from policy_bounds_r234 import run,SCHEMA
from json_integrity_r162 import read_json

class P1LimitEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paths={k:Path(os.environ["R234_"+k]) for k in
            ("R225","R226","R228","TAX","R233","TRACK","XLSX",
             "MANUAL_PDF","MANUAL_TEXT","SOURCE_JS","OUT")}
        cls.r=read_json(cls.paths["OUT"]/"R234_RECEIPT.json")
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="r234-negative-")
        self.root=Path(self.temp.name)
    def tearDown(self):
        self.temp.cleanup()
    def copychange(self,key,fn):
        o=copy.deepcopy(read_json(self.paths[key]))
        fn(o)
        f=self.root/(key+".json");f.write_text(json.dumps(o,ensure_ascii=False))
        return f
    def newrun(self,**overrides):
        p=self.paths
        kw=dict(r225_path=p["R225"],r226_path=p["R226"],
           r228_path=p["R228"],tax_path=p["TAX"],r233_path=p["R233"],
           track_path=p["TRACK"],xlsx_path=p["XLSX"],
           manual_pdf=p["MANUAL_PDF"],manual_text=p["MANUAL_TEXT"],
           source_js=p["SOURCE_JS"],dest=self.root/"new")
        kw.update(overrides)
        return run(**kw)
    def test_23_source_controls_exact_roster(self):
        r=self.r
        self.assertEqual(r["schema"],SCHEMA)
        self.assertEqual(len(r["matrix"]),23)
        self.assertEqual(r["observed_ui_controls"],23)
        self.assertEqual(r["exact_excel_p0_matches"],19)
        self.assertEqual(r["excel_unmatched_but_ui_observed"],4)
        self.assertEqual(len({x["control_id"] for x in r["matrix"]}),23)
        self.assertEqual(sum(x["excel_p0_exact_row_id_or_null"] is not None
                            for x in r["matrix"]),19)
    def test_zero_is_unknown_not_causal_zero(self):
        r=self.r
        self.assertEqual(r["current_numeric_minmax_pairs_verified"],0)
        self.assertEqual(r["current_P1_effective_selected_values_verified"],0)
        self.assertEqual(r["calibrated_causal_factor_and_cash_effect_pairs_verified"],0)
        self.assertEqual(r["original_R145_unknown_annual_cash_effect_count"],23)
        self.assertEqual(r["original_R145_unknown_annual_factor_effect_count"],23)
        self.assertEqual(r["original_R145_test_only_5_year_rows"],115)
        self.assertTrue(all(x["numeric_min_verified"] is None and
                            x["numeric_max_verified"] is None and
                            x["numeric_delta_percent_verified"] is None and
                            x["p1_effective_selected_value_verified"] is None and
                            x["annual_cash_change_ecu_calibrated"] is None and
                            x["city_factors_effect_calibrated"] is None and
                            not x["is_validated_admissible_action"]
                            for x in r["matrix"]))
    def test_handbook_20_percent_and_tax_law_are_not_limits(self):
        r=self.r
        self.assertTrue(r["source_rulebook_example_plus_minus_20_not_generic_bound"])
        self.assertTrue(r["tax_legal_ceiling_rule_but_numeric_rates_unknown"])
        self.assertTrue(r["client_generic_dynamic_minmax_support_not_current_rule"])
        keys={x["control_id"]:x for x in r["matrix"]}
        self.assertEqual(keys["tax.business"]["handbook_non_numeric_rule_class"],
            "STATUTORY_TAX_MAXIMUM_CURRENT_UI_VALUE_UNKNOWN")
        self.assertEqual(keys["institutions_education.table_1.field_2"]["handbook_non_numeric_rule_class"],
            "HANDBOOK_PERIOD_SPECIFIC_PERCENT_EXAMPLE_NOT_NUMERIC_BOUND")
    def test_r233_4_project_paths_are_not_joint_policy_admission(self):
        self.assertEqual(self.r["R233_source_proven_4_project_per_year_8_scenario_paths"],8)
        self.assertFalse(self.r["usable_joint_real_policy_project_optimization"])
        self.assertIsNone(self.r["approved_p1_city_actions"])
        self.assertEqual(self.r["live_R191_R192_R214_gates"],"HOLD")
        self.assertEqual(self.r["gameplay_gate"],"STOP")
        self.assertEqual(self.r["game_writes"],0)
    def test_all_sources_checksum_bound(self):
        from source_join_r228 import digest
        m={"R225":"R225","R226":"R226","R228":"R228",
           "R228_tax_visible":"TAX","R233":"R233","original_R145_TEST_ONLY":"TRACK",
           "current_Selejtezo_excel":"XLSX","original_official_handbook_pdf":"MANUAL_PDF",
           "official_handbook_extracted_text":"MANUAL_TEXT",
           "historical_shared_ui_input_component":"SOURCE_JS"}
        for src,key in m.items():
            self.assertEqual(self.r["source_sha256"][src],digest(self.paths[key]))
    def test_injected_admitted_r226_bound_rejected(self):
        f=self.copychange("R226",lambda o:o["controls"][0].update(actual_allowed_max=99999))
        with self.assertRaisesRegex(ValueError,"HOLD_R228_23_SOURCE_AND_CROSSWALK"):
            self.newrun(r226_path=f)
    def test_tampered_tax_limit_rejected(self):
        f=self.copychange("TAX",lambda o:o.update(bounds_verified=True))
        with self.assertRaisesRegex(ValueError,"HOLD_R228_23_SOURCE_AND_CROSSWALK"):
            self.newrun(tax_path=f)
    def test_r145_pretended_cash_response_rejected(self):
        f=self.copychange("TRACK",
              lambda o:o["tracks"][0]["actions"][0].update(annual_cash_delta_ecu=0.0))
        with self.assertRaisesRegex(ValueError,"HOLD_R145_23_SOURCE_KEYS_EFFECTS_UNKNOWN_NOT_ZERO"):
            self.newrun(track_path=f)
    def test_injected_r233_policy_calibration_rejected(self):
        f=self.copychange("R233",lambda o:o.update(policy_current_and_future_effects_verified=True))
        with self.assertRaisesRegex(ValueError,"HOLD_EXISTING_R233_EIGHT_SCENARIOS_NOT_ACTUAL_POLICY"):
            self.newrun(r233_path=f)
    def test_previous_result_not_overwritten(self):
        with self.assertRaisesRegex(ValueError,"HOLD_NEW_PRIVATE_OUTPUT"):
            self.newrun(dest=self.paths["OUT"])
    def test_fresh_source_reproduces_private_result(self):
        a=self.newrun()
        self.assertEqual(a,self.r)
        self.assertEqual((self.root/"new/R234_RECEIPT.json").read_bytes(),
                         (self.paths["OUT"]/"R234_RECEIPT.json").read_bytes())
        self.assertEqual((self.root/"new/R234_HU.md").read_bytes(),
                         (self.paths["OUT"]/"R234_HU.md").read_bytes())
        self.assertEqual((self.root/"new/R234_P1_SOURCE_MATRIX_PRIVATE.csv").read_bytes(),
                         (self.paths["OUT"]/"R234_P1_SOURCE_MATRIX_PRIVATE.csv").read_bytes())
if __name__=="__main__":unittest.main()
