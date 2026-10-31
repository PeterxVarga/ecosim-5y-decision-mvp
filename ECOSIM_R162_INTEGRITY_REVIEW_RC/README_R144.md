# EcoSim R144 — Integrated Five-Year Planner + Known-Formula City Bridge

**Status:** working offline five-year **project strategy** heuristic, grounded SmartCity **factor aggregation** replayer, R94 historical finance reconciliation, client **project expense / company support** line simulator, and explicitly hypothetical forward finance ledger with **optional long-loan component**. It is **NOT** a verified full-city transition model or a winner predictor.

This extends the **same R143 codebase**; nothing connects to EcoSim or makes game writes. Python standard library only, no Codex run necessary.

## Reused components (unchanged public interfaces)

- `tools/strategy_5y.py`: five-year bounded beam search (projects only), year/condition guardrails and rolling replanning. R144 adds `city_component_bridge` to each ranked plan and makes **user-supplied alternative SmartCity weights** propagate into ranking, sensitivities and annual component replays.
- `tools/portfolio_5y.py`: conservative five-year cost accounting, display prerequisite parsing.
- `tools/r142_proxy_reference.py`: prior R142 default-weight proxy (kept as the legacy reference).
- `tools/decision_evidence.py`: league and calibration gate unchanged.
- `tools/city_bridge.py`: **new, integrated** client-known-component layer.
- `tools/reconcile_r94.py`: **new** historical captured p0/p1 finance identity check.

## Already-generated evidence

- `results/R144_INTEGRATED_QUALIFICATION.json`: 59 integrated offline assertions + explicit `gameplay_gate=STOP`.
- `results/R144_R94_FINANCE_RECONCILIATION.json`: 2026-10-30 p0/p1 cash-flow checks; not an available-project-fund certificate.
- `results/R144_FIRST_ILLUSTRATIVE_PLAN_BRIDGE.json`: five year-by-year known client components for existing R143 best 100k/year **hypothetical** plan.
- `results/R144_R94_PROJECT_ONLY_COUNTERFACTUAL.json`: p1 frozen-other-lines example for projects #8,#13,#27, with/without hypothetical booking of company support; **not** an actual accepted candidate preview.
- `results/R144_EXPLICIT_FINANCE_SCENARIO_ILLUSTRATION.json`: explicitly hypothetical no-new-borrowing ledger.
- `results/R144_EXPLICIT_LONG_LOAN_HYPOTHESIS.json`: optional long-loan ledger at user-supplied hypothetical 12% interest; **credit eligibility unknown**.
- `results/R143_5Y_STRATEGIES_100K_ILLUSTRATIVE.json`: unchanged example strategy ranking now enriched with `city_component_bridge`.

### First-year #8 + #13 + #27 test-card example

| Known component | Client/illustrative value |
|---|---:|
| Signed first-year project expense line (startup + invest + signed runCost) | **90,200 ECU** |
| Conservative first-year project funding requirement (negative runCost ignored) | **99,000 ECU** |
| Separately labelled company support on newly started cards | **3,500 ECU** |
| Historical baseline R94 p1 net result without new projects | **865,588 ECU** |
| If *all nonproject rows remain frozen* and no support is booked | **775,388 ECU** |
| If *all nonproject rows remain frozen* and all labelled support is booked | **778,888 ECU** |

The last two lines are **conditional algebra**, not EcoSim preview, server settlement, available finance or future-year predictions. Other effects (population/business migration, taxes, financing, pension/operating liabilities and feedback) are UNKNOWN. Even the signed negative runCost is **not** guaranteed usable cash.

## Usage

Already-generated outputs can be inspected without running anything. To execute one offline example with deliberately hypothetical *annual project envelope*:

```bash
cd ECOSIM_R143_5Y_ENGINE_R144
./run_offline_strategy.sh --budget-per-year 100000 --out results/my_strategy.json
```

To provide an explicit **nonproject net-cash scenario**, copy `inputs/official_state.template.json` to a new local JSON (never overwrite the template). Add:

```json
"finance_counterfactual": {
  "mode": "EXPLICIT_HYPOTHETICAL_NONPROJECT_NET_ONLY",
  "initial_uncommitted_cash_ecu": 100000,
  "annual_nonproject_net_cash_ecu": [100000,100000,100000,100000,100000],
  "assumption_note": "Hypothesis only, not official EcoSim figures"
}
```

The cash vector is for the remaining horizon, so a year-3 replan needs exactly **three** values, not five. The nonproject net flow must *exclude* the projects being tested. This mode does not automatically borrow to cover deficits.

Optionally, add a **hypothetical long loan** inside `finance_counterfactual`:

```json
"illustrative_long_loan": {
  "opening_balance_ecu": 0,
  "annual_decision_change_ecu": [50000,-30000,0,0,0],
  "annual_interest_rate": [0.12,0.12,0.12,0.12,0.12]
},
"nonproject_flow_excludes_this_loan": true
```

The loader requires that explicit exclusion flag to avoid double-counting the loan. The known client formula is opening debt + positive change − repayment capped at opening debt; interest on closing debt. **The 12% rate is a user-supplied example, not a confirmed live market rate.** Even if computed scenario balances are positive, borrowing may be prohibited or limited by server rules.

An official six-index weight vector can be supplied as `market.smartcity_total_weights`, with keys `Gazdaság`, `Környezet`, `Kormányzás`, `Életkörülmények`, `Mobilitás`, `Emberek`; six nonnegative numbers must sum to one. Do not silently apply historical weights to a known different market. Future factor changes, their nonlinearities and other policy decisions are STILL unknown.

One consolidated local release qualification, if desired:

```bash
./qualify_once.sh
sha256sum -c SHA256SUMS
```

## Decision and evidence boundary

Known: R141 historical p1 displayed factors combine to **52.483733333**, matching displayed **52.48**, and 2026-10-30 R94 p1 income **5,376,812 ECU** less non-reserve expenses **4,511,224 ECU** equals reported net **865,588 ECU**. 18 JS static source hashes were checked in earlier R140B/R142A research, not rerun against bundled JS here (the distributable ZIP does not embed original platform JS).

Unknown, and **never silently zeroed**: actual server cap, authorized project limit, financing eligibility and short-loan constraints, actual spendable cash and grant timing, pension and other obligations, repeatable/delayed project semantics, nonlinear/hidden indirect factors, taxes/fees/institutions/transport policy action responses, competing cities and migration, actual five-year EcoSim score and league placing. Projects are from the **test round**, not a confirmed live-round export.

A single completed offline test is a **software qualification**, not evidence of a winning gameplay choice. All outputs leave `gameplay_decision=STOP` or equivalent. No request is made to modify a live draft, start, save, finalize or borrow.
