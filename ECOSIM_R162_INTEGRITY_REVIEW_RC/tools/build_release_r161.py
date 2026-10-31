#!/usr/bin/env python3
"""Build a reproducible, self-contained ZIP from a qualified R161 directory.

Does not modify release inputs. Only writes the ZIP path provided by operator.
"""
from __future__ import annotations
import argparse
import sys
# The builder must not write __pycache__ into the immutable source tree.
sys.dont_write_bytecode = True
from pathlib import Path
import zipfile
from release_guard_r161 import verify_tree,verify_zip,inventory


def build(source,output):
    source=Path(source).resolve(strict=True)
    output=Path(output).resolve()
    if output.is_relative_to(source):
        raise ValueError('ZIP destination must be outside the release directory')
    if output.exists():raise ValueError('Refuse overwrite of existing immutable ZIP')
    verify_tree(source)
    files=inventory(source)
    output.parent.mkdir(parents=True,exist_ok=True)
    try:
        with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=True) as z:
            for relative in sorted(files):
                info=zipfile.ZipInfo(source.name+'/'+relative,date_time=(2026,10,31,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED
                info.external_attr=(0o100644 << 16)
                info.create_system=3
                z.writestr(info,(source/relative).read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
        return verify_zip(output,source)
    except BaseException:
        if output.exists():output.unlink()
        raise


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',default=str(Path(__file__).resolve().parent.parent))
    p.add_argument('--output',required=True)
    a=p.parse_args()
    result=build(a.root,a.output)
    print('R161_REPRODUCIBLE_ZIP=PASS',result)
if __name__=='__main__':main()
