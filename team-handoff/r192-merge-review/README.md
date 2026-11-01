# R192 – independent merge review, fail-closed current card parity

**Status**: LOCAL_TESTS_PASS; NATIVE_R162_R160_E2E_HOLD; INDEPENDENT_HUMAN_REVIEW_MISSING; GAME_ACTION_GATE=STOP.

### Why
Before R192 the current-state intake checked current 35 project statuses and first-year finance, but search was using historical project costs, effects, prerequisites and partner supports. A changed live card could make the plan invalid.

### Changed
- New `team-handoff/r191-live-admission/tools/catalog_gate_r192.py` checks all 35 current operator-observed card definitions against the original pinned R162 catalog. It never asserts server authentication.
- Existing `run_r191_shadow.py` in the R191 team folder now requires `--current-card-catalog` with a fresh `ECOSIM_R192_CURRENT_CARD_CATALOG_V1` JSON for `--mode current-readonly`. Missing or changed card -> HOLD before search module import. Historical mode forbids live catalog input.
- 18 new negative/positive test cases are committed in `tests/test_r192_catalog.py`.

### Offline qualification on 2026-11-01
- R189 19/19 PASS; R190 6/6 PASS; retained R191 30/30 PASS; new R192 18/18 PASS; total 73/73 PASS.
- Native pinned R162 Python plus original R160 independent auditor not run in this sandbox: private Git clone not accessible; no live state or game authorization.

### Current-only catalog JSON shape
Required: schema `ECOSIM_R192_CURRENT_CARD_CATALOG_V1`, capture_mode `CURRENT_READONLY`, team, market, round, period, captured_at_local, source_evidence_id, source_view and `projects` with exactly 35 rows. Each project row must include `id`, `name`, `startup_cost`, `maintenance_cost`, `investment`, `partner_support`, `project_conditions`, `effects` (each metric + value_percent).

The input must describe **newly observed current qualification cards**, not the old historical snapshot re-labelled as current. If any card definition differs from the R162 PIN, STOP and update the catalog model separately.

### Before merge
Run pinned clean source E2E, save R160 audit receipts, get an independent teammate review. Do not merge `main` merely on mocked local tests.
