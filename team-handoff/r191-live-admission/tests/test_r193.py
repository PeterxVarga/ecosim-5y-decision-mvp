from __future__ import annotations
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from hungarian_decision_r193 import explain, ExplanationHold


def fixture(mode='historical-test'):
    catalog={i: {'id':i,'name':f'Szintetikus projekt {i}', 'startup_cost':0,
                'investment':0, 'maintenance_cost':0,'partner_support':0,
                'project_conditions':[],'effects':[]} for i in range(1,36)}
    catalog[1].update(name='Digitális szolgáltatás',startup_cost=1000,investment=4000,
                      maintenance_cost=300,partner_support=20000,effects=[
                          {'metric':'Digitalizáció','value_percent':2},
                          {'metric':'Munkanélküliség','value_percent':-0.3},
                          {'metric':'Tömegközlekedők aránya, %','value_percent':-0.6},
                          {'metric':'Kisvállalkozások száma','value_percent':1}])
    catalog[2].update(name='Zöld fejlesztés',startup_cost=2000,investment=3000,
                      maintenance_cost=-800,partner_support=10000,
                      effects=[{'metric':'Fenntarthatóság','value_percent':3}])
    catalog[3].update(name='Összekötő útvonal',startup_cost=1000,investment=1000,
                      maintenance_cost=50,partner_support=0,
                      project_conditions=['Zöld fejlesztés — Fut'],
                      effects=[{'metric':'Közlekedési minőség','value_percent':1}])
    adm={'mode':'historical' if mode=='historical-test' else 'current','gameplay_gate':'STOP',
         'current_period':1,'active':[20],'fixed':[]}
    if mode=='current-readonly':
        adm.update(r156_capture={'status':'PASS_OPERATOR_CAPTURE_CONSISTENCY_ONLY'},
                   year1_finance={'status':'PASS_OPERATOR_DECLARED_YEAR1_ENVELOPE_ONLY'},
                   catalog_parity={'status':'PASS_OPERATOR_REPORTED_35_CARD_DEFINITION_PARITY_ONLY'})
    receipt={'schema':'ECOSIM_R191_HARDENED_PINNED_SHADOW_V1',
             'status':'PASS_CONDITIONAL_MODEL_SHADOW_ONLY',
             'gameplay_gate':'STOP','actual_gameplay_approved':False,
             'r162_result_game_action':'STOP','mode':mode,'admission':adm,
             'independent_replay':{'status':'PASS_DISPLAY_RULES_ONLY_NOT_SERVER_APPROVAL',
                                   'hard_violations':0,'conditional_items':0},
             'years':[[1,2],[3],[],[],[]], 'initial_first_year_ids':[1,3],
             'initial_score':0.2, 'final_score':0.23,
             'annual_envelopes':[{'year':y,'scenario_ceiling_ecu':11000} for y in range(1,6)]}
    return receipt,catalog

class R193Test(unittest.TestCase):
    def test_first_year_real_cost_and_grant_no_netting(self):
        r,c=fixture();out=explain(r,c)
        y=out['years'][0]
        self.assertEqual((y['once'],y['annual_positive_maintenance'],y['total'],y['partner_support_label']),
                         (10000,300,10300,30000))
    def test_grant_not_subtracted(self):
        r,c=fixture();r['annual_envelopes'][0]['scenario_ceiling_ecu']=11000
        out=explain(r,c)
        self.assertEqual(out['years'][0]['remaining_scenario_ceiling'],700)
        self.assertIn('partnertámogatást nem vontuk le',out['markdown'])
    def test_historical_not_live_command(self):
        r,c=fixture();out=explain(r,c)
        self.assertIn('TÖRTÉNETI TESZT',out['markdown']);self.assertIn('még ne indítsatok',out['markdown'])
        self.assertIn('GAME_ACTION_GATE=STOP',out['markdown'])
    def test_project_names_why_and_risks(self):
        r,c=fixture();r['annual_envelopes'][0]['scenario_ceiling_ecu']=11000
        out=explain(r,c,modeled_metrics={'Digitalizáció','Munkanélküli arány','Fenntarthatóság','Tömegközlekedők aránya, %'})
        self.assertIn('Digitális szolgáltatás',out['markdown'])
        self.assertIn('Digitalizáció +2%',out['markdown'])
        self.assertIn('Munkanélküliség -0,3%',out['markdown'])
        self.assertIn('Tömegközlekedők aránya, % -0,6%',out['markdown'])
        self.assertIn('nem közvetlenül leképezett',out['markdown'])
    def test_dependent_project_in_next_year(self):
        r,c=fixture();r['annual_envelopes'][0]['scenario_ceiling_ecu']=11000
        out=explain(r,c);self.assertIn('Összekötő útvonal',out['markdown'])
    def test_unmet_dependency_holds(self):
        r,c=fixture();r['years']=[[1,2,3],[],[],[],[]]
        with self.assertRaisesRegex(ExplanationHold,'UNMET_PROJECT_DEPENDENCY'):explain(r,c)
    def test_negative_dependency_holds(self):
        r,c=fixture();c[3]['project_conditions']=['not Zöld fejlesztés — Fut']
        with self.assertRaisesRegex(ExplanationHold,'UNMET_PROJECT_DEPENDENCY'):explain(r,c)
    def test_unmapped_dependency_holds(self):
        r,c=fixture();c[3]['project_conditions']=['Ismeretlen — Fut']
        with self.assertRaisesRegex(ExplanationHold,'UNRESOLVED_PROJECT_DEPENDENCY'):explain(r,c)
    def test_original_first_year_difference(self):
        r,c=fixture();r['annual_envelopes'][0]['scenario_ceiling_ecu']=11000
        out=explain(r,c);self.assertIn('előrébb került:',out['markdown']);self.assertIn('későbbi évre került',out['markdown'])
        self.assertIn('teljes ötéves modellcsomag',out['markdown'])
    def test_no_fake_order(self):
        r,c=fixture();r['annual_envelopes'][0]['scenario_ceiling_ecu']=11000
        self.assertIn('nem jelent kötelező kattintási sorrendet',explain(r,c)['markdown'])
    def test_missing_audit_holds(self):
        r,c=fixture();r['independent_replay']['status']='CONDITIONAL_NOT_SERVER_VERIFIED'
        with self.assertRaisesRegex(ExplanationHold,'INDEPENDENT_AUDIT_NOT_CLEAN'):explain(r,c)
    def test_missing_source_search_stop_holds(self):
        r,c=fixture();r['r162_result_game_action']='GO'
        with self.assertRaisesRegex(ExplanationHold,'SOURCE_SEARCH_NOT_STOP'):explain(r,c)
    def test_historical_current_mismatch(self):
        r,c=fixture();r['mode']='current-readonly'
        with self.assertRaisesRegex(ExplanationHold,'MODE_CONTRADICTION'):explain(r,c)
    def test_current_admission_requires_catalog_parity(self):
        r,c=fixture('current-readonly');del r['admission']['catalog_parity']
        with self.assertRaisesRegex(ExplanationHold,'CURRENT_ADMISSION_NOT_COMPLETE'):explain(r,c)
    def test_current_mode_requires_r156_finance(self):
        r,c=fixture('current-readonly');del r['admission']['year1_finance']
        with self.assertRaisesRegex(ExplanationHold,'CURRENT_ADMISSION_NOT_COMPLETE'):explain(r,c)
    def test_current_language_not_authorization(self):
        r,c=fixture('current-readonly');r['annual_envelopes'][0]['scenario_ceiling_ecu']=11000
        out=explain(r,c)
        self.assertIn('aktuális, ellenőrzendő',out['markdown'])
        self.assertIn('nem végrehajtási engedély',out['markdown'])
    def test_missing_catalog_holds(self):
        r,c=fixture();del c[2]
        with self.assertRaisesRegex(ExplanationHold,'MISSING_PROJECT_CARD'):explain(r,c)
    def test_model_score_regression_holds(self):
        r,c=fixture();r['final_score']=0.10
        with self.assertRaisesRegex(ExplanationHold,'MODEL_SCORE_DETERIORATED'):explain(r,c)
    def test_scenario_budget_exceeded_holds(self):
        r,c=fixture();r['annual_envelopes'][0]['scenario_ceiling_ecu']=10000
        with self.assertRaisesRegex(ExplanationHold,'PLAN_EXCEEDS_SCENARIO_CEILING'):explain(r,c)
    def test_duplicate_and_initially_running_holds(self):
        r,c=fixture();r['years'][1].append(1)
        with self.assertRaisesRegex(ExplanationHold,'DUPLICATE_PROJECT_ID'):explain(r,c)
        r,c=fixture();r['admission']['active'].append(1)
        with self.assertRaisesRegex(ExplanationHold,'PLAN_VS_BASELINE_INCONSISTENCY'):explain(r,c)
    def test_prior_selected_not_recommended_again(self):
        r,c=fixture();r['admission']['fixed']=[1];r['annual_envelopes'][0]['scenario_ceiling_ecu']=11000
        out=explain(r,c)
        self.assertEqual(out['first_year_preselected_ids'],[1]);self.assertEqual(out['first_year_new_ids'],[2]);self.assertIn('ne indítsátok újra',out['markdown'])
    def test_score_not_project_causality(self):
        r,c=fixture();r['annual_envelopes'][0]['scenario_ceiling_ecu']=11000
        out=explain(r,c)
        self.assertIn('nem egyetlen projekt hatása',out['markdown'])
        self.assertFalse(out['global_optimum_claimed'])
    def test_deterministic_and_pure(self):
        r,c=fixture();r['annual_envelopes'][0]['scenario_ceiling_ecu']=11000
        before=copy.deepcopy((r,c));a=explain(r,c);b=explain(r,c)
        self.assertEqual(a,b);self.assertEqual((r,c),before)
    def test_sanitize_card_name(self):
        r,c=fixture();c[1]['name']='**Manipulatív**'
        r['annual_envelopes'][0]['scenario_ceiling_ecu']=11000
        self.assertIn('\\*\\*Manipulatív\\*\\*',explain(r,c)['markdown'])
    def test_negative_maintenance_not_treated_as_cash(self):
        r,c=fixture();r['annual_envelopes'][0]['scenario_ceiling_ecu']=11000
        out=explain(r,c)
        self.assertEqual(out['years'][0]['annual_positive_maintenance'],300)
        self.assertIn('fenntartás: -800 ECU',out['markdown'])

if __name__=='__main__':unittest.main()

# The core renderer is exercised above; runner integration is covered by the
# preserved R191 shim tests plus this output contract smoke test.
