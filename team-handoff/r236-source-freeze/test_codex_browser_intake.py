#!/usr/bin/env python3
"""Fail closed on browser-origin denial, fabricated content or game actions."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from codex_browser_intake import ingest,SCHEMA

class BrowserAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path.home()/"Downloads/ecosim-r236-source-freeze-20261102"
        cls.base=cls.root/"result/R236_PRIVATE_LEDGER.json"
        cls.input=cls.root/"codex-current-tabs-readonly-v1.txt"
        cls.saved=cls.root/"codex-browser-gated-v1"
        cls.data=json.loads(cls.input.read_text())
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="r236-codex-gate-")
        self.path=Path(self.tmp.name)
    def tearDown(self):
        self.tmp.cleanup()
    def modified(self,patch):
        v=copy.deepcopy(self.data);patch(v)
        src=self.path/"edited.json";src.write_text(json.dumps(v,ensure_ascii=False))
        return ingest(self.base,src,self.path/"out")
    def test_readonly_current_origin_declined(self):
        a=json.loads((self.saved/"R236_CODEX_BROWSER_INTAKE_PRIVATE.json").read_text())
        self.assertEqual(a["schema"],SCHEMA)
        self.assertEqual(a["status"],"PARTIAL_NATIVE_BROWSER_AUTH_BLOCKED")
        self.assertEqual(a["observed_approved_ecosim_tabs"],0)
        self.assertEqual(a["origin_blocked_ecosim_tabs"],1)
        self.assertTrue(a["requires_owner_browser_origin_permission"])
        self.assertTrue(a["no_user_permission_bypass_attempted"])
        self.assertFalse(a["data_frozen_for_final_optimization"])
        self.assertFalse(a["run_optimizer"])
        self.assertEqual(a["game_writes"],0)
    def test_unapproved_observation_not_promoted(self):
        def edit(x):
            x["ecosim_tabs"][0]["read_status"]="OBSERVED"
            x["ecosim_tabs"][0]["table_count"]=2
            x["ecosim_tabs"][0]["input_count"]=4
            x["ecosim_tabs"][0]["active_section"]="Adók"
        with self.assertRaisesRegex(ValueError,"HOLD_OBSERVED_CURRENT_PERIOD_SOURCE_REQUIRED"):
            self.modified(edit)
    def test_inferred_blocked_values_rejected(self):
        with self.assertRaisesRegex(ValueError,"HOLD_BLOCKED_MUST_NOT_CONTAIN_INFERRED_DATA"):
            self.modified(lambda x:x["ecosim_tabs"][0].update(input_count=4))
    def test_navigation_and_write_rejected(self):
        for key,val in [("browser_navigation",True),("game_writes",1)]:
            with self.assertRaisesRegex(ValueError,"HOLD_CODEX_NO_NAVIGATION_NO_GAME_WRITES"):
                self.modified(lambda x:x.update({key:val}))
    def test_unsafe_path_and_secret_rejected(self):
        with self.assertRaisesRegex(ValueError,"HOLD_STRICT_ECOSIM_PATH_AND_STATUS"):
            self.modified(lambda x:x["ecosim_tabs"][0].update(path="/billing"))
        with self.assertRaisesRegex(ValueError,"HOLD_NO_TOKENS_OR_SECRETS"):
            self.modified(lambda x:x["ecosim_tabs"][0].update(
                observed_text_excerpt="Authorization: Bearer fake-value"))
    def test_no_overwrite(self):
        with self.assertRaisesRegex(ValueError,"HOLD_NEW_PRIVATE_OUTPUT"):
            ingest(self.base,self.input,self.saved)
    def test_replay(self):
        out=ingest(self.base,self.input,self.path/"new")
        old=json.loads((self.saved/"R236_CODEX_BROWSER_INTAKE_PRIVATE.json").read_text())
        self.assertEqual(out,old)
if __name__=="__main__":unittest.main()
