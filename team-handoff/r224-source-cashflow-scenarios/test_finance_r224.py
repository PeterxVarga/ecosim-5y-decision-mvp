#!/usr/bin/env python3
"""Native private actual-source R224 accounting and fail-closed scenario tests."""
from __future__ import annotations
import json,os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from finance_scenarios_r224 import extract,SCHEMA,CAPS,FRACTIONS,OBJECTIVES,sha
from json_integrity_r162 import read_json
class P1ActualFinanceScenario(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.private=Path(os.environ["R224_CURRENT_FINANCE"])
  cls.r156=Path(os.environ["R224_CURRENT_R156"])
  cls.out=Path(os.environ["R224_RESULT"])
  cls.source=cls.private.read_text(encoding="utf-8")
  cls.flow=extract(cls.source)
  cls.receipt=read_json(cls.out/"R224_RECEIPT.json")
 def test_actual_p1_accounting_and_p0_are_distinct(self):
  c=self.flow
  self.assertEqual(c["source_values_p0_p1_ecu"]["receipts_no_loan"],[5449828,5562335])
  self.assertEqual(c["source_values_p0_p1_ecu"]["expense_ex_reserve"],[4487043,4511224])
  self.assertEqual(c["source_values_p0_p1_ecu"]["period_net_result"],[962785,1051111])
  self.assertEqual(c["source_values_p0_p1_ecu"]["reserve_creation"],[0,1051111])
  self.assertEqual(c["source_values_p0_p1_ecu"]["project_expense_line"],[0,0])
  self.assertEqual(c["source_values_p0_p1_ecu"]["loans_drawn"],[0,0])
 def test_opening_cash_and_grants_excluded_exactly_once(self):
  c=self.flow
  self.assertEqual(c["p1_project_free_cashflow_surplus_ecu"],1051111)
  self.assertEqual(c["p1_surplus_excluding_prior_cash_ecu"],866511)
  self.assertEqual(c["p1_surplus_excluding_prior_cash_and_both_grants_ecu"],674486)
  self.assertEqual(c["source_values_p0_p1_ecu"]["prior_year_cash"][1],184600)
  self.assertEqual(c["source_values_p0_p1_ecu"]["state_development_grant"][1],130000)
  self.assertEqual(c["source_values_p0_p1_ecu"]["company_development_grant"][1],62025)
  self.assertEqual(c["hypothetical_annual_budget_ecu"],[0,168621,337243,674486])
  self.assertFalse(c["incremental_project_funding_observed_and_approved"])
  self.assertFalse(c["grant_earmarking_verified"])
 def test_tampered_p1_reserve_not_accepted(self):
  self.assertIn("<td>Tartalékképzésre</td><td>0</td><td>1 051 111</td>",self.source)
  bad=self.source.replace("<td>Tartalékképzésre</td><td>0</td><td>1 051 111</td>",
                          "<td>Tartalékképzésre</td><td>0</td><td>1 061 111</td>")
  with self.assertRaisesRegex(ValueError,"HOLD_PLAN_RESERVE_IS_ARITHMETIC"):
   extract(bad)
 def test_duplicate_row_name_with_conflicting_values_rejected(self):
  fake=self.source.replace("Bevételek\n","Bevételek\n<table><tr><td>Bevételek összesen</td><td>0</td><td>1</td></tr></table>",1)
  with self.assertRaisesRegex(ValueError,"HOLD_CASHFLOW_ROW_Bevételek összesen"):
   extract(fake)
 def test_wrong_round_and_source_authentication_missing(self):
  with self.assertRaisesRegex(ValueError,"HOLD_FINANCE_SOURCE_IDENTITY"):
   extract(self.source.replace("Piac: I","Piac: Z",1))
  with self.assertRaisesRegex(ValueError,"HOLD_FINANCE_SOURCE_URL"):
   extract(self.source.replace("# SOURCE_URL=https://edu.ecosim.hu/simulation/finance",
                                  "# SOURCE_URL=https://other.example/finance",1))
 def test_original_r156_source_sha_bound(self):
  r=read_json(self.r156/"R217_RECEIPT.json")
  self.assertEqual(r["source_text_sha256"]["finance"],sha(self.private))
  self.assertEqual(self.receipt["source_sha256"]["current_finance_text"],sha(self.private))
  self.assertEqual(self.receipt["source_sha256"]["current_r156_receipt"],
                   sha(self.r156/"R217_RECEIPT.json"))
 def test_24_source_based_hypotheses_are_not_actual_budget(self):
  r=self.receipt
  self.assertEqual(r["schema"],SCHEMA)
  self.assertEqual(r["status"],"PASS_SOURCE_RECONCILED_HYPOTHETICAL_FINANCE_SCENARIOS_ONLY")
  self.assertEqual(r["scenario_count"],24)
  self.assertEqual(len(r["scenarios"]),24)
  self.assertEqual(r["cashflow"],self.flow)
  self.assertIsNone(r["current_R191_real_cap"])
  self.assertIsNone(r["current_R191_actual_spendable_cash"])
  self.assertFalse(r["current_R192_full_admission"])
  self.assertFalse(r["current_R214_live_advice_authorized"])
  self.assertFalse(r["official_score_predicted"])
  self.assertEqual(r["gameplay_gate"],"STOP")
  self.assertEqual(r["game_writes"],0)
 def test_original_audits_and_budget_limits(self):
  r=self.receipt
  budgets=set(self.flow["hypothetical_annual_budget_ecu"])
  combos=set()
  for x in r["scenarios"]:
   self.assertIn(x["hypothetical_cap"],CAPS)
   self.assertIn(x["hypothetical_annual_budget_ecu"],budgets)
   self.assertIn(x["objective"],OBJECTIVES)
   self.assertLessEqual(x["first_year_conservative_requirement_ecu"],
                        x["hypothetical_annual_budget_ecu"])
   self.assertLessEqual(len(x["initial_project_ids"]),x["hypothetical_cap"])
   self.assertTrue(x["validated_by_original_r160"])
   self.assertFalse(x["financing_authorized"])
   self.assertTrue(x["not_an_eligible_game_action"])
   self.assertTrue(x["forecast_impact_on_P1_finance_NOT_verified"])
   self.assertEqual(x["gameplay_gate"],"STOP")
   if x["hypothetical_annual_budget_ecu"]==0:
    self.assertEqual(x["initial_project_ids"],[])
   combos.add((x["hypothetical_cap"],x["hypothetical_annual_budget_ecu"],x["objective"]))
  self.assertEqual(combos,{(cap,budget,obj) for cap in CAPS for budget in budgets for obj in OBJECTIVES})
if __name__=="__main__":unittest.main()
