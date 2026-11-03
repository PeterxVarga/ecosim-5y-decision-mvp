#!/usr/bin/env python3
"""R215 native synthetic XLSX changes generated from genuine historical source."""
from __future__ import annotations
import copy,csv,hashlib,io,json,os,subprocess,sys,tempfile,unittest,zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from factors_r215 import assemble,FactorHold,selected_factors,sha,HIST_SHA
from city_excel_r213 import load_xlsx,TEAM
from r142_proxy_reference import COEFF

NAMESPACE="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

def edited_book(source,out,*,row=220,increase=7,change_header=False):
    old=load_xlsx(source)
    index=old["teams"].index(TEAM)
    addr=chr(ord("B")+index)+str(row)
    count=0
    with zipfile.ZipFile(source) as zin,zipfile.ZipFile(out,"w") as zout:
        for info in zin.infolist():
            b=zin.read(info.filename)
            if info.filename=="xl/worksheets/sheet1.xml":
                root=ET.fromstring(b)
                for cell in root.iter(NAMESPACE+"c"):
                    if cell.attrib.get("r")==addr:
                        value=cell.find(NAMESPACE+"v")
                        if value is None:raise AssertionError("NO_NUMERIC_SELECTED_CELL")
                        value.text=str(float(value.text)+increase)
                        count+=1
                b=ET.tostring(root,encoding="utf-8",xml_declaration=True)
            zout.writestr(info,b)
    if count!=1:raise AssertionError("MODIFIED_CELL_COUNT")
    return addr

class FactorPrefill(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.historical=Path(os.environ["R215_HISTORICAL_WORKBOOK"])
        cls.second=Path(os.environ["R215_OTHER_BINARY_COPY"])
        if sha(cls.historical)!=HIST_SHA:raise AssertionError("SOURCE_DRIFT")
        cls.original=load_xlsx(cls.historical)
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="r215-qualification-")
        self.base=Path(self.tmp.name)
        self.current=self.base/"changed_observation.xlsx"
        edited_book(self.historical,self.current)
    def tearDown(self):self.tmp.cleanup()
    def create(self,name="good",**kw):
        return assemble(self.historical,kw.pop("current",self.current),
                 kw.pop("team",TEAM),kw.pop("source_id","CURRENT_OPERATOR_ROUND_P0_VIEW"),
                 self.base/name)
    def test_30_rows_and_no_fake_plan(self):
        a=self.create()
        self.assertEqual(a["factor_count"],29)
        self.assertEqual(a["index_count"],1)
        self.assertEqual(a["full_city_rows_changed_vs_historical_reference"],1)
        self.assertFalse(a["r156_export_created"])
        self.assertTrue(a["operator_must_verify_p1_plan_column_before_r156"])
        self.assertEqual(a["game_writes"],0)
        with (self.base/"good/R215_FACTORS_FOR_REVIEW.csv").open(encoding="utf-8") as stream:
            out=list(csv.DictReader(stream))
        self.assertEqual(len(out),30)
        self.assertEqual(set(x["metric"] for x in out),set(COEFF)|{"Okosváros index"})
        book=load_xlsx(self.current)
        self.assertEqual({x["metric"]:float(x["value"]) for x in out},selected_factors(book,TEAM))
    def test_source_headers_exact(self):
        r=self.create("headers")
        self.assertEqual(r["current_team_label"],TEAM)
        self.assertFalse(r["current_team_identity_matches_historical_verified"])
    def test_duplicate_binary_different_same_cells_rejected(self):
        with self.assertRaisesRegex(FactorHold,"HOLD_BINARY_DIFFERENT_BUT_NO_NEW_CITY_VALUES"):
            self.create("no_new",current=self.second)
        self.assertFalse((self.base/"no_new").exists())
    def test_same_bytes_rejected(self):
        with self.assertRaisesRegex(FactorHold,"HOLD_HISTORICAL_FILE_REPLAY"):
            self.create("replay",current=self.historical)
    def test_wrong_team_rejected(self):
        with self.assertRaisesRegex(FactorHold,"HOLD_CURRENT_TEAM_NOT_FOUND"):
            self.create("wrong_team",team="MADE_UP_TEAM")
    def test_refuse_synthetic_claim(self):
        with self.assertRaisesRegex(FactorHold,"HOLD_CURRENT_SOURCE_EVIDENCE_ID_REQUIRED"):
            self.create("fake",source_id="R210_MOCK_CURRENT")
    def test_non_numeric_factor_rejected(self):
        b=copy.deepcopy(self.original)
        pos=b["teams"].index(TEAM)
        f=next(x for x in b["rows"] if x["label"] in COEFF)
        f["values"][pos]=None
        with self.assertRaisesRegex(FactorHold,"HOLD_MISSING_OR_NONNUMERIC_FACTOR"):
            selected_factors(b,TEAM)
    def test_output_requires_new_destination(self):
        (self.base/"existing").mkdir()
        with self.assertRaisesRegex(FactorHold,"HOLD_NEW_PRIVATE_OUTPUT"):
            self.create("existing")
    def test_one_command_cli(self):
        cmd=[sys.executable,"-I","-B",str(HERE/"factors_r215.py"),
         "--historical-workbook",str(self.historical),
         "--new-workbook",str(self.current),"--team",TEAM,
         "--source-id","CURRENT_OPERATOR_ROUND_P0_VIEW",
         "--out-dir",str(self.base/"cli_result")]
        output=subprocess.run(cmd,check=True,capture_output=True,text=True,timeout=20)
        result=json.loads(output.stdout)
        self.assertEqual(result["factors"],29)
        self.assertFalse(result["p1_plan_approved"])
    def test_candidate_workbook_with_fewer_rows_rejected(self):
        b=copy.deepcopy(self.original)
        # Verify the literal row id and section drift guard independently;
        # user-visible source is always decoded by existing R213 reader.
        b["rows"].pop()
        self.assertNotEqual(len(b["rows"]),374)
        bad=self.base/"bad_structure.xlsx"
        with zipfile.ZipFile(self.current) as zin,zipfile.ZipFile(bad,"w") as zout:
            for info in zin.infolist():
                v=zin.read(info.filename)
                if info.filename=="xl/worksheets/sheet1.xml":
                    root=ET.fromstring(v)
                    target=root.find("./"+NAMESPACE+"sheetData")
                    for row in list(target):
                        if row.attrib.get("r")=="220":
                            target.remove(row);break
                    v=ET.tostring(root,encoding="utf-8",xml_declaration=True)
                zout.writestr(info,v)
        with self.assertRaises(ValueError):
            self.create("bad",current=bad)
if __name__=="__main__":unittest.main()
