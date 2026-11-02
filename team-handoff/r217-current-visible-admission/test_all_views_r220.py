#!/usr/bin/env python3
"""R220 native source-driven E2E with private logged-in visible page captures.

Never edits EcoSim, executes UI actions, or checks credentials into Git.
"""
import json,os,shutil,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from qualify_all_views_r220 import verify,view_page,CASES,SCHEMA
from prepare_visible_r217 import parse_project_cards,R162
from json_integrity_r162 import read_json

class FourCategoryProof(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.private=Path(os.environ["R220_PRIVATE_PAGES"])
        cls.r217=Path(os.environ["R220_R217_DIR"])
        cls.history=read_json(R162/"data/ecosim_projects_20261030.json")
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="r220-negative-case-")
        self.local=Path(self.temp.name)
        self.pages=self.local/"pages"
        self.pages.mkdir()
        for f in self.private.glob("*.txt"):
            shutil.copyfile(f,self.pages/f.name)
    def tearDown(self):self.temp.cleanup()
    def run_one(self,name="result"):
        return verify(self.pages,self.r217,self.local/name)
    def test_full_35_source_linked(self):
        out=self.run_one()
        self.assertEqual(out["schema"],SCHEMA)
        self.assertEqual(out["observed_card_count"],35)
        self.assertEqual(out["money_parity_count"],35)
        self.assertEqual(out["effect_parity_count"],35)
        self.assertEqual(out["running_ids"],[14,22,23,24,34,35])
        self.assertEqual(out["selected_new_project_ids"],[])
        self.assertEqual(out["unobserved_visible_card_ids"],[])
        self.assertEqual(out["project_conditions_count_verified"],0)
        self.assertFalse(out["complete_r192_definition_admitted"])
        self.assertFalse(out["market_project_start_cap_verified"])
        self.assertFalse(out["spendable_project_cash_verified"])
        self.assertFalse(out["r214_three_option_advice_authorized"])
        self.assertEqual(out["game_writes"],0)
    def test_source_parity_all_four_categories(self):
        self.assertEqual([v[2:] for v in CASES],[(1,14),(15,24),(25,31),(32,35)])
        for key,cat,a,b in CASES:
            with self.subTest(cat=cat):
                content,_=view_page(self.pages,key,cat)
                cards=parse_project_cards(content,self.history,expected_ids=range(a,b+1))
                self.assertEqual(cards["count"],b-a+1)
                self.assertEqual(cards["money_identical_to_historical_count"],b-a+1)
                self.assertEqual(cards["effects_identical_to_historical_count"],b-a+1)
    def test_invalid_category_name_fails_closed(self):
        p=self.pages/"projects_environment.txt"
        p.write_text(p.read_text().replace("# VIEW=Környezet","# VIEW=Sport és Kultúra",1))
        with self.assertRaisesRegex(ValueError,"HOLD_CATEGORY_PROVENANCE"):
            self.run_one()
    def test_hidden_card_in_environment_fails_closed(self):
        p=self.pages/"projects_environment.txt"
        p.write_text(p.read_text().replace("35 - Richter Központ – Új vállalati székház",
                                          "35 - HIDDEN NEW CARD",1))
        with self.assertRaisesRegex(ValueError,"HOLD_CARD_NAME_DRIFT"):
            self.run_one()
    def test_fake_state_change_fails_closed(self):
        p=self.pages/"projects_environment.txt"
        old=p.read_text()
        self.assertIn("34 - Robert Bosch campus bővítés",old)
        body=old.split("34 - Robert Bosch campus bővítés",1)
        before,after=body[0],body[1]
        self.assertIn("<button>Fut</button>",after)
        p.write_text(before+"34 - Robert Bosch campus bővítés"+
                     after.replace("<button>Fut</button>",'<button title="Start">Start</button>',1))
        with self.assertRaisesRegex(ValueError,"HOLD_SUMMARY_STATUS_DRIFT_34"):
            self.run_one()
    def test_missing_transport_view_fails_closed(self):
        (self.pages/"projects_transport.txt").unlink()
        with self.assertRaisesRegex(ValueError,"HOLD_MISSING_PRIVATE_PAGE"):
            self.run_one()
    def test_duplicate_output_rejected_without_overwrite(self):
        self.run_one()
        with self.assertRaisesRegex(ValueError,"HOLD_NEW_PRIVATE_OUTPUT_REQUIRED"):
            self.run_one()
    def test_binary_determinism_on_same_private_sources(self):
        self.run_one("first")
        self.run_one("second")
        for filename in ("R220_RECEIPT.json","R220_HU.md"):
            self.assertEqual((self.local/"first"/filename).read_bytes(),
                             (self.local/"second"/filename).read_bytes())
if __name__=="__main__":unittest.main()
