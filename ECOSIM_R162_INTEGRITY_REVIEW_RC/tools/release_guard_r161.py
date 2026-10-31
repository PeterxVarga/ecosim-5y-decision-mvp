#!/usr/bin/env python3
"""R161 immutable-release integrity guard. No network, no game access.

SHA256SUMS is intentionally NOT self-hashed; the delivery manifest hashes it.
The delivery manifest itself is not recursively hashed; the ZIP's published
SHA256 provides the artifact level reference.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import zipfile

ROOT=Path(__file__).resolve().parent.parent
MANIFEST='R161_RELEASE_MANIFEST.json'
SUMS='SHA256SUMS'
DANGEROUS={'id_rsa','id_ed25519','cookies.json','localstorage.json','session.json','.env','.env.local','.npmrc','credentials.json','service_account.json'}
MAX_FILE=12_000_000


def sha_bytes(data):return hashlib.sha256(data).hexdigest()


def allowed_rel(name):
    if not isinstance(name,str) or not name or '\\' in name or '\x00' in name:
        raise ValueError('R161_INVALID_RELEASE_PATH')
    path=PurePosixPath(name)
    if path.is_absolute() or name.startswith('./') or '..' in path.parts or str(path)!=name or len(path.parts)>12:
        raise ValueError('R161_PATH_TRAVERSAL_OR_NONCANONICAL')
    if any(p in ('.git','__pycache__','.pytest_cache','.venv','node_modules') for p in path.parts):
        raise ValueError('R161_TRANSIENT_OR_PRIVATE_PATH')
    if path.name.lower() in DANGEROUS or path.name.lower().endswith(('.pem','.key','.p12','.pfx','.sqlite')):
        raise ValueError('R161_CREDENTIAL_OR_PRIVATE_FILE_NAME')
    return name


def inventory(folder):
    base=Path(folder).resolve(strict=True)
    if not base.is_dir():raise ValueError('R161_NOT_A_DIRECTORY')
    found={}
    for p in base.rglob('*'):
        rel=p.relative_to(base).as_posix()
        allowed_rel(rel)
        if p.is_symlink():raise ValueError('R161_SYMLINK_FORBIDDEN: '+rel)
        if p.is_dir():continue
        if not p.is_file():raise ValueError('R161_SPECIAL_FILE_FORBIDDEN: '+rel)
        if p.stat().st_size>MAX_FILE:raise ValueError('R161_OVERSIZED_RELEASE_FILE: '+rel)
        found[rel]=sha_bytes(p.read_bytes())
    return found


def validate_sums(content):
    found={}
    for line in content.splitlines():
        if not re.fullmatch(r'[0-9a-f]{64}  .+',line):raise ValueError('R161_BAD_CHECKSUM_LINE')
        digest,name=line.split('  ',1)
        allowed_rel(name)
        if name in found:raise ValueError('R161_DUPLICATE_CHECKSUM_PATH')
        found[name]=digest
    return found


def verify_tree(folder):
    folder=Path(folder).resolve(strict=True)
    files=inventory(folder)
    if SUMS not in files or MANIFEST not in files:raise ValueError('R161_MANIFEST_MISSING')
    expected=validate_sums((folder/SUMS).read_text(encoding='utf-8'))
    if set(expected)!=set(files)-{SUMS,MANIFEST}:
        raise ValueError('R161_RELEASE_FILE_SET_MISMATCH')
    for name,hash_ in expected.items():
        if files[name]!=hash_:raise ValueError('R161_CONTENT_HASH_MISMATCH: '+name)
    meta=json.loads((folder/MANIFEST).read_text(encoding='utf-8'))
    if meta.get('schema')!='ECOSIM_R161_IMMUTABLE_OFFLINE_RELEASE_V1' or meta.get('qualifier')!='PASS_OFFLINE_ONLY':
        raise ValueError('R161_INVALID_RELEASE_METADATA')
    if meta.get('sha256sums_sha256')!=files[SUMS] or meta.get('file_count')!=len(expected):
        raise ValueError('R161_RELEASE_METADATA_MISMATCH')
    if meta.get('gameplay_gate')!='STOP' or meta.get('game_actions')!=0 or meta.get('live_eco_sim_data_verified') is not False:
        raise ValueError('R161_UNAUTHORIZED_LIVE_GAME_CLAIM')
    return {'schema':'ECOSIM_R161_RELEASE_VERIFICATION_V1','status':'PASS_OFFLINE_ONLY',
            'sha256sums_sha256':files[SUMS],'manifest_sha256':files[MANIFEST],
            'checked_files':len(expected),'gameplay_gate':'STOP'}


def verify_zip(archive,folder):
    root_name=Path(folder).name
    expected=inventory(folder)
    with zipfile.ZipFile(archive) as z:
        seen=set()
        for member in z.infolist():
            name=member.filename
            if name.endswith('/'):
                # ZIP releases contain files only, no directory entries.
                raise ValueError('R161_ZIP_DIRECTORY_ENTRY_NOT_CANONICAL')
            if not name.startswith(root_name+'/'):
                raise ValueError('R161_ZIP_ROOT_UNEXPECTED')
            rel=name[len(root_name)+1:]
            allowed_rel(rel)
            if rel in seen:raise ValueError('R161_ZIP_DUPLICATE_MEMBER')
            seen.add(rel)
            mode=member.external_attr >> 16
            if stat.S_IFMT(mode)==stat.S_IFLNK:raise ValueError('R161_ZIP_SYMLINK')
            if member.file_size>MAX_FILE:raise ValueError('R161_ZIP_OVERSIZED_MEMBER')
            if rel not in expected:raise ValueError('R161_ZIP_UNEXPECTED_MEMBER')
            if sha_bytes(z.read(member))!=expected[rel]:
                raise ValueError('R161_ZIP_CONTENT_MISMATCH: '+rel)
        if seen!=set(expected):raise ValueError('R161_ZIP_MISSING_MEMBER')
    return {'zip_sha256':sha_bytes(Path(archive).read_bytes()),'zip_verified_files':len(expected)}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',default=str(ROOT));p.add_argument('--zip')
    a=p.parse_args();receipt=verify_tree(a.root)
    if a.zip:receipt.update(verify_zip(a.zip,a.root))
    print(json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2))
if __name__=='__main__':main()
