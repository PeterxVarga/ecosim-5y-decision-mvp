#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
SOURCE=""
OUTPUT=""
while (( $# )); do
  case "$1" in
    --pages-dir) SOURCE="${2:?}";shift 2;;
    --out-dir) OUTPUT="${2:?}";shift 2;;
    *) echo "HOLD_UNEXPECTED_ARGUMENT" >&2;exit 2;;
  esac
done
test -n "$SOURCE" && test -n "$OUTPUT" || { echo "HOLD_BOTH_INPUT_OUTPUT_REQUIRED" >&2;exit 2; }
test -d "$SOURCE" && ! test -L "$SOURCE" || { echo "HOLD_SOURCE_DIRECTORY" >&2;exit 3; }
test ! -e "$OUTPUT" && test ! -L "$OUTPUT" || { echo "HOLD_NEW_PRIVATE_OUTPUT" >&2;exit 3; }
mkdir -p -m 700 "$OUTPUT"
python3 -I -B "$HERE/../r217-current-visible-admission/prepare_visible_r217.py" \
  --browser-text-dir "$SOURCE" --out-dir "$OUTPUT/current_r156"
python3 -I -B "$HERE/coherent_r223.py" \
  --pages-dir "$SOURCE" --r156-dir "$OUTPUT/current_r156" \
  --out-dir "$OUTPUT/current_r192"
