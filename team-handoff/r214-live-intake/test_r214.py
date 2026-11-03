#!/usr/bin/env python3
"""Original R156-to-R207 source E2E with synthetic fixtures, no EcoSim access."""
from __future__ import annotations
import copy,hashlib,json,sys,tempfile,unittest
from datetime import datetime,timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path[:0]=[str(HERE),str(ROOT/"team-handoff/r207-first-round")]
from run_r214 import build,Hold,sha
from test_r210_current_synthetic_e2e import synthetic_sources,write

class IntegratedCurrentFixture(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="r214-original-e2e-")
        self.base=Path(self.tmp.name)
        now=datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        self.packet,self.cards,self.finance=synthetic_sources(now)
        self.export_path=self.base/"r156.json"
        self.cards_path=self.base/"cards.json"
        self.finance_path=self.base/"finance.json"
        self.save()
    def tearDown(self):self.tmp.cleanup()
    def save(self):
        write(self.export_path,self.packet)
        write(self.cards_path,self.cards)
        write(self.finance_path,self.finance)
    def run_it(self,name,**kw):
        return build(self.export_path,self.finance_path,self.cards_path,
                     150000,self.base/name,qualification=True,**kw)
    def test_two_identical_full_original_module_e2e(self):
        a=self.run_it("a")
        b=self.run_it("b")
        self.assertEqual(a,b)
        self.assertEqual(a["selected_count"],3)
        self.assertEqual(a["source_class"],"MOCK_ONLY_NOT_REAL_CURRENT")
        self.assertEqual(a["gameplay_gate"],"STOP")
        self.assertEqual(a["game_writes"],0)
        self.assertFalse(a["server_authenticated"])
        self.assertFalse(a["financing_approved"])
        for name in ("R214_RECEIPT.json","R214_HU.md","advisory/R207.json",
                     "advisory/R207_HU.md","r156_state.json"):
            self.assertEqual((self.base/"a"/name).read_bytes(),(self.base/"b"/name).read_bytes(),name)
        self.assertFalse((self.base/"a/INCOMPLETE_HOLD").exists())
    def test_source_changes_use_real_r212_and_r160(self):
        self.cards["projects"][12]["startup_cost"]+=1000
        self.save()
        with self.assertRaisesRegex(ValueError,"CURRENT_CARD_DEFINITION_DRIFT"):
            self.run_it("not_allowed")
        self.assertTrue((self.base/"not_allowed/INCOMPLETE_HOLD").exists())
        a=self.run_it("adapted",allow_drift=True)
        self.assertEqual(a["card_drift_ids"],[13])
        self.assertEqual(a["selected_count"],3)
        self.assertEqual(a["game_writes"],0)
        report=json.loads((self.base/"adapted/advisory/R207.json").read_text())
        self.assertTrue(all(x["conditional_display_eligibility_count"]==0
                            for x in report["selected_options"]))
    def test_historical_r156_cannot_claim_current(self):
        self.packet["capture_mode"]="HISTORICAL_REFERENCE"
        self.save()
        with self.assertRaisesRegex(Hold,"HOLD_R156_CURRENT_PLAN_REQUIRED"):
            self.run_it("historic")
        self.assertFalse((self.base/"historic").exists())
    def test_r210_mock_cannot_run_as_live(self):
        with self.assertRaisesRegex(Hold,"HOLD_FAKE_OR_HISTORICAL_CURRENT_SOURCE"):
            build(self.export_path,self.finance_path,self.cards_path,150000,self.base/"false_live")
        self.assertFalse((self.base/"false_live").exists())
    def test_wrong_r156_source_bundle_fails_original_gate(self):
        self.packet["parameters"]["market"]["smartcity_total_weights"]["Gazdaság"]=.9
        self.save()
        with self.assertRaises(ValueError):
            self.run_it("wrong_weights")
        self.assertTrue((self.base/"wrong_weights/INCOMPLETE_HOLD").exists())
    def test_incomplete_cash_fails_original_r191_gate(self):
        self.finance["operator_observed_spendable_ecu"]=4000
        self.save()
        with self.assertRaises(ValueError):
            self.run_it("underfunded")
        self.assertTrue((self.base/"underfunded/INCOMPLETE_HOLD").exists())
    def test_nonexistent_output_invariant(self):
        (self.base/"existing").mkdir()
        with self.assertRaisesRegex(Hold,"HOLD_PRIVATE_NEW_OUTPUT"):
            self.run_it("existing")
    def test_period2_with_source_adapted_catalog(self):
        self.packet["period"]=2
        self.cards["period"]=2
        self.finance["period"]=2
        self.cards["projects"][12]["startup_cost"]+=1000
        # R210 synthetic fixture sets no previously started status by default;
        # unchanged project statuses still preserve all R156 constraints.
        self.save()
        out=self.run_it("period2",allow_drift=True)
        self.assertEqual(out["period"],2)
        self.assertTrue(1<=out["selected_count"]<=3)
        self.assertEqual(out["game_writes"],0)

    def test_real_cli_launcher_in_sandbox(self):
        import subprocess
        command=[sys.executable,"-I","-B",str(HERE/"run_r214.py"),
           "--r156-export",str(self.export_path),
           "--year1-finance",str(self.finance_path),
           "--current-card-catalog",str(self.cards_path),
           "--year1-budget","150000",
           "--qualification-mock","--out-dir",str(self.base/"direct_cli")]
        output=subprocess.run(command,capture_output=True,text=True,check=True,timeout=80)
        self.assertIn('"options": 3',output.stdout)
        data=json.loads((self.base/"direct_cli/R214_RECEIPT.json").read_text())
        self.assertEqual(data["source_class"],"MOCK_ONLY_NOT_REAL_CURRENT")
        self.assertEqual(data["game_writes"],0)
        self.assertFalse((self.base/"direct_cli/INCOMPLETE_HOLD").exists())

    def test_identical_historical_city_export_not_admitted_as_new(self):
        import os
        historical=os.environ.get("R214_BASELINE_PRIVATE")
        duplicate=os.environ.get("R214_BINARY_DIFFERENT_SAME_VALUES")
        if not historical or not duplicate:self.skipTest("Private workbook paths not supplied")
        with self.assertRaisesRegex(Hold,
               "HOLD_CURRENT_EXCEL_HAS_NO_OBSERVED_CHANGE_OR_IS_BINARY_DUPLICATE"):
            self.run_it("binary_duplicate",historical_workbook=Path(historical),
                        current_workbook=Path(duplicate))
        self.assertFalse((self.base/"binary_duplicate").exists())

    def test_changed_city_excel_diff_remains_descriptive(self):
        import os,zipfile
        from xml.etree import ElementTree as ET
        from city_excel_r213 import load_xlsx
        historical=os.environ.get("R214_BASELINE_PRIVATE")
        if not historical:self.skipTest("Private workbook not supplied")
        src=Path(historical);dst=self.base/"candidate_changed_one_cell.xlsx"
        readout=load_xlsx(src)
        ix=readout["teams"].index("Jutalom a nap végén")
        address=chr(ord("B")+ix)+"220"
        namespace="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
        found=0
        with zipfile.ZipFile(src) as zin,zipfile.ZipFile(dst,"w") as zout:
            for info in zin.infolist():
                raw=zin.read(info.filename)
                if info.filename=="xl/worksheets/sheet1.xml":
                    tree=ET.fromstring(raw)
                    for cell in tree.iter(namespace+"c"):
                        if cell.attrib.get("r")==address:
                            n=cell.find(namespace+"v")
                            self.assertIsNotNone(n)
                            n.text=str(float(n.text)+7)
                            found+=1
                    raw=ET.tostring(tree,encoding="utf-8",xml_declaration=True)
                zout.writestr(info,raw)
        self.assertEqual(found,1)
        data=self.run_it("with_city_diff",historical_workbook=src,current_workbook=dst)
        self.assertEqual(data["city_workbook_diff_count"],1)
        delta=json.loads((self.base/"with_city_diff/R214_CITY_DIFF_PRIVATE.json").read_text())
        self.assertEqual(delta["changed_rows"][0]["row"],220)
        self.assertFalse(delta["new_source_is_cryptographically_verified_game_server"])
        self.assertEqual(data["gameplay_gate"],"STOP")

if __name__=="__main__":unittest.main()
