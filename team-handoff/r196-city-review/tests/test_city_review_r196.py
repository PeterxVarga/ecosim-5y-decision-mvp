import sys
import unittest
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from city_review_r196 import (review, CityHold, TABS, REQUIRED_TOPICS, SCHEMA,
                              validate_result, render_hu, read_json)

HASH = 'a'*64
H2 = 'b'*64
NOW=datetime(2026,11,2,12,5,tzinfo=timezone.utc)

def tradeoff(mode='historical-test'):
    return {'schema':'ECOSIM_R195_TWO_ENVELOPE_TRADEOFF_V1',
            'gameplay_gate':'STOP','financing_approved':False,'live_outcome_predicted':False,
            'mode':mode,'input_state_sha256':HASH,'catalog_sha256':H2,
            'max_model_score':.451,'reserve_model_score':.432,
            'annual_comparison':[{'year':i} for i in range(1,6)]}

def evidence(mode='current-readonly', complete=True):
    return {'schema':'ECOSIM_R196_OPERATOR_CITY_VIEWS_V1','mode':mode,
            'tradeoff_sha256':HASH,'input_state_sha256':HASH,'catalog_sha256':H2,
            'tabs':{k: {'status':'OPERATOR_OBSERVED','source_view':'https://edu.ecosim.hu/simulation/'+k,
                        'source_evidence_id':'review-'+k,
                        'captured_at_local':'2026-11-02T12:00:00+00:00',
                        'observed_topics':list(REQUIRED_TOPICS[k])} if complete
                    else {'status':'MISSING'} for k in TABS}}

class CityReviewTests(unittest.TestCase):
    def assertHold(self, fn):
        with self.assertRaises(CityHold): fn()

    def test_historical_without_tab_evidence_passes_analysis_not_live(self):
        r=review(tradeoff(), HASH, now=NOW)
        self.assertEqual(r['status'],'HISTORICAL_PROJECT_MODEL_ONLY')
        self.assertEqual(len(r['views']),10)
        self.assertEqual(len(r['missing_or_partial_views']),10)
        self.assertIs(r['actual_citywide_optimized'],False)
        self.assertEqual(r['gameplay_gate'],'STOP')

    def test_current_without_tabs_fail_closed(self):
        r=review(tradeoff('current-readonly'),HASH,now=NOW)
        self.assertEqual(r['status'],'HOLD_INCOMPLETE_CITY_COVERAGE')

    def test_full_current_operator_evidence_still_not_citywide_approved(self):
        r=review(tradeoff('current-readonly'),HASH,evidence(),now=NOW)
        self.assertEqual(r['status'],'HOLD_CITY_EFFECTS_NOT_JOINTLY_VALIDATED')
        self.assertEqual(r['complete_operator_observed_views'],10)
        self.assertIs(r['financing_approved'],False)

    def test_partial_current_fails_completeness(self):
        v=evidence();v['tabs']['loans']['observed_topics']=[]
        r=review(tradeoff('current-readonly'),HASH,v,now=NOW)
        self.assertIn('loans',r['missing_or_partial_views'])
        self.assertEqual(r['status'],'HOLD_INCOMPLETE_CITY_COVERAGE')

    def test_missing_source_fails(self):
        v=evidence();del v['tabs']['income']['source_evidence_id']
        self.assertHold(lambda:review(tradeoff('current-readonly'),HASH,v,now=NOW))

    def test_stale_current_fails(self):
        v=evidence();v['tabs']['income']['captured_at_local']='2026-10-30T12:00:00+00:00'
        self.assertHold(lambda:review(tradeoff('current-readonly'),HASH,v,now=NOW))

    def test_future_current_fails(self):
        v=evidence();v['tabs']['income']['captured_at_local']='2026-11-02T12:30:00+00:00'
        self.assertHold(lambda:review(tradeoff('current-readonly'),HASH,v,now=NOW))

    def test_wrong_result_hash_fails(self):
        v=evidence();v['tradeoff_sha256']='0'*64
        self.assertHold(lambda:review(tradeoff('current-readonly'),HASH,v,now=NOW))

    def test_wrong_state_hash_fails(self):
        v=evidence();v['input_state_sha256']='0'*64
        self.assertHold(lambda:review(tradeoff('current-readonly'),HASH,v,now=NOW))

    def test_wrong_catalog_hash_fails(self):
        v=evidence();v['catalog_sha256']='0'*64
        self.assertHold(lambda:review(tradeoff('current-readonly'),HASH,v,now=NOW))

    def test_wrong_mode_fails(self):
        self.assertHold(lambda:review(tradeoff('historical-test'),HASH,evidence(),now=NOW))

    def test_extra_view_fails(self):
        v=evidence();v['tabs']['other']={'status':'MISSING'}
        self.assertHold(lambda:review(tradeoff('current-readonly'),HASH,v,now=NOW))

    def test_not_exact_topic_fails(self):
        v=evidence();v['tabs']['finance']['observed_topics'].append('guess_free_money')
        self.assertHold(lambda:review(tradeoff('current-readonly'),HASH,v,now=NOW))

    def test_missing_view_with_fake_source_fails(self):
        v=evidence();v['tabs']['finance']={'status':'MISSING','source_evidence_id':'forged'}
        self.assertHold(lambda:review(tradeoff('current-readonly'),HASH,v,now=NOW))

    def test_bad_source_url_fails(self):
        v=evidence();v['tabs']['finance']['source_view']='https://evil.test/'
        self.assertHold(lambda:review(tradeoff('current-readonly'),HASH,v,now=NOW))

    def test_simulation_prefix_spoof_fails(self):
        v=evidence();v['tabs']['finance']['source_view']='https://edu.ecosim.hu/simulation/finance.evil.test'
        self.assertHold(lambda:review(tradeoff('current-readonly'),HASH,v,now=NOW))

    def test_url_query_token_fails(self):
        v=evidence();v['tabs']['income']['source_view']='https://edu.ecosim.hu/simulation/income?token=secret'
        self.assertHold(lambda:review(tradeoff('current-readonly'),HASH,v,now=NOW))

    def test_unsafe_result_fails(self):
        r=tradeoff();r['gameplay_gate']='GO'
        self.assertHold(lambda:review(r,HASH,now=NOW))

    def test_forged_finance_approval_fails(self):
        r=tradeoff();r['financing_approved']=True
        self.assertHold(lambda:review(r,HASH,now=NOW))

    def test_forged_prediction_approval_fails(self):
        r=tradeoff();r['live_outcome_predicted']=True
        self.assertHold(lambda:review(r,HASH,now=NOW))

    def test_nonfinite_result_fails(self):
        r=tradeoff();r['max_model_score']=float('inf')
        self.assertHold(lambda:review(r,HASH,now=NOW))

    def test_hungarian_report_is_explicit(self):
        r=review(tradeoff(),HASH,now=NOW)
        txt=render_hu(r)
        self.assertIn('R153–R155',txt)
        self.assertIn('Hitelek',txt)
        self.assertIn('GAME_ACTION_GATE=STOP',txt)
        self.assertIn('10',txt)

    def test_json_duplicate_keys_fails(self):
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'bad.json';p.write_text('{"a":1,"a":2}',encoding='utf-8')
            self.assertHold(lambda:read_json(p))

    def test_json_overflow_fails(self):
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'bad.json';p.write_text('{"a":1e999}',encoding='utf-8')
            self.assertHold(lambda:read_json(p))

    def test_json_nan_fails(self):
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'bad.json';p.write_text('{"a":NaN}',encoding='utf-8')
            self.assertHold(lambda:read_json(p))

    def test_current_data_does_not_modify_input(self):
        v=evidence(); before=json.dumps(v,sort_keys=True)
        review(tradeoff('current-readonly'),HASH,v,now=NOW)
        self.assertEqual(json.dumps(v,sort_keys=True),before)

if __name__=='__main__':unittest.main()
