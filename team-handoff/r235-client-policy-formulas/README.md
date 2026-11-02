# R235 — source-proven partial P1 client decision bounds

## Evidence and correction

The screenshot supplied by the operator shows rendered P1 defaults for the
four tax fields (2, 1.9, 1.1 and 0.5) alongside the P0 values.
Previous connected-browser text extraction reported an empty HTML input value;
that static representation is not necessarily the live rendered input value.
Neither observation proves that the defaults were separately changed and saved.
No input value or save state was changed in this round.

Original R234: 23 UI control surfaces and ZERO fully verified current numeric
min/max pairs. New source-anchored knowledge:

- Historical client bundle 840.41fdc8e1.chunk.js, exact SHA-pinned,
  inspected WITHOUT executing game code.
- Four education institution count-change fields share the CLIENT formula:
  minimum change = 1 - previous period school count.
  P0 counts 7, 13, 16 and 10 from the original R225 current visible page
  imply -6, -12, -15 and -9 as PROVISIONAL client-side lower bounds
  for year 1. Upper bounds and server validation remain UNKNOWN.
- Education training uses prior amount multiplied by current-period
  market.institutions.education.decisions.training.min/max[period].
  Development uses the corresponding development min/max multipliers.
  Prior visible amounts: 12,000 and 50,000. The partial R156 bundle does
  NOT contain the necessary market.institutions configuration, so no
  numeric training/development range is presently available.
- Historical tax table uses four generic input field paths without an
  explicit local limit callback. Other shared/client/backend/market rules
  can still apply. This is NOT evidence of unlimited tax rates.

## Native private reproduction

Private receipt and Hungarian report (NOT for public Git):

    ~/Downloads/ecosim-r235-static-formulas-20261102/R235_RECEIPT.json
    ~/Downloads/ecosim-r235-static-formulas-20261102/R235_HU.md

Recreate from existing immutable sources:

    bash team-handoff/r235-client-policy-formulas/run_private.sh --out-dir "$HOME/Downloads/NEW_R235_RESULT"
    bash team-handoff/r235-client-policy-formulas/qualify_private.sh

Checks: original R225/R226/R234 chain, exact historical JS SHA, matching P0
institution count, symbolic min/max formula, and no promotion to a verified
live range or authorized game action. Forged sources and overwrite fail closed.

Next highest-value external evidence: the actual per-period market education
training/development multipliers and tax legal/UI limits, obtained READ ONLY.
For calibration, wait for an observed matching P1 PLAN to P1 FACT transition.
R191/R192/R214 HOLD, R145 factor/cash policy effects UNKNOWN.
GAME_ACTION_GATE=STOP, NO_GAME_WRITES, NO_MERGE, NO_DEPLOY.
