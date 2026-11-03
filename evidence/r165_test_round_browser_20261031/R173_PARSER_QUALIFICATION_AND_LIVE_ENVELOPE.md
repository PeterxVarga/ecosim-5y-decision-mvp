# R173 — R172 Parser Qualification + Safe Live Observation Envelope

**Execution assignment, not a claim of completed implementation.** Work in the existing Fedora workspace and preserve source evidence. Scope is exactly the R172 reported failures and the missing handoff into R171, **not** a new browser crawler or optimizer.

## Observed baseline / claims to independently inspect
- Operator reports R172 golden replay found: 10 unique page snapshots among 11 raw files (1 byte-identical preflight copy), 29 factors, 6 weights, index p0 51.96 FACT / p1 52.48 PLAN, 88 finance p0/p1 numerical pairs, long loan 7.5%, fee aggregate discrepancy +2 ECU p0/p1; all **historical test market Z**.
- Single R172 qualification: 16 PASS / 1 FAIL among 17 tests, due to parsing space-grouped thousands with decimal comma. A subsequent fix was made without a new qualification. Treat `POST_QUALIFICATION_FIX.md` as **unverified** until the final test.
- Structural blockers: duplicate finance labels lack a proven stable semantic identity when row order changes; `CURRENT_READONLY` always blocks and yields no usable R171 review envelope; Projects page omitted and all 70 per-project R156 state flags unknown; true spendable cash, base project cap and project1 bonus unknown; institutional occupancy is not independent enrollment.
- First inspect actual local `r172-evidence/`, `r171-evidence/run_live_import.py`, `r168-evidence-snapshots/`, `r169-evidence/` and R162/R156/R152 code before editing anything. The GitHub task author has not inspected uncommitted local R172 contents.

## Rules: reuse instead of rebuild
1. R172 adapter remains the **single parsing implementation**. Stage a candidate based on the exact R172 post-fix version under `r173-evidence/` if immutable evidence preservation requires it; avoid cloning entire R172 tree, creating a second implementation, or patching provenance records. If safe, minimal changes to the actual adapter are acceptable **only** if its historical evidence and post-fix receipts are kept byte-identical and you record source hashes before/after; prefer a staged candidate to eliminate ambiguity.
2. R171 `run_live_import.py`, R156 `readonly_intake_r156.py`, R152 and R162 `readiness.py` remain authoritative for subsequent validation. Never duplicate their strict business rules; a partial review envelope is NOT an R156 packet.
3. Offline local filesystem only. No Chrome, browser MCP, network to EcoSim, hidden APIs, login/cookie data, no game action, no GitHub write, no Actions, no unrelated source changes. Preserve input byte-for-byte; outputs only `r173-evidence/` plus an explicit source-hash manifest.

## Stage 1 — Research and adversarial falsification
- Inspect R172 actual failure case, changed parser diff, previous qualification logs, subsequent fix notes, locale-number grammar, R172 tests. Verify intended scale/units using actual displayed source text, not assumptions. Numeric parser accepts *only unambiguous* forms consistent with observed UI (e.g. `1 234,56` versus `1\u00a0234,56` if seen), rejects invalid grouping, mixed separator ambiguity and nonfinite values; preserves original text + normalized decimal.
- Inspect all **duplicate finance labels** and their available structure (section/category/breadcrumb, row context, column pair, visible identifier). Falsify any claimed stable mapping by reordering duplicate rows or inserting identical labels. **Do not use position as cross-snapshot semantic ID**. Record either (a) genuinely unique source-supported composite keys with explicit proof, or (b) `AMBIGUOUS_DUPLICATE_ROW` and omit semantic field. Historical row-order match allowed only as `HISTORICAL_ORDERED_NUMERIC_RECONCILIATION`, explicitly not stable row identity for live.
- Check whether the existing R171 acceptance gate needs an `OBSERVATION_ENVELOPE` prior to R156. Avoid relaxing R156 validation or treating an operator-supplied live label alone as server authenticity.

## Stage 2 — Single integrated, bounded implementation
- Close the locale-number regression and add negative tests for spaces/NBSP/thin NBSP only if observed or explicitly supported, decimal comma, signed numbers, invalid mixed grouping, accidental scale drift. Preserve FACT/PLAN.
- Add deterministic `source_row_identity` representation: stable if explicit unique route+section+label+unit or original official ID; ambiguous if duplicates cannot be disambiguated. Repeated values must not be incorrectly joined across snapshots. Expose `stable_id_confidence` and `ambiguous_rows`; no invented identity. Historical 88 row numeric replay can still pass independently.
- Implement a **safe partial review envelope** for `CURRENT_READONLY` in the existing parser or a minimal non-overlapping handoff module. Requirements:
  - Read only new local raw snapshot files, never mix historical and current periods; explicit distinct capture root, source SHA-256 and timestamps for every page.
  - Validate visible round label/season, team, market, period, capture timestamp, URL and FACT/PLAN columns against R171 `PROVENANCE_GATE`. If missing, contradictory, still `Tesztforduló` or only inferred from filenames/OS date, return `LIVE_CAPTURE_IDENTITY_UNVERIFIED` **without current-ready claim**. A partial diagnostic file may still be emitted.
  - If all identity fields directly observed, output `LIVE_READONLY_OBSERVATIONS_FOR_REVIEW` with per-field value/evidence class and nulls for unsupported fields. **Do not** build a full R156 packet unless all 35 per-ID flags, 29 metrics+index and required field sources are independently evidenced and downstream R171/R156 validates them.
  - Keep `confirmed_spendable_cash`, project cap, bonus and all 70 flags null/UNKNOWN without direct authoritative evidence. Never infer from p1 865588 reserve, name translation, or finance balance. No auto-loan assumption.
  - Explicitly separate `parser_qualification`, `provenance_gate`, `R156_admission`, `R162_readiness` and `game_action_gate`; a passing parser test never implies live game readiness. `game_action_gate=STOP`.
  - Redact or reject secrets in raw snapshots, do not expose credential strings or private contact details in output. Ensure snapshot input directory and output directory are isolated; reject symlinks/path traversal and existing destination overwrite; atomic files, preserved old snapshots.
- Avoid reimplementing all of R172; minimal patch/reuse with clear code diff and source linkage. For tests, use the exact R168C historical snapshots as golden and synthetic/in-memory **live-looking** fixtures for negative and positive provenance paths. Synthetic fixtures NEVER qualify actual live capture.
- Optional standalone CLI can be added **only** if existing R172 CLI cannot accept R171 envelope output cleanly. It must never call a browser.

## Stage 3 — One consolidated final qualification, after all changes
One final command runs the complete R172 original regression suite, the new R173 edge/mutation fixtures and golden replay, including:
- Previously failed locale case now PASS; assert actual test count and failure count, never invent 17/17 if tests changed.
- Golden p0/p1 29-factor/6-weight, 88-row numeric comparisons and fee +2 verified against preserved R169; duplicated-label semantic ambiguity either resolves from explicit structure or remains blocked (not falsely PASS).
- 10 unique pages vs one duplicate raw file handled deterministically by hash; duplicate page conflicts fail closed; no silent dropped data.
- Unordered file names/lines do not affect identity where anchored; genuinely ambiguous row mapping marks unknown.
- `CURRENT_READONLY` on test-round snapshot returns `LIVE_CAPTURE_IDENTITY_UNVERIFIED`; absent round/team/market/period returns same. **Synthetic** positively labeled live identity creates only a review envelope, never R156 complete/authority; fake 35 flags rejected, cash reserve not spendable.
- Original source SHA-256 unchanged, outputs no credentials and no game action. Run in one final bounded batch after implementation (not repeated smoke tests); if a test fails, record FAIL, implement fix, then **one necessary final rerun**; never present untested post-fix code as qualified.

## Deliverables under `r173-evidence/`
- `README.md`, `R172_POST_FIX_REVIEW.md`, `SOURCE_AND_DIFF_MANIFEST.json`
- `tools/` only when needed, or a minimal patch file
- `tests/` extended qualification fixtures
- `FINANCE_ROW_IDENTITY_AUDIT.json` per key duplicates and certainties
- `HISTORICAL_GOLDEN_REPLAY.json` with explicit numeric-vs-semantic scope
- `CURRENT_READONLY_ENVELOPE_SCHEMA.json`, `CURRENT_READONLY_NEGATIVE_RESULTS.json`
- `R171_HANDOFF_RECEIPT.json` specifying `OBSERVATION_ONLY` or blocked and R156 refusal
- `FINAL_OFFLINE_QUALIFICATION.json`, `SAFETY_RECEIPT.json`, `LIVE_DAY1_COMMAND.md`

## Honest success status
- `PASS_OFFLINE_PARSER_QUALIFIED`: all old and new parser tests + golden replay completed; inputs unchanged; no false identities. A separate row-semantic-coverage percentage may be partial. This is **not** live-proven.
- `PARTIAL_OFFLINE_PARSER_BLOCKED`: parser works, but one or more supported required fields are ambiguous or missing; output and exact blocker preserved. If semantic row identities are impossible from text snapshots, do not engineer fictitious workarounds.
- `FAIL_OFFLINE_QUALIFICATION`: any regression/test failure after latest change or unsafe behavior.
- `LIVE_ROUND_VALIDATION_NOT_PERFORMED` is ALWAYS true in R173. `R156_BLOCKED_MISSING_PROJECT_STATES` remains true on the historical golden data.
- `GAME_ACTION_GATE=STOP` no matter what parser status is.

After this chunk, **do not** schedule another general audit or another synthetic optimizer. The next natural work is actual, safely identified live-round observation once available.
