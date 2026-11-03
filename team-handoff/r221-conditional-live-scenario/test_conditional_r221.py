#!/usr/bin/env python3
"""R221 source-linked checks using actual PRIVATE Selejtező observations.

Does not fetch/modify EcoSim and explicitly rejects promotion to live advice.
"""
from __future__ import annotations
import copy,json,os,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from conditional_r221 import (
    SCHEMA,CAPS,CASH,OBJECTIVES,RULEBOOK_SHA,sha,valid_data,_choose)
from observation_bundle_r152 import compile_bundle
from strategy_5y import search
from json_integrity_r162 import read_json

class ActualCurrentWhatIf(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r217=Path(os.environ["R221_R217"])
        cls.r220=Path(os.environ["R221_R220"])
        cls.manual=Path(os.environ["R221_RULEBOOK"])
        cls.bundle=Path(os.environ["R221_R156_BUNDLE"])
        cls.generated=Path(os.environ["R221_RECEIPT"])
    def originals(self):
        return valid_data(self.r217,self.r220,self.manual,self.bundle)
    def test_all_current_sources_linked_no_fabricated_cap(self):
        s,orig,proof=self.originals()
        self.assertEqual(orig["running_ids"],[14,22,23,24,34,35])
        self.assertEqual(proof["observed_card_count"],35)
        self.assertIsNone(s["market"]["maxProjectPerTurn"])
        self.assertEqual(s["team"]["already_selected_new_project_ids_current_period"],[])
        self.assertEqual(list(CAPS),[1,2,3])
        self.assertEqual(list(CASH),[0,25000,50000,150000])
        self.assertEqual(sha(self.manual),RULEBOOK_SHA)
    def test_actual_output_not_a_game_authorization(self):
        v=read_json(self.generated)
        self.assertEqual(v["schema"],SCHEMA)
        self.assertEqual(v["status"],"PASS_ACTUAL_SOURCE_HYPOTHETICAL_SCENARIO_SEARCH_ONLY")
        self.assertEqual(len(v["scenarios"]),24)
        self.assertFalse(v["live_advisory_authorized"])
        self.assertIsNone(v["current_max_project_starts_per_period"])
        self.assertIsNone(v["current_spendable_cash"])
        self.assertEqual(v["current_project_conditions_verified"],0)
        self.assertEqual(v["r191_live_eligibility"],"HOLD_CAP_UNKNOWN_OR_ASSUMED")
        self.assertEqual(v["r192_live_catalog"],"HOLD_UNVERIFIED_PROJECT_CONDITIONS")
        self.assertEqual(v["r214_live_finance"],"HOLD_UNKNOWN_SPENDABLE_CASH")
        self.assertEqual(v["game_writes"],0)
        self.assertEqual(v["gameplay_gate"],"STOP")
        self.assertEqual(v["source_sha256"]["r217"],sha(self.r217))
        self.assertEqual(v["source_sha256"]["r220"],sha(self.r220))
        self.assertEqual(v["source_sha256"]["official_rulebook"],sha(self.manual))
    def test_every_r160_audit_verified_under_declared_hypothesis(self):
        r=read_json(self.generated)
        allkeys=set()
        for row in r["scenarios"]:
            cap=row["hypothetical_cap"];cash=row["hypothetical_annual_budget_ecu"]
            self.assertIn(cap,CAPS);self.assertIn(cash,CASH)
            self.assertIn(row["objective"],OBJECTIVES)
            self.assertTrue(row["validated_by_original_r160"])
            self.assertFalse(row["financing_authorized"])
            self.assertFalse(row["source_history_project_conditions_current_verified"])
            self.assertEqual(row["gameplay_gate"],"STOP")
            self.assertLessEqual(len(row["initial_project_ids"]),cap)
            self.assertLessEqual(row["first_year_conservative_requirement_ecu"],cash)
            self.assertEqual(len(row["full_five_year_illustrative_starts"]),5)
            allkeys.add((cap,cash,row["objective"]))
        self.assertEqual(allkeys,{(cap,cash,obj) for cap in CAPS for cash in CASH for obj in OBJECTIVES})
    def test_zero_money_never_suggests_projects(self):
        r=read_json(self.generated)
        self.assertTrue(all(x["initial_project_ids"]==[] and
                            x["first_year_conservative_requirement_ecu"]==0
                            for x in r["scenarios"]
                            if x["hypothetical_annual_budget_ecu"]==0))
    def test_source_receipt_forged_cap_finance_or_visibility_rejected(self):
        orig=read_json(self.r220)
        with tempfile.TemporaryDirectory(prefix="r221-negative-") as td:
            for key,value in (
                ("market_project_start_cap_verified",True),
                ("spendable_project_cash_verified",True),
                ("complete_r192_definition_admitted",True),
                ("project_conditions_count_verified",35),
                ("money_parity_count",34),
                ("game_writes",1)):
                tampered=copy.deepcopy(orig);tampered[key]=value
                p=Path(td)/(key+".json")
                p.write_text(json.dumps(tampered,ensure_ascii=False))
                with self.assertRaisesRegex(ValueError,"HOLD_R220_VISIBLE_CARD_NOT_FULL_ADMISSION"):
                    valid_data(self.r217,p,self.manual,self.bundle)
    def test_wrong_manual_and_hash_link_rejected(self):
        with tempfile.TemporaryDirectory(prefix="r221-manual-") as td:
            manual=Path(td)/"not-the-official-manual.pdf"
            manual.write_bytes(b"%PDF fake hypothetical")
            with self.assertRaisesRegex(ValueError,"HOLD_OFFICIAL_RULEBOOK_CHANGED"):
                valid_data(self.r217,self.r220,manual,self.bundle)
            altered=read_json(self.r217)
            altered["observed_project_statuses"]=34
            r=Path(td)/"fakeR217.json"
            r.write_text(json.dumps(altered,ensure_ascii=False))
            with self.assertRaisesRegex(ValueError,"HOLD_R217_CURRENT_PARTIAL_SOURCE_IDENTITY"):
                valid_data(r,self.r220,self.manual,self.bundle)
    def test_original_search_audited_and_repeat_deterministic(self):
        state,_,_=self.originals()
        a=search(state,start_year=1,cap_override=2,
                 budget_override=[50000]*5,beam_width=8,shortlist=25,
                 allow_same_year=False,objective="nominal")
        b=search(state,start_year=1,cap_override=2,
                 budget_override=[50000]*5,beam_width=8,shortlist=25,
                 allow_same_year=False,objective="nominal")
        self.assertEqual(a,b)
        winner=_choose(a,2,50000,"nominal")
        self.assertEqual(winner["initial_project_ids"],[21,27])
        self.assertEqual(winner["first_year_conservative_requirement_ecu"],50000)
        self.assertFalse(winner["financing_authorized"])
    def test_false_assumption_approval_rejected(self):
        state,_,_=self.originals()
        case=search(state,start_year=1,cap_override=1,
                    budget_override=[25000]*5,beam_width=8,shortlist=25,
                    allow_same_year=False,objective="nominal")
        case["assumptions"]["annual_limit_source"]="OFFICIAL_SERVER_ATTESTED"
        with self.assertRaisesRegex(ValueError,"HOLD_EXPLICIT_NOT_OFFICIAL_CAP_AND_BUDGET"):
            _choose(case,1,25000,"nominal")
if __name__=="__main__":unittest.main()
