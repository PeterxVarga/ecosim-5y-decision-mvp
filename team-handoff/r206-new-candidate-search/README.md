# EcoSim R206 – bounded new five-year candidates, historical only

## Research → Reuse

The repo already contains R162 `strategy_5y.search` (bounded multi-year beam search); it reuses the R142 project proxy, R143 card calendar, R147 direct-effect replay, R148 annual rollout, R157 hypothetical robustness and the independent R160 constraint auditor. R189 can reassign already selected projects between years. Building a parallel optimizer is unnecessary.

R206 wraps **existing** `search` with strict cross-version admission from the R200 16-role historical profile, R204 unified 17-plan packet and R205 five-CSV/100-row provenance reconciliation. The five-year candidate output explicitly identifies any schedules absent from R204. The existing search includes all currently available historical catalog cards, without arbitrary card pruning. Only strict, source-backed R162/R160 audits qualify a plan as *historically test-replayable*, never as eligible in live gameplay.

## Hypothetical envelopes and risk

Three deliberately illustrative project-card envelopes: 50,000 ECU/year with 3 new projects/year, 90,000 ECU/year with 4, and 150,000 ECU/year with 4. **These are not cash availability, actual market cap, or server funding approval.** The 2026-10-30 historical p1 is a plan, not a closed actual city year. Actual loans, support disbursement, tax/fee bases, institutions, population, transport, other teams and official SmartCity scoring remain unknown or only partially observed. A model-score rank is not a forecast.

The source manifest from R205 uses **normalized Library-derived CSV**, not original raw-file byte identity. R206 never publishes those files. The historical project and finance source SHA are pinned via R200/R204; R205 is expected from a completed private historical reconciliation.

## Entry point

`new_candidates.py` takes `--profile`, `--r204`, `--r205`, and `--out-dir`. It reads no EcoSim website, sends no network/game action and never changes a source file. It produces private `R206.json` and `R206_HU.md` in a new output directory. The only project-search implementation called is R162. Search bounds default to beam 3 and shortlist 10, supporting up to 10/40 respectively; performance depends on scenario count and original source search.

A Fedora-native handoff is in `run_private.sh` (existing R200/R204/R205 private reports are required). `test_new_candidates.py` contains only fabricated sources, fake search results and negative/STOP tests; **its success does not qualify native R162 integration**.

## Publication and approval

Only generic code, synthetic regressions, README and a read-only native runner should be committed. The PR remains **draft** pending native E2E, fresh-context review and explicit approval. `GAME_ACTION_GATE=STOP`, actual game writes = 0.
