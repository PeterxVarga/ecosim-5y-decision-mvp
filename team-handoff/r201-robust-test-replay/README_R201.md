# R201 – Source-pinned historical test screening, institutional evidence and robustness

The historical R200 ledger has 16 source roles, but the 51 financial/project results depend on R149/R153–159/R195/R199 and synthetic future policy tracks. R201 **reuses** them and exposes two high-value, previously untreated tests:

1. **Observed institutions**: Validate the original one-page (Education only) UI tables with both p0 actual and p1 target values; independently recompute each institution count × capacity and count × employee averages, and interpret integer-rounded utilisation as an interval. Middle schools show 113% planned utilization against 2,240 seats, a direct overcapacity **diagnostic**, not a server-authorized opening decision. Missing other institution views remain explicitly unmodelled.
2. **Financial P0/P1**: Audit 113 original ledger rows without double-counting totals, preserve 46 display differences but distinguish 44 actual numerical differences from two negative-zero formatting changes. P0 is FACT and P1 is PLAN, not consecutive fact-years.
3. **Bounded robustness of existing candidates**: Reconcile source-pinned R149 15 original five-year schedules × three synthetic policy paths and R199/R195 two exact schedules × the same three paths. For 17 projects plans and 51 partial-fiscal results, calculate worst-case partial mapped index delta, worst partial net and largest zero-opening delayed-revenue stress. Report a *descriptive* Pareto front and hypothetical card-envelope filters 50k / 90k / 100k / 150k. This is **not a new optimizer**, not cash authorization, and not a robust model of real world events. All three policy tracks are synthetic and can be mutually unrepresentative of the game.
4. **Source integrity**: All datasets are loaded through the existing R200 profile and SHA-256 / team / market / period gates. R149/R199 provenance, 17 unique candidate identities and every annual project/cost schedule are checked before comparisons.

## Source and result visibility

The GitHub repository is **PUBLIC**. Commit only this tool, synthetic-only tests, runner, README and .gitignore. The private R200 historical source profile, authenticated Education snapshot, detailed R149 strategy data and computed R201 reports stay on Fedora. Do not commit authenticated captures, cookies, game tokens or private financial files.

## Fedora native run

    bash team-handoff/r201-robust-test-replay/run_private.sh

Requires the R200 private profile at the already-existing gitignored location. To reconstruct it on the owner's authorized Fedora computer:

    bash team-handoff/r200-historical-plugplay/run_historical_private.sh

Runner writes a private R201.json and R201_HU.md to a new temporary evidence directory under Downloads and performs target tests. To run all previous gates:

    python3 -I -B -m unittest discover -s team-handoff/r196-city-review/tests
    python3 -I -B -m unittest discover -s team-handoff/r197-r198-city-join/tests
    python3 -I -B -m unittest discover -s team-handoff/r200-historical-plugplay/tests
    python3 -I -B -m unittest discover -s team-handoff/r201-robust-test-replay/tests

## Non-negotiable limits

- The numbers from the original financial UI **do not have a verified money-unit conversion** to project card ECU, even if the display values appear comparable. Neither the 865,588 displayed reserve transfer nor a modelled positive partial cash flow proves spendable money.
- Institutional enrollment is not known exactly; observed utilization percentages may be rounded and the p1 column is a **target**, not a completed following year.
- User-made tax, staffing and fee changes do not establish causality from two UI columns. The original R153/R155 synthetic baselines have not been calibrated to the live simulator.
- Ten tabs are tracked but not fully captured; public 26-label versus 29-factor server aggregation and game funding rules remain unknown.
- Future live data **must** enter through a new read-only R200 profile and new model qualification, never via historical fallback.
- No game writes, no global optimum or server score prediction. **GAME_ACTION_GATE=STOP**, PR stays draft for independent review.
