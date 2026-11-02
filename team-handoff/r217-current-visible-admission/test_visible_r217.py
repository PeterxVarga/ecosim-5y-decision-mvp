#!/usr/bin/env python3
"""R217 private native verification. No EcoSim writes, page contents not Git tracked."""
import copy,json,os,sys,unittest
from datetime import datetime
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from prepare_visible_r217 import (
  R162,readpage,parse_summary,parse_finance,parse_project_cards,
  number,rows,sha,build)
from json_integrity_r162 import read_json
from admission_r191 import AdmissionHold,validate_state
from observation_bundle_r152 import compile_bundle

ROOT=Path(__file__).resolve().parents[2]
class LiveVisibleR217Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.private=Path(os.environ["R217_PRIVATE_PAGES"])
        cls.output=Path(os.environ["R217_PRIVATE_RECEIPT"])
        cls.org=read_json(R162/"data/ecosim_projects_20261030.json")
        cls.pages={name:readpage(cls.private,name)[0] for name in
            ("summary","finance","loans","projects_economy","income")}
    def test_35_statuses_and_p1_index(self):
        s=parse_summary(self.pages["summary"],self.org)
        self.assertEqual(s["observed_running_project_ids"],[14,22,23,24,34,35])
        self.assertEqual(s["observed_new_selected_ids"],[])
        self.assertEqual(s["observed_index_p0"],51.96)
        self.assertEqual(s["observed_index_p1_plan"],52.48)
        self.assertEqual(len(s["factors_csv"].splitlines()),31)
        self.assertEqual(len(s["projects_csv"].splitlines()),36)
        self.assertFalse(s["index_is_approved_official_result"])
    def test_finance_non_spendable_and_real_p1(self):
        f=parse_finance(self.pages["finance"],self.pages["loans"])
        self.assertEqual(f["observed_p0_and_p1"]["net_earnings"],(962785.,1051111.))
        self.assertEqual(f["observed_p0_and_p1"]["prior_year_cash"],(184600.,184600.))
        self.assertEqual(f["observed_p0_and_p1"]["project_line"],(0.,0.))
        self.assertEqual(f["long_loan_interest_p0_p1"],(7.5,7.5))
        self.assertIsNone(f["observed_spendable_project_cash_ecu"])
        self.assertFalse(f["p1_reserve_is_verified_spendable"])
    def test_fourteen_cards_visible_and_exact_partial_parity(self):
        cards=parse_project_cards(self.pages["projects_economy"],self.org)
        self.assertEqual(cards["count"],14)
        self.assertEqual(cards["money_identical_to_historical_count"],14)
        self.assertEqual(cards["effects_identical_to_historical_count"],14)
        self.assertEqual(cards["remaining_categories_unobserved"],21)
        self.assertFalse(cards["full_current_catalog_ready"])
        self.assertTrue(all(not c["project_conditions_observed"] for c in cards["captured_cards"]))
    def test_sport_culture_cards_source_and_status(self):
        source=self.private/"projects_sport.txt"
        self.assertTrue(source.exists())
        text=source.read_text(encoding="utf-8")
        self.assertIn("# SOURCE_URL=https://edu.ecosim.hu/simulation/projects",text[:250])
        self.assertIn("# VIEW=Sport és Kultúra",text[:350])
        self.assertIn("Periódus: 1/5",text)
        cards=parse_project_cards(text,self.org,expected_ids=range(15,25))
        self.assertEqual(cards["count"],10)
        self.assertEqual(cards["money_identical_to_historical_count"],10)
        self.assertEqual(cards["effects_identical_to_historical_count"],10)
        self.assertFalse(cards["full_current_catalog_ready"])
        self.assertEqual([c["id"] for c in cards["captured_cards"]
                          if c["displayed_status"]=="Fut"],[22,23,24])
        self.assertTrue(all(not c["project_conditions_observed"]
                            for c in cards["captured_cards"]))
    def test_sport_missing_id_fails_closed(self):
        source=(self.private/"projects_sport.txt").read_text(encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"HOLD_EXPECTED_CURRENT_CATEGORY_CARD_IDS"):
            parse_project_cards(source.split("24 - Velodrom")[0],
                                self.org,expected_ids=range(15,25))

    def test_missing_summary_project_must_block(self):
        t=self.pages["summary"].replace("<td>Új ügyfélközpont</td>","<td>WRONG_SOURCE_PROJECT</td>",1)
        with self.assertRaisesRegex(ValueError,"HOLD_HISTORICAL_CARD_NAME_ID_DRIFT"):
            parse_summary(t,self.org)
    def test_shortened_catalog_does_not_auto_fill_from_historical(self):
        with self.assertRaisesRegex(ValueError,"HOLD_FIRST_FOURTEEN_ECONOMY_CARDS"):
            parse_project_cards(self.pages["projects_economy"].split("14 - Új ügyfélközpont")[0],self.org)
    def test_private_source_provenance_required(self):
        wrong=self.pages["finance"].replace("# SOURCE_URL=https://edu.ecosim.hu/simulation/finance",
                                           "# SOURCE_URL=https://other.example/finance",1)
        import tempfile
        with tempfile.TemporaryDirectory(prefix="r217-provenance-") as td:
            (Path(td)/"finance.txt").write_text(wrong)
            with self.assertRaisesRegex(ValueError,"HOLD_PAGE_PROVENANCE_finance"):
                readpage(td,"finance")
    def test_partial_original_r156_bundle_and_cap_hold(self):
        r=read_json(self.output/"R217_RECEIPT.json")
        self.assertEqual(r["status"],"PASS_PARTIAL_CURRENT_R156_BUNDLE_R191_HOLD_CAP_AND_FINANCE")
        self.assertEqual(r["observed_project_statuses"],35)
        self.assertEqual(r["running_ids"],[14,22,23,24,34,35])
        self.assertEqual(r["r191_current_qualification"],"HOLD_CAP_UNKNOWN_OR_ASSUMED")
        _,state,_=compile_bundle(self.output/"r156_immutable/manifest.json")
        self.assertEqual(state["market"]["maxProjectPerTurn"],None)
        with self.assertRaisesRegex(AdmissionHold,"CAP_UNKNOWN_OR_ASSUMED"):
            validate_state(state,mode="current",now=datetime.fromisoformat(
                           state["provenance"]["captured_at_local"]))
        self.assertEqual(r["gameplay_gate"],"STOP")
        self.assertEqual(r["game_writes"],0)
    def test_source_files_hash_bound_to_receipt(self):
        r=read_json(self.output/"R217_RECEIPT.json")
        for name,expected in r["source_text_sha256"].items():
            self.assertEqual(sha(self.private/(name+".txt")),expected)
        self.assertEqual(r["source_r156_packet_sha256"],
                         sha(self.output/"R217_R156_CURRENT_READONLY_PARTIAL.json"))
    def test_refuse_laundering_current_as_complete_r192(self):
        r=read_json(self.output/"R217_RECEIPT.json")
        self.assertFalse(r["total_current_card_definitions_verified"])
        self.assertIsNone(r["verified_spendable_cash_ecu"])
        self.assertFalse(r["owner_approved_gameplay"])
        self.assertEqual(len(r["next_required_sources"]),3)

if __name__=="__main__":unittest.main()
