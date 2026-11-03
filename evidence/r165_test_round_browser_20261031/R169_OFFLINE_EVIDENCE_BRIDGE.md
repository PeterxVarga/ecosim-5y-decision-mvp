# R169 — Offline EcoSim R168C -> R162 Evidence Bridge (Research, Reuse, Falsify)

**Execution mode:** local filesystem only. No browser actions; no game writes. Existing R162 model is the only optimizer; do not rebuild or fork it.

## Source of truth and scope
- Local input: `./r168-evidence-snapshots/` (10 observed page snapshots including dashboard, nine simulation pages; **Projects absent**), with `raw/`, `build_normalized.py`, `finalize_audit.py`, metadata, normalized JSON and coverage/reconciliation files. Read actual paths/schema from disk first. Earlier `r168-evidence/`, `r168-evidence-connected/`, `r168-evidence-observed/` are historical, do not mutate.
- Pinned model baseline: `./ECOSIM_R162_INTEGRITY_REVIEW_RC/` from main in the private repository. Confirm it is present and identify its commit/tag. Reuse `tools/readonly_intake_r156.py`, `tools/readiness.py`, `tools/strategy_5y.py`, `inputs/official_state.template.json`, and pre-existing R152/R149 validators. If a model directory isn't available locally, do not download a random substitute: use this repository's `main` tracked version, in a separate local read-only reference tree.
- R168C observes the **X-Challenge 2026 Tesztforduló, market Z**, not necessarily the live five-year competition. No transfer of test-round calibration to the live competition without an explicit provenance match.
- R168C logs must be inspected locally: this GitHub document does not verify the uncommitted artifacts.

## Objective
Produce one **read-only, evidence-backed bridge** that converts the already-saved R168C data into R162-compatible fields wherever actually observed, pinpoints the smallest remaining blockers, and avoids more generic browser audits.

## Stage A — Inventory, source credibility, falsification
1. Check local snapshot count and SHA-256s, source URLs, captured time, page title/round, team, market, period and column kinds, file size, completeness and coverage. Check that files are nonempty and not truncated, and that raw snapshots have no cookies, tokens, auth headers, session IDs or contact details. **Never commit or upload raw snapshots, identifiable data, or credentials.**
2. Classify every candidate value: `DIRECT_UI_FACT`, `DIRECT_UI_PLAN`, `HISTORICAL_R94_R165_R167`, `DERIVED_ARITHMETIC`, `INFERRED_UNVERIFIED`, `MISSING`. Preserve units and decimal commas, and record exact source file/URL and text locator with each normalized field. A derived check cannot be elevated to a game rule.
3. Reconcile 88 cash-flow p0/p1 row pairs against R94/R165. Cross-check `5,376,812 - 4,511,224 = 865,588` for p1 only; this does **not** prove immediately spendable cash. Keep fee delta convention explicit: sum of six displayed fees minus displayed aggregate = +2 ECU (both p0, p1); reverse convention = -2, not a second discrepancy.
4. Reconcile 29 factor values and six weights, p0 index 51.96 vs p1 target 52.48 if supported by local source. Do not force displayed rounded components to match a higher-precision formula; produce interval/range or residual report if necessary. Derive no hidden formula without counterevidence.
5. Review institution capacity/population and loans as separate observations. Mark the 7.5% long loan rate observed in test-round UI; prior 12% short loan is R167 **historical** unless the current short-loan tab was actually captured. Do not infer automatic loan timing/limits.
6. Investigate six p1 fee input fields: R165 reported blank, R168C displayed values. Record the mismatch in **display state**, and do not treat it as evidence that a save/change occurred.

## Stage B — Reuse R162 readiness and R156 validator
1. Map actually observed `provenance`, `market`, `team`, six index weights, 29 factors, displayed index, project flags, loan rates and cash-related figures into a source-annotated **partial** `official_state` view with unknowns kept null. Do not overwrite `inputs/official_state.template.json`.
2. Strictly distinguish p0 FACT and p1 PLAN. Never fill `confirmed_spendable_cash_ecu_by_year` with forecast cash, a reserve, a budget residual, or p1 planned figures. Never invent the 5-year annual cash vector.
3. Assess the precise R156 intake preconditions. It demands exactly 29 factor rows plus index, **and 35 project status rows** for a complete packet. Because R168C excluded Projects, output `R156_BLOCKED_MISSING_PROJECT_STATES` unless independent, current, fully attributable per-project status evidence exists. Do **not** fill 35 flags as false or recycle R94 historic statuses.
4. If (and only if) all R156 inputs can be proven from immutable, current observations, create a new immutable R156 packet in `./r169-evidence/` and invoke the existing `readonly_intake_r156.py` validator with no decision-config first. If incomplete, produce a `R156_CANDIDATE_INCOMPLETE.json` with explicit null fields and do not invoke its strict validator as a success path.
5. Reuse the exact `tools/readiness.py` categories: `passive_identification`, `cap_calibration`, `finance_validation`, `optional_approved_candidate_validation`. Document the evidence and gaps item-by-item, focusing on market cap, project1 previous-period bonus, selected project IDs, genuinely spendable project cash and loan constraints. An R162 offline PASS must not be represented as live game qualification.

## Stage C — Next information acquisition plan (no execution)
- Rank every remaining unknown by impact on project feasibility and the cost/risk to obtain. Likely highest: 35 current project statuses, max projects per turn/bonus, project-start cash timing, project grants timing, current market/period identity, and loan constraints.
- The `Projects` page has a reported possible client-side restoration effect. Keep it blocked until a **separate operator-approved and documented safe observation** is available. No clicking, navigation, API, browser tooling, UI changes or simulation decisions in R169.
- Generate a short `R170_TARGETED_CAPTURE_PLAN.md` with the minimum human-visible, safe-to-observe views/actions required, including an evidence condition to lift each STOP. Never phrase speculative financing as permission to act.
- Do not optimize based on assumed live five-year conditions or fabricate a definitive winning plan. The existing R162 model may run only an explicitly labelled **historical/offline scenario**, not an owner-approved game plan.

## Outputs (all new, under `./r169-evidence/`)
- `INPUT_MANIFEST.json` with hashes, provenance, source identities and status; no secrets.
- `OBSERVATION_BRIDGE.json` annotated by evidence class and source locator.
- `FACTOR_WEIGHT_RECONCILIATION.json` (fact/plan separated, residuals, rounding limitations).
- `FINANCE_RECONCILIATION.json` (88 rows, income/expense, fees, balance unknowns).
- `OFFICIAL_STATE_PARTIAL.json` preserving template nulls.
- `R156_CANDIDATE_INCOMPLETE.json` or a validated R156 bundle, never both advertised as verified.
- `R162_READINESS_GAPS.json` exact blocker classes.
- `R170_TARGETED_CAPTURE_PLAN.md`, `README.md`, `SAFETY_RECEIPT.json`.
- Optional `tools/build_r169.py`: minimal deterministic **adapter only**, standard-library Python, no new optimizer. Use prior existing scripts where possible.

## Verification and stop conditions
- First pass is source/integrity and falsification. Build in one large chunk and run **one bounded final offline validation**: source hashes, no sensitive data in output, JSON schema/parse, arithmetic and source lineage, readiness false-positive guard, no modified original files.
- Fail closed when local R168C files are missing, snapshots truncated, sources do not support claimed fields, or market/team/period differ from historical assumptions. Clearly report partial results rather than filling data.
- Absolutely no live game actions, no browser operations, no undocumented endpoints, no GitHub Actions, no commit/push, no changes to R162 source tree. `GAME_ACTION_GATE=STOP`.
