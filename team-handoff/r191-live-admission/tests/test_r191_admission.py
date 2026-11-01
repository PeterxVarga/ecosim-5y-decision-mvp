import copy,csv,hashlib,io,json,math,sys,tempfile,types,unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from admission_r191 import AdmissionHold,validate_state,validate_r156_bundle,year1_finance
from run_r191_shadow import verify_source,run
from bounded_shadow_r189 import Hold

BASE=Path(__file__).resolve().parents[1]
ORIGINAL=json.loads((BASE/'examples'/'historical_test_state.json').read_text())
DATE='2026-11-02T12:30:00+01:00'
NOW=datetime.fromisoformat('2026-11-02T13:10:00+01:00')

def current():
    s=copy.deepcopy(ORIGINAL)
    s['provenance'].update(source='CURRENT_READONLY_FROM_OPERATOR',round='Qualification',
        captured_at_local=DATE,source_evidence_id='capture_20261102_1230')
    s['market']['cap_source']='EcoSim market view observed at Qualification 1'
    s['market']['smartcity_total_weights']={'Gazdaság':.25,'Környezet':.2,'Kormányzás':.15,'Életkörülmények':.15,'Mobilitás':.1,'Emberek':.15}
    return s

def finance():
    return {'mode':'CURRENT_YEAR1_OPERATOR_READONLY','source_evidence_id':'finance-20261102','captured_at_local':DATE,
            'period':1,'operator_observed_spendable_ecu':150000,'operator_observed_committed_ecu':30000}


def csv_rows(rows,heads):
    b=io.StringIO();w=csv.DictWriter(b,fieldnames=heads,lineterminator='\n');w.writeheader();w.writerows(rows);return b.getvalue().encode()


def bundle(path,state):
    path.mkdir()
    fields=[{'metric':k,'value':str(v)} for k,v in state['team']['baseline_smartcity_factors'].items()]
    fields.append({'metric':'Okosváros-index','value':'51.96'})
    projects=[{'project_id':str(i),'previous_running':'true' if i in state['team']['initially_active_project_ids'] else 'false','selected_new':'false'} for i in range(1,36)]
    meta=state['provenance']
    manifest={'capture_mode':'CURRENT_READONLY','kind':'PLAN','team':meta['team'],'market':meta['market'],'round':meta['round'],
              'period':meta['current_period'],'captured_at_local':DATE,'source_evidence_id':meta['source_evidence_id']}
    params={'market':{'maxProjectPerTurn':state['market']['maxProjectPerTurn'],
                      'smartcity_total_weights':state['market']['smartcity_total_weights']},
            'team':{'project1_active_previous_period':False}}
    blobs={'manifest.json':json.dumps(manifest).encode(), 'parameters.json':json.dumps(params).encode(),
           'factors.csv':csv_rows(fields,['metric','value']),
           'projects.csv':csv_rows(projects,['project_id','previous_running','selected_new'])}
    for k,v in blobs.items():(path/k).write_bytes(v)
    receipt={'schema':'ECOSIM_R156_ACQUISITION_RECEIPT_V1','capture_mode':'CURRENT_READONLY',
             'market_cap_observed':True,'market_index_weights_observed':True,
             'provided_by':'OPERATOR_EXPORT_NOT_INDEPENDENTLY_SERVER_VERIFIED','gameplay_gate':'STOP',
             'file_sha256':{k:hashlib.sha256(v).hexdigest() for k,v in blobs.items()},
             'sources':{'factors':'EcoSim index','projects':'EcoSim project summary','market_project_cap':'EcoSim settings','market_index_weights':'EcoSim score settings'}}
    (path/'R156_ACQUISITION_RECEIPT.json').write_text(json.dumps(receipt))
    return path

class AdmissionTests(unittest.TestCase):
    def setUp(self):self.state=current()
    def test_historical_pass(self):self.assertEqual(validate_state(ORIGINAL,mode='historical')['mode'],'historical')
    def test_history_as_live_refused(self):
        with self.assertRaisesRegex(AdmissionHold,'HISTORICAL'):validate_state(ORIGINAL,mode='current',now=NOW)
    def test_current_as_history_refused(self):
        with self.assertRaisesRegex(AdmissionHold,'HISTORICAL_TAG'):validate_state(self.state,mode='historical')
    def test_current_observed_metadata_ok(self):self.assertEqual(validate_state(self.state,mode='current',now=NOW)['gameplay_gate'],'STOP')
    def test_stale_source_refused(self):
        with self.assertRaisesRegex(AdmissionHold,'STALE'):validate_state(self.state,mode='current',now=datetime.fromisoformat('2026-11-05T12:00:00+01:00'))
    def test_naive_timestamp_refused(self):
        self.state['provenance']['captured_at_local']='2026-11-02T12:30:00'
        with self.assertRaisesRegex(AdmissionHold,'TIMEZONE'):validate_state(self.state,mode='current',now=NOW)
    def test_missing_cap_refused(self):
        self.state['market']['maxProjectPerTurn']=None
        with self.assertRaisesRegex(AdmissionHold,'CAP_UNKNOWN'):validate_state(self.state,mode='current',now=NOW)
    def test_assumed_cap_refused(self):
        self.state['market']['cap_source']='spoken assumed 4'
        with self.assertRaisesRegex(AdmissionHold,'UNVERIFIED_CAP'):validate_state(self.state,mode='current',now=NOW)
    def test_historical_unknown_prior_refused(self):
        t=copy.deepcopy(ORIGINAL);t['team']['project1_active_previous_period']=None
        with self.assertRaisesRegex(AdmissionHold,'PRIOR_PROJECT1'):validate_state(t,mode='historical')
    def test_missing_weights_refused(self):
        self.state['market']['smartcity_total_weights']=None
        with self.assertRaisesRegex(AdmissionHold,'WEIGHTS'):validate_state(self.state,mode='current',now=NOW)
    def test_overlap_refused(self):
        self.state['team']['already_selected_new_project_ids_current_period']=[14]
        with self.assertRaisesRegex(AdmissionHold,'OVERLAP'):validate_state(self.state,mode='current',now=NOW)
    def test_bad_factor_refused(self):
        self.state['team']['baseline_smartcity_factors']['Fizetőképes piac']=float('inf')
        with self.assertRaisesRegex(AdmissionHold,'FACTORS'):validate_state(self.state,mode='current',now=NOW)
    def test_budget_over_current_residual_refused(self):
        with self.assertRaisesRegex(AdmissionHold,'EXCEEDS_OBSERVED_RESIDUAL'):
            year1_finance(finance(),self.state,illustrative_first_year_budget=130000)
    def test_explicit_year1_budget_pass_but_not_approval(self):
        x=year1_finance(finance(),self.state,illustrative_first_year_budget=100000)
        self.assertFalse(x['actual_server_financing_approved']);self.assertEqual(x['current_year_budget_ceiling_ecu'],120000)
    def test_finance_20_min_later_accepted(self):
        v=finance();v['captured_at_local']='2026-11-02T12:50:00+01:00'
        self.assertEqual(year1_finance(v,self.state,illustrative_first_year_budget=100000)['gameplay_gate'],'STOP')
    def test_finance_3_hours_later_refused(self):
        v=finance();v['captured_at_local']='2026-11-02T15:30:00+01:00'
        with self.assertRaisesRegex(AdmissionHold,'EXCEEDS_ONE_HOUR'):
            year1_finance(v,self.state,illustrative_first_year_budget=100000)
    def test_no_finance_refused(self):
        with self.assertRaisesRegex(AdmissionHold,'EVIDENCE_REQUIRED'):year1_finance(None,self.state,illustrative_first_year_budget=100000)
    def test_finance_period_mismatch(self):
        d=finance();d['period']=2
        with self.assertRaisesRegex(AdmissionHold,'PERIOD_MISMATCH'):year1_finance(d,self.state,illustrative_first_year_budget=100000)
    def test_r156_linked_bundle_pass(self):
        with tempfile.TemporaryDirectory() as t:
            base=bundle(Path(t)/'r156',self.state)
            def read_json(p):return json.loads(Path(p).read_text())
            with patch.dict(sys.modules,{'json_integrity_r162':types.SimpleNamespace(read_json=read_json)}):
                result=validate_r156_bundle(self.state,base,now=NOW)
            self.assertEqual(result['status'],'PASS_OPERATOR_CAPTURE_CONSISTENCY_ONLY');self.assertFalse(result['current_source_is_server_authenticated'])
    def test_r156_hash_tamper_refused(self):
        with tempfile.TemporaryDirectory() as t:
            base=bundle(Path(t)/'r156',self.state)
            (base/'projects.csv').write_text('tampered')
            with patch.dict(sys.modules,{'json_integrity_r162':types.SimpleNamespace(read_json=lambda p:json.loads(Path(p).read_text()))}):
                with self.assertRaisesRegex(AdmissionHold,'SHA256_MISMATCH'):validate_r156_bundle(self.state,base,now=NOW)
    def test_r156_source_data_contradiction(self):
        with tempfile.TemporaryDirectory() as t:
            base=bundle(Path(t)/'r156',self.state)
            self.state['team']['baseline_smartcity_factors']['Fizetőképes piac']=72.51
            with patch.dict(sys.modules,{'json_integrity_r162':types.SimpleNamespace(read_json=lambda p:json.loads(Path(p).read_text()))}):
                with self.assertRaisesRegex(AdmissionHold,'FACTOR_VALUE_MISMATCH'):validate_r156_bundle(self.state,base,now=NOW)
    def test_r156_requires_declared_team_identity(self):
        with tempfile.TemporaryDirectory() as t:
            base=bundle(Path(t)/'r156',self.state)
            self.state['provenance']['market']='Y'
            with patch.dict(sys.modules,{'json_integrity_r162':types.SimpleNamespace(read_json=lambda p:json.loads(Path(p).read_text()))}):
                with self.assertRaisesRegex(AdmissionHold,'PROVENANCE_MISMATCH_market'):validate_r156_bundle(self.state,base,now=NOW)
    def test_r162_source_not_present_fails_closed(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(Hold):verify_source(Path(t))
    def test_r191_requires_source_checkout(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(Hold):run(Path(t),Path(t)/'state.json',100000,4,mode='historical-test')

if __name__=='__main__':unittest.main()
