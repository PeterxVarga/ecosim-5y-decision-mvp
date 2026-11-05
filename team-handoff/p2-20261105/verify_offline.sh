#!/usr/bin/env bash
# Verify checked-in EcoSim P2 offline artifacts. No browser/game calls and no repository writes.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf -- "$TMP"' EXIT

python3 - "$ROOT" <<'PY'
import hashlib, json, pathlib,sys
base=pathlib.Path(sys.argv[1]); m=json.loads((base/'MANIFEST_SHA256.json').read_text())
for relative, data in m['file_entries'].items():
    p=base/relative
    if not p.is_file(): raise SystemExit(f'MISSING: {relative}')
    if hashlib.sha256(p.read_bytes()).hexdigest()!=data['sha256']:
        raise SystemExit(f'SHA256_MISMATCH: {relative}')
print(f'MANIFEST_FILE_SHA256=PASS count={len(m["file_entries"])}')
PY

for file in p2_joint_screen.py r142_proxy_reference.py effect_replay_r147.py indirect_business_sensitivity.py test_joint_model.py test_indirect_business_sensitivity.py; do
  cp -- "$ROOT/src/$file" "$TMP/$file"
done
for file in P2_joined_input.json P2_joint_scenarios.json P2_indirect_business_sensitivity.json; do
  cp -- "$ROOT/data/$file" "$TMP/$file"
done
(
  cd "$TMP"
  python3 -m unittest -q test_joint_model test_indirect_business_sensitivity
)
for file in test_EcoSim_P2_vallalkozasszam_R3.py; do
  cp -- "$ROOT/src/$file" "$TMP/$file"
done
for file in EcoSim_P2_vallalkozasszam_empirikus_R3_20261105.json EcoSim_P2_vallalkozasszam_forrasmegfigyelesek_20261105.json; do
  cp -- "$ROOT/data/$file" "$TMP/$file"
done
(
  cd "$TMP"
  python3 -m unittest -q test_EcoSim_P2_vallalkozasszam_R3
)
echo "ECOSIM_P2_OFFLINE_RELEASE=PASS 17+14 targeted tests; game_writes=0"
