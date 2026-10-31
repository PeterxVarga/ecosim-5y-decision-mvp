#!/usr/bin/env python3
"""Optional strict offline source anchor verification; no JS execution or networking."""
from __future__ import annotations
from pathlib import Path
import argparse,json,hashlib
ROOT=Path(__file__).resolve().parent.parent

def audit(source_path,manifest_path=None):
    manifest=json.loads((Path(manifest_path) if manifest_path else ROOT/'evidence/R147_SOURCE_ANCHORS.json').read_text())
    origin=Path(source_path)
    folder=origin if origin.is_dir() else origin.parent
    verified={}
    for filename,digest in manifest['file_hashes'].items():
        path=folder/filename
        b=path.read_bytes()
        if hashlib.sha256(b).hexdigest()!=digest:
            raise ValueError('Source SHA256 mismatch: '+filename)
        verified[filename]=b
    for item in manifest['anchor_records']:
        b=verified[item['filename']]
        frag=b[item['byte_start']:item['byte_end']]
        if hashlib.sha256(frag).hexdigest()!=item['sha256']:
            raise ValueError('Missing or altered code span: '+item['id'])
    return {'schema':'ECOSIM_R147_SOURCE_ANCHOR_VERIFICATION_V2',
            'source_file_sha256':manifest['file_hashes'],
            'anchors_checked':len(manifest['anchor_records']),'matching':True,
            'code_executed':False,'no_game_actions':True}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source',required=True);parser.add_argument('--out');ns=parser.parse_args()
    r=audit(ns.source)
    if ns.out:
        p=Path(ns.out);p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(r,indent=2)+'\n')
    print('R147_SOURCE_ANCHORS=PASS; spans='+str(r['anchors_checked']))
if __name__=='__main__':main()
