import json,sys,tempfile,types,unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import run_r191_shadow as runner
from bounded_shadow_r189 import Hold

class RunnerIntegrationShims(unittest.TestCase):
    """Unit contract mocks; not counted as native R162/R160 E2E."""
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name);self.root=self.base/'repo'/'ECOSIM_R162_INTEGRITY_REVIEW_RC'
        (self.root/'data').mkdir(parents=True)
        (self.root/'data'/'ecosim_projects_20261030.json').write_text('{}')
        self.state_path=self.base/'state.json';self.state_path.write_bytes((ROOT/'examples'/'historical_test_state.json').read_bytes())
        self.state=json.loads(self.state_path.read_text())
        self.idx={i:dict(id=i,name='mock-'+str(i),startup_cost=0,investment=0,maintenance_cost=0,partner_support=0,
                         project_conditions=[],effects=[]) for i in range(1,36)}
        self.calls=[];self.result_gate='STOP';self.first_invalid=False
        def audit_plan(idx,*,starts,**kwargs):
            self.calls.append(('audit',tuple(tuple(x) for x in starts)))
            valid=not self.first_invalid or len(starts[0])==0
            return {'schema':'ECOSIM_R160_INDEPENDENT_PLAN_AUDIT_V1','hard_rule_violations':[] if valid else ['FAIL'],
                    'conditional_eligibility_items':[],'status':'PASS_DISPLAY_RULES_ONLY_NOT_SERVER_APPROVAL' if valid else 'FAIL_REPLAY'}
        def search(*args,**kwargs):
            self.calls.append(('search',kwargs['objective']))
            return {'top_plans':[{'start_by_year':[{'start_project_ids':list(row)} for row in ([13],[],[],[],[])]},
                                {'start_by_year':[{'start_project_ids':list(row)} for row in ([],[13],[],[],[])]}],
                    'final_gameplay_decision':self.result_gate}
        def cfg(*args):
            s=args[0];return {'initial_active':frozenset(s['team']['initially_active_project_ids']),
                             'fixed_first':frozenset(s['team']['already_selected_new_project_ids_current_period']),
                             'baseline':s['team']['baseline_smartcity_factors'],'project1prev':False}
        def replay(idx,rows,baseline,**kwargs):
            return {'scenario_min_clamp_only_mapped_delta':sum(i*.001+y*.01 for y,r in enumerate(rows) for i in r)}
        self.modules={
            'json_integrity_r162':types.SimpleNamespace(read_json=lambda p:json.loads(Path(p).read_text())),
            'strategy_5y':types.SimpleNamespace(search=search,derive_config=cfg),
            'portfolio_5y':types.SimpleNamespace(project_index=lambda:self.idx),
            'robust_decision_r157':types.SimpleNamespace(replay=replay),
            'independent_audit_r160':types.SimpleNamespace(audit_plan=audit_plan),
            'r142_proxy_reference':types.SimpleNamespace(COEFF={'Digitalizáció':1})}
    def go(self):
        with patch.object(runner,'verify_source',return_value=self.root.parent), patch.dict(sys.modules,self.modules):
            return runner.run(self.root,self.state_path,100000,4,mode='historical-test')
    def test_smoke_full_call_chain(self):
        r=self.go();self.assertEqual(r['schema'],'ECOSIM_R191_HARDENED_PINNED_SHADOW_V1')
        self.assertEqual(r['gameplay_gate'],'STOP');self.assertFalse(r['actual_gameplay_approved'])
        self.assertIn(('search','scenario_min'),self.calls)
        self.assertIn('human_explanation_hu',r)
        self.assertIn('Mit válasszunk most',r['human_explanation_hu']['markdown'])
        self.assertIn('TÖRTÉNETI TESZT',r['human_explanation_hu']['markdown'])
        self.assertTrue(r['project_set_preserved']);self.assertFalse(r['admission']['official_server_attested'])
        self.assertTrue(r['annual_envelopes'][1]['basis']=='HYPOTHETICAL_UNVERIFIED')
    def test_selects_next_auditable_seed(self):
        self.first_invalid=True
        r=self.go();self.assertEqual(r['seed_rank_within_R162_top_plans'],2)
    def test_wrong_game_gate_fails_closed(self):
        self.result_gate='GO'
        with self.assertRaisesRegex(Hold,'GAME_ACTION_GATE_NOT_STOP'):self.go()
    def test_test_source_rejected_in_current(self):
        with patch.object(runner,'verify_source',return_value=self.root.parent),patch.dict(sys.modules,self.modules):
            with self.assertRaisesRegex(Exception,'HISTORICAL_OR_TEST'):
                runner.run(self.root,self.state_path,100000,4,mode='current-readonly')
    def test_live_requires_capture_files_even_when_json_has_current_label(self):
        self.state['provenance'].update(source='CURRENT_READONLY',round='Qualification',source_evidence_id='source123',captured_at_local=datetime.now(ZoneInfo('Europe/Budapest')).isoformat())
        self.state['market']['cap_source']='EcoSim current market observed'
        self.state['market']['smartcity_total_weights']={'Gazdaság':.25,'Környezet':.2,'Kormányzás':.15,'Életkörülmények':.15,'Mobilitás':.1,'Emberek':.15}
        self.state_path.write_text(json.dumps(self.state))
        with patch.object(runner,'verify_source',return_value=self.root.parent),patch.dict(sys.modules,self.modules):
            with self.assertRaisesRegex(Hold,'CURRENT_R156_BUNDLE'):
                runner.run(self.root,self.state_path,100000,4,mode='current-readonly')
    def test_no_results_hold(self):
        self.first_invalid=True
        # Both seeds auditor invalid by forcing no valid starter, other tests check fallback.
        self.idx[13]['name']='conditional'
        with patch.object(runner,'verify_source',return_value=self.root.parent),patch.dict(sys.modules,self.modules):
            with self.assertRaisesRegex(Hold,'BASELINE|NO_UNCONDITIONALLY'):
                # Replacing first candidate behavior via separate policy will hold at improvement baseline or seed.
                def audit_reject(*args,**kwargs):return {'schema':'ECOSIM_R160_INDEPENDENT_PLAN_AUDIT_V1','hard_rule_violations':['NO'], 'conditional_eligibility_items':[],'status':'FAIL_REPLAY'}
                with patch.dict(sys.modules,{'independent_audit_r160':types.SimpleNamespace(audit_plan=audit_reject)}):
                    runner.run(self.root,self.state_path,100000,4,mode='historical-test')

if __name__=='__main__':unittest.main()
