import copy,hashlib,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from corpus_r200 import (
    ROOT,ASSETS,PROFILE_SCHEMA,OUTPUT_SCHEMA,create_historical,inspect,
    parse_json,validate_profile,sha,markdown
)

@unittest.skipUnless(all((ROOT/x).is_file() for x in ASSETS.values()),
                     'Private R94/R199 test corpus not installed on this machine')
class R200Tests(unittest.TestCase):
 def setUp(self):
  self.p=create_historical()
  self.path=Path(__file__).resolve().parents[1]/'profiles/historical_R94_R199.json'
 def hold(self,func,needle='HOLD_'):
  with self.assertRaises(ValueError) as e:func()
  self.assertIn(needle,str(e.exception))
 def result(self):return inspect(self.p,self.path)
 def test_reproduce_historical_observations(self):
  r=self.result();o=r['observations']
  self.assertEqual((o['project_cards'],o['smartcity_factors'],o['index_weights']),(35,29,6))
  self.assertEqual((o['finance_rows'],o['finance_cashflow'],o['finance_wealth']),(113,88,25))
  self.assertEqual(o['finance_fact_plan_changes'],46)
  self.assertEqual((o['institutions_tables'],o['institutions_rows'],
                    o['institutions_numeric_observations'],o['institutions_editable_fields']),
                   (5,37,64,7))
  self.assertEqual(o['taxonomy_crosswalk_rows'],29)
  self.assertEqual(r['gameplay_gate'],'STOP')
 def test_p0_fact_is_not_a_following_year(self):
  o=self.result()['observations']
  self.assertEqual(o['observed_p0_fact_index'],51.96)
  self.assertEqual(o['observed_p1_plan_index'],52.48)
  self.assertTrue(o['p0_and_p1_are_NOT_consecutive_facts'])
 def test_reserve_is_balancing_plan_not_cash_approval(self):
  r=self.result();o=r['observations']
  self.assertEqual(o['observed_p1_revenues_less_nonreserve_expenses_raw'],865588)
  self.assertEqual(o['financial_displayed_totals_raw_scale']['reported_cash_balance']['p1'],865588)
  self.assertFalse(r['actual_cash_verified'])
 def test_fee_r94_rounding_preserved(self):
  o=self.result()['observed_vs_synthetic_fiscal_reconciliation']
  self.assertEqual(o['fee_component_rounding_residual_p0_raw'],2)
  self.assertEqual(o['fee_component_rounding_residual_p1_raw'],2)
 def test_synthetic_not_relabelled_as_real(self):
  r=self.result();o=r['observed_vs_synthetic_fiscal_reconciliation']
  self.assertEqual(o['observed_four_taxes_p0_raw'],499925)
  self.assertEqual(o['observed_six_fees_p0_components_raw'],1802870)
  self.assertNotEqual(o['synthetic_r155_first_year_six_fees_ecu'],
                      o['observed_six_fees_p0_components_raw'])
  self.assertFalse(o['same_monetary_scale_verified'])
  self.assertFalse(o['synthetic_bases_calibrated_to_R94_finance'])
 def test_complete_identity_join_six_pairs(self):
  r=self.result()
  self.assertEqual(len(r['r199_exact_test_scenarios']),6)
  self.assertEqual({x['plan'] for x in r['r199_exact_test_scenarios']},
                   {'R195-max','R195-reserve'})
  self.assertFalse(r['citywide_optimum_certified'])
 def test_ten_views_not_10_complete(self):
  x=self.result()
  self.assertEqual(len(x['ten_tab_evidence']),10)
  self.assertFalse(x['all_ten_tabs_directly_observed'])
  self.assertEqual(x['ten_tab_evidence']['institutions']['status'],'PARTIAL_ONE_SUBVIEW')
 def test_each_hash_is_pinned(self):
  r=self.result()
  self.assertEqual(len(r['sources']),len(ASSETS))
  for key,item in self.p['sources'].items():
   self.assertEqual(item['sha256'],r['sources'][key]['sha256'])
 def test_source_tamper_holds(self):
  self.p['sources']['finance']['sha256']='0'*64
  self.hold(lambda:self.result(),'SOURCE_SHA_finance')
 def test_unlisted_role_holds(self):
  self.p['sources']['random']={'path':'missing','scope':'repo','sha256':'0'*64}
  self.hold(lambda:self.result(),'SOURCE_ROLES')
 def test_missing_role_holds(self):
  del self.p['sources']['taxonomy']
  self.hold(lambda:self.result(),'SOURCE_COMPLETENESS')
 def test_forged_game_go_holds(self):
  self.p['gameplay_gate']='GO'
  self.hold(lambda:self.result(),'GAMEPLAY_GATE')
 def test_round_drift_holds(self):
  self.p['identity']['round']='Unknown'
  self.hold(lambda:self.result(),'CROSS_SOURCE_PERIOD')
 def test_current_disallows_historical(self):
  self.p['mode']='current-readonly'
  self.hold(lambda:self.result(),'NO_HISTORICAL_FALLBACK')
 def test_current_reuse_of_historical_bytes_rejected_even_if_relabelled(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);original=(ROOT/ASSETS['finance']).read_bytes()
   (p/'snapshot.csv').write_bytes(original)
   self.p={'schema':PROFILE_SCHEMA,'mode':'current-readonly',
     'identity':{'team':'New','market':'N','round':'Round','period':1},
     'sources':{'finance':{'scope':'profile','path':'snapshot.csv','sha256':sha(original),
                          'source_class':'OPERATOR_DECLARED_READONLY'}},
     'gameplay_gate':'STOP'}
   self.hold(lambda:inspect(self.p,p/'profile.json'),'CURRENT_IDENTICAL_TO_ARCHIVED_TEST')
 def test_current_new_input_accepts_hash_but_holds_model(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);(p/'finance.csv').write_text('source,evidence\nsample,read_only\n')
   b=(p/'finance.csv').read_bytes()
   prof={'schema':PROFILE_SCHEMA,'mode':'current-readonly',
     'identity':{'team':'New','market':'N','round':'Round','period':2},
     'sources':{'finance':{'scope':'profile','path':'finance.csv','sha256':sha(b),
                          'source_class':'OPERATOR_DECLARED_READONLY'}},
     'gameplay_gate':'STOP'}
   out=inspect(prof,p/'profile.json')
   self.assertEqual(out['status'],'HOLD_CURRENT_SOURCE_INTAKE_ONLY')
   self.assertFalse(out['model_replay_validated'])
   self.assertIn('finance',out['sha_verified_roles_only'])
 def test_duplicate_json_keys_hold(self):
  self.hold(lambda:parse_json(b'{"x":1,"x":2}'),'DUPLICATE_JSON')
 def test_nonfinite_json_hold(self):
  self.hold(lambda:parse_json(b'{"x":1e999}'),'NONFINITE_JSON')
 def test_report_never_claims_spendable_cash(self):
  txt=markdown(self.result())
  self.assertIn('nem igazoltan szabadon költhető',txt)
  self.assertIn('GAME_ACTION_GATE=STOP',txt)
class StandaloneContractTests(unittest.TestCase):
 def test_duplicate_json_rejected_without_private_fixtures(self):
  with self.assertRaisesRegex(ValueError,'HOLD_DUPLICATE_JSON'):
   parse_json(b'{"a":1,"a":2}')
 def test_nonfinite_rejected_without_private_fixtures(self):
  with self.assertRaisesRegex(ValueError,'HOLD_NONFINITE_JSON'):
   parse_json(b'{"a":1e999}')
 def test_current_profile_class_gate_without_fixtures(self):
  p={'schema':PROFILE_SCHEMA,'mode':'current-readonly',
     'identity':{'team':'T','market':'M','round':'R','period':1},
     'sources':{'finance':{'source_class':'HISTORICAL_READONLY'}},'gameplay_gate':'STOP'}
  with self.assertRaisesRegex(ValueError,'HOLD_NO_HISTORICAL_FALLBACK'):
   validate_profile(p)
if __name__=='__main__':unittest.main()
