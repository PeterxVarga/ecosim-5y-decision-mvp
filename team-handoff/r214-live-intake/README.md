# R214 — one private read-only intake → 3-option EcoSim advisory

## User-visible capability

One command orchestrates **the existing original components**:

1. Original R156 operator-local current PLAN export → immutable R152 bundle and original normalized state.
2. R207's original R191 same-period current-state and actual **operator-observed year-one** spendable/committed envelope admission (not a financing approval).
3. Original R192 35-card parity / optional source-validated R212 changed-card adaptation. Adaptation is **opt-in only**.
4. Existing R162/R157 conditional remaining-year searches, R160 independent rule audit and R207 ranked, distinct first-period choices.
5. Private combined R214 receipt with hashes of every supplied source, original R156 manifest/state and final R207 JSON/Hungarian recommendation.
6. Optional R213 source-row diff between exact historical baseline XLSX and a genuinely **changed** operator-supplied workbook with the same 374-row layout. The diff stays descriptive, does not overwrite R156 factor/card/finance input and is **NOT server authentication**.

**Every result remains advisory. GAME_ACTION_GATE=STOP; no EcoSim API/browser/session access, gameplay writes, merge, deployment or official score forecast.**

## Run on Fedora after collecting the read-only current observations

The three mandatory input files are generated from the current round's actually displayed **same-period** state, finance, and card observations; they may not be replaced with old tests. The R156 form already exists at ECOSIM_R162_INTEGRITY_REVIEW_RC/capture/R156_OFFLINE_CAPTURE.html. The file format is the ORIGINAL R156/R191/R192 format; no new schema, manual duplication, login automation or secret is required.

    bash team-handoff/r214-live-intake/run_private.sh \
      --r156-export /private/current_R156_export.json \
      --year1-finance /private/observed_year1_finance.json \
      --current-card-catalog /private/current_35_cards.json \
      --year1-budget NNNN \
      --out-dir /private/new_r214_result

NNNN must be an explicit **illustrative nonnegative, operator-observed bounded** first-year project-card ceiling and satisfy original R191 finance checks. Even a PASS does not authorize spending. No output folder is overwritten. If and only if the **current** 35 cards differ from historical R162 but match R192's complete 35-card schema, add:

    --allow-source-adapted-current-catalog

To compare a new full city workbook against the original source-verified historical one, also add BOTH:

    --historical-workbook "/home/petervarga/Downloads/X-Challenge 2026 Tesztforduló_Jutalom a nap végén_Tesztforduló_Z (1).xlsx" \
    --current-workbook /private/new_current_city_export.xlsx

Only a changed **same-layout** 374-labelled-row workbook is accepted; data identity and true current server provenance must still be independently reviewed. Historical binary copies with identical cells are rejected. If the game changed the workbook layout, R213 cannot silently reinterpret it; HOLD until a separately qualified mapping is available. The finance and project inputs must still be provided separately.

## Private output

- r156_immutable/ — original source receipt and hashed 29-factor/35-project capture.
- r156_state.json — original normalized current state.
- advisory/R207.json + advisory/R207_HU.md — validated original 3-option advisory.
- R214_RECEIPT.json + R214_HU.md — hashed end-to-end source lineage and status.
- R214_CITY_DIFF_PRIVATE.json — only if both source workbooks and observable changes.
- INCOMPLETE_HOLD — intentionally retained on any failure after creating the output directory; **never treat it as PASS**.

No raw capture, historical workbook, finance file, or private output gets committed.

## Qualification

    bash team-handoff/r214-live-intake/qualify_private.sh

Uses original R210 deliberately MOCK current-mode fixtures, the existing R212 changed-card adapter, and locally available source-verified R213 historical XLSX. Verifies raw CLI execution, byte-identical repeat, changed-card opt-in, changed year-2 period, funding/capture errors, and Excel-diff source labels. MOCK qualification is enabled only by the EXPLICIT test-only --qualification-mock switch; without it fake or historical markers cause HOLD.

## Remaining limits

This integration removes **operator orchestration gaps**, not epistemic unknowns. No authenticated current-round data was supplied here; no validated population/business/institution transition, future real cash, approved grants/loans, or real server scoring. The R211 108 historical incremental stress comparisons are not inserted into the current-year budget. Review these separately when real matching observations exist. A PASS here is not permission for gameplay; NO_GAME_WRITES and owner approval rules are unchanged.
