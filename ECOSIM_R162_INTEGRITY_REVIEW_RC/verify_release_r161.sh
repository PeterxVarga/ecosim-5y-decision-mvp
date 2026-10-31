#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname -- "${BASH_SOURCE[0]}")"
exec python3 -I -B tools/release_guard_r161.py --root .
