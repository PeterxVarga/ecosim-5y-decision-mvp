#!/usr/bin/env python3
"""Evidence-first capture gate. Known incomplete data must not be treated as ready."""
import json, os, tempfile, unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from source_freeze_r236 import collect, SCHEMA

class SourceFreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paths={k:Path(os.environ["R236_"+k.upper()]) for k in
              ("r217","r222","r224","r226","r228","r232","r233","r234",
               "r235","income_browser")}
        cls.saved=Path(os.environ["R236_RESULT"])
        cls.data=json.loads((cls.saved/"R236_PRIVATE_LEDGER.json").read_text())
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="r236-source-gate-")
        self.root=Path(self.temp.name)
    def tearDown(self):
        self.temp.cleanup()
    def build(self,**replace):
        sources=dict(self.paths);sources.update(replace)
        return collect(sources,self.root/"result",at_utc="2026-11-02T22:00:00+00:00")
    def fake(self,key,modify):
        source=json.loads(self.paths[key].read_text())
        modify(source)
        p=self.root/(key+".json")
        p.write_text(json.dumps(source,ensure_ascii=False))
        return p
    def test_real_collection_is_not_opt_in_to_optimizing(self):
        s=self.data
        self.assertEqual(s["schema"],SCHEMA)
        self.assertEqual(s["status"],"PARTIAL_SOURCE_COLLECTION_NO_OPTIMIZATION")
        self.assertFalse(s["data_frozen_for_final_optimization"])
        self.assertFalse(s["current_period_full_intake_complete"])
        self.assertFalse(s["game_action_authorized"])
        self.assertFalse(s["run_optimizer"])
        self.assertEqual(s["gameplay_gate"],"STOP")
        self.assertEqual(s["game_writes"],0)
    def test_source_sufficiency_and_freshness(self):
        s=self.data
        v=s["known_period_1_source_counts"]
        self.assertEqual((v["project_cards_observed"],v["city_factor_p0"],
                          v["city_factor_p1_plan"],v["ui_control_surfaces"],
                          v["default_main_views"]),(35,29,29,23,10))
        self.assertEqual(v["fully_verified_control_minmax"],0)
        self.assertEqual(s["total_selector_labels"],27)
        self.assertFalse(s["capture_windows"]["project_cards_coherent_one_hour_capture"])
        self.assertGreater(s["capture_windows"]["project_cards_span_minutes"],100)
        self.assertEqual(len(s["route_selectors"]),10)
        self.assertFalse(s["five_year_future_actuals_present"])
    def test_source_hashes_not_invented(self):
        import hashlib
        for k,p in self.paths.items():
            self.assertEqual(self.data["source_snapshots_sha256"][k],
                hashlib.sha256(p.read_bytes()).hexdigest())
    def test_no_source_overwrite(self):
        with self.assertRaisesRegex(ValueError,"HOLD_NEW_PRIVATE_OUTPUT"):
            collect(self.paths,self.saved)
    def test_false_complete_subviews_fail_closed(self):
        t=self.fake("r226",lambda x:x.update(
            all_selector_subview_contents_observed=True))
        with self.assertRaisesRegex(ValueError,"HOLD_PARTIAL_SUBVIEW_COVERAGE"):
            self.build(r226=t)
    def test_false_admitted_bound_fail_closed(self):
        t=self.fake("r234",lambda x:x.update(current_numeric_minmax_pairs_verified=23))
        with self.assertRaisesRegex(ValueError,"HOLD_POLICY_DATA_STILL_INCOMPLETE"):
            self.build(r234=t)
    def test_forged_35_card_same_hour_fails_closed(self):
        t=self.fake("r222",lambda x:x.update(capture_span_minutes=20))
        with self.assertRaisesRegex(ValueError,"HOLD_CARD_CAPTURE_TIME_WINDOW"):
            self.build(r222=t)
    def test_wrong_market_or_period_in_browser_rejected(self):
        data=json.loads(self.paths["income_browser"].read_text())
        data["text"]=data["text"].replace("Piac: I","Piac: II")
        t=self.root/"other_period.json"
        t.write_text(json.dumps(data,ensure_ascii=False))
        with self.assertRaisesRegex(ValueError,"HOLD_CURRENT_BROWSER_CONTEXT_READONLY_NOT_RENDERED_VALUE"):
            self.build(income_browser=t)
    def test_read_only_repeat(self):
        s=self.build()
        old=dict(self.data)
        old.pop("captured_inventory_at_utc")
        new=dict(s)
        new.pop("captured_inventory_at_utc")
        self.assertEqual(new,old)
        self.assertEqual(s["mode"],"READ_ONLY_SOURCES_DATA_COLLECTION_ONLY")

if __name__=="__main__":unittest.main()
