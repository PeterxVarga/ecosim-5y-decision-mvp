#!/usr/bin/env python3
"""R221 cross-proof against R222 current visible prerequisite text."""
import copy,os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from join_current_conditions import verify,SCHEMA
from json_integrity_r162 import read_json

class ActualDisplayedDependencyVsFiveYears(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
    cls.r221=read_json(os.environ["R222_R221"])
    cls.r222=read_json(os.environ["R222_RECEIPT"])
    cls.join=read_json(os.environ["R222_JOIN"])
 def test_24_scenario_120_year_full_source_parity(self):
    out=verify(self.r221,self.r222)
    self.assertEqual(out["schema"],SCHEMA)
    self.assertEqual(out["validated_24_scenario_count"],24)
    self.assertEqual(out["audited_virtual_year_rows"],120)
    self.assertEqual(out["current_ui_dependency_rules"],{"30":29,"31":27})
    self.assertEqual(out["scenarios_containing_dependency_starts"],{"30":2,"31":2})
    self.assertFalse(out["actual_gameplay_recommendation_authorized"])
    self.assertEqual(out["game_writes"],0)
    self.assertEqual(out["gameplay_gate"],"STOP")
 def test_generated_receipt_matches_independent_verification(self):
    r=verify(self.r221,self.r222)
    for k,v in r.items():
        if k!="r221_source_sha256":self.assertEqual(self.join[k],v)
 def test_missing_predecessor_29_blocks_bubi(self):
    doc=copy.deepcopy(self.r221)
    target=next(x for x in doc["scenarios"]
                if any(30 in y for y in x["full_five_year_illustrative_starts"]))
    for yr in target["full_five_year_illustrative_starts"]:
        if 29 in yr:yr.remove(29)
    with self.assertRaisesRegex(ValueError,"HOLD_DISPLAYED_CURRENT_PREREQUISITE_30_MISSING"):
        verify(doc,self.r222)
 def test_missing_predecessor_27_blocks_park(self):
    doc=copy.deepcopy(self.r221)
    target=next(x for x in doc["scenarios"]
                if any(31 in y for y in x["full_five_year_illustrative_starts"]))
    for yr in target["full_five_year_illustrative_starts"]:
        if 27 in yr:yr.remove(27)
    if 27 in target["initial_project_ids"]:
        target["initial_project_ids"].remove(27)
    with self.assertRaisesRegex(ValueError,"HOLD_DISPLAYED_CURRENT_PREREQUISITE_31_MISSING"):
        verify(doc,self.r222)
 def test_fake_current_condition_becomes_hold(self):
    altered=copy.deepcopy(self.r222)
    altered["observed_explicit_condition_rules"]["30"]=["NEM LÉTEZŐ ELŐFELTÉTEL — Fut"]
    with self.assertRaisesRegex(ValueError,"HOLD_ACTUAL_TWO_DISPLAYED_CONDITIONS"):
        verify(self.r221,altered)
 def test_no_live_admission_laundering(self):
    for name,value in (("live_advisory_authorized",True),("game_writes",1)):
        modified=copy.deepcopy(self.r221);modified[name]=value
        with self.assertRaisesRegex(ValueError,"HOLD_R221_IS_HYPOTHETICAL_NOT_LIVE"):
            verify(modified,self.r222)
if __name__=="__main__":unittest.main()
