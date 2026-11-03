#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
PAGES=""
R156=""
OUT=""
while (( $# ));do
  case "$1" in
    --pages-dir) PAGES="${2:?}";shift 2;;
    --r156-dir) R156="${2:?}";shift 2;;
    --out-dir) OUT="${2:?}";shift 2;;
    *) echo "HOLD_UNEXPECTED_ARG" >&2;exit 2;;
  esac
done
test -n "$PAGES" && test -n "$R156" && test -n "$OUT" || { echo "HOLD_REQUIRED_INPUT";exit 2; }
test -d "$PAGES" && test -d "$R156" && test ! -L "$PAGES" && test ! -L "$R156" &&
test ! -e "$OUT" && test ! -L "$OUT" || { echo "HOLD_PRIVATE_PATH_REQUIREMENT";exit 3; }
exec python3 -I -B "$HERE/intake_r225.py" --pages-dir "$PAGES" --r156-dir "$R156" --out-dir "$OUT"
