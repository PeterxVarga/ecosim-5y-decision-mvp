import copy,sys,unittest
from pathlib import Path
REPO=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
sys.path.insert(0,str(REPO/"team-handoff/r200-historical-plugplay/tools"))
from transition_r203 import run,provenance,exact_plans,make_years,markdown,STATUS,SCHEMA,SCALES,validate_test_fact_plan,validate_test_fact_plan
from corpus_r200 import parse_json
PROFILE=REPO/"team-handoff/r200-historical-plugplay/profiles/historical_R94_R200.json"
P201=Path.home()/"Downloads/ecosim-r201-historical-tgwUX7NS/R201.json"
P202=Path.home()/"Downloads/ecosim-r202-historical-v6w3euqA/R202.json"

class StaticContractTests(unittest.TestCase):
 def test_scenario_intensity_not_forecast(self):
  self.assertEqual(SCALES,(.5,1.,1.5))
 def test_schema_label(self):
  self.assertIn("PARTIAL_ANNUAL_SENSITIVITY",SCHEMA)
 def test_report_action_gate(self):
  test={"status":STATUS,"partial_project_transition_diagnostics":{
    "plan_count":0,"annual_project_only_ledgers":0,
    "direct_factor_sensitivity_evaluations":0,
    "rankings_by_assumed_direct_effect_intensity":[],"plans":[]},
    "r201_financial_candidate_scenarios":0,"r202_observed_source_model_pairs":0,
    "observed_snapshots":[{"period":0,"kind":"FACT","displayed_total_index":51.96},
                          {"period":1,"kind":"PLAN","displayed_total_index":52.48}]}
  out=markdown(test)
  self.assertIn("GAME_ACTION_GATE=STOP",out)
  self.assertIn("megfigyelt állapotátmeneti tanítóminta: 0",out)
  self.assertIn("nem valószínűségek",out)

@unittest.skipUnless(PROFILE.is_file() and P201.is_file() and P202.is_file(),
  "Private historical source profile and R201/R202 outputs required")
class NativeHistoricalEvidenceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p=parse_json(PROFILE.read_bytes())
  cls.r201=parse_json(P201.read_bytes())
  cls.r202=parse_json(P202.read_bytes())
  cls.result=run(cls.p,PROFILE,cls.r201,cls.r202)
 def hold(self,callback,match):
  with self.assertRaisesRegex(ValueError,"HOLD_"+match):
   callback()
 def test_complete_replay_counts(self):
  t=self.result["partial_project_transition_diagnostics"]
  self.assertEqual((t["plan_count"],t["annual_project_only_ledgers"],
                     t["direct_factor_sensitivity_evaluations"]),
                    (17,85,255))
 def test_17_unique_plans_with_five_years(self):
  rows=self.result["partial_project_transition_diagnostics"]["plans"]
  self.assertEqual(len({r["id"] for r in rows}),17)
  self.assertTrue(all(len(r["annual_records"])==5 for r in rows))
 def test_two_r195_exact_plans(self):
  ids={r["id"] for r in self.result["partial_project_transition_diagnostics"]["plans"]}
  self.assertTrue({"R195-max","R195-reserve"}<=ids)
 def test_r149_15_other_plans(self):
  rows=self.result["partial_project_transition_diagnostics"]["plans"]
  self.assertEqual(sum(r["source"]=="R149_BOUNDED_HISTORICAL" for r in rows),15)
 def test_three_static_stress_assumptions_only(self):
  t=self.result["partial_project_transition_diagnostics"]
  self.assertEqual(t["project_effect_intensity_assumptions"],[.5,1.,1.5])
  self.assertTrue(all(len(r["terminal"])==3 for r in t["plans"]))
 def test_rankings_are_permutation_each_intensity(self):
  t=self.result["partial_project_transition_diagnostics"]
  candidates={r["id"] for r in t["plans"]}
  for rank in t["rankings_by_assumed_direct_effect_intensity"]:
   self.assertEqual(set(rank["all_source_partial_order"]),candidates)
   self.assertTrue(rank["not_real_city_ranking"])
 def test_mapped_vs_unmapped_kept_separate(self):
  for r in self.result["partial_project_transition_diagnostics"]["plans"]:
   for v in r["annual_records"]:
    self.assertTrue(all(k["unmodeled_city_drift_has_no_bound"]
      for k in v["conditional_index_stress"]))
    self.assertIsNone(v["actual_server_index"])
 def test_actual_transition_absent(self):
  t=self.result["partial_project_transition_diagnostics"]
  self.assertEqual(t["observed_fact_to_fact_transition_samples"],0)
  self.assertEqual(t["actual_city_transitions_inferred"],0)
  self.assertFalse(t["simulator_outcome_validation"])
 def test_p0_fact_and_p1_plan_not_actual(self):
  self.assertEqual([(x["period"],x["kind"]) for x in
                    self.result["observed_snapshots"]],[(0,"FACT"),(1,"PLAN")])
 def test_unverified_cash_always_stop(self):
  self.assertFalse(self.result["actual_cash_authorized"])
  self.assertFalse(self.result["global_city_optimum_certified"])
  self.assertEqual(self.result["game_writes"],0)
  self.assertEqual(self.result["gameplay_gate"],"STOP")
 def test_source_role_alignment(self):
  self.assertEqual(self.result["source_roles"],16)
  self.assertEqual(self.result["tab_count"],10)
  self.assertEqual(self.result["r201_financial_candidate_scenarios"],51)
  self.assertEqual(self.result["r202_observed_source_model_pairs"],18)
 def test_no_score_confidence_claim(self):
  self.assertFalse(self.result["synthetic_effect_intensity_is_probability_or_confidence_interval"])
  self.assertFalse(self.result["real_simulator_forecast_validated"])
 def test_oversaturated_effect_not_falsely_unique(self):
  rows=self.result["partial_project_transition_diagnostics"]["plans"]
  for r in rows:
   for y in r["annual_records"]:
    for z in y["conditional_index_stress"]:
     lo,hi=z["index_interval_if_only_saturation_unknown"]
     self.assertLessEqual(lo,hi)
 def test_r201_forged_sha_hold(self):
  x=copy.deepcopy(self.r201);x["baseline_source_sha256"]="0"*64
  self.hold(lambda:run(self.p,PROFILE,x,self.r202),"R201_JOIN")
 def test_r201_fake_authority_hold(self):
  x=copy.deepcopy(self.r201);x["gameplay_gate"]="GO"
  self.hold(lambda:run(self.p,PROFILE,x,self.r202),"R201_JOIN")
 def test_r202_fake_live_calibration_hold(self):
  x=copy.deepcopy(self.r202);x["live_prediction_calibrated"]=True
  self.hold(lambda:run(self.p,PROFILE,self.r201,x),"R202_JOIN")
 def test_r202_forged_hash_hold(self):
  x=copy.deepcopy(self.r202);x["source_hashes"]["finance"]="0"*64
  self.hold(lambda:run(self.p,PROFILE,self.r201,x),"R202_JOIN")
 def test_r200_current_mode_hold(self):
  x=copy.deepcopy(self.p);x["mode"]="current-readonly"
  self.hold(lambda:run(x,PROFILE,self.r201,self.r202),"NO_HISTORICAL_FALLBACK")
 def test_other_gameplay_gate_hold(self):
  x=copy.deepcopy(self.r202);x["game_writes"]=1
  self.hold(lambda:run(self.p,PROFILE,self.r201,x),"R202_JOIN")
 def test_p1_fact_tampering_hold(self):
  a,raw,state,passive,desk,exact=provenance(self.p,PROFILE,self.r201,self.r202)
  passive["snapshots"][1]["kind"]="FACT"
  # Forged p1 appears as a second FACT; R203 forbids this before model replay.
  self.hold(lambda:validate_test_fact_plan(passive["snapshots"]),
            "FACT_PLAN_NOT_TRAINING_PAIR")
 def test_exact_two_sources_17(self):
  a,raw,state,passive,desk,exact=provenance(self.p,PROFILE,self.r201,self.r202)
  self.assertEqual(len(exact_plans(desk,exact)),17)
 def test_disallow_changed_project_cost(self):
  a,raw,state,passive,desk,exact=provenance(self.p,PROFILE,self.r201,self.r202)
  broken=copy.deepcopy(exact)
  broken["plans"][0]["project_cost_ecu_by_year"][0]+=100
  self.hold(lambda:make_years(state,desk,broken),"R148_R149_R199_COST_DRIFT")
if __name__=="__main__":unittest.main()
