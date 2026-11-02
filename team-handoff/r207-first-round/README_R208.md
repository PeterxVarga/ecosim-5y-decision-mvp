# EcoSim R208 — first-year decision quality hardening (historical rehearsal only)

**Integrated in the existing R207 code, not a parallel optimizer.** The original R156 capture validator, R162 five-year search, R157 direct-card sensitivity and R160 independent constraint audit are reused unchanged.

## Source-backed defect and correction

The previous R207 grouped plans by first-year IDs and silently retained the first plan's five-year proxy and future continuation. If a later plan used the *same* first-year action but a different four-year continuation, its worse outcome and uncertainties were hidden. It also sorted all actions by proxy and could select three expensive choices while omitting the lowest-budget scenario altogether.

Now the advisory:

- Requires a matching five-year sum and **full annual R160 cost replay**, and rejects any year's card need beyond its explicitly hypothetical scenario ceiling.
- Requires all four original R157 stress profiles, their computed model minimum, and explicit `city_dynamics_uncertainty_bounded=false`, `scenario_min_is_game_lower_bound=false`, and STOP. Missing stress evidence fails closed.
- Aggregates **all** audited future completions for an identical first-year action. Shows sampled nominal and R157 stress ranges, the minimum sampled stress, count of distinct continuations and the five-year card-cost range. Ranges are **not probabilities, confidence intervals, or bounds on actual EcoSim outcomes**.
- Counts distinct scenario names, not duplicated plans, as support. Rejects duplicated scenario labels and materially inconsistent same-action first-year costs.
- Preserves decision diversity by choosing one eligible action for the lowest **available** scenario envelope, then uncovered higher scenario envelopes, then the strongest remaining modeled actions up to three. A scenario with no feasible candidate is not fabricated.
- Preserves original R191/R192 current-source and first-year finance gates in the CLI; **no permission to submit anything in EcoSim**.

## Proportional verification

- `python3 -I -B team-handoff/r207-first-round/test_first_round.py`: 22 standalone synthetic regressions, including seven new tamper and decision-quality cases.
- `python3 -I -B team-handoff/r207-first-round/test_original_r162_integration.py`: exercises the exact original R156 normalization, R162 search, R157 scenario outputs, and R160 independent replay with all 35 cards and 29 historical factor values. The harness converts the archived historical **p1 PLAN** into an **explicitly synthetic** local CURRENT_READONLY fixture solely to exercise the R156 parser; R191/R192 receipt values are also fabricated strictly inside this test. It must **NEVER** be represented as an observed current round, server authentication, or a true R191/R192 E2E test.
- Three illustrative annual card envelopes (75k, 120k, 150k ECU); 3 source search calls; 12 independent R160 audits; 4 distinct first-year project sets; 3 selected options spanning all three envelopes. No game calls or writes.
- Exact original Git blobs verified against GitHub for `strategy_5y.py`, `portfolio_5y.py`, and `independent_audit_r160.py`.

**Cannot certify:** current card catalog identity, any actually spendable amount, real-world tax/fee/loan/grant effects, complete institutions/population/transport transitions, true server score, two closed factual years or current-round readiness. R206 full private R200/R204/R205 admission also remains unexecuted because the Fedora device is offline.

**Release decision:** draft only, no merge, no gameplay actions, `GAME_ACTION_GATE=STOP`.
