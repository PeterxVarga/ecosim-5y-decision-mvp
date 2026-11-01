#!/usr/bin/env python3
"""R195 focused receipt-level fail-closed tests, no R162 mocked E2E claims."""
import copy
import importlib.util
import math
import tempfile
import unittest
from pathlib import Path

SOURCE=Path(__file__).resolve().parents[1]/'tools/compare_r195.py'
spec=importlib.util.spec_from_file_location('r195',SOURCE)
r195=importlib.util.module_from_spec(spec);spec.loader.exec_module(r195)


def receipt(budget,score=0.451337,cost=99000,mode='historical-test'):
    rows=[];env=[];years=[]
    for year in range(1,6):
        pid=year+10
        c=cost-1000*(year-1)
        rows.append({'year':year,'projects':[{'id':pid,'name':f'P{pid}'}],
          'once':c-3000,'annual_positive_maintenance':3000,'total':c,
          'remaining_scenario_ceiling':budget-c,'scenario_ceiling':budget})
        env.append({'year':year,'scenario_ceiling_ecu':budget,
          'basis':'HYPOTHETICAL_UNVERIFIED'})
        years.append([pid])
    admission={'gameplay_gate':'STOP','mode':'historical' if mode=='historical-test' else 'current',
       'current_period':1,'active':[14,22,23,24,34,35],'fixed':[]}
    if mode=='current-readonly':
        admission.update(r156_capture={'status':'PASS_OPERATOR_CAPTURE_CONSISTENCY_ONLY'},
          year1_finance={'status':'PASS_OPERATOR_DECLARED_YEAR1_ENVELOPE_ONLY','limit':budget},
          catalog_parity={'status':'PASS_OPERATOR_REPORTED_35_CARD_DEFINITION_PARITY_ONLY'})
    return {'schema':r195.R191_SCHEMA,'status':'PASS_CONDITIONAL_MODEL_SHADOW_ONLY',
      'r162_source_pin':r195.PIN,'gameplay_gate':'STOP','r162_result_game_action':'STOP',
      'actual_gameplay_approved':False,'actual_live_score_forecast_verified':False,
      'live_ready_decision_authorization':False,
      'independent_replay':{'status':'PASS_DISPLAY_RULES_ONLY_NOT_SERVER_APPROVAL',
        'hard_violations':0,'conditional_items':0},
      'mode':mode,'admission':admission,'final_score':score,
      'human_explanation_hu':{'schema':r195.R193_SCHEMA,'gameplay_gate':'STOP',
        'mode':mode,'live_financing_approved':False,'global_optimum_claimed':False,
        'years':rows},'annual_envelopes':env,'years':years,
      'input_state_sha256':'0'*64,'original_35_catalog_sha256':'1'*64}

class R195Tests(unittest.TestCase):
    def setUp(self):
        self.a=receipt(100000,score=.451337,cost=99500)
        self.b=receipt(90000,score=.38,cost=89500)
    def assert_hold(self,aa=None,bb=None):
        with self.assertRaises(r195.ComparisonHold):r195.compare(aa or self.a,bb or self.b)
    def test_historical_comparison(self):
        r=r195.compare(self.a,self.b)
        self.assertEqual(r['model_score_advantage_max_minus_reserve'],.071337)
        self.assertEqual(r['reserve_min_annual_free_ecu'],10500)
        self.assertEqual(r['max_min_annual_free_ecu'],500)
        self.assertIn('TÖRTÉNETI',r195.render_hu(r))
        self.assertIn('STOP',r195.render_hu(r))
    def test_higher_score_not_assumed(self):
        b=copy.deepcopy(self.b);b['final_score']=.55
        d=r195.compare(self.a,b)
        self.assertLess(d['model_score_advantage_max_minus_reserve'],0)
        self.assertIn('-0.',r195.render_hu(d))
    def test_current_mode_admission(self):
        a=receipt(100000,mode='current-readonly');b=receipt(90000,cost=89500,mode='current-readonly')
        self.assertEqual(r195.compare(a,b)['mode'],'current-readonly')
    def test_current_evidence_absent(self):
        a=receipt(100000,mode='current-readonly');b=receipt(90000,cost=89500,mode='current-readonly')
        del a['admission']['catalog_parity'];self.assert_hold(a,b)
    def test_current_capture_drift(self):
        a=receipt(100000,mode='current-readonly');b=receipt(90000,cost=89500,mode='current-readonly')
        b['admission']['r156_capture']['id']='different';self.assert_hold(a,b)
    def test_source_sha_mismatch(self):
        b=copy.deepcopy(self.b);b['input_state_sha256']='f'*64;self.assert_hold(bb=b)
    def test_catalog_sha_mismatch(self):
        b=copy.deepcopy(self.b);b['original_35_catalog_sha256']='f'*64;self.assert_hold(bb=b)
    def test_wrong_pin(self):
        b=copy.deepcopy(self.b);b['r162_source_pin']='f'*40;self.assert_hold(bb=b)
    def test_wrong_mode(self):
        b=copy.deepcopy(self.b);b['mode']='current-readonly';self.assert_hold(bb=b)
    def test_no_r160(self):
        b=copy.deepcopy(self.b);b['independent_replay']['status']='CONDITIONAL_NOT_SERVER_VERIFIED';self.assert_hold(bb=b)
    def test_r160_hard_violations(self):
        b=copy.deepcopy(self.b);b['independent_replay']['hard_violations']=1;self.assert_hold(bb=b)
    def test_r160_conditional(self):
        b=copy.deepcopy(self.b);b['independent_replay']['conditional_items']=1;self.assert_hold(bb=b)
    def test_game_stop(self):
        b=copy.deepcopy(self.b);b['gameplay_gate']='GO';self.assert_hold(bb=b)
    def test_authorized_flag(self):
        b=copy.deepcopy(self.b);b['actual_gameplay_approved']=True;self.assert_hold(bb=b)
    def test_live_score_claim(self):
        b=copy.deepcopy(self.b);b['actual_live_score_forecast_verified']=True;self.assert_hold(bb=b)
    def test_global_optimum_claim(self):
        b=copy.deepcopy(self.b);b['human_explanation_hu']['global_optimum_claimed']=True;self.assert_hold(bb=b)
    def test_overspend(self):
        b=copy.deepcopy(self.b);b['human_explanation_hu']['years'][0]['total']=91000;self.assert_hold(bb=b)
    def test_inconsistent_finance(self):
        b=copy.deepcopy(self.b);b['human_explanation_hu']['years'][0]['once']+=1;self.assert_hold(bb=b)
    def test_inconsistent_ids(self):
        b=copy.deepcopy(self.b);b['years'][0]=[22];self.assert_hold(bb=b)
    def test_invalid_score(self):
        b=copy.deepcopy(self.b);b['final_score']=float('nan');self.assert_hold(bb=b)
    def test_same_budget(self):
        b=receipt(100000,cost=89500);self.assert_hold(bb=b)
    def test_higher_reserve_budget(self):
        b=receipt(110000,cost=89500);self.assert_hold(bb=b)
    def test_mismatched_start_year(self):
        b=copy.deepcopy(self.b);b['admission']['current_period']=2;self.assert_hold(bb=b)
    def test_missing_receipt(self):
        b=copy.deepcopy(self.b);b.pop('human_explanation_hu');self.assert_hold(bb=b)

if __name__=='__main__':unittest.main()
