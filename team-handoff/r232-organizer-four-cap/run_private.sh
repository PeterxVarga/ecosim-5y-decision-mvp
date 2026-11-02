#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
test "$#" -eq 2 && test "$1" = "--out-dir" || { echo "USAGE: $0 --out-dir NEW_PRIVATE_RESULT_DIR" >&2; exit 2; }
test ! -e "$2" && test ! -L "$2" || { echo "HOLD_NO_OVERWRITE" >&2; exit 2; }
exec python3 -I -B "$HERE/organizer_cap_r232.py" \
 --manifest "$HOME/Downloads/ecosim-r223-fresh-r156-20261102/r156_immutable/manifest.json" \
 --r224 "$HOME/Downloads/ecosim-r224-source-anchored-finance-20261102/R224_RECEIPT.json" \
 --r228 "$HOME/Downloads/ecosim-r228-finance-joined-20261102/R228_RECEIPT.json" \
 --r231 "$HOME/Downloads/ecosim-r231-finance-semantics-20261102/R230_READINESS_PRIVATE.json" \
 --track "$HOME/Downloads/ecosim-r228-finance-joined-20261102/R228_POLICY_UNKNOWN_CONTRACT_TEST_ONLY.json" \
 --out-dir "$2"
