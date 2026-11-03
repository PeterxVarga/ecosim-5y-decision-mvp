#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
test "$#" -eq 2 && test "$1" = "--out-dir" || { echo "USAGE: $0 --out-dir NEW_PRIVATE_DIRECTORY"; exit 2; }
test ! -e "$2" && test ! -L "$2" || { echo "HOLD_NO_OVERWRITE"; exit 2; }
exec python3 -I -B "$HERE/derive_r235.py" \
 --jsfile "$HOME/Downloads/ECOSIM_R142A_CODEX_GATES/private_js/840.41fdc8e1.chunk.js" \
 --source-page "$HOME/Downloads/ecosim-r225-periodic-current-20261102/institutions_education.txt" \
 --r225 "$HOME/Downloads/ecosim-r225-periodic-qualification-v2-20261102/R225_RECEIPT.json" \
 --r226 "$HOME/Downloads/ecosim-r226-final-census-20261102/R226_RECEIPT.json" \
 --r234 "$HOME/Downloads/ecosim-r234-p1-bounds-evidence-20261102/R234_RECEIPT.json" \
 --manifest "$HOME/Downloads/ecosim-r223-fresh-r156-20261102/r156_immutable/manifest.json" \
 --out-dir "$2"
