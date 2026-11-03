import json, math, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from exact_policy_replay_r199 import make_candidates,source_docs,replay,markdown,digest,DOCS,SOURCE,REPO
from bridge_r197 import load
STATE,_=load(REPO/'team-handoff/r191-live-admission/examples/historical_test_state.json')

def example():
    return {'annual_comparison':[{'year':i,
        'max_project_ids':[13] if i==1 else [],
        'reserve_project_ids':[8] if i==1 else [],
        'max_cost_ecu':1000,'reserve_cost_ecu':1000} for i in range(1,6)]}

class ExactTests(unittest.TestCase):
    def hold(self,cb):
        with self.assertRaises(ValueError) as cm:cb()
        self.assertIn('HOLD_',str(cm.exception))
    def test_two_schedules(self):
        p=make_candidates(example(),STATE,None)
        self.assertEqual(len(p),2)
        self.assertEqual(p[0]['project_ids_by_year'][0],[13])
        self.assertEqual(p[1]['candidate_id'],'R195-reserve')
        self.assertEqual(p[0]['five_year_conservative_project_need_ecu'],5000)
    def test_year_drift(self):
        x=example();x['annual_comparison'][2]['year']=4
        self.hold(lambda:make_candidates(x,STATE,None))
    def test_short_horizon(self):
        x=example();x['annual_comparison'].pop()
        self.hold(lambda:make_candidates(x,STATE,None))
    def test_duplicate_same_year(self):
        x=example();x['annual_comparison'][0]['max_project_ids']=[13,13]
        self.hold(lambda:make_candidates(x,STATE,None))
    def test_duplicate_across_years(self):
        x=example();x['annual_comparison'][1]['max_project_ids']=[13]
        self.hold(lambda:make_candidates(x,STATE,None))
    def test_float_id(self):
        x=example();x['annual_comparison'][0]['max_project_ids']=[13.0]
        self.hold(lambda:make_candidates(x,STATE,None))
    def test_invalid_id(self):
        x=example();x['annual_comparison'][0]['max_project_ids']=[36]
        self.hold(lambda:make_candidates(x,STATE,None))
    def test_negative_cost(self):
        x=example();x['annual_comparison'][0]['max_cost_ecu']=-1
        self.hold(lambda:make_candidates(x,STATE,None))
    def test_overflow_cost(self):
        x=example();x['annual_comparison'][0]['max_cost_ecu']=float('inf')
        self.hold(lambda:make_candidates(x,STATE,None))
    def test_boolean_cost(self):
        x=example();x['annual_comparison'][0]['max_cost_ecu']=True
        self.hold(lambda:make_candidates(x,STATE,None))
    def doc(self):
        return {'inputs':{k:{'sha256':digest(SOURCE/v),'filename':Path(v).name}
                          for k,v in DOCS.items()}}
    def test_valid_source_docs(self):
        t,f,o=source_docs(self.doc())
        self.assertEqual(t['source_class'],'SYNTHETIC_TEST_ONLY')
        self.assertEqual(f['source_class'],o['source_class'])
    def test_source_sha_drift(self):
        d=self.doc();d['inputs']['tax_scenarios']['sha256']='0'*64
        self.hold(lambda:source_docs(d))
    def test_source_name_drift(self):
        d=self.doc();d['inputs']['tax_scenarios']['filename']='other.json'
        self.hold(lambda:source_docs(d))
    def test_current_mode_blocked(self):
        self.hold(lambda:replay({'mode':'current-readonly'},'x',{}, {},{},'y',{},'z'))
    def test_state_hash_mismatch(self):
        t={'mode':'historical-test','input_state_sha256':'a'*64}
        self.hold(lambda:replay(t,'x',{}, {},{'inputs':{'state':{'sha256':'b'*64}}},'y',{},'c'*64))
    def test_markdown_stop(self):
        s=markdown({'exact_project_plans':0,'project_policy_pairs':0,'plans':[]})
        self.assertIn('GAME_ACTION_GATE=STOP',s)
        self.assertIn('NEM adható hozzá',s)
    def test_json_duplicate_key(self):
        with tempfile.TemporaryDirectory() as x:
            p=Path(x)/'a.json';p.write_text('{"x":1,"x":2}')
            with self.assertRaisesRegex(ValueError,'DUPLICATE_JSON_KEY'):
                load(p)
    def test_json_overflow(self):
        with tempfile.TemporaryDirectory() as x:
            p=Path(x)/'a.json';p.write_text('{"x":1e999}')
            with self.assertRaisesRegex(ValueError,'NONFINITE_JSON'):
                load(p)
if __name__=='__main__':unittest.main()
