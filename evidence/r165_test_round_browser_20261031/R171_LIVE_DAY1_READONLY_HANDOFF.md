# R171 — Live Round Day-1 Read-Only Capture and Decision-Readiness Handoff

Status: PREPARED_NOT_EXECUTED. The user has reported R170 `PASS_OFFLINE_EVIDENCE_ONLY` and `R170_READY_FOR_LIVE_RECHECK`; these are **not** live-game qualifications.

## Schedule/source & scope
- Organizer: https://www.xchallenge.hu/ — test 2026-10-30 through 2026-11-01; live five rounds 2026-11-02 through 2026-11-12. This calendar **does not prove the session is live**; obtain visible current round/market/team/period from the UI. Exact first-round opening hour not established by this source.
- The 2026 public site advertises **26 assessment criteria in six categories**, while the Z test-round screens captured **29 displayed factors**. This is an unresolved terminology/version difference, **not** evidence to discard three factors or to alter R162 coefficients.
- EcoSim product overview https://edu.ecosim.hu/smartcity mentions 6 general aspects and annual project decisions, but no authoritative per-turn cap, spendable balance, grant settlement or automatic loan trigger.
- DO NOT use a generic EcoSim/BANK rulebook or a different competition's rules as SmartCity authority.

## Source material
- Local `./r170-evidence/` (especially `FINAL_OFFLINE_QUALIFICATION.json`, `PROJECT_ID_NAME_CROSSWALK.csv`, `PARTIAL_STATE_R170.json`, `LIVE_ROUND_DAY1_READONLY_CHECKLIST.md`, `PROJECTS_VIEW_SAFE_OBSERVATION_PRECONDITIONS.md`), and `./r169-evidence/` and `./r168-evidence-snapshots/`, all read-only. **The author has not independently inspected the user's uncommitted R170 local files; first inspect them.**
- Canonical existing `ECOSIM_R162_INTEGRITY_REVIEW_RC/` in private `PeterxVarga/ecosim-5y-decision-mvp`. Reuse R156/R152/R149, `tools/readiness.py`, `tools/strategy_5y.py`, no new optimizer.
- Provenance Z test/period1/1, 51.96 FACT and 52.48 PLAN is *historical only* when live date/market/team/round differs.

## Phase A — Can be done now, completely OFFLINE
1. Read the existing R170 day-one checklist and Projects preconditions; reconcile these with the actual R170 qualification before creating anything. Verify SHA, source fields and unknown statuses.
2. Implement **small deterministic adapters only if needed** to import `R168C`'s normalized UI snapshots into the existing R156 schema with explicit `UNKNOWN` fields. Reuse the actual `build_normalized.py` and `finalize_audit.py` instead of cloning their logic.
3. Generate a **live provenance acceptance gate** with required observed fields: exact round label (must NOT be `Tesztforduló`), competition/season, team, market, period within 1..5, snapshot timestamp, source URL, p0 FACT / p1 PLAN labeling. Never transfer test-round market Z, index 51.96 or project data as live values by default. If any required identity source is absent, `LIVE_CAPTURE_IDENTITY_UNVERIFIED` and STOP.
4. Generate `SNAPSHOT_IMPORT_SCHEMA.json`, `LIVE_CAPTURE_PREFLIGHT.md`, `PROVENANCE_GATE.json`, `R156_READINESS_MAPPING.json`, `OPEN_QUESTIONS_RANKED.md` and minimal `run_live_import.py` (only if necessary). No browser access during Phase A.
5. Do one bundled offline validation with **synthetic in-memory negative fixtures**: test-round label rejected, missing team/market rejected, 35 unverified status flags rejected, empty or truncated snapshot rejected, implied spendable cash rejected. No 70 invented flags and no fictitious project cap.

## Phase B — Execute **only when operator confirms an actual live round is displayed**, not before
1. User opens logged-in EcoSim in the existing dedicated Chromium profile and **verifies visibly**: no unsaved decisions, current round is live, correct team/market/period. User authorizes passive observation, NOT game action.
2. If browser MCP is available, restrict to `list_pages`, `select_page` with `bringToFront=false`, `take_snapshot` with `verbose=false`. **No auto-navigation**, click, fill, evaluate_script, client state mutation, network/HAR, raw authenticated response, cookies/tokens or undocumented APIs. If any page isn't already open, request user to open manually after safety checks. Do not call `navigate_page` or use other tools to bypass an input restriction.
3. Save **one page per file**, not 10 snapshots in one tool response. Reuse the MCP's proven `--filesystemRoot` from R168C configuration. E.g. if it is `<repo>/r168-evidence-snapshots`, use a NEW child `<repo>/r168-evidence-snapshots/live-day1/raw/` as `take_snapshot.filePath`. Never guess paths; check `codex mcp list`. These are local captured UI files, **not** to commit/upload.
4. Start from dashboard only. If still labelled `X-Challenge 2026 Tesztforduló`, **STOP** and mark `NOT_LIVE`, even if the date is Nov 2 or later. Do not continue live capture using Z-test state.
5. If identity passes, read the **existing already open** summary/finance/income/loans and any other available views; record raw and sanitized values with exact source, timestamp and fact-vs-plan status. Do not claim spending permission from a reserve line.
6. Projects page has risk of client-side state restoration. Do NOT open or trigger it automatically. If the operator explicitly elects to open it, confirm no unsaved decisions and the separate Projects preconditions; request the operator to open the page manually. Capture only the page already opened. If there is any ambiguity/warning, STOP. Collect all 35 project ID/status/budget/requirement entries **only when directly shown**, and map verified flags to R156; retain otherwise UNKNOWN.
7. Capture actual year-1 project limit/bonus predicate, existing selected new project IDs, start-affordable cash/cost commitments, loans/grants if explicitly visible. Otherwise mark UNKNOWN. Do not infer from client-side hypothetical labels or R94 historical catalog.
8. No model strategy/game preview execution in Phase B. No saves, no finalization, no external authenticated requests, no automatic screen navigation.

## Phase C — Strict offline intake and stop-safe output
1. Offline-import the captured live files and verify they pass the provenance gate; re-run R170 name-ID mapping only as **candidate** until live ID/status evidence proves it.
2. If R156 complete 29+index factors and all 35 project flags are explicitly supported, invoke `tools/readonly_intake_r156.py` and existing downstream checkers for **read-only scenario qualification only**; otherwise classify `R156_BLOCKED_MISSING_PROJECT_STATES` or other true blocker. An R156 result does not imply available project cash or live game authorization.
3. Write into `./r171-evidence/`: `LIVE_PROVENANCE.json`, `LIVE_OBSERVATIONS_SANITIZED.json`, `R156_INTAKE_STATUS.json`, `R162_READINESS.json`, `PROJECT_FLAGS_EVIDENCE.csv` (can carry UNKNOWN), `FINANCE_AND_LIMITS.json`, `LIVE_ACTION_BLOCKERS.md`, `FINAL_OFFLINE_QUALIFICATION.json`, `README.md`, `SAFETY_RECEIPT.json`. Keep raw data under the configured MCP root; preserve history.
4. Output exact observed round/market/team/period and classification `LIVE_CONFIRMED` / `TEST_ONLY` / `UNVERIFIED`. Model readiness and gameplay gate must remain separate.
5. Run **one final bounded validation** (source hashes and lineage, schemas, values, nullability, no secrets in output, fact/plan discrimination, state identity, no unauthorized writes, no skipped risk gate). No GitHub Actions and no commit/push.
6. **Game action gate remains STOP**. Only a subsequent, explicit human-approved decision can authorize any change in the simulation.

## Operator instruction (after 2026-11-02, conditional on live UI)
First verify the logged-in dashboard's header/date/market/team/period. If still test round, stop. If live, bring only previously open safe pages into view; ask for confirmation before any risky projects page. Run the full observed-to-R162 pipeline as a *single* chunk, recording unknowns and blockers. Do not open the risky page or modify game inputs yourself.
