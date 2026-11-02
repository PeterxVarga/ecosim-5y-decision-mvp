#!/usr/bin/env python3
"""7-column team layout regression built from existing historical private Excel.

Synthetic fixture mirrors 7-team Selejtező_I structure, but is NOT genuine
current game data, and never represents user-uploaded private workbook.
"""
from __future__ import annotations
import json,os,sys,tempfile,unittest,zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from factors_r215 import assemble,selected_factors,FactorHold
from city_excel_r213 import load_xlsx,TEAM

NS="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
def sample_7_team_xlsx(source,dest):
    found=set()
    with zipfile.ZipFile(source) as zin,zipfile.ZipFile(dest,"w") as zout:
        for info in zin.infolist():
            data=zin.read(info.filename)
            if info.filename=="xl/worksheets/sheet1.xml":
                tree=ET.fromstring(data)
                rows=tree.findall("./"+NS+"sheetData/"+NS+"row")
                head=rows[0]
                for col,label in (("G","SYNTHETIC_EXTRA_SIX"),("H","SYNTHETIC_EXTRA_SEVEN")):
                    cell=ET.SubElement(head,NS+"c",{"r":col+"1","t":"inlineStr"})
                    inner=ET.SubElement(cell,NS+"is")
                    ET.SubElement(inner,NS+"t").text=label
                for row in rows:
                    n=int(row.attrib["r"])
                    if n not in (161,370,382):continue
                    cell=next((x for x in row.findall(NS+"c")
                               if x.attrib.get("r")=="D"+str(n)),None)
                    if cell is None:raise AssertionError("MISSING_EXPECTED_CELL")
                    val=cell.find(NS+"v")
                    if val is None:raise AssertionError("MISSING_VALUE")
                    val.text={161:"390",370:"5694225.86",382:"14723528.9"}[n]
                    found.add(n)
                data=ET.tostring(tree,encoding="utf-8",xml_declaration=True)
            zout.writestr(info,data)
    if found!={161,370,382}:raise AssertionError("REQUIRED_MOCK_DIFFERENCES")
class SevenTeamAdapterTest(unittest.TestCase):
    def test_real_original_reader_reused_with_seven_team_layout(self):
        historical=Path(os.environ["R215_HISTORICAL_WORKBOOK"])
        with tempfile.TemporaryDirectory(prefix="r216-seven-team-") as td:
            out=Path(td);source=out/"mock7.xlsx"
            sample_7_team_xlsx(historical,source)
            original=load_xlsx(historical)
            self.assertEqual(len(original["teams"]),5)
            adapted=load_xlsx(source,require_legacy_team=False)
            self.assertEqual(len(adapted["teams"]),7)
            self.assertEqual(len(adapted["rows"]),374)
            self.assertEqual(len(adapted["rows"][0]["values"]),7)
            self.assertEqual(len(selected_factors(adapted,TEAM)),30)
            receipt=assemble(historical,source,TEAM,
                "CURRENT_OPERATOR_SELEJTEZO_UNVERIFIED",out/"report")
            self.assertEqual(receipt["full_city_rows_changed_vs_historical_reference"],3)
            self.assertEqual(receipt["factor_count"],29)
            self.assertFalse(receipt["r156_export_created"])
            self.assertFalse(receipt["server_attested"])
            self.assertEqual(receipt["gameplay_gate"],"STOP")
            self.assertIn("Okosváros index,51.96",
                (out/"report/R215_FACTORS_FOR_REVIEW.csv").read_text())
    def test_old_legacy_mode_must_not_silently_admit_seven_teams(self):
        historical=Path(os.environ["R215_HISTORICAL_WORKBOOK"])
        with tempfile.TemporaryDirectory(prefix="r216-seven-team-") as td:
            source=Path(td)/"mock7.xlsx"
            sample_7_team_xlsx(historical,source)
            with self.assertRaisesRegex(ValueError,"HOLD_SUPPORTED_TEAM_COLUMNS"):
                load_xlsx(source,require_legacy_team=True)
if __name__=="__main__":unittest.main()
