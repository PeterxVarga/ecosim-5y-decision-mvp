# R174 — Final offline E2E rehearsal and pre-live freeze gate

**Status: EXECUTION INSTRUCTIONS, NOT EXECUTED.** Target the user's existing Fedora workspace (`~/Downloads/ecosim-r168-audit`). This is the final rehearsal **before** an actual live-round observation. Do not treat an offline PASS as permission to act in the game.

## Objective and justification
The user reports R173 `PASS_OFFLINE_PARSER_QUALIFIED`, 32 passed, 0 failed/skipped, a 29-factor/6-weight/88-finance-row historical replay, +2 ECU visible service-fee sum residual in both columns. The R173 parser can produce a partial `CURRENT_READONLY` review envelope using synthetic identity evidence, but a live current input has **never** been qualified. R156 still refuses incomplete 35-project states. The value of R174 is a **single complete workflow rehearsal** from immutable captured evidence through existing parser, provenance check, admission and readiness—not another parser subsystem or an optimizer.

The local R173 implementation, scripts and receipts are **not visible from this task document**. Inspect them directly; never assume exact exported function names or CLI flags. Preserve old files. If a reliable integration cannot be built from the actual exports, stop with an explicit, reproducible integration blocker and no invented PASS.

## Inputs (read-only)
- `r173-evidence/`: `README.md`, `FINAL_OFFLINE_QUALIFICATION.json`, `HISTORICAL_GOLDEN_REPLAY.json`, `CURRENT_READONLY_ENVELOPE_SCHEMA.json`, `R171_HANDOFF_RECEIPT.json`, `LIVE_DAY1_COMMAND.md`, source/diff manifest and actual parser/tests. Confirm reported 32/32 pertains to **last code version**, and verify its hash.
- `r172-evidence/` for pre-fix history only; do not run unqualified code.
- `r171-evidence/`: actual `run_live_import.py`, `PROVENANCE_GATE.json`, `LIVE_CAPTURE_PREFLIGHT.md` and supporting scripts. Reuse exact schema. No duplicate admission logic.
- `r170-evidence/`, `r169-evidence/`, and immutable `r168-evidence-snapshots/raw/`: 11 files, reportedly 10 unique pages and one byte-identical preflight capture, all **test-round Z**. Verify local counts and hashes rather than treating them as axioms.
- `ECOSIM_R162_INTEGRITY_REVIEW_RC/tools/readonly_intake_r156.py`, `observation_bundle_r152.py`, `intake_r149.py`, `readiness_r148.py`, `readiness.py` and the exact 29 factor keys. R162 is canonical; do not modify it.
- `evidence/r165_test_round_browser_20261031/` (if present in pinned repo) for historical checks only.

## Stage 0: risk-scoped research and falsification (no new code yet)
1. Inventory source files, interpreter requirements, import boundaries, CLI arguments, existing receipt hashes and global filesystem side effects. Verify the reported R173 success against disk, **without rerunning** its 32 unit tests at this stage.
2. Identify the shortest native path connecting R173 parser output -> R171 provenance gate -> R156 intake admission -> R162 readiness. Create **thin orchestration only**, no reimplementation of any validator or parser.
3. Record independent testable claims and falsifiers:
   - Historical Z/Tesztforduló **must not** pass `CURRENT_READONLY` live-provenance gate.
   - A partial envelope with 35 missing project identities or any of 70 flags UNKNOWN **must not** become an R156 packet.
   - A complete **synthetic** identity fixture may produce only a *review envelope*, never `LIVE_CONFIRMED` from historical data, never independently server-verified, never `game_action_gate=GO`.
   - R156/R162 readiness cannot be upgraded by planned reserve `865588`, long-loan display `7.5%`, candidate crosswalk, marketing's 26 criteria, or implied project cap `4`.
   - Duplicate finance row labels remain ambiguous when uniqueness fails (20 rows / 9 labels reported); do not join them semantically based on row order.
   - `FACT` p0 / `PLAN` p1 must remain separated, and reconciliation +2/-2 is one discrepancy under opposite subtraction conventions.
   - No input/candidate file may overwrite historical files, symlinks or outside destinations.

## Stage A: one minimal end-to-end orchestration
Build `r174-evidence/tools/run_r174_rehearsal.py` **only if** there is not already a suitable reusable orchestration entrypoint. Python standard library preferred; invoke actual R173 and R171 module/API or CLI interfaces, not invented commands. No network, no browser, no game.

The orchestrator must run three isolated scenarios using local raw files and clearly labelled **synthetic-only** negative fixtures:
A. `HISTORICAL_REPLAY`: R168C original test-round Z/1/1 -> R173 parser -> R169/R173 goldens (29 factors, six weights, 88 numeric p0/p1 finance pairs, index 51.96 FACT / 52.48 PLAN, +2 visible fees both columns), then attempt the R171 live-provenance gate. **Expected**: golden replay consistent; `LIVE_CAPTURE_IDENTITY_UNVERIFIED` or `TEST_ONLY`; **NO current R156 packet**.
B. `SYNTHETIC_LIVE_IDENTITY_PARTIAL`: generate a bounded fixture with an unambiguously *synthetic*, non-test-labelled explicit round/team/market/period/season/FACT/PLAN/timestamp and source text. Feed it through the real R173 parser and R171 review gate. **Expected**: at most `LIVE_READONLY_OBSERVATIONS_FOR_REVIEW`/synthetic review envelope; 35 per-project states stay unknown; R156 refused, R162 decision not ready. If the parser refuses unknown UI layout, record the exact reason instead of relaxing source identity requirements.
C. `ADVERSARIAL_FAIL_CLOSED`: inject in isolated copies: contradictory round/market/period across pages, duplicate label collisions and reordering, incomplete 29 metrics, ambiguous locale thousands+comma, missing source proof, and a faux `confirmed_spendable_cash` derived from p1 reserve. **Expected**: either explicit abort or quarantined unknowns/warnings; zero false live qualification, zero invented project flags and no inferred spending authority.

If creating a synthetic complete R156 case would be cheap using existing fixtures, optionally test the *actual* R156 validator with those explicit 35 supported booleans. It must be labelled `SYNTHETIC_VALIDATOR_REACHABILITY_ONLY` and never used as present-day project evidence. **Never spend a separate major chunk building a synthetic 35-project game state just to get PASS.**

## Stage B: safety, immutability and final verification
- All temporary outputs inside a fresh, unique `r174-evidence/` staging directory. Detect `--out-dir` overlap, existing immutable destination, symlinks, path traversal and uncontrolled writes. Preserve every input SHA-256. Never create any files under `r168-evidence*`, `r169-evidence`, `r170-evidence`, `r171-evidence`, `r172-evidence`, `r173-evidence` or the R162 source tree.
- Separate **parser qualification** (reported R173) from **E2E integration qualification** (new R174) and from **current-live provenance** (not tested with real live data).
- Require a machine-readable step ledger with `scenario_id`, `component_name`, `input_sha256`, `status`, `expected_status`, `evidence`, and `assertions`. For blocked-by-design outcomes, count them as successful *safety assertions*, not as successful live validation.
- Never use absolute paths that assume the author's Fedora user beyond deriving the current repository root. Never auto-open/browser-navigate an EcoSim page, run its authenticated API, collect HAR, inspect cookies or tokens, or mutate a game setting.
- One final bounded offline invocation **after** implementation, containing parser integration + scenario assertions + source integrity/sensitive data/receipt checks. Do not burn time on a sequence of tiny runs. If this fails and a code fix is made, **one necessary final rerun on the final bits** is required before declaring PASS.
- Code in outputs may be copied in the runner for reproducibility only when strictly necessary, but no parallel parser or model fork. Document dependencies on old files explicitly.

## Deliverables only in `r174-evidence/`
1. `README.md` — what ran, exact command, known limitations.
2. `tools/run_r174_rehearsal.py` or equivalent tiny orchestration/reuse script.
3. `INPUT_HASHES.json` / `SOURCE_MANIFEST.json`.
4. `E2E_STEP_LEDGER.json`: complete tool-stage trace, including blocked-by-design statuses.
5. `HISTORICAL_REPLAY_RESULT.json`, `SYNTHETIC_LIVE_PARTIAL_RESULT.json`, `ADVERSARIAL_NEGATIVE_RESULT.json`.
6. `R156_R162_GATE_SUMMARY.json`: unknown per-project flags, caps, costs, spends and model status; precise reasons.
7. `FINAL_OFFLINE_QUALIFICATION.json`: final code SHA-256, pass/fail/skipped counts, exact input baselines, explicit qualification level.
8. `SAFETY_RECEIPT.json`: unchanged historical source SHA, no browser, no gameplay changes, `GAME_ACTION_GATE=STOP`.
9. `LIVE_DAY1_ONE_SHOT_RUNBOOK.md`: shortest possible Nov 2+ procedure to (1) visually confirm actual non-test-round, team/market/period and no unsaved decisions; (2) user-approved passive per-page snapshots; (3) R173 parser -> R171 gate -> existing R156/R162 readiness. Retain the Projects safety gate. Specify exact command only from actual verified CLI entrypoints; otherwise write placeholders marked `UNVERIFIED`.

## Strict outcome definitions
- `PASS_OFFLINE_E2E_FAIL_CLOSED` **only if** all mandatory A/B/C assertions and source integrity checks pass on last code version, and true live validation remains unclaimed. This is a technical readiness to **accept observations for review**, not gameplay readiness.
- `PARTIAL_OFFLINE_E2E_BLOCKED` if integration cannot safely bridge one of the components (list exact missing API/schema/source evidence); no new parser or unsafe workaround.
- `FAIL_OFFLINE_E2E` on mismatches, a false accept, lost data or unqualified final code.
- Always `LIVE_ROUND_VALIDATION_NOT_PERFORMED=true`, `R156_CURRENT_ADMISSION=BLOCKED_UNLESS_COMPLETE_SOURCE_PROVEN_FLAGS`, `R162_GAME_DECISION=STOP`, `GAME_ACTION_GATE=STOP`.

## Afterward
**Freeze the offline parser/integration pipeline if and only if `PASS_OFFLINE_E2E_FAIL_CLOSED`.** Next major chunk is the genuinely live, operator-authorized observation once the UI proves its round/market/team/period. If R174 fails, patch **only the demonstrated integration defect**, requalify once, then freeze; avoid endless new R175/R176 synthetic rounds. No GitHub Actions (billing unavailable), no commits/pushes from Codex, no changing PR #1 or R162 baseline.
