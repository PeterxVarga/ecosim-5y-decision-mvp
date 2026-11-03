# R203 — FACT-vs-PLAN-safe annual transition evidence (R148 reuse)

## Objective and falsification

The R94/R156 corpus contains **p0 FACT** and **p1 PLAN**, not two consecutive settled FACT years. Thus there is no observed city-transition training pair in the admitted test corpus. The p1-factors-based R191 initial state is not a validated live server state.

The existing R148 annual_component_rollout already applies direct source-supported card effects, cash/card costs, and explicit hypotheses, while maintaining unknown city drift, incomplete financing, latent saturation, and unmapped indirect effects. R203 REUSES it, not another unverified simulator.

## Exact historical evidence

- R200 SHA-locked 16 source roles / ten-tab coverage; R201 17 plans × three synthetic policy tracks = 51 partial fiscal results; R202 18 observed-to-synthetic revenue/payroll channel matches.
- 15 R149 plus 2 exact R195 full five-year schedules = 17.
- 17 × 5 = **85 R148 annual component ledgers** with exact year/card cost reconciliation and no actual city transitions.
- R148 combined_factor_replay is run with 0.5×, 1× and 1.5× assumed direct project effect intensities for each annual cumulative project set = **255 partial factor stress calculations**. At 1× the model must reproduce the original R148 annual ledger exactly.
- Index output is a *direct-component-only conditional score*, NOT an EcoSim server prediction. Saturation-only bands do not bound business/population/market responses, indirect effects, taxes, loans, or real city performance.
- Conditional rankings are model-sensitivity diagnostics, not a validated global optimum. No learned error probabilities.

## Future operator-declared closed-FACT contract

The independent fact_pair_r203.py provides a STRUCTURAL-only gate for two consecutive closed FACT snapshots with 29 factor keys, two independent evidence IDs, same team/market and appropriate financial fields. It rejects the current p0 FACT / p1 PLAN pair.

An accepted pair is descriptive data, not cryptographically authenticated EcoSim server evidence or an identified causal model. It returns only observed differences, with GAME_ACTION_GATE=STOP.

    python3 -I -B team-handoff/r203-transition-evidence/tools/fact_pair_r203.py \
      --input /private/two_closed_FACT_snapshots.json \
      --out-dir /private/fresh_output_directory

## Native historical reproduction

On the user's Fedora device, with the gitignored R200 source profile and the earlier private R201/R202 reports:

    bash team-handoff/r203-transition-evidence/run_private.sh

Private source and result files are never committed to the PUBLIC repository. The runner creates a fresh read-only R203 JSON + Hungarian Markdown report under Downloads. No EcoSim access or gameplay writes.

## Readiness limits

Actual consecutive completed years, verified financial units, whole-city state variables and transitions, city policy effects, client-server score formula, grants/loans and spendable funds are NOT known. Current-mode modeling remains HOLD. The experiment is historical/offline with fixed p1 planned baseline, not live accuracy certification.

**GAME_ACTION_GATE=STOP. PR draft, no merge.**
