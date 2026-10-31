#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
cd "$(dirname -- "${BASH_SOURCE[0]}")"
exec python3 -I -B tools/qualify_r161.py
