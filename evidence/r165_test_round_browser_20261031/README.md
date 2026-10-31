# R165 — Browser-readonly test-round evidence (2026-10-31)

## Provenance
- X-Challenge 2026 **Tesztforduló**, Market **Z**, team **Jutalom a nap végén**, period **1/1**.
- Connected signed-in browser tabs: /simulation/projects (Gazdaságfejlesztés only), /simulation/finance, /simulation/income.
- Capture: 2026-10-31T19:08:59.911Z; DOM text read only; no game mutations, no refresh, no backend export/server-state certification.
- **p0 = FACT; p1 = PLAN.** Do not use these as consecutive observed annual states or as measured 5-year forecast error.

## Observations and arithmetic checks
- p1 planned revenue: **5376812 ECU**; expenses excluding reserve and loans: **4511224 ECU**; net: **865588 ECU**; reserve transfer: **865588 ECU**.
- p0 revenue: 5449828 ECU; comparable expenditure: 4487043 ECU; net: 962785 ECU.
- All three main financial arithmetic checks pass. **Reserve is NOT confirmed spendable project money.**
- Six service-fee revenue lines sum to 1802870 ECU (p0) and 1862033 ECU (p1), but finance aggregates show 1802868 ECU and 1862031 ECU: **-2 ECU** each. Likely display rounding, not proven.
- Six editable service fee fields have **blank p1 inputs**, represented as null, not 0.
- 14 visible project cards from economic-development category; remaining 21 project card details not visible. Project #12 maintenance **-12000 ECU**, #13 maintenance **-8800 ECU**: preserve sign, do NOT infer whether or when cash savings occur.

## Model integration and decision
- This JSON is observational evidence, not a replacement for `inputs/official_state.template.json`; it does NOT supply confirmed project cap, liquid budget, future FACTs, or full dynamics.
- R163 source-normalized PLAN/FACT snapshots and the R164 7.5% long-term loan observation can be reconciled separately. Current 3-tab source does not independently reobserve the loan page.
- Reuse existing R162 R156/R152 intake and R160 project consistency audit; **do not fork an optimizer**.
- **PASS_READONLY_EVIDENCE_ONLY / gameplay STOP.** No action or save in the game.

This is a proposed evidence update to a private repository; R162 release is unchanged.
