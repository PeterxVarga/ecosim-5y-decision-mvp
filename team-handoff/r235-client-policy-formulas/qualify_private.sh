#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
export R235_JS="$HOME/Downloads/ECOSIM_R142A_CODEX_GATES/private_js/840.41fdc8e1.chunk.js"
export R235_PAGE="$HOME/Downloads/ecosim-r225-periodic-current-20261102/institutions_education.txt"
export R235_R225="$HOME/Downloads/ecosim-r225-periodic-qualification-v2-20261102/R225_RECEIPT.json"
export R235_R226="$HOME/Downloads/ecosim-r226-final-census-20261102/R226_RECEIPT.json"
export R235_R234="$HOME/Downloads/ecosim-r234-p1-bounds-evidence-20261102/R234_RECEIPT.json"
export R235_MANIFEST="$HOME/Downloads/ecosim-r223-fresh-r156-20261102/r156_immutable/manifest.json"
export R235_OUT="$HOME/Downloads/ecosim-r235-static-formulas-20261102"
test -f "$R235_OUT/R235_RECEIPT.json" || { echo "HOLD_R235_MISSING_PRIVATE_OUTPUT"; exit 3; }
python3 -I -B "$HERE/test_derive_r235.py"
echo R235_PARTIAL_CLIENT_BOUNDS=PASS_4_LOWER_2_SYMBOLIC
echo GAME_ACTION_GATE=STOP
