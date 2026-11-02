# EcoSim R228 — actual R227 Excel → R226/TAX UI → ORIGINAL R145/R148 five-year conditional integration

## Outcome: one existing chain, not a parallel optimizer

This project was previously missing integration of the **374-row Selejtező I
Excel** with currently observed editable P1 decision controls. R228 reuses
the **original R145 policy tracks**, **original R148 project-policy factor
replay**, existing **R224 (24 conditional five-year project scenarios)**,
and read-only R226 19-control current UI source. No new simulator or
parallel optimizer was implemented.

Private **original Excel**:
`~/Downloads/X-Challenge 2026 Selejtező_Jutalom a nap végén_Selejtező_I.xlsx`;
pinned SHA `a130d6606c4488112c8825d79d5fb6aaa65a65f4dca7d1e1f9e4029cdafe53f4`.
The reproducible, standard-library XLSX importer verifies the original
ZIP/XML, seven team names and order, 374 labelled Excel rows and 324
numeric data values for Jutalom a nap végén; never substitutes old Z-market
test values or another team's figures.

Source-linked UI:
- **19** actual R226 UI controls (from ten real top-level views, only
  selected subviews) reused with their exact unique decision keys.
- **4** newly read-only observed current `Bevételek → Adók` inputs with
  P0 values 2%, 1.9%, 1.1%, 0.5%, private normalized UI observation
  `~/Downloads/ecosim-r228-tax-active-view-readonly-20261102.json`.
  This small private observation is *operator-visible*, **not
  server-attested or a true P1 selected decision**.
- **19** control P0 values match the pinned XLSX via **exact Excel
  row ID + section + label + numeric P0 value**. Repeated institution
  `Nyitás / Zárás (+/-)` and two distinct `Karbantartás` rows are
  never heuristically merged.
- **4** observed controls have no unambiguously source-identifiable
  individual Excel decision row: Education→Bérek, Education→Képzés,
  Education→Fejlesztés, Long-term loan delta. Keep these UNKNOWN.
- Excel contains 355 other labelled rows that are *not linked to one
  of 23 observed editable P0 controls*. This does **not** imply 355
  missing actions; many are headers or financial facts.

## Combined original five-year path

All 24 R224 conditional project schedules are passed into the **original
R145 `replay_policy_joint`**, backed by original R148
`combined_factor_replay`. Thus the actual source-linked 5-year
project schedules are evaluated together with the **known absence of
a calibrated policy response**:
- **24 × 5 = 120** annual joint calculation rows
- **23 per-year unknown factor impacts and 23 per-year unknown cash
  impacts remain UNKNOWN** in the original R145 model
- The source-visible controls themselves are only observed on P1.
  The 5-year schema-only UNKNOWN-sentinel is *not a declaration that
  those exact controls exist or have been selected in P2–P5*.
- Conditional project-only mapped indices are **NOT** actual
  joint city score forecasts, and the report sets each actual index
  and cashflow forecast to `null`.
- Source R224 scenario caps and financial envelopes remain
  **hypothetical**. R191 cap, spendable/committed cash, R192 admission
  and original R214 live advice still HOLD.

## R153/R154 tax model falsification

The existing **original R153** source-backed corporate-friendliness
factor and **original R154** four-channel tax revenue model are
available. R228 inspects their required input-field contracts but
does NOT call them with unsupported market data:
- The `Iparűzési adó, %` current P0 baseline **2%** is source-matched.
- R153 requires `services_fee_percentage` (not a direct
  replacement for six distinct per-person tariff values).
- R153/R154 require `vehicle_tax_amount`,
  `building_tax_amount` and R154 `communal_tax_amount`;
  the UI calls the observed values **percentages**, not verified
  per-unit ECU amounts. An unsafe implicit % → ECU conversion is forbidden.
- Market-specific formula weights/divisors, sensitivities and all
  five years of exogenous tax bases are NOT source-verified.
- Consequently `R153_actual_tax_counterfactual_allowed=false`,
  `R154_actual_tax_revenue_forecast_allowed=false`.
This is explicit rejection of a falsely precise model, not a test failure.

## R224 finance-to-five-year bridge (same 24 candidates)

The R228 replay now attaches R224's **original first-year conservative card
requirement**, hypothetical budget headroom and explicit *no-authorization*
flags to all 24 R145/R148 paths. The source schedule and first-year IDs must
match exactly, the original R160 audit must pass, and no requirement may
exceed its own hypothetical scenario budget. Any R224 claim of approved funds
or game eligibility fails closed. This reuses R224's original scenarios,
not a new optimizer; the Hungarian private report shows all 24 paired
rows (cap/budget, P1 card load, project-only conditional fifth-year index).
These numbers are NOT actual spendable funds, a full city score or P2–P5
finance predictions.

## Private reproduction on authorized Fedora

```bash
bash team-handoff/r228-excel-city-policy-join/run_private.sh \
 --out-dir "$HOME/Downloads/a_NEW_private_R228_result"

bash team-handoff/r228-excel-city-policy-join/qualify_private.sh
```

The one-command runner takes the user-owned source XLSX and existing
private source receipts (R226, current tax UI, R156, R224) but writes only
to a **new directory**. Existing directories are not overwritten.
Private output in
`~/Downloads/ecosim-r228-finance-joined-20261102/` includes:
- `R228_RECEIPT.json`: 19 exact source links, four unmatched
  controls, all conditional 24 × 5 joint rows, first-year R224 cost/budget
  source bridge, R153/R154 gate matrix
- `R228_POLICY_UNKNOWN_CONTRACT_TEST_ONLY.json`: schema test,
  NEVER an actual operator policy or action list
- `R228_HU.md`: operator-readable outcome and caveats.

Native tests cover actual pinned user XLSX (374/324),
19/23 exact source joins, all 120 R148 annual rows and 23 unknowns,
R153/R154 unit/parameter gates, mutated workbook, fabricated
tax input, mutated R226 control min, wrong repeated-row match, output
overwrite and SHA-linked provenance.

All *raw/private Excel, browser snapshots and generated receipts
remain off GitHub*. Only portable source/runner/tests/docs committed.

## Gate and best next high-ROI evidence

**No validated winning five-year strategy**. This integration proves
that the model *does not lie* about the currently unknown policy effects.
Next largest ROI: obtain independent actual
  (1) Market I project cap and committed/free cash,
  (2) real allowed periodic decision bounds and calibrated PLAN→FACT
      transition observations,
  (3) market formula coefficients/units for R153/R154,
and then run original R145/R148/R162 counterfactuals. Do not ask for
re-exporting the 374 known XLSX rows.

**GAME_ACTION_GATE=STOP. NO_GAME_WRITES, NO_MERGE, NO_DEPLOY.**

## R230: real-source first-year thresholds, original R191/R192 admission HOLD

The already-integrated R224/R229 24 hypothetical five-year schedules contain
**13 distinct first-year project bundles**. R230 reuses them unchanged and
materializes the exact *candidate start counts* and R224 conservative first-year
card costs. These are **necessary scenario costs**, not sufficiency proofs for
the city's real financial and project-start rules.

R230 independently replays the original R191 validate_state current validator
on the original R156 state, and reconciles the known R222 original R192
same-hour capture failure. R191 presently returns
CAP_UNKNOWN_OR_ASSUMED, and R192 returns
HOLD_CATALOG_NOT_SAME_PERIOD_CAPTURE_WINDOW. R230 therefore exposes
**zero actual eligible first-year actions**, not even the zero-project
hypothesis. In particular, the R224 P1 cash-flow surplus and the
hypothetical cap values 1/2/3 are never promoted to actual authority.

Source-linked output is private:
~/Downloads/ecosim-r230-first-year-readiness-20261102/R230_HU.md
and R230_READINESS_PRIVATE.json. Run with:

    bash team-handoff/r228-excel-city-policy-join/run_r230_private.sh \
      --out-dir "$HOME/Downloads/another_NEW_private_R230_result"
    bash team-handoff/r228-excel-city-policy-join/qualify_r230_private.sh

Actual R191/R192/R214 owner evidence still requires: a source-identified
Market I cap, same-period operator-observed spendable and committed ECU,
and a coherent 35-card/source state snapshot within one hour.
Even these operator inputs alone are **not server attestation or game action
authorization**. Do not paste a fabricated cap or use synthetic R210 credentials
to bypass the gate. Keep all private receipts and browser data out of public Git.
No game writes, merge, deployment, or autonomous execution.
