import json
import unittest
from pathlib import Path
from p2_joint_screen import load, compute, direct_eligibility, cost_for, conditional_delta
from r142_proxy_reference import COEFF, proxy_value

class SourceBoundedP2Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.src, cls.idx=load(); cls.r=compute()
 def test_project_status_cost_data_35(self):
  self.assertEqual(len(self.idx),35)
  self.assertEqual(sum(p['live_cost_status_verified'] for p in self.idx.values()),35)
  self.assertEqual(sum(p['status_p2']=='Fut' for p in self.idx.values()),10)
  self.assertEqual(self.src['quality']['historical_live_cost_conflicts'],[])
 def test_effect_coverage_not_silent_zero(self):
  self.assertEqual(sum(len(p['effects']) for p in self.idx.values()),272)
  self.assertEqual(self.src['quality']['effect_unmapped_count_historical'],30)
  self.assertEqual(len(COEFF),29)
 def test_signed_annual_maintenance_matches_live_finance(self):
  total=sum(p['maintenance_cost'] for p in self.idx.values() if p['status_p2']=='Fut')
  self.assertEqual(total,-65800)
  self.assertEqual(self.src['baseline']['p2_signed_running_maintenance_ecu'],total)
 def test_smartcity_baseline_reconciliation(self):
  b=self.src['baseline']
  self.assertAlmostEqual(proxy_value(b['p2_plan_factors']),60.52115,places=5)
  self.assertAlmostEqual(proxy_value(b['p1_fact_factors']),58.86597916666667,places=5)
  self.assertEqual(round(proxy_value(b['p2_plan_factors']),2),60.52)
  self.assertEqual(round(proxy_value(b['p1_fact_factors']),2),58.87)
 def test_finance_nonproject_bridge(self):
  b=self.src['baseline']
  self.assertEqual(b['p2_nonproject_operating_net_ecu'],493062)
  self.assertEqual(b['p2_annual_net_including_running_projects_ecu'],558862)
  self.assertEqual(b['p2_reserve_reconstructed_ecu'],868142)
  self.assertEqual(b['rounding_difference_ui_minus_reconstructed_ecu'],1)
 def test_dependencies_strict(self):
  active={i for i,p in self.idx.items() if p['status_p2']=='Fut'}
  self.assertFalse(direct_eligibility([30],self.idx,active))
  self.assertFalse(direct_eligibility([29,30],self.idx,active,strict=True))
  self.assertTrue(direct_eligibility([31],self.idx,active))
 def test_each_budget_scenario(self):
  for budget,group in self.r['by_hypothetical_p2_budget'].items():
   for key in ('top_nominal','top_sensitivity_min'):
    for row in group[key]:
     self.assertTrue(1<=len(row['ids'])<=4)
     self.assertTrue(direct_eligibility(row['ids'],self.idx,{i for i,p in self.idx.items() if p['status_p2']=='Fut'}))
     self.assertLessEqual(row['conservative_incremental_p2_cash_requirement'],int(budget))
     self.assertEqual(cost_for(row['ids'],self.idx)['conservative_incremental_p2_cash_requirement'],row['conservative_incremental_p2_cash_requirement'])
     self.assertEqual(row['scenario_no_grant_reserve_after_conservative_increment'],868143-row['conservative_incremental_p2_cash_requirement'])
 def test_no_forecast_or_authorization(self):
  self.assertEqual(self.src['game_mutations'],0)
  self.assertTrue(self.r['restrictions']['cash_envelopes_are_hypothetical'])
  self.assertFalse(self.r['restrictions']['project_effects_unmapped_never_treated_as_zero'] is False)
  self.assertEqual(self.r['restrictions']['gameplay_decision'],'STOP')
  self.assertEqual(self.r['restrictions']['future_cash_p3_p5'],'UNKNOWN')

if __name__=='__main__': unittest.main(verbosity=2)
