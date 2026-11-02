#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO="$(cd -- "$HERE/../.." && pwd)"
export R215_HISTORICAL_WORKBOOK="$HOME/Downloads/X-Challenge 2026 Tesztforduló_Jutalom a nap végén_Tesztforduló_Z (1).xlsx"
export R215_OTHER_BINARY_COPY="$HOME/Downloads/X-Challenge 2026 Tesztforduló_Jutalom a nap végén_Tesztforduló_Z.xlsx"
test -f "$R215_HISTORICAL_WORKBOOK" && test -f "$R215_OTHER_BINARY_COPY" || exit 4
python3 -I -B -W error::ResourceWarning "$HERE/test_factors_r215.py"
python3 -I -B "$HERE/test_seven_team_r216.py"
export R213_XLSX="$R215_HISTORICAL_WORKBOOK" R213_ORIGINAL_XLSX="$R215_OTHER_BINARY_COPY"
export R213_R156="$REPO/ECOSIM_R162_INTEGRITY_REVIEW_RC/capture/R156_HISTORICAL_TEST_EXPORT.json"
export R213_PROJECTS="$REPO/ECOSIM_R162_INTEGRITY_REVIEW_RC/data/ecosim_projects_20261030.json"
export R213_LOANS="$HOME/Downloads/ecosim-r205-library-evidence/loans.csv"
export R213_R211="$HOME/Downloads/ecosim-r211-qualification-HkHi3Tdj/first/R211.json"
python3 -I -B "$REPO/team-handoff/r213-city-excel/test_city_excel_r213.py"
echo R215_NATIVE_E2E=PASS_MOCK_XLSX_TO_REVIEWABLE_FACTORS
echo GAME_ACTION_GATE=STOP
