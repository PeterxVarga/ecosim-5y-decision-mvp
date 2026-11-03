#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO="$(cd -- "$HERE/../.." && pwd)"
SOURCE="$HOME/Downloads/X-Challenge 2026 Tesztforduló_Jutalom a nap végén_Tesztforduló_Z (1).xlsx"
ORIGINAL="$HOME/Downloads/X-Challenge 2026 Tesztforduló_Jutalom a nap végén_Tesztforduló_Z.xlsx"
R156="$REPO/ECOSIM_R162_INTEGRITY_REVIEW_RC/capture/R156_HISTORICAL_TEST_EXPORT.json"
CARDS="$REPO/ECOSIM_R162_INTEGRITY_REVIEW_RC/data/ecosim_projects_20261030.json"
LOANS="$HOME/Downloads/ecosim-r205-library-evidence/loans.csv"
R211="$HOME/Downloads/ecosim-r211-qualification-HkHi3Tdj/first/R211.json"
EXPECTED="c6cd0681a28872beb556652b584674f442c5105c379f365027ee9dbd3efe69bc"
OLD_EXPECTED="4db0e1b415d5670af1427985eaccb8f9fe0b096c6402a67e1fb41fca21e76667"
for p in "$SOURCE" "$ORIGINAL" "$R156" "$CARDS" "$LOANS" "$R211"; do
    test -f "$p" || { echo "HOLD_REQUIRED_PRIVATE_SOURCE_MISSING";exit 4; }
done
printf '%s  %s\n' "$EXPECTED" "$SOURCE" "$OLD_EXPECTED" "$ORIGINAL" | sha256sum -c -
export R213_XLSX="$SOURCE" R213_ORIGINAL_XLSX="$ORIGINAL"
export R213_R156="$R156" R213_PROJECTS="$CARDS" R213_LOANS="$LOANS" R213_R211="$R211"
python3 -I -B -W error::SyntaxWarning "$HERE/test_city_excel_r213.py"
OUT="$(mktemp -d "$HOME/Downloads/ecosim-r213-qualified-XXXXXXXX")"
for n in first second; do
    python3 -I -B -W error::SyntaxWarning "$HERE/city_excel_r213.py" \
      --workbook "$SOURCE" --identical-earlier-workbook "$ORIGINAL" \
      --expected-workbook-sha "$EXPECTED" --r156 "$R156" \
      --projects "$CARDS" --loans-csv "$LOANS" \
      --r211-historical "$R211" --out-dir "$OUT/$n"
done
cmp "$OUT/first/R213.json" "$OUT/second/R213.json"
cmp "$OUT/first/R213_HU.md" "$OUT/second/R213_HU.md"
echo "R213_NATIVE_E2E=PASS_BYTE_IDENTICAL_HISTORICAL_FULL_CITY_SOURCE"
echo "R213_PRIVATE_RESULT=$OUT/first/R213_HU.md"
echo "GAME_ACTION_GATE=STOP"
