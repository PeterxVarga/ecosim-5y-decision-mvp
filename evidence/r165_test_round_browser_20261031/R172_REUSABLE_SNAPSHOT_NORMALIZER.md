# R172 — Reusable, Fail-Closed EcoSim Snapshot Normalizer (live-ready adapter)

**Status:** IMPLEMENTATION ASSIGNMENT, NOT a completed parser. Execution belongs on the user's Fedora workspace containing the actual R168C raw snapshots.

## The concrete blocker
R171 Phase A passed 19/19 offline checks, but `r168-evidence-snapshots/build_normalized.py` and `finalize_audit.py` bind to historical filenames/row indexes and overwrite historical artifacts. Live snapshots cannot safely be normalized without manual inspection. Remove **that** blocker before Nov 2 using existing test-round snapshots as golden references, without inventing new live values or constructing a second optimizer.

**Research -> Reuse -> Build.** Before writing code, inspect exact on-disk R168C/R169/R170/R171 inputs, check which parsing functions from historical scripts can be safely extracted/reused, and verify R162/R156/R152 schema and admission rules. No speculative new abstraction. Modify neither original evidence nor R162 source. Build only the justified narrow adapter and tests in a new R172 output directory.

## Inputs to inspect (offline)
- `r168-evidence-snapshots/raw/*`, its `README.md`, `SANITIZED_OBSERVATIONS.json`, `COVERAGE_MATRIX.csv`, `RECONCILIATION.json`, `build_normalized.py`, `finalize_audit.py`. Raw Chrome DevTools snapshot **text** is the canonical R168C source; verify exact format, anchors and existence first. No assumption it is HTML/JSON.
- `r169-evidence/` `OBSERVATION_BRIDGE.json`, `OFFICIAL_STATE_PARTIAL.json`, `FINAL_OFFLINE_QUALIFICATION.json`; `r170-evidence/` crosswalk, readiness and final qualification; `r171-evidence/` preflight, provenance gate, `run_live_import.py` and its offline checks.
- Existing model `ECOSIM_R162_INTEGRITY_REVIEW_RC/tools/observation_bundle_r152.py`, `readonly_intake_r156.py`, `intake_r149.py`, `readiness_r148.py`, `strategy_5y.py`, factor names `r142_proxy_reference.COEFF` (exactly 29) and `WEIGHTS` (exactly 6). R152/R156 require 35 authenticated explicit per-ID flags; R168C Projects excluded.

## Stage 0 — Research & falsification and source integrity
1. Inventory the existing raw files (expected 10 snapshots, dashboard + 9 simulation pages) **without recreating captures**. Record actual hashes, paths, sizes, line counts, observed URLs, headings, time and current visible round/team/market/period. Log any missing, truncated or sensitive input; never upload raw snapshots.
2. Determine whether `build_normalized.py`/`finalize_audit.py` have reusable pure functions. Reuse minimum parser fragments / refactor by copy into the new adapter only after noting differences. Avoid reimplementing validation from R156/R152 or finance/index formulas from R162.
3. Inspect exact source snapshots to identify **stable anchored extraction**, not hardcoded line numbers. For any field that cannot be located unambiguously, record null/UNKNOWN and `parse_warning` with source location. Do not optimize for a guessed future UI format. Note each source's `FACT` vs `PLAN` labels.
4. Pre-register falsifiers: reordered text lines, extra navigation labels, duplicated row labels, absent markets/teams, changes of locale decimal separators, a page changed between capture times, missing row index, two competing p0/p1 values, a 2026 test-round label in live mode, nonexistent Projects flags and projected cash falsely promoted to spendable cash.

## Stage A — Build the single new adapter (one large implementation chunk)
Add `r172-evidence/tools/normalize_snapshots_r172.py` (and only the minimum support files justified by actual raw data). Python stdlib preferred. CLI:
`python3 r172-evidence/tools/normalize_snapshots_r172.py --snapshot-root ./r168-evidence-snapshots/raw --mode HISTORICAL_REFERENCE --out-dir ./r172-evidence/golden-output`
- Input/output **must not** overlap; refuse symlinks/path traversal, missing or oversized files, duplicate route names, truncation, invalid UTF-8, secrets, or attempts to overwrite existing outputs; write immutable atomic bundle; only files under the designated output root.
- Discover pages by **actual content URL/heading/provenance**, not files' names or ordering; use normalized name lookup with exact source row and sha256 for every emitted number. If a route label is absent, mark `UNATTRIBUTED` rather than silently assigning one. If raw format is insufficient to identify a source, fail closed or preserve partial output with explicit diagnostic (never a fake success).
- Implement anchored extraction for the existing **29 metrics, 6 weights and p0/p1 SmartCity indexes**, snapshot-specific p0 FACT/p1 PLAN 88 finance row pairs if present, six service fee lines, visible loan rates, capacity vs enrollment and population identities, and visible market/team/period/round.
- Extract only supported fields. Numbers should preserve sign/unit, decimal comma vs dot, and raw text; reject ambiguous number parsing. Every value carries `raw_snapshot_sha256`, `source_path`, `line_range`, `route`, `observed_column`, `observation_time`, and `evidence_class` (`DIRECT_UI_FACT`, `DIRECT_UI_PLAN`, `HISTORICAL`, `DERIVED_CHECK`, `UNKNOWN`).
- `previous_running`/`selected_new` remain UNKNOWN for 35 projects without an independently proven identifier/flag source. Summary semantic name matching is NOT ID proof. `confirmed_spendable_cash`, project cap and bonus remain null when absent. The p1 PLAN reserve `865588` is not spendable cash.
- **Do not automatically emit R156 packets from partial input.** Produce R156 readiness matrix and `R156_BLOCKED_MISSING_PROJECT_STATES` until all flag predicates are supported. When complete real/current input eventually exists, hand off to **existing** R171 `run_live_import.py` and R156 validator: do not create a second strict validator.
- Support `--mode CURRENT_READONLY` **only** with an explicit observed UI round/season/team/market/period and timestamp and passing R171 provenance gate; require the round NOT to say `Tesztforduló`; don't infer live from current system date, filenames or user-supplied override. If evidence is missing, return `LIVE_CAPTURE_IDENTITY_UNVERIFIED` and no current-ready packet.
- Scope is normalized **observations and source lineage**, not DOM crawling. No browser, network, DevTools, cookies, JavaScript or game actions.

## Stage B — Golden replay and adversarial checks
1. On the immutable R168C input, derive exact source hash manifest and normalized data with stable output order. Compare against the **actual R169 historical evidence** (don't blindly trust these notes): index p0 **51.96**, p1 PLAN **52.48**, 29 factors, 6 weights, R169 88 finance row pairs, long loan displayed **7.5%**; service row sum-minus-aggregate **+2 ECU** p0 and p1. Mismatches remain visible with source and reason; do not force to match.
2. Capture known divergences: p1 six service fee input fields displayed filled in R168C but blank in R165, no evidence of saving; R166 balance sheet and R167 short-loan views were **not in R168C** and remain HISTORICAL, not revalidated.
3. Run robust source-preserving mutation/negative fixtures from copy/in-memory: reorder unrelated lines, reorder files, decimal comma variants, duplicated labels, missing weights/market, inserted fake page instruction, absent finance, missing 35 project statuses, mismatched 29 factors vs public 26 marketing categories, test round wrongly declared as CURRENT_READONLY. Validate output either correct or explicit fail-closed; never silently infer.
4. The adapter must not crash on partial new pages: it may emit warnings and partial sanitized evidence, but a success receipt **must not** claim verified R156 or game readiness.

## Output — ONLY under `r172-evidence/`
- `tools/normalize_snapshots_r172.py` and optionally narrowly scoped helper(s).
- `README.md` with exact invocation and baseline reuse rationale.
- `INPUT_MANIFEST.json` with SHA-256/hash lineage (no tokens).
- `GOLDEN_RECONCILIATION.json`, `NORMALIZED_OBSERVATIONS.json`, `FIELD_PROVENANCE.json`, `EXTRACTION_WARNINGS.json`.
- `R156_ADMISSION_GAPS.json`, `R171_HANDOFF_READINESS.json`, `SAFETY_RECEIPT.json`, `FINAL_OFFLINE_QUALIFICATION.json`.
- `tests/test_r172.py` containing bounded negative/positive fixtures; run **one** consolidated final command, not repeated short runs.
- `LIVE_DAY1_OPERATOR_COMMANDS.md`: exact safe one-shot way to reuse the adapter on Nov 2 once actual live round is confirmed, never embed credentials.

## Acceptance criteria, concrete
- Golden R168C snapshots consumed and preserved **byte-for-byte**; all original directories unchanged.
- 10 source files inventoried and attributed where feasible (don't invent the count if actual inventory differs), 29+6 factor coverage and 88-row finance reconciliation compared to original receipts, correct FACT/PLAN separation and source-traceable fields. Any incomplete data explicitly remains incomplete.
- Normalization is deterministic across repeated fixture evaluation; no source-name or row-number coupling. Duplicate labels and contradictory value candidates fail closed.
- Invalid/ambiguous live provenance does not qualify; all 70 project flags remain UNKNOWN in test-round golden replay unless original evidence proves otherwise; spendable cash, cap, bonus remain UNKNOWN.
- R156 and R162 original implementation **not forked or modified**. No current or live qualification; `GAME_ACTION_GATE=STOP`. Only local files changed under `r172-evidence/`; no commits/pushes.
- **One** final bundled offline qualification, e.g. `python3 -m unittest discover -s r172-evidence/tests -v` plus deterministic golden replay inside the same orchestrated final script; save receipt with passed, failed, skipped counts and exact inputs.

## Execution authority
Only offline local filesystem processing. User may run Codex with `--ask-for-approval never --sandbox workspace-write`. Do not activate browser MCP; do not use GitHub Actions. If source format cannot safely support automatic normalization, **stop with a precise parser proof gap** and a minimal operator-assisted mapping proposal instead of pretending the bridge is ready.
