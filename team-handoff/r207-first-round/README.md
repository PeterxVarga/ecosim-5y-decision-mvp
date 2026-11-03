# EcoSim R207 — Live-first decision alternatives, no gameplay writes

**Goal:** Stop producing another isolated source audit. Reuse R156 current operator capture, R191 state/finance admission, R192 35-card parity, the original R162 bounded 5-year search, and R160 independent plan audit. For a **same-period and current-round** observed packet, produce up to three *distinct first-year project-start choices*, with a five-year conditional proxy and project-card cost. This is advisory **only** and never a server-authenticated decision.

## Research and reuse decisions

- R156 already handles immutable offline input capture and hashes; R191 already checks fresh current period, the R156 bundle, first-year finance; R192 already checks the live 35-card catalog against R162's historical solver catalog. **R207 calls these modules directly, rather than rebuilding their logic.**
- R162 already contains the beam search for new plans, R157 source-model sensitivities, and R160 independent schedule audit. R207 runs three bounded, strictly hypothetical scenarios (50/80/100% of an **operator-provided illustrative first-year ceiling**, future years equally hypothetical) using the existing R162 search implementation. No R206 historical output is accepted as current-round truth.
- Only **unconditionally** R160-audited display-rule plans are included. If fewer than three distinct first actions survive, fewer than three are reported. No fictional alternatives.
- No current-round source capture means no actual candidate can be generated yet. Offline synthetic tests do **not** qualify real live behavior.

## Current-round command

First use the **existing** R156 and R191/R192 workflows to capture (read-only): the current 29 factors and displayed total, all 35 card statuses and current card details, actual market cap and weights, previous project 1 status, observed first-year financing and obligations, and source IDs/time stamps. All files must belong to the same team, market, round and period. The current card definitions must match the pinned R162 test catalog or the script stops for model refresh.

From the repository root:

```bash
bash team-handoff/r207-first-round/run_private.sh \
  --state /private/current_state.json \
  --r156-bundle /private/r156_immutable_bundle \
  --year1-finance /private/current_year1_finance.json \
  --current-card-catalog /private/current_catalog_35.json \
  --year1-budget YOUR_EXPLICIT_NONNEGATIVE_ILLUSTRATIVE_CARD_CEILING \
  --out-dir /private/new_r207_output
```

Replace the paths and ceiling with **current, independently observed/operator-entered** values. The command deliberately has no defaults for them. The R191 finance gate also checks that the declared first-year illustrative scenario does not exceed the declared observed residual; this is **not** actual financing authorization. Initial source capture from the live application must be made without saving/confirming any gameplay changes.

## Admission and limits

- Any historical/test provenance, stale/contradictory capture, mismatching current 35-card catalog, missing R156 provenance or R191 finance evidence is a **HOLD**.
- R162 search output is rechecked for explicit source scenario, first-year card-cost ceiling, no network or game writes, exact period, and R160 every-year ID and card-cost replay. Any uncertain display dependency is excluded from the selected advisory options. A 3-way search failing one hypothetical envelope is flagged, never portrayed as a valid plan.
- Output is a new private `R207.json` and `R207_HU.md`. Does not read credentials, contact EcoSim or use browser automation. `GAME_ACTION_GATE=STOP` and `game_writes=0`.
- Not a server-verified cash amount, loan/grant timing, complete city transition, official EcoSim score, or an authorized recommendation to press a button. Owner review is required for any real game change.

## Verification

`python3 -I -B team-handoff/r207-first-round/test_first_round.py` – synthetic negative, diversity and fail-closed checks. A full Fedora source-pinned R156/R160/R191/R192/R162 current-round run **has not been executed** as of this draft while the Fedora device was offline.
