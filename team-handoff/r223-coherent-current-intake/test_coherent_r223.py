#!/usr/bin/env python3
"""R223 private-source qualification, synthetic time-coherence gate tests."""
from __future__ import annotations
import json,os,shutil,sys,tempfile,unittest
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from coherent_r223 import capture,Hold
from json_integrity_r162 import read_json

class FreshCurrentIntake(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.current=Path(os.environ["R223_FRESH_PAGES"])
        cls.r156=Path(os.environ["R223_FRESH_R156"])
        cls.previous=Path(os.environ["R223_PREVIOUS_PAGES"])
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="r223-synthetic-time-test-")
        self.root=Path(self.tmp.name)
        self.pages=self.root/"pages"
        self.pages.mkdir()
        for item in self.current.glob("*.txt"):
            shutil.copy2(item,self.pages/item.name)
    def tearDown(self):self.tmp.cleanup()
    def add_old_three(self,synthetic_fresh_times=False):
        for name in ("projects_sport","projects_transport","projects_environment"):
            f=self.pages/(name+".txt")
            shutil.copy2(self.previous/(name+".txt"),f)
            if synthetic_fresh_times:
                now=datetime.now(timezone.utc).timestamp()
                os.utime(f,(now,now))
    def check(self,name="report"):
        return capture(self.pages,self.r156,self.root/name)
    def test_actual_five_fresh_views_are_partial_not_authorized(self):
        result=self.check()
        self.assertEqual(result["status"],"HOLD_MISSING_CURRENT_CATEGORY_VIEWS")
        self.assertEqual(result["observed_visible_cards"],14)
        self.assertEqual([x["view"] for x in result["missing_current_category_views"]],
                         ["Sport és Kultúra","Közlekedés","Környezet"])
        self.assertFalse(result["r214_live_advisory_authorized"])
        self.assertEqual(result["game_writes"],0)
    def test_old_actual_three_views_stale_and_must_hold(self):
        self.add_old_three(False)
        result=self.check()
        self.assertEqual(result["observed_visible_cards"],35)
        self.assertEqual(result["status"],"HOLD_NOT_SAME_HOUR_OR_FUTURE_SOURCE")
        self.assertGreater(result["source_capture_span_minutes"],60)
        self.assertFalse((self.root/"report/R223_R192_CURRENT_CATALOG_PRIVATE.json").exists())
    def test_synthetic_freshness_exercises_original_r192_path(self):
        self.add_old_three(True) # Synthetic mocked mtimes only, NEVER live evidence
        r=self.check()
        self.assertEqual(r["status"],"PASS_R192_OPERATOR_CURRENT_CATALOG_TIME_PARITY_ONLY")
        self.assertEqual(r["observed_visible_cards"],35)
        self.assertEqual(r["observed_condition_sections"],2)
        self.assertEqual(r["r192_catalog_admission"],
                         "PASS_OPERATOR_REPORTED_35_CARD_DEFINITION_PARITY_ONLY")
        self.assertIsNone(r["actual_numeric_market_cap"])
        self.assertIsNone(r["actual_spendable_ecu"])
        self.assertFalse(r["r214_live_advisory_authorized"])
        self.assertEqual(r["gameplay_gate"],"STOP")
        cat=read_json(self.root/"report/R223_R192_CURRENT_CATALOG_PRIVATE.json")
        self.assertEqual(len(cat["projects"]),35)
        self.assertEqual({x["id"]:x["project_conditions"] for x in cat["projects"] if x["project_conditions"]},
                          {30:["Bicikliútfejlesztés — Fut"],31:["Vasútfejlesztés — Fut"]})
    def test_spoofed_bubi_condition_cannot_pass_original_r192(self):
        self.add_old_three(True)
        p=self.pages/"projects_transport.txt"
        s=p.read_text()
        self.assertIn("Bicikliútfejlesztés — Fut",s)
        p.write_text(s.replace("Projekt feltételek\n\nBicikliútfejlesztés — Fut\n\n","",1))
        with self.assertRaisesRegex(ValueError,"HOLD_CURRENT_CARD_DEFINITION_DRIFT_30"):
            self.check()
    def test_wrong_sport_category_fails_closed(self):
        self.add_old_three(True)
        p=self.pages/"projects_sport.txt"
        p.write_text(p.read_text().replace("# VIEW=Sport és Kultúra","# VIEW=Környezet",1))
        with self.assertRaisesRegex(ValueError,"HOLD_CATEGORY_PROVENANCE_projects_sport"):
            self.check()
    def test_summary_source_tampering_refused_before_any_admission(self):
        p=self.pages/"summary.txt"
        p.write_text(p.read_text().replace("Periódus: 1/5","Periódus: 2/5"))
        with self.assertRaisesRegex(Hold,"HOLD_FRESH_R156_SOURCE_HASH_summary"):
            self.check()
        self.assertFalse((self.root/"report").exists())
    def test_refuse_existing_destination(self):
        (self.root/"report").mkdir()
        with self.assertRaisesRegex(Hold,"HOLD_PRIVATE_NEW_RESULT_DIR"):
            self.check()

if __name__=="__main__":unittest.main()
