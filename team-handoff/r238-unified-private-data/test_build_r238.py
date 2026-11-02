#!/usr/bin/env python3
"""Proportional source-integrity tests for an immutable, private observed data bundle."""
import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_r238 import load,sha,SCHEMA

class TestUnifiedData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b=Path.home()/"Downloads"
        cls.root=Path(__file__).resolve().parents[2]
        cls.src={
          "r236":cls.b/"ecosim-r236-source-freeze-20261102/result/R236_PRIVATE_LEDGER.json",
          "r226":cls.b/"ecosim-r226-final-census-20261102/R226_RECEIPT.json",
          "r222":cls.b/"ecosim-r222-current-conditions-20261102/R222_RECEIPT.json",
          "r228":cls.b/"ecosim-r228-finance-joined-20261102/R228_RECEIPT.json",
          "r234":cls.b/"ecosim-r234-p1-bounds-evidence-20261102/R234_RECEIPT.json",
          "r233":cls.b/"ecosim-r233-source-reconciled-20261102/R233_RECEIPT.json",
          "r217":cls.b/"ecosim-r223-fresh-r156-20261102/R217_RECEIPT.json",
          "r224":cls.b/"ecosim-r224-source-anchored-finance-20261102/R224_RECEIPT.json",
          "r235":cls.b/"ecosim-r235-static-formulas-20261102/R235_RECEIPT.json",
          "income_browser":cls.b/"ecosim-r236-source-freeze-20261102/20261102_income_taxes_readonly_browser.txt",
          "xlsx":cls.b/"X-Challenge 2026 Selejtező_Jutalom a nap végén_Selejtező_I.xlsx",
          "projects":cls.root/"ECOSIM_R162_INTEGRITY_REVIEW_RC/data/ecosim_projects_20261030.json",
          "p1_factors":cls.b/"ecosim-r223-fresh-r156-20261102/r156_immutable/factors.csv",
          "p1_project_states":cls.b/"ecosim-r223-fresh-r156-20261102/r156_immutable/projects.csv",
        }
        cls.final=cls.b/"ecosim-r238-pinned-final-private-20261102"
        cls.receipt=json.loads((cls.final/"R238_RECEIPT.json").read_text())
        cls.data=json.loads((cls.final/"ECOSIM_P1_OBSERVED_PRIVATE.json").read_text())
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="ecosim-r238-integrity-")
        self.work=Path(self.tmp.name)
    def tearDown(self):
        self.tmp.cleanup()
    def test_cross_section_counts_and_source_sha(self):
        d=self.data
        self.assertEqual(d["schema"],SCHEMA)
        self.assertEqual(len(d["pages"]),10)
        self.assertEqual(len(d["projects"]["observed_visible_cards_original"]),35)
        self.assertEqual(len(d["excel"]["all_374_labelled_p0_rows"]),374)
        self.assertEqual(d["excel"]["own_numeric_p0_count"],324)
        self.assertEqual(len(d["city_factors"]["rows"]),29)
        self.assertEqual(len(d["controls"]["rows"]),23)
        self.assertEqual(d["controls"]["exact_excel_p0_matches"],19)
        self.assertEqual(d["controls"]["unmatched_excel_controls"],4)
        self.assertEqual(d["controls"]["verified_full_minmax"],0)
        for k,p in self.src.items():
            self.assertEqual(d["source_file_sha256"][k],sha(p))
        self.assertEqual(self.receipt["bundle_sha256"],
                         sha(self.final/"ECOSIM_P1_OBSERVED_PRIVATE.json"))
    def test_no_promoted_fake_finance_or_policy(self):
        d=self.data
        self.assertEqual((d["city_factors"]["p0_index_ui"],
                          d["city_factors"]["p1_plan_index_ui"]),(51.96,52.48))
        self.assertFalse(d["city_factors"]["p1_is_observed_fact"])
        self.assertFalse(d["more_recent_open_income_tax_source"]["effective_saved_p1_tax_rates_verified"])
        self.assertEqual(d["institution_client_partial_lower_bounds"]["verified_full_allowed_ranges"],0)
        self.assertIsNone(d["finance"]["spendable_budget_ecu_verified"])
        self.assertFalse(d["data_gates"]["ready_for_final_optimization"])
        self.assertFalse(d["data_gates"]["project_same_hour_capture"])
        self.assertFalse(d["run_optimizer"])
        self.assertEqual(d["gameplay_gate"],"STOP")
        self.assertEqual(d["game_writes"],0)
    def test_sha_pinned_project_cannot_be_silently_changed(self):
        bad=self.work/"projects.json"
        bad.write_bytes(self.src["projects"].read_bytes()+b"\n")
        paths=dict(self.src,projects=bad)
        with self.assertRaisesRegex(ValueError,"HOLD_ORIGINAL_CARD_AND_R156_ROW_BYTES"):
            load(paths,self.b,self.work/"out")
    def test_claiming_complete_r236_ledger_is_rejected(self):
        x=json.loads(self.src["r236"].read_text())
        x["data_frozen_for_final_optimization"]=True
        bad=self.work/"r236.json"
        bad.write_text(json.dumps(x,ensure_ascii=False))
        paths=dict(self.src,r236=bad)
        with self.assertRaisesRegex(ValueError,"HOLD_R236_COLLECTION_ONLY"):
            load(paths,self.b,self.work/"out")
    def test_recreate_private_bundle_exact(self):
        r=load(self.src,self.b,self.work/"new")
        self.assertEqual(r["bundle_sha256"],self.receipt["bundle_sha256"])
        self.assertEqual((self.work/"new"/"ECOSIM_P1_OBSERVED_PRIVATE.json").read_bytes(),
                         (self.final/"ECOSIM_P1_OBSERVED_PRIVATE.json").read_bytes())
    def test_existing_private_output_cannot_be_overwritten(self):
        with self.assertRaisesRegex(ValueError,"HOLD_OUTSIDE_REPO_NEW_PRIVATE_DIR"):
            load(self.src,self.b,self.final)

if __name__=="__main__":unittest.main()
