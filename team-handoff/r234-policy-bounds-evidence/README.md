# EcoSim R234 – actual P1 input bounds evidence, fail-closed source gating

## Outcome / reason for this slice

An actual five-year joint **project + tax/tariff/institution** optimizer would
produce fictitious actions unless the current simulation's decision bounds,
selected P1 values and factor/cash response were known. The previous
original R225→R226→R228 inventory already observed **23** P1 numeric input
surfaces; R233 already has **8** organizer-constrained (4 starts/year)
conditional five-year project paths. Do not rebuild the optimizer.

R234 source-joins the existing inventories into a strict, per-field decision
readiness matrix. It does not confuse no data with zero effect or an
available action. The original R145 tracks are documented coverage sentinels,
NOT operator-selected policy decisions. Every one of 23 annual factor/cash
effects remains UNKNOWN for every one of the five future years.

### Evidence established

- Current selected UI subviews: 19 original controls from R226 + 4 actual
  tax controls captured by R228 = 23 distinct controls.
- Original Excel P0 exact label, section and value crosswalk: 19 of 23;
  four other P0 inputs are observed but cannot be uniquely mapped to Excel.
- P1 actual selected decisions: 0/23 proven; numeric P1 min/max: 0/23
  proven; calibrated cash/factor response: 0/23 proven.
- Official Hungarian manual, SHA-pinned: training/development decision change
  may be restricted by period-specific simulator settings; the plus/minus 20%
  in the manual is **an example**, not a current numeric rule.
  Tax categories are subject to statutory maxima; **current rate ceilings
  must come from the live UI**, not assumed legal numeric percentages.
- A historical generic UI table component conditionally merges
  field-level min/max via hardMin/hardMax. This proves the component pattern,
  not that the current 23 EcoSim fields use that path, or what numbers apply.
- R233's P1-plan model and original four-per-year organizer limit remain
  unchanged; no actual P1–P5 city-score forecast or financing authorization.

### Why direct discovery remains blocked

The available connected authenticated Browser view is read-only text of
selected subviews, with blank P1 input values and UI warning symbols. It does
not return an actionable current per-field tooltip/limit object or causal
PLAN→FACT transition. The 35 project cards' earlier timestamp mismatch
remains separately blocked. No DOM click, hover, direct authenticated API,
form edit, or save was used to manufacture numeric min/max or effects.
The current UI evidence is operator-visible, not a server-signed export.

### Private reproduction

On the owner's Fedora, run:

    bash team-handoff/r234-policy-bounds-evidence/run_private.sh --out-dir "$HOME/Downloads/a_NEW_private_R234_result"
    bash team-handoff/r234-policy-bounds-evidence/qualify_private.sh

Actual current private outputs:
- ~/Downloads/ecosim-r234-p1-bounds-evidence-20261102/R234_RECEIPT.json
- ~/Downloads/ecosim-r234-p1-bounds-evidence-20261102/R234_P1_SOURCE_MATRIX_PRIVATE.csv
- ~/Downloads/ecosim-r234-p1-bounds-evidence-20261102/R234_HU.md

Tests validate original R225/R226/R228/R233 source SHA links, Excel P0,
four actual tax rows, the complete original R145 five-year UNKNOWN contract,
handbook quotes, conservative rule classifications, and reject forged bounds,
cash impacts, policy approval and private-output overwrite.

## Highest-value next external evidence

Safe, explicit read-only observation of the **current-period per-field
numeric constraint tooltip / underlying published market rule**, prioritizing
the tax limits and the institution training/development control.
After later P1 decisions/FACTs are observed, calibrate one source-matched
cash/factor response with the existing R153/R154 and R145/R148 code.
Do not infer a causal response from one baseline P0/P1 pair.

Security: This PUBLIC repository receives only generic source/tests.
All source snapshots, game Excel, private receipts/CSV, player identity,
session data and calculation outputs stay off Git. NO_GAME_WRITES, NO_MERGE,
NO_DEPLOY; original R191/R192/R214 GAME_ACTION_GATE=STOP.
