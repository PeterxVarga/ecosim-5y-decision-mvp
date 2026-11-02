#!/usr/bin/env python3
"""R232 focused public-organizer rule + real existing-source E2E safety."""
from __future__ import annotations
import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from organizer_cap_r232 import CAP,SCHEMA,compute
from json_integrity_r162 import read_json

class OfficialFourCap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paths={k:Path(os.environ["R232_"+k]) for k in (
            "MANIFEST","R224","R228","R231","TRACK","OUTPUT")}
        cls.saved=read_json(cls.paths["OUTPUT"]/"R232_RECEIPT.json")
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="r232-negative-")
        self.root=Path(self.tmp.name)
    def tearDown(self):
        self.tmp.cleanup()
    def newrun(self,**changes):
        args={"manifest":self.paths["MANIFEST"],
            "r224":self.paths["R224"],"r228":self.paths["R228"],
            "r231":self.paths["R231"],"track_path":self.paths["TRACK"],
            "dest":self.root/"fresh"}
        args.update(changes)
        return compute(**args)
    def mutate(self,key,edit):
        v=copy.deepcopy(read_json(self.paths[key]))
        edit(v)
        p=self.root/(key+".json")
        p.write_text(json.dumps(v,ensure_ascii=False))
        return p
    def test_original_organizer_video_provenance_explicit(self):
        v=self.saved
        self.assertEqual(v["schema"],SCHEMA)
        self.assertEqual(v["video_evidence"]["video_id"],"3GNCkvECOdk")
        self.assertEqual(v["video_evidence"]["spoken_at_seconds"],1268)
        self.assertEqual(v["video_evidence"]["base_max_new_projects_per_virtual_year"],4)
        self.assertEqual(v["video_evidence"]["five_year_base_max_new_projects"],20)
        self.assertEqual(v["video_evidence"]["evidence_kind"],
                         "OFFICIAL_ORGANIZER_PUBLIC_VIDEO_CAPTIONS_NOT_SERVER_CONFIG")
        self.assertTrue(v["video_evidence"]["do_not_promote_to_current_R191_live_cap"])
        self.assertIsNone(v["current_game_server_project_cap"])
    def test_no_legacy_project1_extra_fifth_starts_in_any_year(self):
        v=self.saved
        self.assertEqual(v["scenario_count"],8)
        self.assertEqual(len(v["scenarios"]),8)
        self.assertEqual(sorted((s["hypothetical_annual_cash_budget_ecu_NOT_SPENDABLE"],s["objective"])
                                for s in v["scenarios"]),sorted((c,o) for c in
                                  [0,168621,337243,674486] for o in
                                  ["nominal","scenario_min"]))
        for s in v["scenarios"]:
            self.assertEqual(s["annual_project_cap_organizer_announced"],CAP)
            self.assertEqual(len(s["yearly_project_starts"]),5)
            self.assertTrue(all(0<=c<=CAP for c in s["annual_start_counts"]))
            self.assertEqual(s["total_five_year_project_starts"],
                             sum(s["annual_start_counts"]))
            self.assertLessEqual(s["total_five_year_project_starts"],20)
            self.assertEqual(s["p1_project_ids"],s["yearly_project_starts"][0])
            self.assertTrue(s["project_1_client_extra_slot_not_used"])
            self.assertEqual(s["policy_unknown_cash_each_year"],[23]*5)
            self.assertEqual(s["policy_unknown_factor_each_year"],[23]*5)
            self.assertFalse(s["source_rule_eligibility_independently_server_verified"])
            self.assertIsNone(s["actual_game_winning_strategy"])
            self.assertEqual(s["gameplay_gate"],"STOP")
    def test_eight_r160_audits_no_game_authority(self):
        v=self.saved
        self.assertEqual(v["gameplay_gate"],"STOP")
        self.assertEqual(v["game_writes"],0)
        self.assertIsNone(v["actual_permitted_game_decision"])
        self.assertIsNone(v["official_five_year_score"])
        self.assertIsNone(v["actual_spendable_ecu"])
        self.assertEqual(v["original_R191_current_admission"],
                         "HOLD_CAP_UNKNOWN_OR_ASSUMED")
        self.assertEqual(v["original_R192_catalog_time_admission"],
                         "HOLD_CATALOG_NOT_SAME_PERIOD_CAPTURE_WINDOW")
    def test_source_sha_chain_exact(self):
        import hashlib
        for k,v in (("R156_manifest","MANIFEST"),("R224","R224"),("R228","R228"),
                    ("R231","R231"),("R145_policy_track","TRACK")):
            self.assertEqual(self.saved["source_sha256"][k],
                             hashlib.sha256(self.paths[v].read_bytes()).hexdigest())
    def test_forged_old_finance_cap_does_not_pass(self):
        f=self.mutate("R224",lambda v:v.update(current_R191_real_cap=4))
        with self.assertRaisesRegex(ValueError,"HOLD_ORIGINAL_R224_R229_R231_SHA_CHAIN"):
            self.newrun(r224=f)
    def test_forged_latest_r231_finance_pass_does_not_pass(self):
        f=self.mutate("R231",lambda v:v.update(original_R191_current_state_admission="PASS"))
        with self.assertRaisesRegex(ValueError,"HOLD_R231_ORIGINAL_LIVE_ADMISSION_STILL_HOLD"):
            self.newrun(r231=f)
    def test_r232_output_not_overwritten(self):
        with self.assertRaisesRegex(ValueError,"HOLD_NEW_PRIVATE_DIRECTORY"):
            compute(self.paths["MANIFEST"],self.paths["R224"],self.paths["R228"],
                    self.paths["R231"],self.paths["TRACK"],self.paths["OUTPUT"])

if __name__=="__main__":unittest.main()
