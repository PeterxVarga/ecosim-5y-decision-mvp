#!/usr/bin/env python3
"""Public-safe synthetic R205 source tampering / reconciliation tests."""
import csv
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location("r205",Path(__file__).with_name("reconcile.py"))
r=importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)

TAX=["Iparűzési adó","Gépjárműadó","Kommunális adó","Építményadó"]
FEE=["Temetkezés","Parkolásüzemeltetés","Kommunális","Víz, csatorna, távhő","Bérlakás díjak","Személyszállítás"]
def row(**kw):return dict(kw)
def build():
    base=[]
    groups={}
    for category,view,names in (("four_tax_channels","taxes",TAX),("six_fee_channels","service_fees",FEE)):
        recs=[]
        for i,name in enumerate(names):
            key=len(base)
            values={"p0_number":str(100+key),"p1_number":str(101+key)}
            base.append(row(row_id=f"r{key}",view=view,table_index="0",table_title="Finance",label=name,
                            team="Test Team",market="Z",period="1/1",**values))
            recs.append(row(channel="transport" if name=="Személyszállítás" else f"channel{key}",
                            source_label="Tömegközlekedés" if name=="Személyszállítás" else name,
                            source_row_id=f"finance.r{key}",p0_actual_raw=100+key,p1_target_raw=101+key))
        groups[category]=recs
    for j,label in enumerate(("Fejlesztési célú állami támogatás","Vállalatoktól érkező fejlesztési támogatás")):
        base.append(row(row_id=f"grant{j}",view="state_laws",table_index="2",table_title="Támogatások",label=label,
                        p0_number="50",p1_number="50",team="Test Team",market="Z",period="1/1"))
    while len(base)<49:
        j=len(base)
        base.append(row(row_id=f"dummy{j}",view="state_laws",table_index="1",table_title="Other",label=f"Dummy{j}",
                        p0_number="1",p1_number="1",team="Test Team",market="Z",period="1/1"))
    loans=[]
    for typ,rate in (("long_term",4.0),("short_term",9.0)):
        loans.append(row(row_id=f"loan_{typ}",view=typ,label="Kamat, %",
                         p0_number=str(rate),p1_number=str(rate),team="Test Team",market="Z",period="1/1"))
    while len(loans)<7:
        j=len(loans)
        loans.append(row(row_id=f"loan_other{j}",view="long_term",label=f"Other{j}",
                         p0_number="0",p1_number="0",team="Test Team",market="Z",period="1/1"))
    urls={f"S{i:02}":f"https://edu.ecosim.hu/simulation/{i}" for i in range(15)}
    index=[row(source_id=k,url=url,scope=json.dumps({"team":"Test Team","market":"Z","period":"1/1","competition":"X Test"}))
           for k,url in urls.items()]
    observations=[row(observation_id=f"O{i}",source_id="S00",source_url=urls["S00"],
                      team="Test Team",market="Z",period="1/1") for i in range(24)]
    for i,source_id,rate in ((12,"S08",4.0),(13,"S09",9.0)):
        observations[i].update(source_id=source_id,source_url=urls[source_id],
                               source_location="row=Kamat, %",original_text="Kamat, %"+chr(9)+str(rate)+chr(9)+str(rate))
    rules=[row(heading=n,view=view,source_url=urls["S00"],text_raw=text)
           for n,view,text in (
             ("Tax","taxes","General tax rule"),
             ("Service","service_fees","General fee rule"),
             ("State","state_laws","General support rule"),
             ("Long","long_term","Period: csak felvenni, vagy visszafizetni"),
             ("Short","short_term","Automatikus if negative balance"))]
    payload={"income.csv":base,"loans.csv":loans,"rules.csv":rules,
             "observations.csv":observations,"source_index.csv":index}
    profile={"schema":"ECOSIM_R200_INPUT_PROFILE_V1","mode":"historical-test","gameplay_gate":"STOP",
             "identity":{"team":"Test Team","market":"Z","round":"Test","period":1}}
    source={"finance":"hashF","institutions":"hashI"}
    r202={"schema":"ECOSIM_R202_TEST_REVENUE_AND_INSTITUTION_CALIBRATION_GATE_V1",
          "status":"PASS_SOURCE_DIAGNOSTIC_HOLD_GLOBAL_CALIBRATION","gameplay_gate":"STOP",
          "game_writes":0,"source_hashes":source,"observed_channel_groups":groups}
    r204={"schema":"ECOSIM_UNIFIED_HISTORICAL_DECISION_PACKET_V1","mode":"historical-test",
          "status":"PASS_PARTIAL_HISTORICAL_DECISION_SUPPORT_LIVE_HOLD","gameplay_gate":"STOP",
          "game_writes":0,"decision":{"live":"HOLD"},"source_hashes":source}
    return payload,profile,r202,r204

class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder=Path(self.temp.name)
        self.payload,self.profile,self.r202,self.r204=build()
        self.rewrite()
    def rewrite(self):
        for name,rows in self.payload.items():
            with (self.folder/name).open("w",newline="",encoding="utf-8") as f:
                writer=csv.DictWriter(f,fieldnames=sorted(set().union(*(set(item) for item in rows))))
                writer.writeheader();writer.writerows(rows)
        self.manifest={"schema":"ECOSIM_R205_NORMALIZED_LIBRARY_SOURCE_MANIFEST_V1",
                       "representation":"LIBRARY_PARSED_NORMALIZED_CSV_NOT_ORIGINAL_BYTES",
                       "sources":{name:{"file_id":"file_synthetic","normalized_sha256":r.sha(self.folder/name)}
                                  for name in r.FILES}}
    def check(self):return r.validate(self.folder,self.profile,self.r202,self.r204,self.manifest)
    def rejects(self,error):
        with self.assertRaisesRegex(ValueError,"HOLD_"+error):self.check()
    def test_clean(self):
        data=self.check()
        self.assertEqual(len(data["r202_finance_channel_crosschecks"]),10)
        self.assertEqual(sum(x["rows"] for x in data["source_files"].values()),100)
        self.assertFalse(data["game_actions_permitted"])
    def test_manifest_tamper(self):
        self.payload["income.csv"][0]["p0_number"]="999"
        self.rewrite()
        self.manifest["sources"]["income.csv"]["normalized_sha256"]="bad"
        self.rejects("LIBRARY_SOURCE_HASH_income.csv")
    def test_r202_mismatch(self):
        self.r202["observed_channel_groups"]["four_tax_channels"][0]["p0_actual_raw"]=999
        self.rejects("R202_RECONCILIATION_channel0")
    def test_rate_mismatch(self):
        self.payload["loans.csv"][0]["p0_number"]="9"
        self.rewrite()
        self.rejects("OBSERVED_LOAN_RATE_long_term")
    def test_observation_url_mismatch(self):
        self.payload["observations.csv"][0]["source_url"]="https://wrong.invalid"
        self.rewrite()
        self.rejects("OBSERVATION_SOURCE_ID")
    def test_future_claim_rejected(self):
        self.r204["decision"]["live"]="GO"
        self.rejects("R204_NO_LIVE")
    def test_duplicate_id(self):
        self.payload["income.csv"][1]["row_id"]=self.payload["income.csv"][0]["row_id"]
        self.rewrite()
        self.rejects("DUPLICATE_ROW_ID")
    def test_source_scope_mismatch(self):
        self.payload["source_index.csv"][0]["scope"]=json.dumps({"team":"Other","market":"Z","period":"1/1","competition":"X Test"})
        self.rewrite()
        self.rejects("SOURCE_SCOPE")
if __name__=="__main__":unittest.main()
