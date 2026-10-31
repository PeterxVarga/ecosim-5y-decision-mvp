# R175 — Pre-Live Strategy Readiness Pack (not another parser)

**Status: IMPLEMENTATION ASSIGNMENT, NOT EXECUTED.** 2026 X-Challenge test round ends 2026-11-01, public schedule lists live rounds from 2026-11-02. This task is entirely offline and must finish without any live-game observation, action or new optimizer. The R174 parser/E2E chain is FROZEN following operator-reported `PASS_OFFLINE_E2E_FAIL_CLOSED` (13/13) and stays unchanged.

## Critical-path objective
Improve actual decision speed and quality on live Day 1 by **(A) preserving the qualified offline tools, (B) precomputing evidence-labelled conditional first-year strategy families using R162's EXISTING robust/proxy search, (C) resolving or precisely documenting the public 26 vs test-UI 29 factor taxonomy mismatch, and (D) preparing a 10-minute operator review decision sheet**. Do not confuse hypothetical rankings with game recommendations, full score forecasts, or verified budgets.

## Sources and scope
1. On-disk `r174-evidence/qualification/FINAL_OFFLINE_QUALIFICATION.json`, `E2E_STEP_LEDGER.json`, `SAFETY_RECEIPT.json`, `r174-evidence/LIVE_DAY1_ONE_SHOT_RUNBOOK.md`; `r173-evidence/` parser + receipt; `r171-evidence/` live import; `r170-evidence/` crosswalk; `r169-evidence/`; R168C frozen raw snapshot manifest. Operator reported R174 success but **this GitHub author has not verified the local artifacts**. Compare on-disk hashes, code version, statuses and source lineage first; never fabricate.
2. Canonical `ECOSIM_R162_INTEGRITY_REVIEW_RC/`: `tools/strategy_5y.py` uses `tools/robust_decision_r157.py` (four explicitly synthetic effect-intensity/retention profiles and sampled first-action regret), `tools/portfolio_5y.py`, R160 independent replay, R142/R148 source-anchored factor proxies, 35 historical project cards. Reuse existing API/CLI and exact schemas. The R162 code has a historical fallback of 4 project starts/year and historical running-project states; **these are NOT live facts**.
3. Public 2026 organizer page https://www.xchallenge.hu/ currently describes **26 evaluation criteria in six categories** with specific Hungarian titles, 20+ project examples and 5 live years; university explainer https://epget.bme.hu/wp/hirek/x-challenge-2026-tunj-ki-ott-ahol-a-donteshozok-figyelnek/ describes five-year terminal balance and league competition. The recorded Z test UI has **29 factors / 6 weights** and 35 historical projects. This mismatch is a research hypothesis, not grounds to delete 3 factor rows. Do not import a different 2025 Smart City competition's rulebook.

## Stage 0 — research, falsification, reuse check
- Read the actual local R174 receipts and R162 R157 API first. Inspect existing illustrative scenario runners and reports to avoid rebuilding sensitivity logic. If R162 project catalog lacks demonstrated stable identity for new live market, keep every scenario `HISTORICAL_ONLY`.
- Pre-register false claims to avoid: `test budget=live spendable`, `historical project1 bonus enabled today`, `5-year model is exact game score forecast`, `R157 profile-min is real-world lower bound`, `public 26 are exact R162 metrics`, `29 test UI are necessarily the live scoring keys`, `all 35 1-to-1 semantic name matches are confirmed game IDs`.
- Check applicable competition conditions for external decision assistance if accessible in existing *local/public* materials; record UNKNOWN if not. No scraping logged-in game or untrusted APIs.

## Stage A — freeze safety (small, critical, non-destructive)
- Under `r175-evidence/release-freeze/`, create a **source-hash lock manifest** identifying exact R173 parser, R171 provenance, R156/R162 validators, R174 orchestration and receipts, and the local R162 git SHA. Include file path, byte length, SHA-256, observed receipt status, dependencies; do not assert these have been separately independently audited.
- Use only **sanitized** release metadata and code/receipts known to exclude secrets; do NOT copy raw authenticated browser snapshots, credentials, session tokens, user email, personal details or uncontrolled source trees into a public/upload-ready bundle. Work from a fresh output directory; do not modify any R168–R174 source or receipts; reject symlinks and collisions.
- Generate `VERIFY_FROZEN_RELEASE.py` (or reuse an existing hash verifier) to detect drift later. A copy on the **same disk is not a disaster-recovery backup**; describe external private backup as a separate optional operator action, not an automatic push.

## Stage B — six bounded historical strategy cases, maximize reuse
- Use R162 `strategy_5y.search`, R157 `robust_decision_r157`, and R160 independent audit, with **historical Z test project cards and documented baseline only**; don't alter original R162. Use a tiny launcher under `r175-evidence/tools/` *only if needed* to orchestrate existing functions.
- Construct a **small fixed matrix of at most six distinct** explicit hypothetical cases: base project caps {2,4} and 3 expenditure ceilings derived in a deterministic way from **observed historical card cash-cost quantiles** or explicitly labelled synthetic scenarios. If full five-year envelope cannot be justified as a hypothetical constant, use consistent explicitly synthetic year-by-year vectors. Never present as live authorized budgets; do not use p1 865588 reserve as spendable. Do not mix across cases in rank comparisons.
- Handle project-1 prior period status as an **unknown predicate**. Prefer the conservative no-bonus branch; if cheap and useful compare `project1prev=true` as a **separate hypothetical sensitivity** within the runtime bound, clearly labelled. Never assume it is current.
- For each case, generate a **small top candidate shortlist** with: year-one new IDs and historical names, 5-year schedule, dependency caveats, conservatively calculated card expenses (not real cash authorization), proxy terminal index delta, four synthetic R157 sensitivity profiles, sampled first-action regret within the same case, unknown/unmapped effects, saturation uncertainty, R160 independent plan replay warnings and actual gameplay gate STOP.
- Compare *candidate robustness across assumed conditions only* with a `SCENARIO_PERSISTENCE` table (e.g. a project family appears in N/6 cases), NOT a global ranking or win probability. Keep weaker and cheaper fallback/no-project strategies if possible. Never claim that project card effects include all city dynamics, taxes, company migration, population and peer response.
- If running the existing R162 search costs disproportionately more than its informational value, **do not rebuild it**: restrict beam/shortlist and 3 cases, record runtime and coverage. Avoid 20 tiny iterative tests; use one bounded final scenario qualification.
- Do not automatically merge semantic Hungarian name translations from R170 with the historical ID reference; distinguish exact historical ID/name from translator candidates. Do not calculate live actions.

## Stage C — 26 vs 29 explicit mapping review
- Extract 26 **exact marketing labels**, 6 category headings and counts from the PUBLIC organizer page (if no local captured source, use documented public manual/source text or mark `UNVERIFIED_PUBLIC_SOURCE`; this task author did verify https://www.xchallenge.hu/ on 2026-10-31). Match to the **29 actual R162/test UI source factor keys**: `EXACT_LABEL`, `SEMANTIC_CANDIDATE`, `ONE_TO_MANY`, `MISSING_IN_UI`, `NOT_ASSESSABLE`. Preserve both original texts, provenance and don't force a 26:29 bijection.
- Create `METRIC_TAXONOMY_FALSIFICATION.md` and `METRIC_26_TO_29_CANDIDATES.csv`. Rank the top mismatches by impact on scoring, and the minimum future UI-visible evidence that would resolve them. Do **not** change any R162 coefficients or weights on marketing evidence alone.
- State that the public sample sliders on the X-Challenge website are **illustrative**, not authenticated server scoring formulas.

## Stage D — Day-one decision workflow, not a game action
Create `LIVE_DAY1_DECISION_CARD.md`, one page with:
- Exact order: observed *non-test* round/team/market/period -> passive snapshot -> qualified R173/R174 normalization+provenance -> 29 factors/weights and explicit 35 project IDs/states (if safely attributable) -> true market cap/project1 previous-period status -> spendable cash after committed costs, loan/grant settlement -> R156 & R162 readiness.
- **GO/STOP on each component separately**: `parser_qualified` does not imply `live_provenance_confirmed`; `R156_admitted` does not imply `affordability_verified`; only explicit operator approval authorizes gameplay.
- A conditional shortlist selection table: pick matching historical scenario by observed cap/funds/provenance **only if actual market catalog/baseline semantics match**; otherwise report `NO_TRANSFER` and run existing R162 on newly validated data, not historical fallback.
- Real 10-member league ranking comparison only from an observed, complete league snapshot; no invented competitors.
- The site documents two-day live rounds; this task must not schedule a gameplay operation or assert an exact closing hour not in verified source.

## Output only under `r175-evidence/`
- `README.md`, `SOURCE_MANIFEST.json`, `release-freeze/FROZEN_SOURCE_HASHES.json` and optional simple verifier
- `SCENARIO_MATRIX.csv`, `FIRST_YEAR_DECISION_FAMILIES.json`, `SCENARIO_PERSISTENCE.csv`, `CAVEATS_AND_FALSIFIERS.md`
- `METRIC_26_TO_29_CANDIDATES.csv`, `METRIC_TAXONOMY_FALSIFICATION.md`
- `LIVE_DAY1_DECISION_CARD.md`
- `FINAL_OFFLINE_QUALIFICATION.json`, `SAFETY_RECEIPT.json`
- Optional minimal orchestration script only if existing R162 tools do not already handle the requested batch.

## Qualification
Perform **one bounded final offline check** after implementation: frozen source hashes, original source immutability, no secret leakage, six scenario caps and per-case affordability assumptions labelled synthetic, R160 consistency per result, R157 no false bound/probability, 26-to-29 unforced mapping, unknown state flags still UNKNOWN, no generated live R156 complete packet, gameplay STOP. If unable to generate a bounded scenario matrix, report exactly why and preserve the rest as partial; do not fake coverage or PASS.
- `PASS_OFFLINE_STRATEGY_PREP_ONLY`: all planned source/strategy/falsification gates met; historical conditional strategy supports **review**, never live gameplay.
- `PARTIAL_OFFLINE_PREP`: safe but incomplete, with explicit gap.
- `FAIL_OFFLINE_PREP`: source integrity, false authority, or strategy verification failure.
- Always `LIVE_ROUND_VALIDATION_NOT_PERFORMED=true`, `R162_LIVE_DECISION=STOP`, `GAME_ACTION_GATE=STOP`.
No browser, no logged-in EcoSim, no network API, no commits/pushes or GitHub Actions from the user-side execution. Keep the FROZEN R174 pipeline unchanged. Do not make another general parser/research framework.
