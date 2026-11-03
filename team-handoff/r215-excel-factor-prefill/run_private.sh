#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
HISTORICAL="$HOME/Downloads/X-Challenge 2026 Tesztforduló_Jutalom a nap végén_Tesztforduló_Z (1).xlsx"
test -f "$HISTORICAL" || { echo HOLD_HISTORICAL_EXCEL_MISSING;exit 4; }
exec python3 -I -B "$HERE/factors_r215.py" --historical-workbook "$HISTORICAL" "$@"
