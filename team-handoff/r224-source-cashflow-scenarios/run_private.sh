#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
exec python3 -I -B "$HERE/finance_scenarios_r224.py" \
  --current-pages "$HOME/Downloads/ecosim-r223-fresh-readonly-pages-20261102" \
  --current-r156 "$HOME/Downloads/ecosim-r223-fresh-r156-20261102" \
  --r220-receipt "$HOME/Downloads/ecosim-r220-all-35-current-source-20261102/R220_RECEIPT.json" \
  --r222-receipt "$HOME/Downloads/ecosim-r222-current-conditions-20261102/R222_RECEIPT.json" \
  --rulebook "$HOME/Downloads/ecosim-r221-rulebook-readonly-20261102/rulebook_hu.pdf" \
  "$@"
