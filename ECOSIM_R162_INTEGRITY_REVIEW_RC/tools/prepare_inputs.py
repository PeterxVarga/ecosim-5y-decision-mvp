#!/usr/bin/env python3
"""Offline SHA-256 pinned extraction of an existing, local R140B static archive."""
import hashlib, json, os, sys, zipfile
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent
DEFAULT=Path.home()/"Downloads/ecosim-r140b-assets/ECOSIM_R140B_STATIC_EVIDENCE.zip"
SRC=Path(os.environ.get("R140B_ZIP",str(DEFAULT))).expanduser()
TARGET=BASE/"private_js"
PIN=json.loads((BASE/"data/source_sha256.json").read_text())
if not SRC.is_file() or SRC.is_symlink():
    sys.exit(f"R143_BLOCKED=STATIC_EVIDENCE_ZIP_MISSING ({SRC})")
if TARGET.is_symlink(): sys.exit("R143_BLOCKED=JS_TARGET_SYMLINK")
TARGET.mkdir(exist_ok=True)
with zipfile.ZipFile(SRC) as z:
    names=z.namelist()
    for filename,sha in PIN.items():
        key="js/"+filename
        if key not in names: sys.exit(f"R143_BLOCKED=MISSING_JS_IN_ARCHIVE {filename}")
        info=z.getinfo(key)
        if info.file_size>6_000_000: sys.exit("R143_BLOCKED=SIZE_LIMIT")
        b=z.read(key)
        if hashlib.sha256(b).hexdigest()!=sha: sys.exit(f"R143_BLOCKED=SHA_MISMATCH {filename}")
        target=TARGET/filename
        if target.is_symlink(): sys.exit("R143_BLOCKED=TARGET_SYMLINK")
        if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()!=sha:
            sys.exit("R143_BLOCKED=TARGET_CONFLICT")
        target.write_bytes(b)
        target.chmod(0o444)
receipt={"source_zip":str(SRC),"source_zip_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),"js_count":len(PIN),"js_sha256":PIN,"all_hashes_match":True,"no_live_access":True}
(BASE/"results").mkdir(exist_ok=True)
(BASE/"results"/"SOURCE_PREFLIGHT.json").write_text(json.dumps(receipt,indent=2)+'\n')
print(f"R143_SOURCE_PREFLIGHT=PASS JS_FILES={len(PIN)} ZIP_SHA256={receipt['source_zip_sha256']}")
