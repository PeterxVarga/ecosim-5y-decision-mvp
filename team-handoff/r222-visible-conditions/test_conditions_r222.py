#!/usr/bin/env python3
"""Read-only current-source tests, originally observed source never Git tracked."""
from __future__ import annotations
import json,os,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from conditions_r222 import parse_conditions,segments,audit,SCHEMA,sha
from qualify_all_views_r220 import CASES,view_page
from catalog_gate_r192 import validate_catalog,CatalogHold
from json_integrity_r162 import read_json
from observation_bundle_r152 import compile_bundle

class CurrentDisplayedConditions(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
    cls.pages=Path(os.environ["R222_PAGES"])
    cls.r217=Path(os.environ["R222_R217"])
    cls.r220=Path(os.environ["R222_R220"])
    cls.manual=Path(os.environ["R222_RULEBOOK"])
    cls.output=Path(os.environ["R222_OUTPUT"])
    cls.proof=read_json(cls.output/"R222_RECEIPT.json")
    cls.catalog=read_json(cls.output/"R222_R192_CURRENT_CATALOG_TIME_HOLD.json")
 def test_real_all_35_conditions_explicit_and_absent_sections(self):
    ids=[]
    observed={}
    for stem,section,first,last in CASES:
        s,p=view_page(self.pages,stem,section)
        pieces=segments(s)
        self.assertEqual(set(pieces),set(range(first,last+1)))
        for pid,body in pieces.items():
            obs,kind=parse_conditions(body,pid)
            observed[pid]=obs
            ids.append(pid)
            self.assertIn(kind,("NO_CONDITION_SECTION_DISPLAYED","DISPLAYED_EXPLICIT_CONDITION"))
    self.assertEqual(sorted(ids),list(range(1,36)))
    self.assertEqual({k:v for k,v in observed.items() if v},
                     {30:["Bicikliútfejlesztés — Fut"],31:["Vasútfejlesztés — Fut"]})
    self.assertEqual(sum(not v for v in observed.values()),33)
 def test_r192_original_parser_35_card_fields_equal(self):
    from catalog_gate_r192 import _card
    original=read_json(Path(__file__).resolve().parents[2]/
        "ECOSIM_R162_INTEGRITY_REVIEW_RC/data/ecosim_projects_20261030.json")
    self.assertEqual(len(original["projects"]),35)
    for live,old in zip(self.catalog["projects"],original["projects"]):
        self.assertEqual(_card(live,"CURRENT"),_card(old,"HIST"))
 def test_actual_observation_gap_keeps_r192_hold(self):
    _,state,_=compile_bundle(self.r217/"r156_immutable/manifest.json")
    original=read_json(Path(__file__).resolve().parents[2]/
        "ECOSIM_R162_INTEGRITY_REVIEW_RC/data/ecosim_projects_20261030.json")
    with self.assertRaisesRegex(CatalogHold,"CATALOG_NOT_SAME_PERIOD_CAPTURE_WINDOW"):
        validate_catalog(self.catalog,state,original)
    self.assertGreater(self.proof["capture_span_minutes"],60)
    self.assertEqual(self.proof["r192_time_admission"],
                     "HOLD_CATALOG_NOT_SAME_PERIOD_CAPTURE_WINDOW")
 def test_no_production_admission_or_finance(self):
    self.assertEqual(self.proof["status"],
                    "PASS_35_DISPLAYED_CONDITION_FIELDS_MATCH_ORIGINAL_R192_TIME_HOLD")
    self.assertIsNone(self.proof["original_r191_market_cap"])
    self.assertIsNone(self.proof["actual_spendable_project_cash"])
    self.assertFalse(self.proof["r214_live_advisory_authorized"])
    self.assertTrue(self.proof["client_ui_absence_not_cryptographic_proof_of_server_conditions"])
    self.assertEqual(self.proof["gameplay_gate"],"STOP")
    self.assertEqual(self.proof["game_writes"],0)
 def test_sha_of_each_real_page(self):
    for stem,hash_ in self.proof["source_sha256"].items():
        if stem.startswith("projects_"):
            self.assertEqual(sha(self.pages/(stem+".txt")),hash_)
    self.assertEqual(sha(self.r220),self.proof["source_sha256"]["R220"])
    self.assertEqual(sha(self.r217/"R217_RECEIPT.json"),
                     self.proof["source_sha256"]["R217"])
 def test_missing_explicit_bubi_condition_rejected(self):
    original=segments((self.pages/"projects_transport.txt").read_text())
    c=original[30]
    self.assertIn("Projekt feltételek",c)
    fake=c.replace("Projekt feltételek\n\nBicikliútfejlesztés — Fut\n\n","",1)
    self.assertNotEqual(parse_conditions(fake,30)[0],parse_conditions(c,30)[0])
    self.assertEqual(parse_conditions(fake,30)[1],"NO_CONDITION_SECTION_DISPLAYED")
    from catalog_gate_r192 import _card
    old=next(x for x in self.catalog["projects"] if x["id"]==30)
    spoof={**old,"project_conditions":parse_conditions(fake,30)[0]}
    self.assertNotEqual(_card(spoof,"SPOOF"),_card(old,"CURRENT"))
 def test_unsupported_or_duplicate_condition_fails_closed(self):
    c=segments((self.pages/"projects_transport.txt").read_text())[31]
    with self.assertRaisesRegex(ValueError,"HOLD_UNSUPPORTED_DISPLAYED_CONDITION_GRAMMAR"):
        parse_conditions(c.replace("Vasútfejlesztés — Fut","Vasútfejlesztés — UNKNOWN"),31)
    with self.assertRaisesRegex(ValueError,"HOLD_DUPLICATE_CONDITION_SECTION"):
        parse_conditions(c.replace("Projekt feltételek\n",
                                    "Projekt feltételek\nProjekt feltételek\n",1),31)
 def test_does_not_erase_absence_of_hidden_server_conditions(self):
    self.assertEqual(self.proof["no_condition_section_displayed_cards"],33)
    self.assertTrue(self.proof["client_ui_absence_not_cryptographic_proof_of_server_conditions"])
 def test_no_overwrite_real_private_report(self):
    with self.assertRaisesRegex(ValueError,"HOLD_NEW_PRIVATE_OUTPUT"):
        audit(self.pages,self.r217,self.r220,self.manual,self.output)
if __name__=="__main__":unittest.main()
