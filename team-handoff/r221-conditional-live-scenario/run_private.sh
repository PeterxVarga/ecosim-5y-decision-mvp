#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
exec python3 -I -B "$HERE/conditional_r221.py" \
  --r217-receipt "$HOME/Downloads/ecosim-r217-current-admission-20261102/R217_RECEIPT.json" \
  --r220-receipt "$HOME/Downloads/ecosim-r220-all-35-current-source-20261102/R220_RECEIPT.json" \
  --official-rulebook "$HOME/Downloads/ecosim-r221-rulebook-readonly-20261102/rulebook_hu.pdf" \
  --r156-bundle "$HOME/Downloads/ecosim-r217-current-admission-20261102/r156_immutable" \
  "$@"
