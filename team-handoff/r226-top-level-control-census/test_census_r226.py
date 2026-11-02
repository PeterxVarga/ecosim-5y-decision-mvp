#!/usr/bin/env python3
"""Source-based R226 ten-menu current P1 and negative test suite."""
from __future__ import annotations
import copy,os,json,sys,tempfile,shutil,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from census_r226 import build,parse_page,loan_control,EXPECTED_NAV,ROUTES,SCHEMA,sha
from json_integrity_r162 import read_json
from policy_tracks import load_tracks,policy_money_replay,policy_factor_replay
from observation_bundle_r152 import compile_bundle
class ActualCurrentTopLevelCensus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.primary=Path(os.environ["R226_PRIMARY"])
        cls.previous=Path(os.environ["R226_R225_PAGES"])
        cls.r225=Path(os.environ["R226_R225_RECEIPT"])
        cls.r156=Path(os.environ["R226_R156"])
        cls.result=Path(os.environ["R226_RESULT"])
        cls.receipt=read_json(cls.result/"R226_RECEIPT.json")
    def setUp(self):
        self.t=tempfile.TemporaryDirectory(prefix="r226-top-menus-")
        self.root=Path(self.t.name)
        self.top=self.root/"top"
        self.top.mkdir()
        for file in self.primary.glob("*.txt"):
            shutil.copy2(file,self.top/file.name)
    def tearDown(self):self.t.cleanup()
    def run_once(self):
        return build(self.top,self.previous,self.r225,self.r156,self.root/"result")
    def test_actual_ten_pages_nineteen_editable_and_nested_labels(self):
        v=self.receipt
        self.assertEqual(v["schema"],SCHEMA)
        self.assertEqual(v["top_level_route_count"],10)
        self.assertEqual([r["route"] for r in v["routes"]],list(ROUTES))
        self.assertEqual(v["observed_editable_text_inputs"],19)
        self.assertEqual(v["original_R225_reused_input_count"],18)
        self.assertEqual(v["additional_long_loan_observed_input_count"],1)
        self.assertEqual(v["distinct_selector_button_labels"],27)
        self.assertTrue(v["selector_buttons_are_nested_or_alternate_not_complete_decision_views"])
        self.assertFalse(v["all_selector_subview_contents_observed"])
        self.assertTrue(v["all_captured_default_views_within_60_min_of_R156"])
        self.assertEqual(sum(x["text_inputs_visible"] for x in v["routes"]),19)
    def test_original_r145_does_not_suppress_unknown19(self):
        t=load_tracks(self.result/"R226_R145_UNKNOWN_TEST_ONLY.json")
        _,state,_=compile_bundle(self.r156/"r156_immutable/manifest.json")
        _,applied,unknown=policy_factor_replay(
           state["team"]["baseline_smartcity_factors"],t[0],1,1)
        cash=policy_money_replay(t[0],1,1)
        self.assertEqual(t[0]["mode"],"DOCUMENTED_OBSERVATION_ONLY")
        self.assertEqual(len(unknown),19)
        self.assertEqual(applied,[])
        self.assertFalse(cash["complete"])
        self.assertEqual(len(cash["undisclosed_policy_cash_decisions"]),19)
    def test_real_long_loan_current_p0_but_no_p1_authorization(self):
        r=self.receipt
        c=next(x for x in r["controls"] if x["domain"]=="loans")
        self.assertEqual(c["p0_visible_number"],0.0)
        self.assertEqual(c["label"],"Felvétel / Visszafizetés (+/-)")
        self.assertEqual(c["p1_visible_input_raw"],"")
        self.assertIsNone(c["p1_current_decision_value"])
        self.assertIsNone(c["actual_allowed_min"])
        self.assertIsNone(c["actual_allowed_max"])
        self.assertFalse(c["game_write_authorized"])
        self.assertIsNone(r["actual_market_cap"])
        self.assertIsNone(r["actual_spendable_project_cash"])
        self.assertEqual(r["gameplay_gate"],"STOP")
        self.assertEqual(r["game_writes"],0)
    def test_all_ten_source_hashes_and_original_r225_link(self):
        r=self.receipt
        for entry in r["routes"]:
            route=entry["route"]
            source=self.top/(route+".txt")
            if not source.exists():
                from census_r226 import source_file
                source=source_file(route,self.top,self.previous)
            self.assertEqual(entry["source_sha256"],sha(source))
        self.assertEqual(r["source_sha256"]["original_r225"],
                         sha(self.r225/"R225_RECEIPT.json"))
    def test_removed_nav_link_fails_closed(self):
        p=self.top/"loans.txt"
        p.write_text(p.read_text().replace(
          '<a href="https://edu.ecosim.hu/simulation/finance">Pénzügyek</a>','',1))
        with self.assertRaisesRegex(ValueError,"HOLD_TEN_MAIN_NAV_ROUTES_loans"):
            self.run_once()
    def test_unobserved_subview_forgery_blocks(self):
        p=self.top/"population.txt"
        p.write_text(p.read_text().replace(
          '<button title="Foglalkozás, kereset"></button>',
          '<button title="Teljesen másik nézet"></button>',1))
        with self.assertRaisesRegex(ValueError,"HOLD_CURRENT_SELECTOR_TOPOLOGY_population"):
            self.run_once()
    def test_an_unexpected_editable_field_is_not_lost(self):
        p=self.top/"corporations.txt"
        old='<td>Mennyiség</td><td>4 742</td><td>4 763</td>'
        self.assertIn(old,p.read_text())
        p.write_text(p.read_text().replace(
          old,'<td>Mennyiség</td><td>4 742</td><td><input type="text" value=""/></td>',1))
        with self.assertRaisesRegex(ValueError,"HOLD_DEFAULT_VIEW_EDITABLE_CELL_COUNT_corporations"):
            self.run_once()
    def test_old_finance_source_time_is_rejected(self):
        p=self.top/"finance.txt"
        mtime=p.stat().st_mtime
        os.utime(p,(mtime-86400,mtime-86400))
        with self.assertRaisesRegex(ValueError,"HOLD_OUTSIDE_CURRENT_R156_60_MIN_WINDOW_finance"):
            self.run_once()
    def test_current_round_identity_mismatch_rejected(self):
        p=self.top/"summary.txt"
        p.write_text(p.read_text().replace("Piac: I","Piac: Z",1))
        with self.assertRaisesRegex(ValueError,"HOLD_REAL_CURRENT_TEAM_PERIOD_summary"):
            self.run_once()
    def test_loan_ambiguous_new_second_editable_fails_closed(self):
        p=self.top/"loans.txt"
        a=p.read_text()
        self.assertIn('<td>Nyitó hitel állomány</td><td>0</td><td>0</td>',a)
        p.write_text(a.replace(
            '<td>Nyitó hitel állomány</td><td>0</td><td>0</td>',
            '<td>Nyitó hitel állomány</td><td>0</td><td><input type="text" value=""/></td>',1))
        with self.assertRaisesRegex(ValueError,"HOLD_DEFAULT_VIEW_EDITABLE_CELL_COUNT_loans"):
            self.run_once()
    def test_no_source_replacement_or_overwrite(self):
        (self.root/"result").mkdir()
        with self.assertRaisesRegex(ValueError,"HOLD_PRIVATE_NEW_OUTPUT"):
            self.run_once()
    def test_production_cap_and_cash_no_laundering(self):
        v=self.receipt
        self.assertEqual(v["unknown_minmax_count"],19)
        self.assertEqual(v["unknown_p1_approved_decisions_count"],19)
        self.assertEqual(v["unknown_factor_effect_count"],19)
        self.assertEqual(v["unknown_cash_response_count"],19)
        self.assertFalse(v["original_R145_cashflow_complete"])
        self.assertIsNone(v["actual_P1_policy_recommendation"])
        self.assertIsNone(v["five_year_joint_policy_city_score_forecast"])
if __name__=="__main__":unittest.main()
