import copy
import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('p198',Path(__file__).resolve().parents[1]/'tools/paired_decision_r198.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
H='a'*64;G='b'*64

def sample():
    t={'schema':'ECOSIM_R195_TWO_ENVELOPE_TRADEOFF_V1','mode':'historical-test',
       'gameplay_gate':'STOP','financing_approved':False,'input_state_sha256':H,'max_model_score':.45,'reserve_model_score':.4,
       'annual_comparison':[{'year':1,'max_project_ids':[1], 'max_cost_ecu':100.,'reserve_project_ids':[2], 'reserve_cost_ecu':80.},
                            {'year':2,'max_project_ids':[3], 'max_cost_ecu':90.,'reserve_project_ids':[4], 'reserve_cost_ecu':70.},
                            {'year':3,'max_project_ids':[5], 'max_cost_ecu':90.,'reserve_project_ids':[6], 'reserve_cost_ecu':70.},
                            {'year':4,'max_project_ids':[], 'max_cost_ecu':0.,'reserve_project_ids':[], 'reserve_cost_ecu':0.},
                            {'year':5,'max_project_ids':[], 'max_cost_ecu':0.,'reserve_project_ids':[], 'reserve_cost_ecu':0.}]}
    plans=[{'candidate_id':'P1','project_ids_by_year':[[1],[3],[5],[],[]], 'conservative_project_need_ecu_by_year':[100,90,90,0,0]},
           {'candidate_id':'P2','project_ids_by_year':[[2],[4],[6],[],[]], 'conservative_project_need_ecu_by_year':[80,70,70,0,0]}]
    d={'schema':'ECOSIM_R149_OFFLINE_DECISION_MVP_V1','gameplay_gate':'STOP','game_writes':0,'run_mode':'HISTORICAL_ILLUSTRATION',
       'inputs':{'state':{'sha256':H}},'start_year':1,'candidate_comparison':plans}
    for key in m.bridge.__globals__['KEYS']:
        d[key]={'source_class':'SYNTHETIC_TEST_ONLY','gameplay_gate':'STOP'}
    d['r155_source_operating_cash_tradeoffs']['path_counterfactuals']=[{'path_id':'baseline'}]
    d[m.TIMING]['true_cash_availability_or_financing_proven']=False
    d[m.TIMING]['combinations']=[
        {'candidate_id':p['candidate_id'],'path_id':'baseline','gameplay_gate':'STOP',
         'affordability_authorized':False,'actual_spendable_cash_ecu':None,'true_funding_gap_ecu':None,
         'annual_rows':[{'year':i+1,'projects_started_ids':z,'project_card_need_ecu':c} for i,(z,c) in enumerate(zip(p['project_ids_by_year'],p['conservative_project_need_ecu_by_year']))],
         'five_year_partial_net_after_card_cost_ecu':-140.,'hypothetical_peak_zero_opening_cash_shortfall_immediate_ecu':220.,
         'hypothetical_peak_zero_opening_cash_shortfall_positive_receipts_deferred_ecu':270.,'conditional_terminal_mapped_proxy_delta':1.3}
        for p in plans]
    return t,d

class Tests(unittest.TestCase):
    def run_join(self,t,d):return m.join(t,H,d,G)
    def fail(self,t,d,code):
        with self.assertRaisesRegex(ValueError,code):self.run_join(t,d)
    def test_exact_both(self):
        t,d=sample();v=self.run_join(t,d)
        self.assertEqual(v['status'],'PARTIAL_IDENTICAL_CANDIDATE_POLICY_EVIDENCE_NO_GAME_AUTHORITY')
        self.assertEqual(len(v['findings'][0]['paired_paths']),1)
        self.assertEqual(v['findings'][0]['exact_candidate_id'],'P1')
        self.assertEqual(v['findings'][1]['exact_candidate_id'],'P2')
        self.assertFalse(v['funds_authorized']);self.assertEqual(v['gameplay_gate'],'STOP')
        self.assertIn('nem jogosít',m.render_hu(v))
    def test_only_first_year_does_not_join(self):
        t,d=sample();d['candidate_comparison'][0]['project_ids_by_year'][1]=[7]
        d[m.TIMING]['combinations'][0]['annual_rows'][1]['projects_started_ids']=[7]
        v=self.run_join(t,d)
        self.assertEqual(v['findings'][0]['status'],'HOLD_NO_EXACT_PROJECT_SCHEDULE_MATCH')
        self.assertEqual(v['findings'][0]['first_year_only_matches'],1)
    def test_only_cost_difference_blocks(self):
        t,d=sample();d['candidate_comparison'][0]['conservative_project_need_ecu_by_year'][1]=91
        d[m.TIMING]['combinations'][0]['annual_rows'][1]['project_card_need_ecu']=91
        v=self.run_join(t,d)
        self.assertEqual(v['findings'][0]['status'],'HOLD_EXACT_PROJECTS_BUT_COSTS_DIFFER')
        self.assertEqual(v['findings'][0]['paired_paths'],[])
    def test_timing_project_tamper(self):
        t,d=sample();d[m.TIMING]['combinations'][0]['annual_rows'][0]['projects_started_ids']=[30]
        self.fail(t,d,'TIMING_PROJECT_DRIFT')
    def test_timing_cost_tamper(self):
        t,d=sample();d[m.TIMING]['combinations'][0]['annual_rows'][0]['project_card_need_ecu']=123
        self.fail(t,d,'TIMING_PROJECT_COST_DRIFT')
    def test_duplicate_cid(self):
        t,d=sample();d['candidate_comparison'].append(copy.deepcopy(d['candidate_comparison'][0]))
        self.fail(t,d,'DUPLICATE_R149_CANDIDATE_ID')
    def test_duplicate_pair(self):
        t,d=sample();d[m.TIMING]['combinations'].append(copy.deepcopy(d[m.TIMING]['combinations'][0]))
        self.fail(t,d,'DUPLICATE_R159_PAIR')
    def test_missing_candidate(self):
        t,d=sample();d[m.TIMING]['combinations'][0]['candidate_id']='UNKNOWN'
        self.fail(t,d,'UNKNOWN_R159_CANDIDATE')
    def test_unknown_path(self):
        t,d=sample();d[m.TIMING]['combinations'][0]['path_id']='MISSING'
        self.fail(t,d,'UNKNOWN_R159_PATH')
    def test_explicit_game_stop_required(self):
        t,d=sample();d[m.TIMING]['combinations'][0]['gameplay_gate']='GO'
        self.fail(t,d,'TIMING_CLAIMS_APPROVAL')
    def test_approval_false(self):
        t,d=sample();d[m.TIMING]['combinations'][0]['affordability_authorized']=True
        self.fail(t,d,'TIMING_CLAIMS_APPROVAL')
    def test_timestamp_year_range(self):
        t,d=sample();t['annual_comparison'][1]['year']=4
        self.fail(t,d,'NONCONTIGUOUS_R195_YEARS')
    def test_mismatched_state(self):
        t,d=sample();d['inputs']['state']['sha256']='c'*64
        self.fail(t,d,'STATE_HASH_MISMATCH')
    def test_mixed_policy_source(self):
        t,d=sample();d['r153_source_backed_tax_sensitivity']['source_class']='OPERATOR_DECLARED_READONLY_HYPOTHESIS'
        self.fail(t,d,'SOURCE_MODE_MISMATCH')
    def test_nonfinite_cash(self):
        t,d=sample();d[m.TIMING]['combinations'][0]['five_year_partial_net_after_card_cost_ecu']=float('inf')
        self.fail(t,d,'Out of range float values')
    def test_duplicate_project_across_years(self):
        t,d=sample();t['annual_comparison'][1]['max_project_ids']=[1]
        self.fail(t,d,'DUPLICATE_R195_PROJECT_ACROSS_YEARS')
    def test_new_state_current_synthetic_forbidden(self):
        t,d=sample();t['mode']='current-readonly';d['run_mode']='CURRENT_SNAPSHOT_REVIEW'
        self.fail(t,d,'SYNTHETIC_MODE_FORBIDDEN_IN_CURRENT')

if __name__=='__main__':unittest.main()
