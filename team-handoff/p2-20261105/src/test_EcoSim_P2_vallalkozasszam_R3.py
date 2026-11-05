#!/usr/bin/env python3
"""Targeted source-bounded offline checks for company-count indicator R3."""
from pathlib import Path
import json,unittest,math
ROOT=Path(__file__).resolve().parent
E=json.loads((ROOT/'EcoSim_P2_vallalkozasszam_empirikus_R3_20261105.json').read_text())
B=json.loads((ROOT/'EcoSim_P2_vallalkozasszam_forrasmegfigyelesek_20261105.json').read_text())
class TestR3(unittest.TestCase):
 def test_p0_counts(self):self.assertEqual(E['p0_company_total'],4857)
 def test_seven_qualifier_fact_teams(self):self.assertEqual(E['fit']['p1_fact_samples_total'],7)
 def test_six_exact_to_displayed_decimals(self):self.assertEqual(E['fit']['p1_fact_displayed_2_decimal_exact'],6)
 def test_all_teams_rounding_compatible(self):self.assertEqual(E['fit']['p1_fact_rounding_compatible'],7)
 def test_two_historical_test_samples_exact(self):self.assertEqual(E['fit']['historical_test_z_two_dec_exact'],2)
 def test_p2_rounding_compatible_not_exact(self):
  s=E['samples']['p2_plan'];self.assertTrue(s['compatible_with_integer_rounding']);self.assertFalse(s['exact_to_displayed_2_decimals'])
 def test_p2_cumulative_approach_fails(self):self.assertGreater(abs(E['fit']['p2_cumulative_since_p0_prediction']-59.85),.5)
 def test_p2_multiplicative_50_fails(self):self.assertGreater(abs(E['fit']['p2_wrong_50_times_yoy_growth_prediction']-59.85),4)
 def test_joint_project_trial_and_rollback(self):
  x=E['controlled_historical_preview'];self.assertEqual(x['projects'],[4,13,21,27]);self.assertEqual(x['rollback_factor'],x['before_factor']);self.assertLess(abs(x['predicted_factor_delta_under_hypothesis']-x['observed_factor_delta']),.004)
 def test_r3_coefficient_correction(self):
  c=E['p2_model_coefficients'];self.assertAlmostEqual(c['r3_to_r2_ratio'],1.0526805193574784)
 def test_scenario_enumeration(self):self.assertEqual(E['p2_portfolio_screen']['evaluated_unique_feasible_within_450000'],12386)
 def test_450k_r3_winner(self):self.assertEqual(E['p2_portfolio_screen']['by_budget']['450000']['leaders']['year_on_year_hypothesis'][0]['ids'],[4,8,16,33])
 def test_450k_direct_winner(self):self.assertEqual(E['p2_portfolio_screen']['by_budget']['450000']['leaders']['direct'][0]['ids'],[4,8,21,33])
 def test_no_game_writes(self):self.assertTrue(E['no_game_writes'])
if __name__=='__main__':unittest.main(verbosity=1)
