# R144 — Evidence-first integration report (2026-10-31)

## Objective and outcome

Upgrade the actual R143 five-year project engine into a unified **known-formula component** model, not another Codex task or new project. Reuse R142 proxy, R143 project accounting, prior R94 observed cash-flow data and R142A static client evidence; add integration **before** any additional game-model optimization effort.

### Delivered

1. **Score decomposition and weight adapter:** six SmartCity subindexes with the observed government extra debt quarter, inverse socioeconomic share and mobility/people penalty quarter. Historical p1 factor aggregation 52.483733333. Explicit market weight vectors propagate through the heuristic, unlike old hardcoded R141-only weights. Values are computed from displayed factors, not actual future factors.
2. **Client project accounting bridge:** startup + investment of newly started projects; signed maintenance of all relevant active non-repeatable projects; separate company-support label. Conservative funding demands use positive maintenance only and never pre-credit support. Running test-round six projects included only as historical initial state fallback.
3. **History reconciliation:** p0/p1 finance table observed rows and 8 identities/controls, with no false inference that the 865,588 ECU net surplus is spendable cash. Historical fixed-other-lines conditional p1 arithmetic is separated from actual EcoSim preview.
4. **Forward counterfactual ledger:** only if an explicit hypothetical nonproject net flow and opening cash are provided, an annual no-new-borrowing liquidity scenario is computed. Optional long-loan opening/changes/rates uses the known client components; credit eligibility and settlement remain UNKNOWN.
5. **One integrated release gate:** 59 offline checks, including 30 retained R143 checks, historical accounting, weight propagation, factor aggregation, negative maintenance and support separation, missing-input rejection and loan scenario guards.

### Not delivered / cannot honestly infer

- Full server-backed or deterministic five-year city evolution.
- Tax, fee, institution, payroll, service or regional movement response function.
- Game-certified available finance, loan limits, project start authorization, score or winner.
- Market/team current configuration, 2026-11-02 live round states or 2026-11-01 approved test candidate preview.

### Next dependency, highest value

The **actual official market/team configuration and paired observational data**: current six index weights and 28 factor observations; current already selected/active project IDs and past `project1` state; spendable financing and commitments, credit constraints and grant timing; and, when independently approved and reversible, one candidate's actual index and finance preview. Until those data exist, engineering additional years of fabricated economic dynamics is lower ROI than calibrating the proven client components.

All outputs are **read-only/offline**, and the software remains a conditional planner with `STOP` gameplay gate.
