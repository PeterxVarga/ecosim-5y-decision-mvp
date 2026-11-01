import importlib.util, unittest
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'tools/bridge_r197.py'
s=importlib.util.spec_from_file_location('r197',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
H='a'*64

def data():
 t={'schema':'ECOSIM_R195_TWO_ENVELOPE_TRADEOFF_V1','gameplay_gate':'STOP','financing_approved':False,'mode':'historical-test','input_state_sha256':H,'max_model_score':.45,'reserve_model_score':.43,'annual_comparison':[{'year':1}]}
 d={'schema':'ECOSIM_R149_OFFLINE_DECISION_MVP_V1','gameplay_gate':'STOP','game_writes':0,'run_mode':'HISTORICAL_ILLUSTRATION','inputs':{'state':{'sha256':H}},'start_year':1}
 for key in m.KEYS:d[key]={'source_class':'SYNTHETIC_TEST_ONLY','gameplay_gate':'STOP'}
 return t,d
class Tests(unittest.TestCase):
 def test_same_state(self):
  t,d=data();r=m.assemble(t,H,d,H);self.assertTrue(r['same_initial_state_verified']);self.assertEqual(r['gameplay_gate'],'STOP');self.assertFalse(r['cross_model_cash_additive_to_budget'])
 def test_state_mismatch(self):
  t,d=data();d['inputs']['state']['sha256']='b'*64
  with self.assertRaisesRegex(ValueError,'STATE_HASH_MISMATCH'):m.assemble(t,H,d,H)
 def test_unsafe_game_action(self):
  t,d=data();d['game_writes']=1
  with self.assertRaisesRegex(ValueError,'R149_PROOF_GATE_FAILED'):m.assemble(t,H,d,H)
 def test_synthetic_current_rejected(self):
  t,d=data();t['mode']='current-readonly';d['run_mode']='CURRENT_SNAPSHOT_REVIEW'
  with self.assertRaisesRegex(ValueError,'SYNTHETIC_MODE_FORBIDDEN_IN_CURRENT'):m.assemble(t,H,d,H)
 def test_mixed_source_rejected(self):
  t,d=data();d[m.KEYS[0]]['source_class']='OPERATOR_DECLARED_READONLY_HYPOTHESIS'
  with self.assertRaisesRegex(ValueError,'SOURCE_MODE_MISMATCH'):m.assemble(t,H,d,H)
 def test_bad_city(self):
  t,d=data()
  with self.assertRaisesRegex(ValueError,'R196_PROOF_GATE_FAILED'):m.assemble(t,H,d,H,{'schema':'ECOSIM_R196_CITY_CROSS_TAB_REVIEW_V1','r195_result_sha256':'b'*64,'r195_input_state_sha256':H,'gameplay_gate':'STOP'})
 def test_bad_year(self):
  t,d=data();d['start_year']=2
  with self.assertRaisesRegex(ValueError,'START_YEAR_MISMATCH'):m.assemble(t,H,d,H)
if __name__=='__main__':unittest.main()
