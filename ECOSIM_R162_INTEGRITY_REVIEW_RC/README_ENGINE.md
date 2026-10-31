# EcoSim R143 — Integrated Offline 5-Year Decision Engine (October 31, 2026)

**A functioning five-year, conditional PROJECT planner, not a verified EcoSim multi-year city simulator.** The goal is to reuse the R143 V2.1 project cards, cost calendar, R142 factor proxy and evidence gate as **one runnable tool**. It requires only Python 3 standard library. No Codex, external Python dependencies, browsers, website requests or account credentials.

## Existing components reused, not rebuilt

- `tools/portfolio_5y.py`: five-year conservative card expenses, dependency evidence, source-currency convention; original remains untouched.
- `tools/r142_proxy_reference.py`: mapped SmartCity factor weighted proxy; original remains untouched and is not presented as the game server.
- `tools/readiness.py`: optional historical league snapshot integrity checks; original remains untouched.
- `data/ecosim_projects_20261030.json`: **35 cards from test round**, not current live game state.
- `evidence/`: R142A research evidence and R143 V2.1 constraints, not copied into a new research line.
- NEW `tools/strategy_5y.py`, `tools/decision_evidence.py`, `tools/qualify_integrated.py`, `run_offline_strategy.sh`, `qualify_once.sh`.

## Run — one example (strictly offline)

```bash
cd ECOSIM_R143_5Y_ENGINE
./run_offline_strategy.sh --budget-per-year 100000 --beam 12 --shortlist 40 \
  --out results/R143_5Y_STRATEGIES_MY_SCENARIO.json
```

**100000 ECU is a deliberately hypothetical ANNUAL project spending envelope**, not verified available money and not a recommendation. When no budget is provided, the engine searches without an affordability cap and flags that as an unfinanceable assumption; no loan or grants are presumed. All candidate rankings are subject to unavailable indirect effects, financing and possible server gating.

Outputs include `.json` and `.md` with annual projects, a conservative **project-card-only** cash requirement, unknown effects, 3 explicitly hypothetical effect-retention sensitivities, and `gameplay_decision=STOP`.

## Re-planning with an observed round (no live fetch)

Copy and fill `inputs/official_state.template.json` from legitimate official UI or export. Do not copy tokens, session cookies, network captures or sensitive metadata. The following must be supplied for a later year:

- `team.initially_active_project_ids`: active projects at start of the current year.
- `team.baseline_smartcity_factors`: all mapped index factor values observed **at the current year**; do not reuse the 2026-10-30 test-p1 baseline for an actual subsequent round.
- `market.maxProjectPerTurn`, `team.project1_active_previous_period` and `team.already_selected_new_project_ids_current_period`, where truly known.
- `team.confirmed_spendable_cash_ecu_by_year` + `team.committed_costs_ecu_by_year` only when legitimately confirmed. Unknown subsequent-year cash cannot be inferred from year-1 surplus.

```bash
./run_offline_strategy.sh --state inputs/my_authorized_state.json \
  --start-year 3 --beam 12 --shortlist 40 --out results/year3_replan.json
```

The engine plans **remaining years only**, starting at the provided year and observed factors. This is rolling *offline* replanning, not autonomous adaptation or automatic data fetching.

## Calibration and league data (read only)

Optionally pass `--league inputs/my_league_snapshot.json` and `--calibration inputs/my_preexisting_observations.json` using the documented existing templates. Without complete, provenance-bearing same-league scores, qualification and rank remain **UNKNOWN**. Previously approved and verifiably restored A/B observations can provide descriptive residuals only; this software never runs, requests, or silently authorizes an EcoSim A/B experiment. A self-reported residual is not independent causal verification.

## Explicit model scope, uncertainties

**Supported within stated assumptions:** all 29 test-round non-running candidate projects, one-time startup+investment and annual **positive** maintenance, conservative annual envelopes (if supplied), recorded dependency labels including conditional same-year co-start, optional `project1` previous-year client bonus, factor-level static multiplicative mapped effects, bounded five-year beam search, rolling replanning, league observation quality checks, shadow calibration measurements.

**NOT supported or intentionally UNKNOWN:** whole city tax/tariff/institution/payroll decisions, loan eligibility/interest settlement, actual cash and grant payments, repeatable or delayed projects, factor caps/nonlinearities/indirect effects, migration and regional competition, server enforcement, actual game index p2–p5, organizer's final tie breakers, optimizer permissibility. Existing running six cards were recorded during the **test round**. Unmapped Hungarian metric aliases are reported, not assumed zero.

Video 2026-10-29: **four projects/year** and **12% loan example** are officially spoken but do not prove live `market.maxProjectPerTurn`, repayment terms or available funding. `project1` previous-period bonus in the client may not follow the simple 20-in-5-years spoken ceiling. The engine allows this **conditionally**, never states that a server accepts it.

This is bounded **beam search**, not guaranteed global optimization. Rankings apply only to known mapped card effects under a frozen counterfactual baseline; the 50% effect and 85% yearly-retention variants are **sensitivity examples, not calibrated confidence intervals**. Five-year spending sums omit many city expenses. Cards with signed negative annual maintenance are conservatively counted at zero for budget requirements; grants never reduce required upfront funds.

### Decision gate

Even a successful offline qualification only proves the software runs consistently. It does **not** validate a single game candidate and never authorizes in-game Start, Save, finalize or credit. Terminal actual index and winning outcome remain unproven. Use the original `R143_V21_CHANGES_AND_GATES.md` for evidence requirements.
