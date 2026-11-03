#!/usr/bin/env python3
"""Self-contained source-identity and STOP-gate regression checks."""
import copy,importlib.util,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location("r204_engine",Path(__file__).with_name("decision_engine.py"))
engine=importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)

def fixture():
 result={
 "R201":{"baseline_source_sha256":"B","finance_source_sha256":"F","institutions_source_sha256":"I",
         "r149_source_sha256":"T","r199_source_sha256":"U","calibrated_five_year_live_prediction":False,
         "simulator_score_formula_proven":False,"scenario_robustness":{"candidate_count":17,"scenario_count":51}},
 "R202":{"source_hashes":{"finance":"F","institutions":"I"},"live_prediction_calibrated":False,
         "global_city_optimum_certified":False,"model_identifiability":{},"units_and_bases":{},"research_priority":[]},
 "R203":{"source_sha256":{"r200_profile_source_state":"B","finance":"F","institutions":"I","r149":"T","r199":"U"},
         "r201_financial_candidate_scenarios":51,"r202_observed_source_model_pairs":18,"tab_count":10,
         "ten_tab_coverage":{str(i):{} for i in range(10)},"partial_project_transition_diagnostics":{},
         "model_input_is_p1_plan_not_p0_fact":True,"real_simulator_forecast_validated":False,
         "global_city_optimum_certified":False,"actual_cash_authorized":False}
 }
 for k,v in result.items():
  v.update(schema=engine.EXPECTED[k][0],status=engine.EXPECTED[k][1],
           mode="historical-test",game_writes=0,gameplay_gate="STOP")
 return result

class Tests(unittest.TestCase):
 def setUp(self):self.docs=fixture()
 def packet(self):
  old_load,old_sha=engine.load,engine.sha
  engine.load=lambda p:copy.deepcopy(self.docs[str(p)])
  engine.sha=lambda p:"synthetic-hash"
  try:return engine.assemble({k:k for k in engine.EXPECTED})
  finally:engine.load,engine.sha=old_load,old_sha
 def test_valid(self):
  p=self.packet()
  self.assertEqual(p["scenario_count"],51)
  self.assertEqual(p["decision"]["live"],"HOLD")
 def test_source_drift(self):
  self.docs["R202"]["source_hashes"]["finance"]="DRIFT"
  with self.assertRaisesRegex(ValueError,"HOLD_CALIBRATION_SOURCE_IDENTITY"):self.packet()
 def test_action_drift(self):
  self.docs["R203"]["game_writes"]=1
  with self.assertRaisesRegex(ValueError,"HOLD_R203_NO_GAME_WRITE"):self.packet()
 def test_live_claim(self):
  self.docs["R201"]["calibrated_five_year_live_prediction"]=True
  with self.assertRaisesRegex(ValueError,"HOLD_R201_OVERCLAIM"):self.packet()
 def test_fact_plan_confusion(self):
  self.docs["R203"]["model_input_is_p1_plan_not_p0_fact"]=False
  with self.assertRaisesRegex(ValueError,"HOLD_FACT_PLAN_SEPARATION"):self.packet()
if __name__=="__main__":unittest.main()
