import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from fact_pair_r203 import admissible,SCHEMA

class FactPairTests(unittest.TestCase):
 def case(self):
  def row(i):
   return {"id":f"observed-{i}","team":"Operator team","market":"Test market",
     "period":i,"kind":"FACT","captured_at":"2026-11-02",
     "source_evidence_id":f"independent-proof-{i}",
     "factors":{f"Factor {j:02}":float(j+i) for j in range(29)},
     "displayed_total_index":51.+i,"revenue_ecu":100+i*12,
     "expense_ecu":90+i*13}
  return {"schema":SCHEMA,"source_class":"OPERATOR_DECLARED_READONLY",
          "snapshots":[row(1),row(2)]}
 def hold(self,x,reason):
  with self.assertRaisesRegex(ValueError,"HOLD_"+reason):
   admissible(x)
 def test_two_consecutive_facts_structural_admission(self):
  o=admissible(self.case())
  self.assertEqual(o["periods"],[1,2])
  self.assertEqual(o["observed_transition_pair_admitted_for_descriptive_analysis"],1)
  self.assertFalse(o["evidence_authenticated_against_server"])
  self.assertFalse(o["city_causality_or_transition_parameters_identified"])
  self.assertEqual((o["game_writes"],o["gameplay_gate"]),(0,"STOP"))
 def test_reject_plan_as_fact(self):
  x=self.case();x["snapshots"][1]["kind"]="PLAN"
  self.hold(x,"FACT_NOT_PLAN")
 def test_reject_missing_year(self):
  x=self.case();x["snapshots"][1]["period"]=3
  self.hold(x,"CONSECUTIVE_CLOSED_PERIODS")
 def test_reject_same_year(self):
  x=self.case();x["snapshots"][1]["period"]=1
  self.hold(x,"CONSECUTIVE_CLOSED_PERIODS")
 def test_reject_wrong_team(self):
  x=self.case();x["snapshots"][1]["team"]="Another"
  self.hold(x,"TEAM_MARKET_IDENTITY")
 def test_reject_wrong_market(self):
  x=self.case();x["snapshots"][1]["market"]="Another"
  self.hold(x,"TEAM_MARKET_IDENTITY")
 def test_reject_duplicate_proof_id(self):
  x=self.case();x["snapshots"][1]["source_evidence_id"]="independent-proof-1"
  self.hold(x,"INDEPENDENT_FACT_RECORD_IDS")
 def test_reject_28_factors(self):
  x=self.case();del x["snapshots"][1]["factors"]["Factor 28"]
  self.hold(x,"29_NUMERIC_FACTORS")
 def test_reject_different_factor_names(self):
  x=self.case();x["snapshots"][1]["factors"]["Replaced"]=x["snapshots"][1]["factors"].pop("Factor 28")
  self.hold(x,"FACTOR_NAME_IDENTITY")
 def test_nonfinite_factor(self):
  x=self.case();x["snapshots"][0]["factors"]["Factor 00"]=float("inf")
  self.hold(x,"29_NUMERIC_FACTORS")
 def test_reject_forged_source_class(self):
  x=self.case();x["source_class"]="HISTORICAL_READONLY"
  self.hold(x,"NO_HISTORICAL_AUTOMATIC_LIVE_FALLBACK")
 def test_reject_forged_schema(self):
  x=self.case();x["schema"]="OTHER"
  self.hold(x,"NO_HISTORICAL_AUTOMATIC_LIVE_FALLBACK")
 def test_reject_unexpected_source_field(self):
  x=self.case();x["snapshots"][0]["cash_approved"]=True
  self.hold(x,"FACT_SNAPSHOT_SCHEMA")
 def test_reject_negative_expense(self):
  x=self.case();x["snapshots"][0]["expense_ecu"]=-1.
  self.hold(x,"NONNEGATIVE_FINANCE")
 def test_nominal_delta_not_transition_model(self):
  o=admissible(self.case())
  self.assertEqual(o["observed_displayed_index_difference_raw"],1.)
  self.assertEqual(o["observed_revenue_difference_raw"],12.)
  self.assertFalse(o["financial_units_independently_verified"])
 def test_no_model_training_from_two_snapshots(self):
  o=admissible(self.case())
  self.assertFalse(o["city_causality_or_transition_parameters_identified"])
if __name__=="__main__":unittest.main()
