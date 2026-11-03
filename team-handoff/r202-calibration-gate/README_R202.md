# EcoSim R202 – historical finance and operating model calibration gate

## Research, reuse, falsification

This is a historical source-consistency audit, NOT a fitted server model or new optimization engine. It directly reuses the R200 source-profile checks and existing R154 four-tax and R155 six-fee plus eight institutional wage-component functions. R200B/R201's 17×3 bounded Pareto analyses are retained, not rewritten.

The p0 actual versus p1 planned test export supplies 4 directly mapped tax channels, 6 service-fee channels and 8 wage categories: 18 observed–synthetic pairs. The crosswalk uses exact tab/table/row index/label to avoid duplicate label ambiguities, especially transport cost versus service income.

## Evidence findings (private report)

- The first-year synthetic hypothetical bases and wage/fee assumptions are NOT calibrated to observed R94 p0 financial rows. The four-tax, six-fee and eight-wage totals are each reconciled with R200. The observed eight wage components sum to the observed total wage subtotal.
- Observed versus synthetic channel ratios are inconsistent with one exact universal multiplier across the CURRENT FIXED synthetic baselines. This is NOT proof that client formulas are wrong or that a currency conversion ratio is identified: population, vehicle and business/housing counts, worker input, fee conditions and sensitivities are not independently verified.
- A 2-raw-unit six-fee subtotal discrepancy survives independent reconciliation in p0 and p1.
- Do not fit monetary scale using these ratios. p0 is a FACT, p1 is a PLAN, not a closed consecutive actual year. R195's absolute robust scores are not additive to R153/R154/R155 partial deltas.
- R155 institutional wage components rely on synthetic staff inputs. The observed institution snapshot covers one Education subtab, not all city staff.

## Missing evidence

Verified project-card to ledger monetary scale; original p0 tax/fee choices, independently observed population/vehicle/business/housing inputs, closed FACT periods for transition calibration, complete institution/transport/business/population subtabs, server score formula, loan/grant and settlement terms, actual spendable project funds.

## Private native reproduction

The GitHub repository is PUBLIC. Never commit authenticated EcoSim raw extracts, the SHA-pinned private profile, or the report. Only generic code, tests, documentation, runner and .gitignore are in this draft.

On the authorized Fedora machine:

    bash team-handoff/r202-calibration-gate/run_private.sh

The runner requires the local Git-ignored R200 profile, creates a fresh evidence directory in Downloads, executes the original client-source model comparison and tests, and does not call EcoSim or modify gameplay. On a public clone with no private profile, only self-contained synthetic tests run.

    python3 -I -B -m unittest discover -s team-handoff/r202-calibration-gate/tests -v

## Qualification

PASS_SOURCE_DIAGNOSTIC_HOLD_GLOBAL_CALIBRATION means source authenticity and partial arithmetic checks PASS, NOT that the simulator is calibrated or live-ready. Current profile must fail closed through R200, no historical fallback.

GAME_ACTION_GATE=STOP. Draft PR, no merge or release.
