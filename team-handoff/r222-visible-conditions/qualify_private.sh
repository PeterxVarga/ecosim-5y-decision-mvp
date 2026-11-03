#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
HERE="$(cd -- "$(dirname -- "$0")" && pwd)"
export R222_PAGES="$HOME/Downloads/ecosim-r217-live-readonly-20261102"
export R222_R217="$HOME/Downloads/ecosim-r217-current-admission-20261102"
export R222_R220="$HOME/Downloads/ecosim-r220-all-35-current-source-20261102/R220_RECEIPT.json"
export R222_RULEBOOK="$HOME/Downloads/ecosim-r221-rulebook-readonly-20261102/rulebook_hu.pdf"
export R222_OUTPUT="$HOME/Downloads/ecosim-r222-current-conditions-20261102"
export R222_R221="$HOME/Downloads/ecosim-r221-current-source-scenarios-20261102/R221.json"
export R222_RECEIPT="$R222_OUTPUT/R222_RECEIPT.json"
export R222_JOIN="$HOME/Downloads/ecosim-r222-current-dependency-join-20261102/R222_DEPENDENCY_JOIN.json"
python3 -I -B "$HERE/test_conditions_r222.py"
python3 -I -B "$HERE/test_r221_join.py"
echo "R222_CURRENT_SOURCE_E2E=PASS_35_CARD_2_VISIBLE_DEPENDENCIES_AND_120_PLANNED_YEARS"
echo "R192_GATE=HOLD_CATALOG_NOT_SAME_PERIOD_CAPTURE_WINDOW"
echo "GAME_ACTION_GATE=STOP"
