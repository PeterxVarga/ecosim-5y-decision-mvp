#!/usr/bin/env python3
"""Focused source identity, actual-R191 HOLD, and non-promotion regressions."""
from __future__ import annotations
import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from readiness_r230 import build,SCHEMA
from json_integrity_r162 import read_json

class R230RealSourceGates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r228=Path(os.environ["R230_R228"])
        cls.r224=Path(os.environ["R230_R224"])
        cls.r222=Path(os.environ["R230_R222"])
        cls.manifest=Path(os.environ["R230_MANIFEST"])
        cls.output=Path(os.environ["R230_RESULT"])
        cls.result=read_json(cls.output/"R230_READINESS_PRIVATE.json")
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="r230-source-guard-")
        self.base=Path(self.tmp.name)
    def tearDown(self):
        self.tmp.cleanup()
    def mutate(self,source,change,name):
        obj=copy.deepcopy(read_json(source));change(obj)
        new=self.base/name;new.write_text(json.dumps(obj,ensure_ascii=False),encoding="utf8")
        return new
    def run_candidate(self,**overrides):
        args=dict(r228_path=self.r228,r224_path=self.r224,r222_path=self.r222,
                  manifest_path=self.manifest,output=self.base/"new")
        args.update(overrides)
        return build(**args)
    def test_fresh_source_receipt_keeps_original_r191_r192_gates_closed(self):
        r=self.result
        self.assertEqual(r["schema"],SCHEMA)
        self.assertEqual(r["status"],"PASS_SOURCE_GATED_THRESHOLDS_HOLD_ACTUAL_ELIGIBILITY")
        self.assertEqual(r["original_R191_current_state_admission"],"HOLD_CAP_UNKNOWN_OR_ASSUMED")
        self.assertEqual(r["original_R192_catalog_admission"],"HOLD_CATALOG_NOT_SAME_PERIOD_CAPTURE_WINDOW")
        self.assertIsNone(r["actual_eligible_first_year_actions"])
        self.assertIsNone(r["actual_market_project_start_cap"])
        self.assertIsNone(r["actual_spendable_cash_ecu"])
        self.assertIsNone(r["actual_winning_five_year_plan"])
        self.assertEqual(r["game_writes"],0)
        self.assertFalse(r["merge_authorized"])
        self.assertFalse(r["deploy_authorized"])
    def test_all_24_scenarios_accounted_once_in_13_groups(self):
        g=self.result["candidate_thresholds"]
        self.assertEqual(self.result["observed_24_scenarios"],24)
        self.assertEqual(self.result["distinct_sampled_first_year_variants"],13)
        self.assertEqual(sum(x["conditional_model_scenario_count"] for x in g),24)
        self.assertEqual(len({tuple(x["first_year_project_ids"]) for x in g}),13)
        self.assertTrue(all(x["starts_requested"]==len(x["first_year_project_ids"])
              and x["actual_eligibility"] is None
              and x["actual_residual_cash_ecu"] is None
              and x["scenario_budgets_are_hypothetical"] is True for x in g))
        self.assertEqual([x["source_R224_conservative_card_cost_ecu_NOT_SPENDABLE"]
                for x in g if x["first_year_project_ids"]==[19,33]],[483000])
    def test_input_sha_chain_matches_original_source_files(self):
        from source_join_r228 import digest
        for k,p in (("R228",self.r228),("R224",self.r224),
                    ("R222",self.r222),("R156_manifest",self.manifest)):
            self.assertEqual(self.result["source_sha256"][k],digest(p))
    def test_changed_r224_scenario_cost_fails_source_hash(self):
        f=self.mutate(self.r224,lambda r:r["scenarios"][2].update(
            first_year_conservative_requirement_ecu=0),"bad224.json")
        with self.assertRaisesRegex(ValueError,"HOLD_R229_SHA_LINK_TO_ORIGINAL_SOURCES"):
            self.run_candidate(r224_path=f)
    def test_r228_false_approval_or_score_fails_closed(self):
        f=self.mutate(self.r228,lambda r:r.update(actual_five_year_winning_plan=[13]),"bad228.json")
        with self.assertRaisesRegex(ValueError,"HOLD_R228_STRICT_SOURCE_NOT_LIVE"):
            self.run_candidate(r228_path=f)
    def test_r222_source_time_falsification_fails_closed(self):
        f=self.mutate(self.r222,lambda r:r.update(
            r192_time_admission="PASS_SERVER_APPROVED"),"bad222.json")
        with self.assertRaisesRegex(ValueError,"HOLD_R222_SOURCE_OBSERVATION_HOLD"):
            self.run_candidate(r222_path=f)
    def test_changed_r228_candidate_not_matching_r224_fails_closed(self):
        def edit(r):
            r["conditional_joint_scenarios"][2]["first_year_project_ids"]=[1]
        f=self.mutate(self.r228,edit,"bad228.json")
        with self.assertRaisesRegex(ValueError,"HOLD_SOURCE_PAIR_OR_COST_DRIFT"):
            self.run_candidate(r228_path=f)
    def test_existing_output_is_never_overwritten(self):
        with self.assertRaisesRegex(ValueError,"HOLD_NEW_PRIVATE_OUTPUT"):
            build(self.r228,self.r224,self.r222,self.manifest,self.output)
    def test_recompute_preserves_existing_bytes(self):
        result=self.run_candidate()
        new=read_json(self.base/"new/R230_READINESS_PRIVATE.json")
        self.assertEqual(result,new)
        self.assertEqual(new,self.result)
        self.assertEqual((self.base/"new/R230_HU.md").read_bytes(),
                         (self.output/"R230_HU.md").read_bytes())


    def test_r231_official_rulebook_auto_debt_not_an_actual_credit_offer(self):
        obj=read_json(Path(os.environ["R231_RESULT"])/"R230_READINESS_PRIVATE.json")
        policy=obj["source_backed_financing_semantics_R231"]
        self.assertEqual(policy["source"],"R224_SHA_PINNED_OFFICIAL_HU_RULEBOOK")
        self.assertTrue(policy["game_can_auto_borrow_to_balance_shortfall"])
        self.assertFalse(policy["cash_shortfall_alone_proves_start_forbidden"])
        self.assertTrue(policy["conservative_R191_cash_gate_is_not_equivalent_to_game_start_legality"])
        self.assertIsNone(policy["game_project_start_cap_numeric_value"])
        self.assertIsNone(policy["automatic_borrowing_interest_rate"])
        self.assertIsNone(policy["automatic_borrowing_exact_amount"])
        self.assertFalse(policy["full_financing_and_server_decision_verified"])
        self.assertIsNone(obj["actual_eligible_first_year_actions"])
        self.assertEqual(obj["game_writes"],0)
    def test_r231_cash_stress_only_not_loan_forecast(self):
        obj=read_json(Path(os.environ["R231_RESULT"])/"R230_READINESS_PRIVATE.json")
        groups=obj["candidate_thresholds"]
        self.assertEqual(len(groups),13)
        for x in groups:
            self.assertTrue(x["cash_stress_is_hypothetical_only"])
            scenario=x["cash_shortfalls_given_illustrative_balances_ecu"]
            self.assertEqual([v["illustrative_cash_ecu"] for v in scenario],
                             [0,168621,337243,674486])
            cost=x["source_R224_conservative_card_cost_ecu_NOT_SPENDABLE"]
            for v in scenario:
                self.assertEqual(v["unfunded_card_cost_only_ecu"],
                                 max(0,cost-v["illustrative_cash_ecu"]))
                self.assertIsNone(v["actual_automatic_loan_required_ecu"])
            self.assertIsNone(x["game_start_legality_given_cash_shortfall"])
            self.assertIsNone(x["auto_loan_interest_and_score_cost"])
    def test_r231_forged_handbook_is_rejected(self):
        pdf=Path(os.environ["R231_RULEBOOK"])
        txt=Path(os.environ["R231_RULEBOOK_TEXT"])
        copy_pdf=self.base/"manual.pdf";copy_pdf.write_bytes(pdf.read_bytes()+b"x")
        with self.assertRaisesRegex(ValueError,"HOLD_R231_OFFICIAL_HANDBOOK_SOURCE_HASH"):
            self.run_candidate(rulebook_path=copy_pdf,rulebook_text_path=txt)
        copy_txt=self.base/"manual.txt";copy_txt.write_text(txt.read_text()+" Forgery")
        with self.assertRaisesRegex(ValueError,"HOLD_R231_OFFICIAL_HANDBOOK_SOURCE_HASH"):
            self.run_candidate(rulebook_path=pdf,rulebook_text_path=copy_txt)
    def test_r231_repeat_is_byte_identical_and_preserves_old_r230(self):
        result=self.run_candidate(rulebook_path=Path(os.environ["R231_RULEBOOK"]),
                                  rulebook_text_path=Path(os.environ["R231_RULEBOOK_TEXT"]))
        fresh=read_json(self.base/"new/R230_READINESS_PRIVATE.json")
        saved=read_json(Path(os.environ["R231_RESULT"])/"R230_READINESS_PRIVATE.json")
        self.assertEqual(result,fresh)
        self.assertEqual(fresh,saved)
        self.assertEqual((self.base/"new/R230_HU.md").read_bytes(),
                         (Path(os.environ["R231_RESULT"])/"R230_HU.md").read_bytes())
        self.assertNotIn("source_backed_financing_semantics_R231",self.result)

if __name__=="__main__":
    unittest.main()
