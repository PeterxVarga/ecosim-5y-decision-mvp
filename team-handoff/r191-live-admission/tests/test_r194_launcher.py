"""Executable R194 team dispatcher CLI smoke tests; no fake R162 release claim."""
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT=Path(__file__).resolve().parents[1]/'run_team.sh'

def call(*args):
    return subprocess.run(['bash',str(SCRIPT),*args],text=True,capture_output=True,timeout=10)

class LauncherTests(unittest.TestCase):
    def test_bash_syntax(self):
        r=subprocess.run(['bash','-n',str(SCRIPT)],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)
    def test_help_lists_modes_and_stop(self):
        r=call('--help');self.assertEqual(r.returncode,0)
        self.assertIn('historical',r.stdout)
        self.assertIn('current',r.stdout)
        self.assertIn('GAME_ACTION_GATE=STOP',r.stdout)
    def test_missing_mode_fails(self):
        r=call();self.assertNotEqual(r.returncode,0)
    def test_current_missing_required_files_fails(self):
        r=call('current','--state','/no/r194-state.json','--r156-bundle','/no/r194-bundle',
               '--year1-finance','/no/r194-fin.json','--current-card-catalog','/no/r194-catalog.json',
               '--annual-budget','100000','--cap','4')
        self.assertNotEqual(r.returncode,0)
        self.assertIn('HOLD=CURRENT_OBSERVATION_FILES_MISSING',r.stderr)
    def test_current_missing_flags_fails(self):
        r=call('current','--state');self.assertNotEqual(r.returncode,0)
        self.assertIn('HOLD=MISSING_VALUE',r.stderr)
    def test_unrecognized_flag_fails(self):
        r=call('current','--unsafe','yes');self.assertNotEqual(r.returncode,0)
        self.assertIn('HOLD=UNRECOGNIZED_OPTION',r.stderr)

if __name__=='__main__':unittest.main()
