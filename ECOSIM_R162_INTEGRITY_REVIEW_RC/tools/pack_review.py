#!/usr/bin/env python3
"""Package only small, explicitly approved, non-source report filenames."""
import json, re, sys, zipfile
from pathlib import Path
root=Path(__file__).resolve().parent.parent; out=root/'results'
needed=['R143_5Y_MODEL_COVERAGE.md','R143_5Y_FINANCE_GATES.md','R143_CALIBRATION_PLAN.md','R143_SCENARIO_HANDOFF.md','R143_STATUS.json','R143_PROJECT_CASH_CALENDAR.json','R143_READINESS.json','CODEX_LAST.md','SOURCE_PREFLIGHT.json']
for x in needed:
    p=out/x
    if not p.is_file() or p.is_symlink() or p.stat().st_size>500_000:sys.exit(f'R143_BLOCKED=MISSING_OR_OVERSIZED {x}')
    text=p.read_text(errors='replace')
    if re.search(r'(?i)authorization\s*:\s*bearer\s+[-a-zA-Z0-9._=]{20,}',text) or re.search(r'eyJ[a-zA-Z0-9_-]{25,}\.eyJ[a-zA-Z0-9_-]{25,}\.',text):sys.exit('R143_BLOCKED=SUSPECTED_CREDENTIALS')
s=json.loads((out/'R143_STATUS.json').read_text())
if s.get('no_live_actions') is not True or s.get('final_gameplay_decision')!='STOP' or s.get('true_game_model_validated') is not False:sys.exit('R143_BLOCKED=UNSUPPORTED_GO')
p=out/'ECOSIM_R143_5Y_REVIEW.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
    for x in needed:z.write(out/x,x)
print('R143_REVIEW=PASS '+str(p))
