#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
exec python3 -I -B "$HERE/census_r226.py" "$@"
