"""Real CLI bootstrap/integrity tests, not native R162 E2E."""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]
REPO_HANDOFF = HERE.parent
RUNNER = HERE / 'tools' / 'run_r191_shadow.py'
ORIGINAL = REPO_HANDOFF / 'r189-r190' / 'tools' / 'bounded_shadow_r189.py'
EXPECTED = '5042d7da2d762bd393ab0e6848acee46e2bdbae8'


def invoke(root):
    return subprocess.run([sys.executable, '-B', str(root/'r191-live-admission/tools/run_r191_shadow.py'), '--help'],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)


class R194Bootstrap(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'team-handoff'
        (self.root/'r189-r190/tools').mkdir(parents=True)
        (self.root/'r191-live-admission/tools').mkdir(parents=True)
        shutil.copy2(ORIGINAL, self.root/'r189-r190/tools/bounded_shadow_r189.py')
        for item in (HERE/'tools').glob('*.py'):
            if item.name == 'bounded_shadow_r189.py':
                continue
            shutil.copy2(item, self.root/'r191-live-admission/tools'/item.name)

    def test_release_path_has_only_one_r189_source(self):
        self.assertTrue(ORIGINAL.is_file())
        self.assertFalse((HERE/'tools/bounded_shadow_r189.py').exists())

    def test_git_blob_matches_reviewed_r189(self):
        data = ORIGINAL.read_bytes()
        actual = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        self.assertEqual(actual,EXPECTED)

    def test_python_cli_bootstrap_real_layout_pass(self):
        r = invoke(self.root)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn('--mode',r.stdout)
        self.assertIn('--r156-bundle',r.stdout)
        self.assertIn('--current-card-catalog',r.stdout)

    def test_sibling_missing_fail_closed(self):
        (self.root/'r189-r190/tools/bounded_shadow_r189.py').unlink()
        r=invoke(self.root)
        self.assertNotEqual(r.returncode,0)
        self.assertIn('HOLD=PINNED_R189_SIBLING_SOURCE_MISSING_OR_UNSAFE',r.stderr)

    def test_sibling_tamper_fail_closed(self):
        p=self.root/'r189-r190/tools/bounded_shadow_r189.py'
        p.write_bytes(p.read_bytes()+b'\n# tampered\n')
        r=invoke(self.root)
        self.assertNotEqual(r.returncode,0)
        self.assertIn('HOLD=UNREVIEWED_R189_SOURCE_DRIFT',r.stderr)

    def test_sibling_symlink_fail_closed(self):
        p=self.root/'r189-r190/tools/bounded_shadow_r189.py'
        p.unlink()
        p.symlink_to(ORIGINAL)
        r=invoke(self.root)
        self.assertNotEqual(r.returncode,0)
        self.assertIn('HOLD=PINNED_R189_SIBLING_SOURCE_MISSING_OR_UNSAFE',r.stderr)

    def test_malicious_pythonpath_does_not_preempt_sibling_source(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d,'bounded_shadow_r189.py').write_text('raise RuntimeError("UNSAFE")\n')
            env=dict(os.environ,PYTHONPATH=d)
            r=subprocess.run([sys.executable,'-B',str(self.root/'r191-live-admission/tools/run_r191_shadow.py'),'--help'],
                env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=10)
            self.assertEqual(r.returncode,0,r.stderr)

    def test_syntax_compile(self):
        import ast
        for p in [RUNNER,HERE/'tools/admission_r191.py',HERE/'tools/catalog_gate_r192.py',HERE/'tools/hungarian_decision_r193.py',ORIGINAL]:
            ast.parse(p.read_text())

    def test_native_launcher_syntax(self):
        r=subprocess.run(['bash','-n',str(HERE/'run_native_r162_r193.sh')],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)

if __name__=='__main__': unittest.main()
