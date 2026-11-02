#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
exec python3 -I -B "$HERE/join_current_conditions.py" \
  --r221 "$HOME/Downloads/ecosim-r221-current-source-scenarios-20261102/R221.json" \
  --r222 "$HOME/Downloads/ecosim-r222-current-conditions-20261102/R222_RECEIPT.json" \
  "$@"
