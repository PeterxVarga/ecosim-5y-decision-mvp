#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
SRC="$HOME/Downloads"
AUDIT="$SRC/ecosim-r168-audit/r175b-evidence"
NATIVE="$SRC/ecosim-r199-native-20261102"
R195="/tmp/ecosim-r195-tradeoff-2qiKmOEe"
FIX="$HERE/fixtures"
PROFILE="$HERE/profiles/historical_R94_R199.json"

# Guard BEFORE any source copies, because the destination GitHub repo is public.
for f in "$FIX/institutions_R94_readonly.json" "$FIX/R199_EXACT_PROJECT_POLICY_REPLAY.json" "$PROFILE"; do
  git -C "$REPO" check-ignore -q "$f" || { echo "STOP_UNSAFE_GIT_DESTINATION=$f"; exit 9; }
done
mkdir -p "$FIX" "$HERE/profiles"
copy_if_needed() {
 local src="$1" dst="$2"
 test -s "$src" || { echo "HOLD_MISSING_PRIVATE_TEST_SOURCE=$src"; exit 4; }
 if [[ -e "$dst" ]]; then cmp -s "$src" "$dst" || { echo "HOLD_EXISTING_DIFFERENT_PRIVATE_SOURCE=$dst"; exit 5; }
 else cp -- "$src" "$dst"; fi
}
copy_if_needed "$SRC/ecosim-institutions-20261030T142638Z-125386.json" "$FIX/institutions_R94_readonly.json"
copy_if_needed "$SRC/ecosim-r2-catalog-20261030T143513Z-170146.json" "$FIX/institutions_R94_numeric_catalog.json"
copy_if_needed "$SRC/ecosim-r2-reanalysis-20261030T143513Z-170146.json" "$FIX/institutions_R94_reanalysis.json"
copy_if_needed "$AUDIT/source/CROSSWALK.csv" "$FIX/R175B_factor_crosswalk.csv"
copy_if_needed "$AUDIT/R175B_QUALIFICATION.json" "$FIX/R175B_QUALIFICATION.json"
copy_if_needed "$R195/TRADEOFF.json" "$FIX/R195_TWO_PROJECT_PLANS.json"
copy_if_needed "$NATIVE/native-output/R199.json" "$FIX/R199_EXACT_PROJECT_POLICY_REPLAY.json"
if [[ ! -e "$PROFILE" ]]; then
 python3 -I -B "$HERE/tools/corpus_r200.py" --create-historical-profile "$PROFILE"
fi
OUT="$(mktemp -d "$SRC/ecosim-r200-historical-XXXXXXXX")"
rmdir -- "$OUT"
python3 -I -B "$HERE/tools/corpus_r200.py" --profile "$PROFILE" --out-dir "$OUT"
python3 -I -B -m unittest discover -s "$HERE/tests" -v
echo "R200_PRIVATE_EVIDENCE=$OUT"
echo "R200_REPORT=$OUT/R200_HU.md"
echo "GAME_ACTION_GATE=STOP"
