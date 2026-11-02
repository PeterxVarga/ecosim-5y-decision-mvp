#!/usr/bin/env python3
"""R213 target-native source tests. Real private Excel/CSV data never in GitHub."""
from __future__ import annotations
import copy,json,os,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from city_excel_r213 import (load_xlsx,build,compare_r156,coverage,finances,
                            link_r211,diff_candidate_baseline,hold,TEAM,SCHEMA,SECTIONS)

class HistoricalFullCityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        env={name:os.environ.get(name) for name in
             ("R213_XLSX","R213_ORIGINAL_XLSX","R213_R156","R213_PROJECTS","R213_LOANS","R213_R211")}
        if not all(env.values()):raise RuntimeError("R213_PRIVATE_SOURCE_PATHS_REQUIRED")
        cls.env={k:Path(v) for k,v in env.items()}
        cls.excel=load_xlsx(cls.env["R213_XLSX"])
        cls.older=load_xlsx(cls.env["R213_ORIGINAL_XLSX"])
        cls.r156=json.loads(cls.env["R213_R156"].read_text())
        cls.projects=json.loads(cls.env["R213_PROJECTS"].read_text())
    def result(self):
        return build(self.excel,self.r156,self.projects,self.env["R213_LOANS"],self.env["R213_R211"])
    def test_exact_374_rows_ten_domains(self):
        self.assertEqual(len(self.excel["rows"]),374)
        self.assertEqual(tuple(x["label"] for x in self.excel["rows"]
                               if x["depth"]==0),SECTIONS[1:])
        self.assertEqual(len(self.excel["teams"]),5)
    def test_duplicate_export_has_identical_parsed_cells(self):
        self.assertNotEqual(self.excel["sha256"],self.older["sha256"])
        self.assertEqual(self.excel["teams"],self.older["teams"])
        self.assertEqual(self.excel["rows"],self.older["rows"])
    def test_29_exact_factors_and_nonrealized_plan(self):
        b=compare_r156(self.excel,self.r156)
        self.assertEqual(b["matched_factor_labels"],29)
        self.assertEqual(b["p0_observed_index"],51.96)
        self.assertEqual(b["p1_same_period_plan_index"],52.48)
        self.assertFalse(b["p1_is_later_realized_fact"])
        self.assertEqual(len({x["metric"] for x in b["factor_deltas"]}),29)
    def test_wrong_r156_team_or_plan_kind_rejected(self):
        for field,value in (("team","OTHER"),("kind","FACT"),("capture_mode","CURRENT_READONLY")):
            modified=copy.deepcopy(self.r156);modified[field]=value
            with self.assertRaisesRegex(ValueError,"HOLD_R156_HISTORICAL_PLAN"):
                compare_r156(self.excel,modified)
    def test_missing_factor_label_rejected(self):
        bad=copy.deepcopy(self.r156)
        bad["factors_csv"]=bad["factors_csv"].replace("Adminisztráció","Unknown additional")
        with self.assertRaisesRegex(ValueError,"HOLD_R156_29_FACTOR_IDENTITY"):
            compare_r156(self.excel,bad)
    def test_missed_values_never_zeroed(self):
        c=coverage(self.excel)
        self.assertFalse(c["workbook_loan_details_observed"])
        self.assertTrue(c["other_teams_finance_not_assumed_zero"])
        self.assertEqual(c["by_team"][TEAM]["observed_value_cells"],324)
        for team,summary in c["by_team"].items():
            if team!=TEAM:
                self.assertEqual(summary["observed_value_cells"],211)
                self.assertEqual(summary["missing_value_cells"],163)
    def test_finance_residual_and_unresolved_asset_variance(self):
        f=finances(self.excel)
        self.assertEqual(f["flow_balance_residual_ecu"],0.01)
        self.assertEqual(f["assets_subtotal_disagreement_ecu"],20000)
        self.assertFalse(f["assets_totals_reconciled"])
        self.assertFalse(f["historical_net_income_is_spendable_project_cash"])
        self.assertEqual(f["historical_grants_recognized_as_new_spendable_cash_ecu"],0)
    def test_complete_source_join_stays_historical(self):
        r=self.result()
        self.assertEqual(r["schema"],SCHEMA)
        self.assertEqual(r["historical_project_catalog"]["active_p1"],6)
        self.assertEqual(r["historical_loans"]["long_term_historical_interest_pct"],7.5)
        self.assertEqual(r["historical_loans"]["short_term_historical_interest_pct"],12)
        self.assertEqual(r["R211_partial_finance_bridge"]["r211_incremental_stress_cases"],108)
        self.assertTrue(r["R211_partial_finance_bridge"]["observed_p0_cash_not_ADDED_to_r211_delta"])
        self.assertFalse(r["official_score_predicted"])
        self.assertFalse(r["next_year_city_transition_validated"])
        self.assertIsNone(r["actual_spendable_cash_ecu"])
        self.assertEqual(r["gameplay_gate"],"STOP")
        self.assertEqual(r["game_writes"],0)
    def test_unapproved_r211_financing_claim_blocked(self):
        source=json.loads(self.env["R213_R211"].read_text())
        with tempfile.TemporaryDirectory(prefix="r213-bad-link-") as td:
            for field,value in (("loan_authorization",True),
                                ("actual_city_cash_balance",5000),
                                ("status","LIVEREADY"),
                                ("incremental_stress_case_count",0)):
                bad=copy.deepcopy(source);bad[field]=value
                p=Path(td)/(field+".json");p.write_text(json.dumps(bad))
                with self.assertRaisesRegex(ValueError,"HOLD_R211_PARTIAL_FINANCE_GATES"):
                    link_r211(p)
    def test_wrong_project_cards_fail_closed(self):
        bad=copy.deepcopy(self.projects);bad["projects"].pop()
        with self.assertRaisesRegex(ValueError,"HOLD_HISTORICAL_35_CARD_CATALOG"):
            build(self.excel,self.r156,bad,self.env["R213_LOANS"],self.env["R213_R211"])
    def test_new_export_diff_without_live_claim(self):
        candidate=copy.deepcopy(self.excel)
        candidate["sha256"]="f"*64
        r=next(x for x in candidate["rows"] if x["row"]==220)
        pos=candidate["teams"].index(TEAM)
        r["values"][pos]+=7
        diff=diff_candidate_baseline(self.excel,candidate,source_claim="CURRENT_UNVERIFIED_OPERATOR_EXPORT")
        self.assertEqual(diff["changed_count"],1)
        self.assertEqual(diff["changed_rows"][0]["row"],220)
        self.assertEqual(diff["changed_rows"][0]["numeric_difference_if_comparable"],7)
        self.assertFalse(diff["new_source_is_cryptographically_verified_game_server"])
        self.assertEqual(diff["gameplay_gate"],"STOP")
    def test_new_export_diff_rejects_provenance_and_structure(self):
        with self.assertRaisesRegex(ValueError,"HOLD_NEW_CANDIDATE_MUST_DIFFER_BY_SOURCE_SHA"):
            diff_candidate_baseline(self.excel,self.excel,source_claim="CURRENT_UNVERIFIED_OPERATOR_EXPORT")
        altered=copy.deepcopy(self.excel);altered["sha256"]="f"*64
        with self.assertRaisesRegex(ValueError,"HOLD_EXPLICIT_UNVERIFIED_SOURCE_LABEL"):
            diff_candidate_baseline(self.excel,altered,source_claim="SERVER_AUTHENTICATED")
        altered["rows"][0]["label"]="Changed row definition"
        with self.assertRaisesRegex(ValueError,"HOLD_CURRENT_WORKBOOK_STRUCTURE_CHANGED"):
            diff_candidate_baseline(self.excel,altered,source_claim="CURRENT_UNVERIFIED_OPERATOR_EXPORT")

if __name__=="__main__":unittest.main()
