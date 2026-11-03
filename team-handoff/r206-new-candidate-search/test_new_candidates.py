#!/usr/bin/env python3
"""Source-independent tamper tests for R206 (fake source, fake search)."""
import copy
import importlib.util
import hashlib
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location('r206',Path(__file__).with_name('new_candidates.py'))
r=importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)

def data():
    states={'provenance':{'team':'fixture','market':'Z','current_period':1,
                          'source':'TEST_P1_HISTORICAL_NOT_LIVE'},
            'team':{'initially_active_project_ids':[14,22,23,24,34,35],
                    'baseline_smartcity_factors':{f'f{i}':50.0 for i in range(29)}}}
    profile={'schema':'ECOSIM_R200_INPUT_PROFILE_V1','mode':'historical-test','gameplay_gate':'STOP',
             'identity':{'team':'fixture','market':'Z','round':'Test','period':1}}
    old=[]
    for i in range(17):
        annual=[]
        for y in range(1,6):
            annual.append({'year':y,'projects_started_ids':[i+1] if y==1 else []})
        old.append({'annual_records':annual})
    sha=r.digest(b'fixture')
    r204={'schema':'ECOSIM_UNIFIED_HISTORICAL_DECISION_PACKET_V1',
          'status':'PASS_PARTIAL_HISTORICAL_DECISION_SUPPORT_LIVE_HOLD',
          'mode':'historical-test','gameplay_gate':'STOP','game_writes':0,
          'source_hashes':{'r200_profile_source_state':sha},
          'annual_transition_diagnostics':{'plans':old},
          'decision':{'live':'HOLD','current_city_optimum':'NOT_PROVEN'}}
    r205={'schema':'ECOSIM_R205_HISTORICAL_LIBRARY_SOURCE_RECONCILIATION_V1',
          'status':'PASS_PREVIOUSLY_UPLOADED_EVIDENCE_RECONCILED_LIVE_HOLD',
          'mode':'historical-test','gameplay_gate':'STOP','game_writes':0,
          'live_city_model_validated':False,'verified_spendable_cash':False,
          'game_actions_permitted':False,
          'r202_finance_channel_crosschecks':[{} for _ in range(10)],
          'source_files':{str(i):{'rows':20} for i in range(5)}}
    return profile,states,r204,r205,sha

def fake_search(state,start_year,budget_override,cap_override,beam_width,shortlist,allow_same_year,objective):
    assert start_year==1 and objective=='nominal' and allow_same_year is True
    cap=cap_override;budget=budget_override[0]
    entries=[]
    # Two distinct new paths per scenario; deterministic and price-bounded.
    for i in range(2):
        years=[{'year':y,'start_project_ids':[i+25] if y==1 else [],
                'conservative_card_cash_requirement_ecu':10} for y in range(1,6)]
        audit={'schema':'ECOSIM_R160_INDEPENDENT_PLAN_AUDIT_V1','gameplay_gate':'STOP',
                'hard_rule_violations':[],'conditional_eligibility_items':[],
                'actual_game_eligibility':None,'actual_funding_approval':None,
                'years':[{'independently_replayed_conservative_cash_need_ecu':10} for _ in range(5)]}
        entries.append({'start_by_year':years,'five_year_conservative_card_cost_ecu':50,
                        'terminal_mapped_proxy_delta':1.0+i,
                        'illustrative_half_effect_sensitivity':[{'mapped_proxy_delta':.5}],
                        'illustrative_85pct_yearly_retention_sensitivity':[{'mapped_proxy_delta':.7}],
                        'excluded_unknown_effects':[1],
                        'r160_independent_constraint_replay':audit})
    return {'schema':'ECOSIM_R148_SOURCE_BOUNDED_OFFLINE_STRATEGY_V1',
            'final_gameplay_decision':'STOP','game_write_actions':0,'network_actions':0,
            'actual_five_year_score_forecast_validated':False,
            'assumptions':{'annual_project_limit':cap,
                           'official_cash_envelopes_or_illustrative_scenario':budget_override,
                           'budget_source':'EXPLICIT_ILLUSTRATIVE_CLI_SCENARIO_NOT_SPENDABLE_CASH',
                           'annual_limit_source':'EXPLICIT_ILLUSTRATIVE_CLI_ASSUMPTION'},
            'top_plans':entries,'search_stats':[]}

class Tests(unittest.TestCase):
    def setUp(self):
        self.p,self.state,self.r204,self.r205,self.sha=data()
        self.historical=r.validate_sources(self.p,self.state,self.r204,self.r205,self.sha)
    def test_valid_cross_source(self):
        self.assertEqual(len(self.historical),17)
    def test_new_candidate_generation(self):
        out=r.generate(self.state,self.historical,fake_search)
        self.assertEqual(out['unique_candidates'],2)
        self.assertEqual(out['distinct_new_vs_r204'],2)
        self.assertEqual(len(out['hypothetical_scenarios']),3)
        self.assertTrue(all(len(p['hypothetical_scenarios'])==3 for p in out['candidates']))
        self.assertEqual(out['gameplay_gate'],'STOP')
        self.assertIn('Nem teljes városszimuláció',r.report(out))
    def test_no_causal_promotion(self):
        self.r205['verified_spendable_cash']=True
        with self.assertRaisesRegex(ValueError,'HOLD_R205_SOURCE_GATE'):
            r.validate_sources(self.p,self.state,self.r204,self.r205,self.sha)
    def test_source_sha_fail_closed(self):
        with self.assertRaisesRegex(ValueError,'HOLD_STATE_SOURCE_SHA'):
            r.validate_sources(self.p,self.state,self.r204,self.r205,'bad')
    def test_input_is_plan_not_live(self):
        self.state['provenance']['source']='ACTUAL'
        with self.assertRaisesRegex(ValueError,'HOLD_STATE_NOT_LIVE'):
            r.validate_sources(self.p,self.state,self.r204,self.r205,self.sha)
    def test_original_search_not_live(self):
        def bad(*a,**kw):
            v=fake_search(*a,**kw)
            v['game_write_actions']=1
            return v
        with self.assertRaisesRegex(ValueError,'HOLD_ORIGINAL_R162_SEARCH_GATE'):
            r.generate(self.state,self.historical,bad)
    def test_reject_audit_failure(self):
        def bad(*a,**kw):
            v=fake_search(*a,**kw)
            v['top_plans'][0]['r160_independent_constraint_replay']['hard_rule_violations']=['BAD']
            return v
        with self.assertRaisesRegex(ValueError,'HOLD_R160_AUDIT'):
            r.generate(self.state,self.historical,bad)
    def test_reject_budget_overspend(self):
        def bad(*a,**kw):
            v=fake_search(*a,**kw)
            v['top_plans'][0]['start_by_year'][0]['conservative_card_cash_requirement_ecu']=1000000
            return v
        with self.assertRaisesRegex(ValueError,'HOLD_NEW_CARD_COST'):
            r.generate(self.state,self.historical,bad)
    def test_reject_invalid_candidates(self):
        def bad(*a,**kw):
            v=fake_search(*a,**kw)
            v['top_plans'][0]['start_by_year'][1]['start_project_ids']=[25]
            return v
        with self.assertRaisesRegex(ValueError,'HOLD_DUPLICATE_PROJECT'):
            r.generate(self.state,self.historical,bad)
    def test_reject_faked_spendable_budget(self):
        def bad(*a,**kw):
            v=fake_search(*a,**kw)
            v['assumptions']['budget_source']='VERIFIED_SPENDABLE_CASH'
            return v
        with self.assertRaisesRegex(ValueError,'HOLD_NOT_HYPOTHETICAL'):
            r.generate(self.state,self.historical,bad)
    def test_invalid_search_bounds(self):
        with self.assertRaisesRegex(ValueError,'HOLD_SEARCH_LIMITS'):
            r.generate(self.state,self.historical,fake_search,beam_width=500)

if __name__=='__main__':unittest.main()
