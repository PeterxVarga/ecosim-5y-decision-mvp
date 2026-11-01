"""Independent negative tests: current historical card parity is mandatory."""
import copy
import json
import sys
import tempfile
import types
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from catalog_gate_r192 import CatalogHold,validate_catalog
import run_r191_shadow as runner
from bounded_shadow_r189 import Hold

class CatalogGate(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,11,2,13,0,tzinfo=timezone.utc)
        self.date='2026-11-02T14:00:00+01:00'
        self.state={'provenance':{'team':'Example team','market':'Z','round':'Qualification','current_period':1,'captured_at_local':self.date}}
        self.original={'projects':[{'id':i,'name':f'project {i}', 'startup_cost':1000,
            'maintenance_cost':-12 if i==3 else 20,'investment':300,'partner_support':10,
            'project_conditions':['project 1'] if i==2 else [],
            'effects':[{'metric':'Economic','value_percent':2.5}] if i%2 else []}
            for i in range(1,36)]}
        self.capture={'schema':'ECOSIM_R192_CURRENT_CARD_CATALOG_V1',
            'capture_mode':'CURRENT_READONLY','team':'Example team','market':'Z',
            'round':'Qualification','period':1,'captured_at_local':self.date,
            'source_evidence_id':'operator-current-proj-capture',
            'source_view':'EcoSim EDU Projects read-only',
            'projects':copy.deepcopy(self.original['projects'])}
    def checked(self):return validate_catalog(self.capture,self.state,self.original,now=self.now)
    def test_35_current_cards_parity(self):
        r=self.checked()
        self.assertEqual(r['observed_card_count'],35)
        self.assertFalse(r['server_attested']);self.assertEqual(r['gameplay_gate'],'STOP')
    def test_absent_catalog_is_hold(self):
        self.capture['projects']=None
        with self.assertRaisesRegex(CatalogHold,'ALL_35'):self.checked()
    def test_extra_unknown_card_is_hold(self):
        self.capture['projects'][0]['id']=36
        with self.assertRaisesRegex(CatalogHold,'INVALID_CARD_ID'):self.checked()
    def test_duplicate_id_hold(self):
        self.capture['projects'][0]['id']=2
        with self.assertRaisesRegex(CatalogHold,'DUPLICATE_CURRENT'):self.checked()
    def test_project_cost_drift_hold(self):
        self.capture['projects'][15]['investment']+=1
        with self.assertRaisesRegex(CatalogHold,'DEFINITION_DRIFT_IDS_16'):self.checked()
    def test_project_condition_drift_hold(self):
        self.capture['projects'][20]['project_conditions']=['new prerequisite']
        with self.assertRaisesRegex(CatalogHold,'DEFINITION_DRIFT_IDS_21'):self.checked()
    def test_project_effect_drift_hold(self):
        self.capture['projects'][0]['effects'][0]['value_percent']+=0.2
        with self.assertRaisesRegex(CatalogHold,'DEFINITION_DRIFT_IDS_1'):self.checked()
    def test_project_name_drift_hold(self):
        self.capture['projects'][0]['name']='another'
        with self.assertRaisesRegex(CatalogHold,'DEFINITION_DRIFT_IDS_1'):self.checked()
    def test_partner_support_drift_hold(self):
        self.capture['projects'][0]['partner_support']=100
        with self.assertRaisesRegex(CatalogHold,'DEFINITION_DRIFT_IDS_1'):self.checked()
    def test_wrong_period_hold(self):
        self.capture['period']=2
        with self.assertRaisesRegex(CatalogHold,'PERIOD_MISMATCH'):self.checked()
    def test_stale_card_capture_hold(self):
        self.capture['captured_at_local']='2026-10-30T10:00:00+01:00'
        with self.assertRaisesRegex(CatalogHold,'CAPTURE_WINDOW'):self.checked()
    def test_historical_evidence_source_hold(self):
        self.capture['source_evidence_id']='historical_R94'
        with self.assertRaisesRegex(CatalogHold,'HISTORICAL_CATALOG_AS_CURRENT'):self.checked()
    def test_future_timestamp_hold(self):
        self.capture['captured_at_local']='2026-11-03T14:00:00+01:00'
        self.state['provenance']['captured_at_local']=self.capture['captured_at_local']
        with self.assertRaisesRegex(CatalogHold,'STALE_OR_FUTURE'):self.checked()
    def test_nonfinite_effect_hold(self):
        self.capture['projects'][0]['effects'][0]['value_percent']=float('inf')
        with self.assertRaisesRegex(CatalogHold,'INVALID_CARD_EFFECT'):self.checked()
    def test_nonfinite_money_hold(self):
        self.capture['projects'][0]['investment']=float('nan')
        with self.assertRaisesRegex(CatalogHold,'INVALID_CARD_MONEY'):self.checked()
    def test_unknown_mode_hold(self):
        self.capture['capture_mode']='HISTORICAL_REFERENCE'
        with self.assertRaisesRegex(CatalogHold,'CURRENT_CATALOG_EVIDENCE'):self.checked()
    def test_unverified_catalog_prevents_search(self):
        # Actual runner execution: a valid *current* state, mocked R162 source,
        # and present R156/finance arguments must HOLD before calling search.
        from zoneinfo import ZoneInfo
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            state=json.loads((ROOT/'examples'/'historical_test_state.json').read_text())
            state['provenance'].update(source='CURRENT_READONLY',round='Qualification',
                source_evidence_id='observed qualification',
                captured_at_local=datetime.now(ZoneInfo('Europe/Budapest')).isoformat())
            state['market'].update(cap_source='Observed in current market',
                smartcity_total_weights={'Gazdaság':.25,'Környezet':.2,'Kormányzás':.15,
                    'Életkörülmények':.15,'Mobilitás':.1,'Emberek':.15})
            path=root/'current.json';path.write_text(json.dumps(state))
            modules={'json_integrity_r162':types.SimpleNamespace(read_json=lambda p:json.loads(Path(p).read_text()))}
            with patch.object(runner,'verify_source',return_value=root),patch.dict(sys.modules,modules):
                with self.assertRaisesRegex(Hold,'CURRENT_35_CARD_OBSERVATION_REQUIRED'):
                    runner.run(root,path,100000,4,mode='current-readonly',
                        r156_bundle=root/'dummy',year1_finance_path=root/'dummy')
    def test_invalid_sign_of_card_startup_hold(self):
        self.capture['projects'][0]['startup_cost']=-1
        with self.assertRaisesRegex(CatalogHold,'NEGATIVE_CARD_STARTUP'):self.checked()

if __name__=='__main__':unittest.main()
