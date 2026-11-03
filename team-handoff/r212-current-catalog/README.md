# EcoSim R212 — current-round 35-card drift-aware, read-only advisory

## Outcome

**Critical-path fix:** The original R192 validator intentionally blocks any change in a project card versus the 2026-10-30 historical test catalog. That makes the existing R207 CLI unusable if the official current-round catalog differs. R212 adds an **explicit operator-opt-in** to reuse the original R162 search and R160 independent audit with a complete, observed *current* 35-card catalog in memory. **Default behavior remains unchanged and fail-closed.**

This does NOT mean the current EcoSim server authenticated the data or approved the result. All current observations are operator-declared. Historical projections and proxy values are not an official SmartCity score, and no decision is sent to the game.

### The safe adaptation contract

- First always run the original R156 immutable source capture and R191 current state + year-one finance checks; the R192 original strict catalog-parity check also runs first.
- Only when R192's **specific card-definition drift** error is encountered **and** `--allow-source-adapted-current-catalog` is supplied, the new adapter may be considered.
- R212 validates the same current-period team/market/round, time-window, source identifiers, 35/35 IDs, every original R192 card property (reuse original `_card` parser), uniqueness and finite amounts. Every changed ID and material semantic/dependency drift is reported. Historical / test / synthetic-labeled sources are rejected.
- R212 only patches `strategy_5y.project_index` **in process**, restoring it in a `finally` block. Historical JSON and all R162 module files remain untouched. The original R160 audit independently checks search results against the **same current source-backed index**.
- No historical card `status_p1` is silently copied to the current adapter. Current active/selected statuses come from the separately validated R156 capture.
- No catalog similarity assumption is required for the current cards when the option is enabled, but the **solver still requires exactly 35 cards with numeric IDs 1–35**. A different game schema/count must HOLD for a separate qualified adapter, not silently truncate.
- Even with all 35 cards observed, official eligibility, market scoring, future city dynamics, grant disbursement, loans and cash limits remain UNKNOWN. First-year scenario budget must pass R191 and is still not spending authorization.

## Existing CLI, with one explicit opt-in

The full actual current-round data must be obtained through R156's **READ-ONLY** capture and its associated year-one finance and card observations. Nothing in this repository auto-logs in, guesses market IDs, or fetches an authenticated server session.

```bash
bash team-handoff/r207-first-round/run_private.sh \
  --state /private/current_state.json \
  --r156-bundle /private/immutable_r156_current_bundle \
  --year1-finance /private/current_year1_finance.json \
  --current-card-catalog /private/current_35_card_catalog.json \
  --year1-budget YOUR_VERIFIED_OPERATOR_DECLARED_NONNEGATIVE_ILLUSTRATIVE_BUDGET \
  --allow-source-adapted-current-catalog \
  --out-dir /private/new_r212_advisory
```

For **unchanged** cards, omit the opt-in and the original R192 strict path remains in force. The current card catalog schema remains `ECOSIM_R192_CURRENT_CARD_CATALOG_V1` with `capture_mode=CURRENT_READONLY` and all original card fields. The read-only input HTML under `ECOSIM_R162_INTEGRITY_REVIEW_RC/capture/R156_OFFLINE_CAPTURE.html` is available as an aid for the original R156 immutable bundle.

## Source-pinned test evidence

```bash
bash team-handoff/r212-current-catalog/run_qualification.sh
```

- Original R207 22 tests, R210 full R156/R191/R192/R162/R160/R207 mock current-mode admission, and R212 catalog drift checks.
- R212 native test uses a **mock** modified cost card and again verifies two byte-identical outputs, up to three distinct first actions, source hash, original R162 provider restoration, R160 audits, negative tests for mismatched team/period, stale capture, invalid amounts and duplicate cards.
- A second explicit mock test starts at **period 2** with projects 13/27 previously active and another changed card; the search must never re-start an already active project.
- These fixtures are **synthetic**, even when the source contract says `CURRENT_READONLY`, and they do not independently prove live city parity, current official market rules or lending/score eligibility.

## Race and preservation rules

All runs use a newly created private output directory. `GAME_ACTION_GATE=STOP`, no game writes, no deploy/merge. Do not copy synthetic capture data into real decisions. Keep original R156/R191 receipts and the raw current card observation together with the final R207 report for same-market review.
