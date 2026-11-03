#!/usr/bin/env python3
"""R211 public-safe tests. The original R209 policies are SYNTHETIC_TEST_ONLY."""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from finance_stress_r211 import STRESSES,build,model_receipts,verify_join,rank_options
sys.path.insert(0,str(HERE.parents[1]/"r207-first-round"))
from test_r209_policy_finance_reuse import exercise

class R211Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src=exercise(include_joined=True)
        cls.tmp=tempfile.TemporaryDirectory()
        cls.base=Path(cls.tmp.name)
        cls.private=cls.base/"fictional-previous-library";cls.private.mkdir()
        cls.rows={"income.csv":49,"loans.csv":7,"rules.csv":5,
                  "observations.csv":24,"source_index.csv":15}
        cls.source_files={}
        for name,count in cls.rows.items():
            p=cls.private/name;p.write_text("SYNTHETIC_R211_FAKE_FILE\n",encoding="utf-8")
            cls.source_files[name]={"normalized_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"rows":count}
        cls.r205={"schema":"ECOSIM_R205_HISTORICAL_LIBRARY_SOURCE_RECONCILIATION_V1",
                  "status":"PASS_PREVIOUSLY_UPLOADED_EVIDENCE_RECONCILED_LIVE_HOLD",
                  "mode":"historical-test","gameplay_gate":"STOP","game_writes":0,
                  "source_files":cls.source_files,
                  "observed_long_term_loan_interest_pct":7.5,
                  "observed_short_term_loan_interest_pct":12.,
                  "observed_finance_terms":{"loan_ceiling":"UNKNOWN","settlement_timing":"UNKNOWN"},
                  "observed_development_grants":{
                    "actually_spendable":"UNVERIFIED","timing":"UNKNOWN",
                    "state_p0_raw":140000.,"company_p0_raw":60000.}}
        cls.r205_path=cls.base/"r205.json"
        cls.r205_path.write_text(json.dumps(cls.r205)+"\n")
        cls.r206={"schema":"ECOSIM_R206_REUSED_SEARCH_HISTORICAL_CANDIDATES_V1",
                  "status":"PASS_HISTORICAL_BOUNDED_SEARCH_LIVE_HOLD",
                  "mode":"historical-test","gameplay_gate":"STOP","game_writes":0,
                  "verified_spendable_cash":False,"verified_city_transition":False,
                  "source_sha256":{"r205_reconciliation":hashlib.sha256(cls.r205_path.read_bytes()).hexdigest()}}
    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()
    def joined(self):return copy.deepcopy(self.src["joined"])
    def good(self,r205=None,r206=None,joined=None):
        return build(self.src["receipt"],joined if joined is not None else self.src["joined"],
                     self.src["candidates"],r205 if r205 is not None else self.r205,
                     r206 if r206 is not None else self.r206,self.r205_path,self.private)
    def rejects(self,fn,message):
        with self.assertRaisesRegex(ValueError,"HOLD_"+message):fn()
    def test_full_108_case_validation(self):
        r=self.good()
        self.assertEqual(r["combination_count"],36)
        self.assertEqual(r["incremental_stress_case_count"],108)
        self.assertEqual(len(r["three_budget_tier_diagnostics"]),3)
        self.assertTrue(all(v["not_a_real_funding_gap"] for v in r["plans"]))
        self.assertIsNone(r["actual_city_cash_balance"])
        self.assertEqual(r["cross_model_r205_r206_provenance"]["cash_recognized_from_loans_or_grants_ecu"],0)
        self.assertEqual(r["gameplay_gate"],"STOP")
        self.assertEqual(r["game_writes"],0)
    def test_mutated_source_sha_blocked(self):
        r=copy.deepcopy(self.r205)
        r["source_files"]["loans.csv"]["normalized_sha256"]="0"*64
        self.rejects(lambda:self.good(r205=r),"PRIVATE_SOURCE_HASH_loans.csv")
    def test_false_grant_cash_claim_rejected(self):
        r=copy.deepcopy(self.r205)
        r["observed_development_grants"]["actually_spendable"]="YES"
        self.rejects(lambda:self.good(r205=r),"GRANTS_UNCERTAINTY_GATE")
    def test_fake_loan_limit_rejected(self):
        r=copy.deepcopy(self.r205)
        r["observed_finance_terms"]["loan_ceiling"]=1000000
        self.rejects(lambda:self.good(r205=r),"LOAN_UNCERTAINTY_GATE")
    def test_r206_wrong_lineage_blocked(self):
        r=copy.deepcopy(self.r206)
        r["source_sha256"]["r205_reconciliation"]="0"*64
        self.rejects(lambda:self.good(r206=r),"R206_R205_IDENTITY")
    def test_missing_policy_pair_blocked(self):
        j=self.joined();j["combinations"].pop()
        self.rejects(lambda:self.good(joined=j),"EXACT_12x3_COVERAGE")
    def test_mutated_annual_card_cost_blocked(self):
        j=self.joined();j["combinations"][0]["annual_rows"][0]["project_card_need_ecu"]+=1
        self.rejects(lambda:self.good(joined=j),"ACCOUNTING_CARD_COST")
    def test_mutated_instant_receipt_blocked(self):
        j=self.joined();j["combinations"][0]["annual_rows"][0]["four_tax_delta_ecu"]+=1
        self.rejects(lambda:self.good(joined=j),"ACCOUNTING_ANNUAL_NET")
    def test_mutated_deferred_income_blocked(self):
        j=self.joined();j["combinations"][0]["annual_rows"][0]["new_positive_tax_and_fee_deltas_deferred_ecu"]+=5
        self.rejects(lambda:self.good(joined=j),"ACCOUNTING_ANNUAL_DEFERRED_NET")
    def test_mismatched_annual_project_ids_blocked(self):
        j=self.joined();j["combinations"][0]["annual_rows"][0]["projects_started_ids"]=[35]
        self.rejects(lambda:self.good(joined=j),"YEAR_PROJECT_IDENTITY")
    def test_live_or_current_claim_blocked(self):
        r=copy.deepcopy(self.r205);r["mode"]="current-readonly"
        self.rejects(lambda:self.good(r205=r),"R205_HISTORICAL_GATE")
    def test_stress_is_monotone_for_nonnegative_extras(self):
        r=self.good()
        for c in r["cases"]:
            ordered=[v["sampled_incremental_buffer_against_unknown_reference_path_deferred_ecu"] for v in c["stress_cases"]]
            self.assertEqual(ordered,sorted(ordered))
            self.assertTrue(all(x["actual_available_cash"] is None for x in c["stress_cases"]))

if __name__=="__main__":unittest.main()
