import copy,json,math,sys,unittest
from pathlib import Path

REPO=Path(__file__).resolve().parents[3]
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
sys.path.insert(0,str(REPO/"team-handoff/r200-historical-plugplay/tools"))
from robust_r201 import (school_rows,expense_delta_table,scenario_book,analyze,md,STATUS)
from corpus_r200 import parse_json,csvdata,resolve

PROFILE=REPO/"team-handoff/r200-historical-plugplay/profiles/historical_R94_R200.json"

class StandaloneR201(unittest.TestCase):
 def raises_hold(self,call,word):
  with self.assertRaisesRegex(ValueError,"HOLD_"+word):
   call()
 def fake_school(self):
  names=("Middle schools","Elementary schools","Kindergartens","Nurseries")
  def line(label,a,b):
   return {"cells":[{"text":label},{"text":str(a)},{"text":str(b),"editable":False}]}
  def table():
   return {"rows":[line("Number",2,2),line("Average capacity",100,100),
    line("Total capacity",200,200),line("Utilization, %",113,113),
    line("Average number of employees",5,5),
    line("Total number of employees",10,10)]}
  return {"read_only":True,"pages":[{"path":"/simulation/institutions",
    "body_text":" ".join(names),"tables":[{"rows":[]}] + [table() for _ in names]}]}
 def test_school_arithmetic_and_interval(self):
  r=school_rows(self.fake_school())
  self.assertEqual(len(r),4)
  self.assertEqual(r[0]["p1"]["capacity"],200)
  self.assertEqual(r[0]["p1"]["approx_attendees_interval_if_rounded_to_integer"],[225,227])
  self.assertTrue(r[0]["p1"]["certainly_over_capacity_on_display"])
 def test_capacity_disagreement_holds(self):
  s=self.fake_school();s["pages"][0]["tables"][1]["rows"][2]["cells"][2]["text"]="201"
  self.raises_hold(lambda:school_rows(s),"CAPACITY_IDENTITY")
 def test_employee_disagreement_holds(self):
  s=self.fake_school();s["pages"][0]["tables"][2]["rows"][-1]["cells"][2]["text"]="11"
  self.raises_hold(lambda:school_rows(s),"EMPLOYEE_IDENTITY")
 def test_no_school_source_holds(self):
  s=self.fake_school();s["read_only"]=False
  self.raises_hold(lambda:school_rows(s),"INSTITUTION_SNAPSHOT_SCOPE")
 def test_missing_sections_holds(self):
  s=self.fake_school();s["pages"][0]["body_text"]="None"
  self.raises_hold(lambda:school_rows(s),"INSTITUTION_BODY_SECTIONS")
 def test_reordered_sections_holds(self):
  s=self.fake_school();s["pages"][0]["body_text"]="Nurseries Kindergartens Elementary schools Middle schools"
  self.raises_hold(lambda:school_rows(s),"INSTITUTION_SECTION_ORDER")
 def test_utilization_negative_holds(self):
  s=self.fake_school();s["pages"][0]["tables"][1]["rows"][3]["cells"][2]["text"]="-20"
  self.raises_hold(lambda:school_rows(s),"INSTITUTION_NEGATIVE")
 def test_expense_deltas_numeric_not_signed_zero(self):
  f=[dict(row_id=str(i),view="v",table_title="t",label="test",
         p0_number=str(a),p1_number=str(b)) for i,(a,b) in
         enumerate([(0,-0),(0,0),(1,2),(3,1)])]
  self.assertEqual(len(expense_delta_table(f)),2)
 def test_md_disclaims(self):
  x={"institutional_capacity_diagnostics":[],
      "scenario_robustness":{"candidate_robust_front_sample_ids":[],
                             "illustrative_cap_filters":[]},
      "r200_source_count":0,"status":STATUS,"finance_numeric_deltas_not_additive":[]}
  out=md(x)
  self.assertIn("GAME_ACTION_GATE=STOP",out)
  self.assertIn("nem bizonyítottan rendelkezésre álló pénz",out)

@unittest.skipUnless(PROFILE.is_file(),"Owner-private archived test files not mounted; only standalone tests")
class FullR201(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.profile=parse_json(PROFILE.read_bytes())
  cls.snap=analyze(cls.profile,PROFILE)
  cls.inst=parse_json(resolve("institutions",cls.profile,PROFILE))
  cls.desk=parse_json(resolve("r149",cls.profile,PROFILE))
  cls.r199=parse_json(resolve("r199",cls.profile,PROFILE))
 def raises_hold(self,call,word):
  with self.assertRaisesRegex(ValueError,"HOLD_"+word):call()
 def test_native_17_51(self):
  s=self.snap["scenario_robustness"]
  self.assertEqual((s["candidate_count"],s["scenario_count"]),(17,51))
  self.assertEqual(len(s["candidate_robust_front_sample_ids"]),9)
  self.assertFalse(s["selected_or_server_approved"])
 def test_four_cap_filter_counts(self):
  z=self.snap["scenario_robustness"]["illustrative_cap_filters"]
  self.assertEqual([p["fit_count_not_finance_approved"] for p in z],[5,6,12,17])
  self.assertTrue(all(p["actual_spendable_cash_authorized"] is False for p in z))
 def test_r195_two_plans(self):
  plans=self.snap["scenario_robustness"]["candidate_summaries"]
  self.assertEqual(sum(x["source"]=="R195_EXACT_HISTORICAL" for x in plans),2)
  self.assertEqual(sum(x["source"]=="R149_SAMPLED_HISTORICAL" for x in plans),15)
 def test_school_4_groups_and_arithmetic(self):
  schools=self.snap["institutional_capacity_diagnostics"]
  self.assertEqual([r["p1"]["capacity"] for r in schools],[2240,5720,2880,450])
  self.assertEqual([r["p1"]["employees"] for r in schools],[483,663,352,270])
  self.assertEqual([r["p1"]["displayed_utilization_pct"] for r in schools],
                   [113,88,72,77])
 def test_school_middle_overcapacity_interval(self):
  a=self.snap["institutional_capacity_diagnostics"][0]["p1"]
  self.assertTrue(a["capacity_gap_interval_if_rounded"][0]>0)
  self.assertTrue(a["certainly_over_capacity_on_display"])
 def test_finance_44_numeric_46_display(self):
  self.assertEqual(len(self.snap["finance_numeric_deltas_not_additive"]),44)
  self.assertEqual(self.snap["finance_textual_changes"],46)
  self.assertEqual(self.snap["finance_signed_zero_only_display_changes"],2)
 def test_no_live_authority(self):
  r=self.snap
  self.assertFalse(r["calibrated_five_year_live_prediction"])
  self.assertFalse(r["financial_spend_authority"])
  self.assertEqual((r["game_writes"],r["gameplay_gate"]),(0,"STOP"))
 def test_all_17_combinations_each_path(self):
  data=self.snap["scenario_robustness"]["candidate_summaries"]
  self.assertTrue(all(len(x["policy_paths"])==3 for x in data))
 def test_tampered_old_calendar(self):
  d=copy.deepcopy(self.desk)
  d["candidate_comparison"][0]["project_ids_by_year"][0].append(35)
  self.raises_hold(lambda:scenario_book(d,self.r199),"R149_ANNUAL_PAIR_MISMATCH")
 def test_tampered_r149_cash_stress(self):
  d=copy.deepcopy(self.desk)
  d["r158_annual_partial_cash_timing"]["combinations"][0][
     "hypothetical_peak_zero_opening_cash_shortfall_positive_receipts_deferred_ecu"]=-1
  self.raises_hold(lambda:scenario_book(d,self.r199),"NONFINITE_SCENARIO")
 def test_removed_one_original_pair(self):
  d=copy.deepcopy(self.desk)
  d["r158_annual_partial_cash_timing"]["combinations"].pop()
  self.raises_hold(lambda:scenario_book(d,self.r199),"OLD_45_PAIR_COUNT")
 def test_r199_calendar_drift(self):
  x=copy.deepcopy(self.r199)
  x["plans"][0]["policy_paths"][0]["annual_rows"][0]["projects_started_ids"]=[]
  self.raises_hold(lambda:scenario_book(self.desk,x),"R199_ANNUAL_PAIR_MISMATCH")
 def test_r199_duplicate_pair(self):
  x=copy.deepcopy(self.r199)
  x["plans"][0]["policy_paths"].append(copy.deepcopy(x["plans"][0]["policy_paths"][0]))
  self.raises_hold(lambda:scenario_book(self.desk,x),"THREE_POLICY_51")
 def test_profile_mutation_stops_before_screening(self):
  x=copy.deepcopy(self.profile)
  x["sources"]["r149"]["sha256"]="0"*64
  self.raises_hold(lambda:analyze(x,PROFILE),"SOURCE_SHA_r149")

if __name__=="__main__":unittest.main()
