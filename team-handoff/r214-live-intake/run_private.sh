#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
exec python3 -I -B "$HERE/run_r214.py" "$@"
