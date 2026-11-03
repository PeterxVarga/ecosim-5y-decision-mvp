# EcoSim R211 – historical partial-finance stress integration

## Intended E2E capability

Source-pinned R205 loan/grant observations + R206 historical identity + **original** R153/R154/R155/R158/R159 fiscal timing applied to the R209 12 project schedules × 3 policy paths. Generate a read-only Hungarian decision diagnostic with 108 (36×3) *incremental* cash-pressure stress cases, with exact annual replay and no invented cash, loan limits, approved credit or subsidy disbursements.

**THIS IS NOT AN ECO-SIM CASH BALANCE, FUNDING GAP OR APPROVED PROJECT BUDGET.** R159 reports **changes versus a fixed, unknown reference fiscal path**, not the city's absolute income or cash. A large model-relative "buffer" must never be represented as actual money needed for a real game decision. The R205 7.5%/12% historical loan-rate observations and grant revenue lines are reported only as provenance, and contribute **0 ECU** to usable cash.

## R211 engineering / reuse

- Reuse R209's checked original R162 search and R153–R159 policy/cash calculators. R209 gets only an optional `include_joined` return of its already computed R159 rows; the preexisting default test result does not change.
- R205's five normalized CSVs and SHA-256 source manifest (private on Fedora) must exactly match the R205 qualified report. Its historical monetary units are explicitly distinguished from real approved finance.
- R206's historically pinned R205 report SHA must match the one used; live/historical source confusion causes HOLD. No change of source class is allowed.
- For each of 36 combinations, independently recompute five year labels/IDs, project card costs, all four-tax/six-fee/institution splits, immediate vs deferred annual incremental net, cumulative values, and both R159 peak relative-pressure fields. Reject any drift.
- Evaluate three explicitly **illustrative additional obligations**: 0, 10,000 ECU/year, 25,000 ECU/year. These are a model-level extra-pressure sensitivity, **not verified future costs**. No grant/loan income is assumed.
- Compare the four R209 plans in each LOW/MID/HIGH assumed card-envelope tier. Display **one lowest worst-case cash-pressure diagnostic per tier**, not a globally optimum financial plan; preserve 12-plan and 36-policy evidence.
- Preserve `GAME_ACTION_GATE=STOP`, game writes 0, status historical-only.

## Run

On Fedora, with private historical inputs already present:

```bash
bash team-handoff/r211-financial-stress/run_private.sh
```

This runs the R211 12 targeted tests, the original R209 source-model join, and runs R211 twice to byte-compare its JSON and Hungarian report. The runner uses the existing original source modules and native Python; no dependencies are installed.

Reproducible private output `R211.json` and `R211_HU.md`. Raw historical normalized data, private reports and credentials **are never committed**.

## Additional 1→2-year replan drill (same approved scope)

`test_mock_year2_replan_r211.py` reuses the original R203 two-closed-FACT structural gate with a deliberately FAKE pair (p1 historical PLAN factors relabelled only inside the mock fixture plus an artificial 0.5 point factor perturbation). It then constructs an explicit hypothetical year-two active project set and calls **the existing R162 year-two-to-five search and R160 independent audit**. Two replays are byte-compared. A PLAN inserted in the pair, a skipped year, and a different market team are rejected.

This is proof that a **synthetic period transition can be ingested and replanned structurally**, not that two actual closed FACT years or causal city dynamics exist. The sampled model may yield several five-year continuations but only one distinct next-year action; do not claim three independent options where they do not exist.

## Evidence limitations / next ROI

The real turn needs **same-period observed spendable funds and committed liabilities**, current loan ceilings/rates, grant timing, and 35 current cards to make a reliable first-year financing assessment; future city transition, population/transport/company responses and official server score remain UNKNOWN. R210 proves only a MOCK current-mode E2E. R211 does not authorize gameplay, release, merge or live financial assumptions.
