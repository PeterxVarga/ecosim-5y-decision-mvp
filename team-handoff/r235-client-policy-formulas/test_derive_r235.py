#!/usr/bin/env python3
"""Source-anchored P1 partial client bounds, no false full-game admission."""
import copy,json,os,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from derive_r235 import build,SCHEMA
from json_integrity_r162 import read_json
class ClientBoundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src={k:Path(os.environ["R235_"+k]) for k in
                 ("JS","PAGE","R225","R226","R234","MANIFEST","OUT")}
        cls.saved=read_json(cls.src["OUT"]/"R235_RECEIPT.json")
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory(prefix="r235-test-")
        self.temp=Path(self.temporary.name)
    def tearDown(self):self.temporary.cleanup()
    def runnew(self,**kw):
        p=self.src
        args=dict(jsfile=p["JS"],source_page=p["PAGE"],r225_file=p["R225"],
                  r226_file=p["R226"],r234_file=p["R234"],
                  manifest=p["MANIFEST"],out=self.temp/"new")
        args.update(kw)
        return build(**args)
    def test_source_derived_four_school_minimums(self):
        v=self.saved
        self.assertEqual(v["schema"],SCHEMA)
        self.assertEqual([r["derived_client_min_change"] for r in
                          v["school_change_client_lower_bounds"]],[-6,-12,-15,-9])
        self.assertEqual([r["previous_period_school_count"] for r in
                          v["school_change_client_lower_bounds"]],[7,13,16,10])
        self.assertEqual(v["school_client_lower_bound_count"],4)
        self.assertTrue(all(not s["complete_allowed_range"]
                            and not s["usable_as_approved_game_action"]
                            and s["client_max_change"] is None
                            and s["server_attested_current_min"] is None
                            for s in v["school_change_client_lower_bounds"]))
    def test_training_development_market_factors_unobserved(self):
        v=self.saved
        self.assertEqual(v["symbolic_range_count"],2)
        self.assertEqual([x["previous_value_p0"] for x in
                          v["institution_annual_training_development_symbolic_bounds"]],
                         [12000,50000])
        self.assertTrue(all(x["current_market_multiplier_min"] is None and
                            x["current_market_multiplier_max"] is None and
                            x["current_client_min_amount"] is None and
                            x["current_client_max_amount"] is None and
                            x["server_attested_current_bounds"] is None and
                            not x["universal_plus_minus_20_percent"]
                            for x in v["institution_annual_training_development_symbolic_bounds"]))
    def test_tax_missing_explicit_limit_is_not_unlimited(self):
        v=self.saved
        self.assertTrue(v["four_tax_client_table_has_no_explicit_limit_callback"])
        self.assertTrue(v["tax_server_legal_ceiling_unknown"])
        self.assertTrue(v["tax_current_effective_saved_p1_unknown"])
        self.assertTrue(v["rendered_p1_may_differ_from_HTML_VALUE_ATTRIBUTE"])
        self.assertTrue(v["screenshot_seen_in_chat_not_source_attested_by_this_local_runner"])
    def test_r234_full_live_admission_stays_hold(self):
        v=self.saved
        self.assertEqual(v["original_r234_current_verified_full_minmax_pairs"],0)
        self.assertTrue(v["client_partial_bound_does_not_promote_R234_numeric_pair_count"])
        self.assertIsNone(v["real_accepted_policy_actions"])
        self.assertIsNone(v["policy_cash_and_factor_effects"])
        self.assertEqual(v["gameplay_gate"],"STOP")
        self.assertEqual(v["game_writes"],0)
    def test_source_shas_exact(self):
        from source_join_r228 import digest
        for k,p in [('client_historical_840_js','JS'),
            ('visible_institutions_text','PAGE'),('R225','R225'),
            ('R226','R226'),('R234','R234'),('R156_manifest','MANIFEST')]:
            self.assertEqual(self.saved["source_sha256"][k],digest(self.src[p]))
    def test_forged_js_rejected(self):
        new=self.temp/"modified.js"
        new.write_bytes(self.src["JS"].read_bytes()+b"\n")
        with self.assertRaisesRegex(ValueError,"HOLD_HISTORICAL_CLIENT_EXACT_SHA"):
            self.runnew(jsfile=new)
    def test_forged_p0_school_count_rejected(self):
        new=self.temp/"changed.txt"
        src=self.src["PAGE"].read_text()
        self.assertIn("<td>Szám</td><td>7</td>",src)
        new.write_text(src.replace("<td>Szám</td><td>7</td>",
                                   "<td>Szám</td><td>8</td>",1))
        with self.assertRaisesRegex(ValueError,"HOLD_R225_R226_PAGE_SOURCE_CHAIN"):
            self.runnew(source_page=new)
    def test_forged_admitted_r234_rejected(self):
        new=self.temp/"r234.json"
        src=copy.deepcopy(read_json(self.src["R234"]))
        src["current_numeric_minmax_pairs_verified"]=4
        new.write_text(json.dumps(src,ensure_ascii=False))
        # A partial historical client bound is not a R234 verified live pair.
        with self.assertRaisesRegex(ValueError,"HOLD_ORIGINAL_R234_SOURCE_AND_STOP"):
            self.runnew(r234_file=new)
    def test_original_directory_preserved(self):
        with self.assertRaisesRegex(ValueError,"HOLD_NEW_PRIVATE_RESULT"):
            self.runnew(out=self.src["OUT"])
    def test_reproduction_exact(self):
        r=self.runnew()
        self.assertEqual(r,self.saved)
        for name in ("R235_RECEIPT.json","R235_HU.md"):
            self.assertEqual((self.temp/"new"/name).read_bytes(),
                             (self.src["OUT"]/name).read_bytes())
if __name__=="__main__":unittest.main()
