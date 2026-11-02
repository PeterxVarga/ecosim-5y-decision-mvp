#!/usr/bin/env python3
"""R228 focused actual-source & fail-closed integration qualification."""
from __future__ import annotations
import copy,json,os,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from source_join_r228 import (parse_excel,tax_source,match,R226_ROW_MAP,TAX_MAP,
                             join,digest,SCHEMA,need)
from json_integrity_r162 import read_json
from policy_tracks import load_tracks,policy_money_replay,policy_factor_replay
from observation_bundle_r152 import compile_bundle

class ExcelUiR145R148RealSource(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.excel=Path(os.environ["R228_EXCEL"])
  cls.r226=Path(os.environ["R228_R226"])
  cls.tax=Path(os.environ["R228_TAX"])
  cls.r156=Path(os.environ["R228_R156"])
  cls.r224=Path(os.environ["R228_R224"])
  cls.out=Path(os.environ["R228_RESULT"])
  cls.receipt=read_json(cls.out/"R228_RECEIPT.json")
  cls.xlsx=parse_excel(cls.excel)
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix="r228-failclosed-")
  self.tmp=Path(self.temp.name)
 def tearDown(self):self.temp.cleanup()
 def test_original_exact_source_374_rows_324_numerics(self):
  x=self.xlsx
  self.assertEqual(x["labelled"],374)
  self.assertEqual(x["own_numeric"],324)
  self.assertEqual(x["own_non_numeric"],50)
  self.assertEqual(len(x["seven_teams"]),7)
  self.assertEqual(self.receipt["source_sha256"]["excel"],digest(self.excel))
  self.assertEqual(x["rows"][198]["own_p0"],2.0)
  self.assertEqual(x["rows"][199]["own_p0"],1.9)
 def test_twenty_three_fields_nineteen_exact_four_unmatched(self):
  v=self.receipt
  self.assertEqual(v["schema"],SCHEMA)
  self.assertEqual(v["status"],"PASS_R227_EXCEL_SOURCE_JOIN_R145_R148_UNKNOWN_PRESERVED_NOT_LIVE")
  self.assertEqual(v["r226_controls"],19)
  self.assertEqual(v["new_tax_view_controls"],4)
  self.assertEqual(v["observed_total_controls"],23)
  self.assertEqual(v["exact_xlsx_vs_ui_p0_matches"],19)
  self.assertEqual(len(v["exact_links"]),19)
  self.assertEqual(len(v["unmatched_controls"]),4)
  self.assertEqual(len(set(x["excel_row"] for x in v["exact_links"])),19)
  self.assertEqual(len(set(x["control_id"] for x in v["exact_links"])),19)
 def test_19_source_links_are_not_game_actions(self):
  for x in self.receipt["exact_links"]:
   self.assertEqual(x["match"],"EXACT_LABEL_SECTION_AND_NUMERIC_P0")
   self.assertEqual(x["excel_p0"],x["observed_ui_p0"])
   self.assertIsNone(x["p1_selected"])
   self.assertIsNone(x["allowed_min"])
   self.assertIsNone(x["allowed_max"])
   self.assertIsNone(x["calibrated_cash_response"])
   self.assertIsNone(x["calibrated_factor_response"])
   self.assertFalse(x["game_write_authorized"])
 def test_original_r145_unknown_each_of_five_future_years(self):
  track=load_tracks(self.out/"R228_POLICY_UNKNOWN_CONTRACT_TEST_ONLY.json")[0]
  self.assertEqual(len(track["actions"]),23*5)
  _,state,_=compile_bundle(self.r156/"r156_immutable/manifest.json")
  for year in range(1,6):
   _,applied,unknown=policy_factor_replay(
       state["team"]["baseline_smartcity_factors"],track,year,1)
   money=policy_money_replay(track,year,1)
   self.assertEqual(applied,[])
   self.assertEqual(len(unknown),23)
   self.assertFalse(money["complete"])
   self.assertEqual(len(money["undisclosed_policy_cash_decisions"]),23)
 def test_original_r148_joint_twenty_four_five_year_replays(self):
  v=self.receipt
  self.assertEqual(v["r148_original_joint_scenario_count"],24)
  self.assertEqual(v["r148_original_joint_annual_rows"],120)
  self.assertEqual(len(v["conditional_joint_scenarios"]),24)
  for s in v["conditional_joint_scenarios"]:
   self.assertEqual(len(s["annual_replay"]),5)
   for yr in s["annual_replay"]:
    self.assertEqual(yr["unknown_policy_factor_effects"],23)
    self.assertEqual(yr["unknown_policy_cash_impacts"],23)
    self.assertIsNone(yr["actual_index_forecast"])
    self.assertIsNone(yr["actual_cashflow_forecast"])
 def test_r153_r154_reject_false_money_percent_mapping(self):
  t=self.receipt["actual_tax_model_readiness"]
  self.assertEqual(t["source_verified_business_tax_percentage"],2.0)
  self.assertEqual(t["vehicle_UI_unit"],"PERCENT_NOT_VERIFIED_ECU_AMOUNT")
  self.assertIsNone(t["vehicle_tax_amount"])
  self.assertIsNone(t["building_tax_amount"])
  self.assertIsNone(t["market_coefficients_and_tax_divisors"])
  self.assertIsNone(t["services_fee_percentage"])
  self.assertFalse(t["R153_actual_tax_counterfactual_allowed"])
  self.assertFalse(t["R154_actual_tax_revenue_forecast_allowed"])
  self.assertTrue(t["do_not_convert_ui_percent_to_tax_amount_without_source"])
 def test_no_owner_approval_or_project_start_inferred(self):
  v=self.receipt
  self.assertEqual(v["current_P1_selected_actions_approved"],0)
  self.assertIsNone(v["current_market_cap_verified"])
  self.assertIsNone(v["current_spendable_project_cash_verified"])
  self.assertFalse(v["current_R192_full_catalog_time_admitted"])
  self.assertIsNone(v["actual_first_year_eligible_recommendation"])
  self.assertIsNone(v["actual_five_year_winning_plan"])
  self.assertEqual(v["gameplay_gate"],"STOP")
  self.assertEqual(v["game_writes"],0)
 def test_excel_source_pin_rejects_file_tampering(self):
  p=self.tmp/"tampered.xlsx"
  data=bytearray(self.excel.read_bytes())
  data[200]=(data[200]+1)%256
  p.write_bytes(data)
  with self.assertRaisesRegex(ValueError,"HOLD_EXCEL_ORIGINAL_PIN_MISMATCH"):
   parse_excel(p)
 def test_wrong_visible_tax_value_does_not_match_excel(self):
  s=read_json(self.tax)
  s["controls"][0]["p0"]=3
  tmp=self.tmp/"bad_tax.json"
  tmp.write_text(json.dumps(s))
  with self.assertRaisesRegex(ValueError,"HOLD_EXCEL_UI_VALUE_DRIFT_198"):
   join(self.excel,self.r226,tmp,self.r156,self.r224,self.tmp/"out")
 def test_invented_tax_p1_is_not_admitted(self):
  s=read_json(self.tax)
  s["controls"][0]["p1_input"]="3"
  tmp=self.tmp/"bad_tax.json"
  tmp.write_text(json.dumps(s))
  with self.assertRaisesRegex(ValueError,"HOLD_NO_APPROVED_TAX_P1_INPUT"):
   tax_source(tmp)
 def test_r226_source_control_list_modification_rejected(self):
  o=read_json(self.r226)
  o["controls"][0]["actual_allowed_min"]=100
  tmp=self.tmp/"fake_r226.json"
  tmp.write_text(json.dumps(o))
  with self.assertRaisesRegex(ValueError,"HOLD_R226_NOT_APPROVED_CONTROL"):
   join(self.excel,tmp,self.tax,self.r156,self.r224,self.tmp/"out")
 def test_untrusted_unmapped_row_does_not_fuzzy_join(self):
  c={"decision_key":"invented","domain":"transport_ice_bus",
     "label":"Karbantartás","p0_visible_number":175000}
  with self.assertRaisesRegex(ValueError,"HOLD_EXCEL_UI_VALUE_DRIFT_145"):
   match(self.xlsx,c,145)
 def test_output_destination_cannot_be_overwritten(self):
  p=self.tmp/"existing";p.mkdir()
  with self.assertRaisesRegex(ValueError,"HOLD_NEW_PRIVATE_RESULT_DIR"):
   join(self.excel,self.r226,self.tax,self.r156,self.r224,p)
 def test_source_sha_covers_all_five_inputs(self):
  v=self.receipt["source_sha256"]
  self.assertEqual(v["r226_receipt"],digest(self.r226))
  self.assertEqual(v["tax_view"],digest(self.tax))
  self.assertEqual(v["r224_receipt"],digest(self.r224))
  self.assertEqual(v["r156_manifest"],digest(self.r156/"r156_immutable/manifest.json"))
if __name__=="__main__":unittest.main()
