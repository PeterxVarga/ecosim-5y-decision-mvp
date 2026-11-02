#!/usr/bin/env python3
"""Read-only source-driven R225 tests against private authenticated UI pages."""
from __future__ import annotations
import os,json,sys,tempfile,shutil,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from intake_r225 import build,parse_source,GROUPS,TOTAL_CONTROLS,TAB_COUNT,sha,SCHEMA
from policy_tracks import load_tracks,policy_factor_replay,policy_money_replay
from observation_bundle_r152 import compile_bundle
from json_integrity_r162 import read_json

class ActualPeriodicInputs(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.pages=Path(os.environ["R225_PRIVATE_PAGES"])
  cls.r156=Path(os.environ["R225_PRIVATE_R156"])
  cls.receipt=Path(os.environ["R225_PRIVATE_RECEIPT"])
  cls.result=read_json(cls.receipt/"R225_RECEIPT.json")
 def setUp(self):
  self.t=tempfile.TemporaryDirectory(prefix="r225-failclosed-")
  self.folder=Path(self.t.name)
  self.pages2=self.folder/"pages"
  self.pages2.mkdir()
  for file in self.pages.glob("*.txt"):shutil.copy2(file,self.pages2/file.name)
 def tearDown(self):self.t.cleanup()
 def invoke(self):
  return build(self.pages2,self.r156,self.folder/"result")
 def test_actual_current_18_fields_exact_source_categories(self):
  r=self.result
  self.assertEqual(r["schema"],SCHEMA)
  self.assertEqual(r["observed_editable_controls"],TOTAL_CONTROLS)
  self.assertEqual(TOTAL_CONTROLS,18)
  self.assertEqual(r["known_subview_count"],TAB_COUNT)
  self.assertEqual(TAB_COUNT,12)
  self.assertEqual(r["unobserved_subviews_count"],9)
  count={s:sum(x["domain"]==s for x in r["controls"]) for s in GROUPS}
  self.assertEqual(count,{"institutions_education":7,"transport_ice_bus":5,"income_service_fees":6})
  self.assertEqual(len({x["decision_key"] for x in r["controls"]}),18)
 def test_p0_numbers_are_real_p1_bounds_impact_approval_all_unknown(self):
  r=self.result
  self.assertEqual(r["p1_decision_values_verified"],0)
  self.assertEqual(r["numeric_bounds_verified"],0)
  self.assertEqual(r["calibrated_policy_effects_verified"],0)
  for x in r["controls"]:
   self.assertIsInstance(x["p0_visible_number"],float)
   self.assertIsNone(x["p1_current_decision_value"])
   self.assertIsNone(x["actual_allowed_min"])
   self.assertIsNone(x["actual_allowed_max"])
   self.assertIsNone(x["factor_response"])
   self.assertIsNone(x["cash_response_ecu"])
   self.assertFalse(x["game_write_authorized"])
  self.assertIsNone(r["actual_market_cap"])
  self.assertIsNone(r["actual_project_spendable_cash"])
  self.assertEqual(r["game_writes"],0)
 def test_readonly_source_and_same_hour_sha(self):
  self.assertTrue(self.result["capture_times_within_60_min_of_R156"])
  self.assertTrue(self.result["file_mtime_is_not_cryptographic_server_attestation"])
  hashes=self.result["sha256"]["periodic_page_sources"]
  for n,v in hashes.items():
   self.assertEqual(sha(self.pages/(n+".txt")),v)
  self.assertEqual(self.result["sha256"]["current_r156_receipt"],
                   sha(self.r156/"R217_RECEIPT.json"))
 def test_actual_r145_reuse_unknowns_remain_unknown(self):
  path=self.receipt/"R225_R145_UNKNOWN_EFFECT_CONTRACT_TEST_ONLY.json"
  t=load_tracks(path)
  self.assertEqual(len(t),1)
  self.assertEqual(t[0]["mode"],"DOCUMENTED_OBSERVATION_ONLY")
  self.assertEqual(len(t[0]["actions"]),18)
  _,state,_=compile_bundle(self.r156/"r156_immutable/manifest.json")
  f,applied,unknown=policy_factor_replay(state["team"]["baseline_smartcity_factors"],
                                          t[0],1,1)
  money=policy_money_replay(t[0],1,1)
  self.assertEqual(len(unknown),18)
  self.assertEqual(applied,[])
  self.assertFalse(money["complete"])
  self.assertEqual(len(money["undisclosed_policy_cash_decisions"]),18)
 def test_missing_education_decision_field_rejected(self):
  p=self.pages2/"institutions_education.txt"
  text=p.read_text().replace('<td>Bérek</td><td>550</td><td><input type="text" value=""/>',
                              '<td>Bérek</td><td>550</td><td>550',1)
  p.write_text(text)
  with self.assertRaisesRegex(ValueError,"HOLD_EXACT_KNOWN_CONTROL_LIST"):
   self.invoke()
 def test_unseen_income_subview_not_laundered_as_service_fees(self):
  p=self.pages2/"income_service_fees.txt"
  p.write_text(p.read_text().replace("# ACTIVE_VIEW=Szolgáltatások díjai",
                                     "# ACTIVE_VIEW=Adók",1))
  with self.assertRaisesRegex(ValueError,"HOLD_SOURCE_PROVENANCE"):
   self.invoke()
 def test_missing_bus_maintenance_field_rejected(self):
  p=self.pages2/"transport_ice_bus.txt"
  p.write_text(p.read_text().replace('<td>Karbantartás</td><td>175,000</td>',
                                     '<td>Nem ellenőrzött érték</td><td>175,000</td>',1))
  with self.assertRaisesRegex(ValueError,"HOLD_EXACT_KNOWN_CONTROL_LIST"):
   self.invoke()
 def test_extra_editable_service_fees_field_refused(self):
  p=self.pages2/"income_service_fees.txt"
  s=p.read_text()
  s=s.replace('<td>Temetkezés</td><td>32 973</td><td>33 617</td>',
              '<td>Temetkezés</td><td>32 973</td><td><input type="text" value=""/></td>',1)
  p.write_text(s)
  with self.assertRaisesRegex(ValueError,"HOLD_EXACT_KNOWN_CONTROL_LIST"):
   self.invoke()
 def test_fake_p1_nonempty_not_approved_or_effect_calibrated(self):
  p=self.pages2/"income_service_fees.txt"
  p.write_text(p.read_text().replace('<td>Tömegközlekedés / fő</td><td>12.4</td><td><input type="text" value=""/>',
                                      '<td>Tömegközlekedés / fő</td><td>12.4</td><td><input type="text" value="17"/>',1))
  r=self.invoke()
  x=next(x for x in r["controls"] if x["label"]=="Tömegközlekedés / fő")
  self.assertEqual(x["p1_visible_input_raw"],"17")
  self.assertIsNone(x["p1_current_decision_value"])
  self.assertFalse(x["game_write_authorized"])
  self.assertEqual(r["R145_unknown_factor_effects_propagated"],18)
 def test_source_mtime_forced_outside_window_rejected(self):
  p=self.pages2/"transport_ice_bus.txt"
  stamp=p.stat().st_mtime
  os.utime(p,(stamp-86400,stamp-86400))
  with self.assertRaisesRegex(ValueError,"HOLD_NOT_WITHIN_60_MIN_OF_CURRENT_R156"):
   self.invoke()
 def test_existing_output_refused(self):
  (self.folder/"result").mkdir()
  with self.assertRaisesRegex(ValueError,"HOLD_NEW_PRIVATE_OUTPUT"):
   self.invoke()
 def test_csv_contains_no_fabricated_current_decisions(self):
  text=(self.receipt/"R225_PERIODIC_UI_CONTROL_INVENTORY.csv").read_text()
  self.assertEqual(len(text.splitlines()),19)
  self.assertIn("UNKNOWN",text)
  self.assertNotIn("OFFICIAL_LIVE_ADMISSION",text)
if __name__=="__main__":unittest.main()
