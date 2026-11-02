#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
test "$#" -eq 2 && test "$1" = "--out-dir" || { echo "USAGE: $0 --out-dir NEW_PRIVATE_DIRECTORY" >&2; exit 2; }
OUT="$2"
test ! -e "$OUT" && test ! -L "$OUT" || { echo "HOLD_NEW_PRIVATE_OUTPUT_REQUIRED" >&2; exit 2; }
exec python3 -I -B "$HERE/readiness_r230.py" \
 --r228 "$HOME/Downloads/ecosim-r228-finance-joined-20261102/R228_RECEIPT.json" \
 --r224 "$HOME/Downloads/ecosim-r224-source-anchored-finance-20261102/R224_RECEIPT.json" \
 --r222 "$HOME/Downloads/ecosim-r222-current-conditions-20261102/R222_RECEIPT.json" \
 --manifest "$HOME/Downloads/ecosim-r223-fresh-r156-20261102/r156_immutable/manifest.json" \
 --out-dir "$OUT"
