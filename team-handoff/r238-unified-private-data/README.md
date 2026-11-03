# R238 – Unified private EcoSim P1 observational data intake

**User intent:** gather all actual available source data first. Do not run the
five-year optimizer until the necessary data have been collected and verified.
No new UI permissions or game interaction are required for this source join.

## Reuse, not a second simulator

R238 reuses the ORIGINAL R162 35-card JSON and ORIGINAL R228 XLSX parser.
It consolidates source artifacts, not synthetic scenario outputs, into one
strictly PRIVATE P1 JSON data file.

Includes:

- All 374 labelled rows of the original 7-team Excel, including 324 numeric
  values for our team's P0 and unaltered other team cell strings.
- All 35 historical project card descriptions, prices, visible factor effects,
  display conditions, plus separately observed partial R156 states.
- 29 detailed city factors (P0 facts, P1 plans), and separate aggregate
  P0 51.96 / P1 plan 52.48; CSV row 30 is the aggregate index.
- Original, SHA-matching 10 selected/default main-page snapshots of R226
  and the 27 selector labels which are NOT 27 independently captured views.
- R234 23 distinct observed P1 input controls, 19 unambiguous Excel P0
  crosswalks, and 4 unresolved crosswalks.
- R224 financial P0 and P1 plan values, explicitly NOT a confirmed
  first-year spendable budget.
- R235 partial client school minima and unknown education spending multipliers.
- A newer READ-ONLY browser text of the open Income/Taxes subview, kept
  separate from earlier Income/Services. Serialized HTML input attributes
  are not necessarily the current React-rendered values or saved decisions.

Every file and each view is source SHA-linked and the PRIVATE output bundle
has a reproducible SHA-256 in its receipt.

## Not a complete current-year read

The ten default/selected screens are source-verified, but alternate subviews
remain missing. Historical 35-card captures span more than 100 minutes, so
R192 same-hour capture remains HOLD. Current market rules, verified server
project cap, tax bounds, spendable funding, actual approved P1 decisions,
and causal policy factor/cash responses are still UNKNOWN.
P2-P5 actual facts cannot be observed while the game is in P1.

Do not produce an approved game action from this partial, mixed-freshness
packet. The user has not authorized any game writes, merge or deployment.

## Reproduction on owner Fedora

Private data, kept outside the PUBLIC GitHub repository:

    ~/Downloads/ecosim-r238-pinned-final-private-20261102/ECOSIM_P1_OBSERVED_PRIVATE.json
    ~/Downloads/ecosim-r238-pinned-final-private-20261102/R238_RECEIPT.json

Recreate at a NEW private destination:

    bash team-handoff/r238-unified-private-data/run_private.sh --out-dir "$HOME/Downloads/NEW_ECOSIM_R238_PRIVATE"
    bash team-handoff/r238-unified-private-data/qualify_private.sh

Tests pin the original source hashes, validate the Excel parser and exact
ten-view source crosswalk, the 35 projects, 29 factor pairs, 23 control
inventory, unknown constraints, no overwrite and deterministic replay.

Next best ROI: collect missing alternate subviews and source-verified finance
and market rules through authorized browser controls, not speculative
formula-building. The previous Codex native-browser origin permission was
declined in a distinct session; do not bypass it. ChatGPT Browser's read-only
current tab source remains usable but cannot navigate in Chat mode.

GAME_ACTION_GATE=STOP. NO_GAME_WRITES, NO_SEND, NO_MERGE, NO_DEPLOY.
