import json,sys,tempfile,unittest,subprocess,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from bounded_shadow_r189 import Hold,improve

def catalog():
    d={i:dict(id=i,name=f'SYNTHETIC_{i}',startup_cost=2_000_000,investment=0,
                  maintenance_cost=0,project_conditions=[]) for i in range(1,36)}
    for i in [1,2,3]:d[i].update(startup_cost=0,maintenance_cost=0)
    return d

def auditor_factory(idx,initial,budgets,cap,fixed=(),bonus=False,start=1):
    def audit(rows):
        hard=[];conditional=[];prev=set(initial);started=set()
        for off,ids in enumerate(rows):
            y=start+off;now=set(ids)
            if now&prev or now&started:hard.append('DUPLICATE')
            if off==0 and not set(fixed)<=now:hard.append('FIXED')
            allowance=cap+(int(bonus) if off==0 else int(1 in prev))
            if len(now)>allowance:hard.append('CAP')
            if sum(idx[i]['startup_cost']+idx[i]['investment'] for i in now)+sum(max(0,idx[i]['maintenance_cost']) for i in now|prev)>budgets[off]:hard.append('CASH')
            for i in now:
                for cond in idx[i]['project_conditions']:
                    dep=int(cond)
                    if dep in now:conditional.append('SAME_YEAR_ORDER')
                    elif dep not in prev:hard.append('PREREQ')
            started|=now;prev|=now
        return {'schema':'ECOSIM_R160_INDEPENDENT_PLAN_AUDIT_V1','hard_rule_violations':hard,
                'conditional_eligibility_items':conditional,
                'status':'FAIL_REPLAY' if hard else ('CONDITIONAL_NOT_SERVER_VERIFIED' if conditional else 'PASS_DISPLAY_RULES_ONLY_NOT_SERVER_APPROVAL')}
    return audit

class R189Tests(unittest.TestCase):
    def setUp(self):
        self.idx=catalog();self.budget=[100_000]*5;self.kw=dict(initial_active=[],fixed_first_ids=[],start_year=1,
             annual_budgets=self.budget,base_project_cap=2,previous_project1_active=False,max_evaluations=220,max_passes=3)
    def audit(self,**opts):return auditor_factory(self.idx,[],self.budget,2,**opts)
    @staticmethod
    def score(rows):return sum(y*0.01+pid*.0001 for y,r in enumerate(rows,1) for pid in r)
    def runit(self,starts,**kw):return improve(starts,self.idx,score_fn=self.score,audit_fn=self.audit(),**dict(self.kw,**kw))
    def test_better_year_no_regression(self):
        s=[[1,2],[],[],[],[]];r=self.runit(s)
        self.assertTrue(r['strictly_improved']);self.assertGreater(r['final_score'],r['initial_score'])
        self.assertEqual(set(sum(r['years'],[])),{1,2});self.assertEqual(r['gameplay_gate'],'STOP')
        self.assertLessEqual(r['evaluated_candidates'],220)
    def test_preserves_fixed_first(self):
        s=[[1,2],[],[],[],[]];r=improve(s,self.idx,score_fn=self.score,
            audit_fn=self.audit(fixed=[1]),**dict(self.kw,fixed_first_ids=[1]));self.assertIn(1,r['years'][0])
    def test_budget_fail_closed(self):
        with self.assertRaisesRegex(Hold,'ENVELOPES'):
            self.runit([[1],[],[],[],[]],annual_budgets=None)
    def test_missing_project_catalog_refused(self):
        with self.assertRaisesRegex(Hold,'35_CARD'):improve([[1],[],[],[],[]],{1:self.idx[1]},
            score_fn=self.score,audit_fn=self.audit(),**self.kw)
    def test_unknown_bonus_refused(self):
        with self.assertRaisesRegex(Hold,'PREVIOUS_PROJECT1'):
            self.runit([[1],[],[],[],[]],previous_project1_active=None)
    def test_cap_no_overflow(self):
        r=self.runit([[1,2],[3],[],[],[]]);self.assertTrue(all(len(x)<=2 for x in r['years']))
    def test_conditional_dependency_holds(self):
        self.idx[2]['project_conditions']=['1']
        with self.assertRaisesRegex(Hold,'BASELINE_NOT_UNCONDITIONALLY_VALID'):
            self.runit([[1,2],[],[],[],[]])
    def test_unknown_catalog_id_rejected(self):
        with self.assertRaisesRegex(Hold,'BAD_PROJECT_SELECTION'):
            self.runit([[99],[],[],[],[]])
    def test_existing_project_never_dropped(self):
        r=self.runit([[1],[2],[],[],[]]);self.assertEqual(len(sum(r['years'],[])),2)
    def test_negative_score_nonfinite_rejected(self):
        with self.assertRaisesRegex(Hold,'NONFINITE_ORIGINAL_SCORE'):
            improve([[1],[],[],[],[]],self.idx,score_fn=lambda _:float('nan'),audit_fn=self.audit(),**self.kw)
    def test_base_invalid_rejected(self):
        with self.assertRaisesRegex(Hold,'BASELINE_NOT_UNCONDITIONALLY_VALID'):
            self.runit([[4],[],[],[],[]])
    def test_never_calls_scorer_on_invalid(self):
        seen=[]
        def limited(rows):
            assert all(i<=3 for row in rows for i in row),'invalid candidate scored';seen.append(1);return self.score(rows)
        r=improve([[1,2],[],[],[],[]],self.idx,score_fn=limited,audit_fn=self.audit(),**self.kw)
        self.assertTrue(len(seen)>1)
    def test_determinism(self):
        a=self.runit([[1,2],[],[],[],[]]);b=self.runit([[1,2],[],[],[],[]]);self.assertEqual(a,b)
    def test_twenty_selected_across_full_35_structure(self):
        for i in range(1,21):self.idx[i]['startup_cost']=1000
        starts=[list(range(y*4+1,y*4+5)) for y in range(5)]
        def score(rows):return sum(i*(6-y) for y,row in enumerate(rows,1) for i in row)
        r=improve(starts,self.idx,initial_active=[],fixed_first_ids=[],start_year=1,
             annual_budgets=[20_000]*5,base_project_cap=4,previous_project1_active=False,
             score_fn=score,audit_fn=auditor_factory(self.idx,[],[20_000]*5,4),
             max_evaluations=1600,max_passes=3)
        self.assertLessEqual(r['evaluated_candidates'],1600)
        self.assertEqual(set(sum(r['years'],[])),set(range(1,21)))
        self.assertTrue(all(len(row)<=4+int(y>0 and any(1 in prior for prior in r['years'][:y])) for y,row in enumerate(r['years'])))
        self.assertGreater(r['final_score'],r['initial_score'])
    def test_invalid_start_year_holds_cleanly(self):
        with self.assertRaisesRegex(Hold,'INVALID_START_YEAR'):
            self.runit([[1],[],[],[],[]],start_year='1')
    def test_zero_evaluation_budget_holds(self):
        with self.assertRaisesRegex(Hold,'INVALID_BUDGET'):
            self.runit([[1],[],[],[],[]],max_evaluations=0)
    def test_source_tree_write_prohibited(self):
        root=Path(__file__).resolve().parents[1]
        cmd=[sys.executable,str(root/'tools/run_r162_shadow.py'),'--repo-root',str(root),
             '--state',str(root/'README.md'),'--annual-budget','50000', '--cap','4',
             '--out',str(root/'forbidden_write.json')]
        p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('Cannot write into the R162 source tree',p.stderr)
        self.assertFalse((root/'forbidden_write.json').exists())
    def test_wrong_git_pin_holds(self):
        from run_r162_shadow import run
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            subprocess.run(['git','init','-q',str(root)],check=True,stdout=subprocess.PIPE)
            subprocess.run(['git','-C',str(root),'config','user.email','test@example.org'],check=True)
            subprocess.run(['git','-C',str(root),'config','user.name','Test'],check=True)
            (root/'x').write_text('fixture')
            subprocess.run(['git','-C',str(root),'add','x'],check=True)
            subprocess.run(['git','-C',str(root),'commit','-qm','fixture'],check=True)
            with self.assertRaisesRegex(Hold,'PIN_MISMATCH'):
                run(root,root/'state.json',100000,2)
    def test_no_source_runner_holds(self):
        from run_r162_shadow import run
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaisesRegex(Hold,'PINNED_GIT_REPOSITORY_REQUIRED'):
                run(Path(t),Path(t)/'state.json',100000,2)

if __name__=='__main__':unittest.main()
