from __future__ import annotations
import unittest
from indirect_business_sensitivity import compute, counts_effect, load, METRICS

class IndirectBusinessSensitivityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=compute()
        cls.data,cls.idx=load()
    def test_effect_coverage(self):
        q=self.r['data_counts'];self.assertEqual(q['indirect_total'],30)
        self.assertEqual(q['small_effect_count'],22)
        self.assertEqual(q['medium_effect_count'],8)
        self.assertEqual(q['projects_with_any_indirect'],23)
        self.assertEqual(q['project_count'],35)
    def test_all_effects_included_exactly_once(self):
        rows=self.r['all_30_indirect_effects']
        from_sources=[(p['id'],e['metric'],e['value_percent']) for p in self.data['projects'] for e in p['effects'] if e['metric'] in METRICS]
        self.assertEqual(sorted((r['id'],r['metric'],r['value_percent']) for r in rows), sorted(from_sources))
    def test_secant_observation_not_causal(self):
        obs=self.r['observation']; self.assertEqual(obs['observed_company_total_change_all_sizes'],480)
        self.assertAlmostEqual(obs['observed_factor_change'],9.34)
        self.assertEqual(self.r['status'],'OFFLINE_STRESS_TEST_NOT_CAUSAL_ESTIMATE')
    def test_direct_only_baseline_preserved(self):
        d=self.r['rankings_by_budget']
        exp={'75000':[8,9,26,28], '150000':[4,8,16,21],
             '300000':[8,21,26,33], '450000':[4,8,21,33]}
        for budget,ids in exp.items():self.assertEqual(d[budget]['direct_only_leader']['ids'],ids)
    def test_450k_flip_threshold(self):
        d=self.r['rankings_by_budget']['450000']
        self.assertEqual(d['reference_equal_weight_1x']['ids'],[4,8,16,33])
        self.assertEqual(d['first_leader_flip_equal_firm_weight_grid'],0.1)
        focus=self.r['focused_pair_comparisons'][0]
        self.assertLess(focus['equal_weight_crossing_secant_multiple'],0.1)
        self.assertGreater(focus['equal_weight_crossing_secant_multiple'],0)
    def test_150k_stable_at_reference_scale(self):
        d=self.r['rankings_by_budget']['150000']
        self.assertEqual(d['direct_only_leader']['ids'],d['reference_equal_weight_1x']['ids'])
    def test_cash_limits_and_finite_values(self):
        for budget,row in self.r['rankings_by_budget'].items():
            B=int(budget)
            for s in row['scenarios']:
                for c in s['top6']:
                    self.assertLessEqual(c['safe_p2_cost'],B)
                    self.assertLessEqual(len(c['ids']),4)
                    self.assertGreaterEqual(c['indirect_proxy_delta'],-1e-12)
                    self.assertTrue(abs(c['total_conditional_delta'])<100)
    def test_no_game_writes(self):
        self.assertTrue(self.r['no_game_writes'])
        self.assertEqual(self.data['game_mutations'],0)
        self.assertEqual(self.r['model_gates']['company_count_to_factor_causal'],'NOT_IDENTIFIABLE')
    def test_company_count_one_project(self):
        z=counts_effect([2],self.idx)
        self.assertAlmostEqual(z['small_delta'],3.1356)
        self.assertAlmostEqual(z['medium_delta'],1.08)

if __name__=='__main__':unittest.main(verbosity=2)
