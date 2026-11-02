import copy,json,math,sys,unittest
from pathlib import Path
REPO=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
sys.path.insert(0,str(REPO/"team-handoff/r200-historical-plugplay/tools"))
from calibrate_r202 import (
    build,channels,ratio_diagnostic,exact_ledger_row,report_md,
    FEE_ROWS,TAX_ROWS,WAGE_ROWS,SCHEMA,STATUS)
from corpus_r200 import parse_json,resolve,sha

PROFILE=REPO/"team-handoff/r200-historical-plugplay/profiles/historical_R94_R200.json"
class StandaloneTests(unittest.TestCase):
 def row(self,idx,label,p0="10",p1="11",view="cash_flow",table="Bevételek"):
  return {"row_id":"r"+str(idx),"view":view,"table_title":table,
    "row_index":str(idx),"label":label,"p0_number":p0,"p1_number":p1}
 def hold(self,func,reason):
  with self.assertRaisesRegex(ValueError,"HOLD_"+reason):
   func()
 def test_exact_row_by_id_and_label(self):
  a=self.row(8,"Iparűzési adó")
  b=self.row(8,"Iparűzési adó",p0="700",table="Kiadások")
  out=exact_ledger_row([a,b],"cash_flow","Bevételek","8","Iparűzési adó")
  self.assertEqual(out["p0_actual_raw"],10.)
 def test_wrong_label_hold(self):
  self.hold(lambda:exact_ledger_row([self.row(8,"bad")],"cash_flow","Bevételek","8","Iparűzési adó"),
            "LEDGER_ROW_IDENTITY")
 def test_duplicate_ledger_row_hold(self):
  x=self.row(8,"Iparűzési adó")
  self.hold(lambda:exact_ledger_row([x,x],"cash_flow","Bevételek","8","Iparűzési adó"),
            "LEDGER_ROW_IDENTITY")
 def test_nonfinite_ledger_hold(self):
  self.hold(lambda:exact_ledger_row([self.row(8,"Iparűzési adó",p0="NaN")],
            "cash_flow","Bevételek","8","Iparűzési adó"),"LEDGER_NUMERIC")
 def test_negative_ledger_hold(self):
  self.hold(lambda:exact_ledger_row([self.row(8,"Iparűzési adó",p0="-1")],
            "cash_flow","Bevételek","8","Iparűzési adó"),"LEDGER_NUMERIC")
 def test_boolean_like_row_hold(self):
  self.hold(lambda:exact_ledger_row([self.row(8,"Iparűzési adó",p0="true")],
            "cash_flow","Bevételek","8","Iparűzési adó"),"LEDGER_NUMERIC")
 def test_model_channel_set_hold(self):
  self.hold(lambda:channels([], "cash_flow","Bevételek",[("a","1","A")],{"b":1}),
            "CHANNEL_SET")
 def test_model_nonfinite_hold(self):
  x=[self.row(1,"A")]
  self.hold(lambda:channels(x,"cash_flow","Bevételek",[("a","1","A")],{"a":math.inf}),
            "MODEL_CHANNEL_NONFINITE")
 def test_ratios_same_scale_is_only_diagnostic(self):
  data={"sample":[{"observed_to_model_ratio_unqualified":2.} for _ in range(4)]}
  result=ratio_diagnostic(data)
  self.assertTrue(result["exact_universal_baseline_scale_supported"])
  self.assertFalse(result["universal_currency_conversion_identified"])
 def test_ratios_heterogeneous(self):
  data={"sample":[{"observed_to_model_ratio_unqualified":p}
                 for p in [1.,1.1,2.,8.]]}
  result=ratio_diagnostic(data)
  self.assertEqual(result["ratio_max_div_min"],8.)
  self.assertFalse(result["exact_universal_baseline_scale_supported"])
 def test_insufficient_ratio_holds(self):
  self.hold(lambda:ratio_diagnostic({"sample":[{"observed_to_model_ratio_unqualified":3.}]}),
            "INSUFFICIENT_SCALE_PAIRS")
 def test_report_has_stop(self):
  doc={"status":STATUS,"source_roles_total":0,"observed_channel_groups":{},
       "units_and_bases":{"compared_positive_channel_count":4,"ratio_min":1.,
                          "ratio_max":9.,"ratio_max_div_min":9.},
       "ledger_vs_model_totals":{},
       "observed_fee_component_minus_reported_total_raw":{"p0_actual_raw":2,"p1_target_raw":2},
       "model_identifiability":{},"research_priority":[]}
  s=report_md(doc)
  self.assertIn("GAME_ACTION_GATE=STOP",s)
  self.assertIn("nem átváltási tényező",s)
 def test_model_channel_roles(self):
  self.assertEqual(len(TAX_ROWS),4)
  self.assertEqual(len(FEE_ROWS),6)
  self.assertEqual(len(WAGE_ROWS),8)
  self.assertEqual(len({(idx,label) for _,idx,label in TAX_ROWS+FEE_ROWS+WAGE_ROWS}),18)
 def test_typed_synthetic_json_rejects_nan(self):
  with self.assertRaisesRegex(ValueError,"NONFINITE_JSON"):
   parse_json(b'{"x":Infinity}')

@unittest.skipUnless(PROFILE.exists(),"Owner-private source profile not installed")
class NativeObservedTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.profile=parse_json(PROFILE.read_bytes())
  cls.result=build(cls.profile,PROFILE)
 def test_channel_counts_and_source_hashes(self):
  self.assertEqual(sum(map(len,self.result["observed_channel_groups"].values())),18)
  self.assertEqual(len(self.result["source_hashes"]),5)
  self.assertEqual(self.result["source_roles_total"],16)
 def test_four_tax_reconciliation(self):
  groups=self.result["ledger_vs_model_totals"]
  self.assertGreater(groups["four_tax_channels"]["p0_actual_components_raw"],0)
  self.assertGreater(groups["six_fee_channels"]["p0_actual_components_raw"],0)
  self.assertGreater(groups["eight_wage_channels"]["p0_actual_components_raw"],0)
 def test_observed_synthetic_mismatch_is_not_calibration(self):
  ratios=self.result["units_and_bases"]
  self.assertEqual(ratios["compared_positive_channel_count"],18)
  self.assertGreater(ratios["ratio_max_div_min"],10)
  self.assertFalse(ratios["universal_currency_conversion_identified"])
  self.assertFalse(ratios["underlying_exogenous_city_bases_identified"])
 def test_no_false_cash_authority(self):
  result=self.result
  self.assertFalse(result["global_city_optimum_certified"])
  self.assertFalse(result["live_prediction_calibrated"])
  self.assertEqual((result["game_writes"],result["gameplay_gate"]),(0,"STOP"))
 def test_no_borrowed_consecutive_actual_year(self):
  self.assertTrue(self.result["p0_is_actual_and_p1_is_plan"])
  self.assertTrue(self.result["p1_not_a_following_actual_year"])
  self.assertFalse(self.result["model_identifiability"]["can_calibrate_multi_year_transitions_from_two_actual_years"])
 def test_fee_rounding_residual_takes_source(self):
  fee=self.result["observed_fee_component_minus_reported_total_raw"]
  self.assertEqual(fee["p0_actual_raw"],fee["p1_target_raw"])
  self.assertGreater(fee["p0_actual_raw"],0)
 def test_year_one_synthetic_source_only(self):
  self.assertEqual(self.result["model_source"],
       "R154_R155_REUSED_CLIENT_COMPONENTS_STATIC_EXOGENOUS")
 def test_tampered_profile_hash_holds(self):
  p=copy.deepcopy(self.profile);p["sources"]["finance"]["sha256"]="0"*64
  with self.assertRaisesRegex(ValueError,"HOLD_SOURCE_SHA_finance"):
   build(p,PROFILE)
 def test_current_mode_holds(self):
  p=copy.deepcopy(self.profile);p["mode"]="current-readonly"
  with self.assertRaisesRegex(ValueError,"HOLD_NO_HISTORICAL_FALLBACK"):
   build(p,PROFILE)
if __name__=="__main__":unittest.main()
