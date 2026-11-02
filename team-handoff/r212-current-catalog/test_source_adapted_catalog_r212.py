#!/usr/bin/env python3
"""R212: native original R156/R191 -> current card drift -> R162/R160/R207.
All fixtures explicitly MOCK; never live EcoSim, cash approval or server score.
"""
import copy, hashlib, json, sys, tempfile, unittest
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SRC=ROOT/"ECOSIM_R162_INTEGRITY_REVIEW_RC"
sys.path[:0]=[str(HERE),str(ROOT/"team-handoff/r207-first-round"),
              str(ROOT/"team-handoff/r191-live-admission/tools"),str(SRC/"tools")]
import strategy_5y
from catalog_adapter_r212 import prepare,AdapterHold,original_search_with_current_index
from test_r210_current_synthetic_e2e import synthetic_sources,write
from readonly_intake_r156 import create_bundle
from observation_bundle_r152 import compile_bundle
from catalog_gate_r192 import validate_catalog,CatalogHold
from first_round import run_cli

def fixture():
    now=datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    export,catalog,finance=synthetic_sources(now)
    catalog["projects"][12]["startup_cost"]+=1000
    return export,catalog,finance

class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.export,self.catalog,self.finance=fixture()
        self.original=json.loads((SRC/"data/ecosim_projects_20261030.json").read_text())
        self.tmp=tempfile.TemporaryDirectory(prefix="ecosim-r212-adapter-")
        self.base=Path(self.tmp.name)
        self.bundle,_=create_bundle(self.export,self.base/"r156")
        _,self.state,_=compile_bundle(self.bundle/"manifest.json")
    def tearDown(self): self.tmp.cleanup()
    def prepare(self,doc=None):
        return prepare(doc or self.catalog,self.state,self.original,
                       catalog_hash="0"*64)
    def test_original_r192_blocks_changed_card(self):
        with self.assertRaisesRegex(CatalogHold,"CURRENT_CARD_DEFINITION_DRIFT_IDS_13"):
            validate_catalog(self.catalog,self.state,self.original)
    def test_admitted_index_is_source_backed(self):
        r=self.prepare()
        self.assertEqual(r["receipt"]["current_card_definition_drift_ids"],[13])
        self.assertEqual(r["index"][13]["startup_cost"],
                         self.original["projects"][12]["startup_cost"]+1000)
        self.assertNotIn("status_p1",r["index"][13])
        self.assertFalse(r["receipt"]["server_attested"])
        self.assertEqual(r["receipt"]["gameplay_gate"],"STOP")
    def test_missing_and_duplicate_card_rejected(self):
        a=copy.deepcopy(self.catalog);a["projects"].pop()
        with self.assertRaisesRegex(AdapterHold,"EXACT_35"):
            self.prepare(a)
        a=copy.deepcopy(self.catalog);a["projects"][12]["id"]=11
        with self.assertRaisesRegex(AdapterHold,"DUPLICATE_CARD_CURRENT"):
            self.prepare(a)
    def test_wrong_team_period_and_stale_source_rejected(self):
        for field,value,reason in [("team","OTHER","SOURCE_TEAM"),
                                   ("period",2,"PERIOD"),
                                   ("source_evidence_id","historical-test-export","HISTORICAL_AS_CURRENT"),
                                   ("captured_at_local","2020-01-01T00:00:00+00:00","CAPTURE_WINDOW")]:
            a=copy.deepcopy(self.catalog);a[field]=value
            with self.assertRaisesRegex(AdapterHold,reason):
                self.prepare(a)
    def test_broken_money_and_effect_rejected(self):
        a=copy.deepcopy(self.catalog);a["projects"][12]["startup_cost"]=float("nan")
        with self.assertRaisesRegex(AdapterHold,"INVALID_CARD_CURRENT"):
            self.prepare(a)
        a=copy.deepcopy(self.catalog);a["projects"][12]["effects"]=[{"metric":"A","value_percent":"invalid"}]
        with self.assertRaisesRegex(AdapterHold,"INVALID_CARD_CURRENT"):
            self.prepare(a)
    def test_adaptation_context_restores_index_on_failure(self):
        native=strategy_5y.project_index
        with self.assertRaisesRegex(RuntimeError,"forced"):
            with original_search_with_current_index(strategy_5y,self.prepare()["index"]):
                self.assertNotEqual(strategy_5y.project_index,native)
                raise RuntimeError("forced")
        self.assertIs(strategy_5y.project_index,native)
    def test_full_current_mode_mock_e2e_drift_optin(self):
        st=self.base/"state.json";fi=self.base/"finance.json";ca=self.base/"catalog.json"
        write(st,self.state);write(fi,self.finance);write(ca,self.catalog)
        basic=["--repo-root",str(ROOT),"--state",str(st),"--r156-bundle",str(self.bundle),
               "--year1-finance",str(fi),"--current-card-catalog",str(ca),
               "--year1-budget","150000"]
        old=sys.argv
        try:
            # The safety default must reject modified catalog, before writing output.
            sys.argv=["first_round.py",*basic,"--out-dir",str(self.base/"should_not_exist")]
            with self.assertRaisesRegex(CatalogHold,"CURRENT_CARD_DEFINITION_DRIFT"):
                run_cli()
            self.assertFalse((self.base/"should_not_exist").exists())
            before=strategy_5y.project_index
            for i in (1,2):
                sys.argv=["first_round.py",*basic,"--allow-source-adapted-current-catalog",
                          "--out-dir",str(self.base/f"adapted{i}")]
                run_cli()
            self.assertIs(strategy_5y.project_index,before)
        finally:sys.argv=old
        a=(self.base/"adapted1/R207.json").read_bytes()
        b=(self.base/"adapted2/R207.json").read_bytes()
        self.assertEqual(a,b)
        self.assertEqual((self.base/"adapted1/R207_HU.md").read_bytes(),
                         (self.base/"adapted2/R207_HU.md").read_bytes())
        data=json.loads(a)
        self.assertEqual(data["project_catalog_source_schema"],
                         "ECOSIM_R212_SOURCE_ADAPTED_CATALOG_V1")
        self.assertEqual(data["source_adapted_card_drift_ids"],[13])
        self.assertEqual(data["current_observed_card_catalog_sha256"],
                         hashlib.sha256(ca.read_bytes()).hexdigest())
        self.assertEqual(data["gameplay_gate"],"STOP")
        self.assertEqual(data["game_writes"],0)
        self.assertGreaterEqual(data["selected_count"],1)
        self.assertLessEqual(data["selected_count"],3)
        self.assertTrue(all(x["conditional_display_eligibility_count"]==0 for x in data["selected_options"]))

    def test_second_round_with_changed_card_and_started_projects(self):
        import csv,io
        export,catalog,finance=fixture()
        export["period"]=2;catalog["period"]=2;finance["period"]=2
        raw=list(csv.DictReader(io.StringIO(export["projects_csv"])))
        for line in raw:
            if line["project_id"] in ("13","27"):
                line["previous_running"]="true"
                line["selected_new"]="false"
        dst=io.StringIO()
        writer=csv.DictWriter(dst,fieldnames=["project_id","previous_running","selected_new"],
                              lineterminator="\n")
        writer.writeheader();writer.writerows(raw)
        export["projects_csv"]=dst.getvalue()
        export["parameters"]["team"]["already_selected_new_project_ids_current_period"]=[]
        catalog["projects"][7]["startup_cost"]+=1500
        bundle,_=create_bundle(export,self.base/"second_period")
        _,state,_=compile_bundle(bundle/"manifest.json")
        self.assertEqual(state["provenance"]["current_period"],2)
        self.assertIn(13,state["team"]["initially_active_project_ids"])
        st=self.base/"period2_state.json";fi=self.base/"period2_finance.json";ca=self.base/"period2_catalog.json"
        write(st,state);write(fi,finance);write(ca,catalog)
        oldargs=sys.argv
        try:
            sys.argv=["first_round.py","--repo-root",str(ROOT),"--state",str(st),
                      "--r156-bundle",str(bundle),"--year1-finance",str(fi),
                      "--current-card-catalog",str(ca),"--year1-budget","150000",
                      "--allow-source-adapted-current-catalog",
                      "--out-dir",str(self.base/"year2_advisory")]
            run_cli()
        finally:sys.argv=oldargs
        p=json.loads((self.base/"year2_advisory/R207.json").read_text())
        self.assertEqual(p["period"],2)
        self.assertIn(8,p["source_adapted_card_drift_ids"])
        self.assertEqual(p["gameplay_gate"],"STOP")
        self.assertTrue(1<=p["selected_count"]<=3)
        self.assertTrue(all(13 not in item["first_year_new_project_ids"]
                            for item in p["selected_options"]))

if __name__=="__main__":unittest.main()
