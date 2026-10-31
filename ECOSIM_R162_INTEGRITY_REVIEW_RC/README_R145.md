# R145 – Combined five-year project + operating-policy scenario engine

**Working offline software, NOT a complete EcoSim emulator.** Extends R144 in place. No web, browser, login, game write, or Codex execution. Python standard library only.

## What was implemented (not just planned)

1. `tools/policy_tracks.py` — strict parser for tax, service fee, institution, staffing, transport, environment and social operating-decision tracks. Each action has a year, a declared effect-duration, **optional** percentage response per supported factor, **optional** annual cash delta, and source/assumption note. Missing effects are recorded as unknown, never treated as validated zeros.
2. `tools/joint_5y.py` — for each bounded, explicitly supplied five-year operating track, **reuses the existing R143/R144 project optimizer** with an adjusted illustrative project envelope. Positive hypothetical policy cash never increases the envelope; negative cash is reserved only where the user explicitly declares that the envelope excludes the extra policy expenditure. Omitted overlap evidence leaves financing **unknown**.
3. Linked factor replay — combines project-card mapped effects and supplied policy effects into the existing six-index SmartCity aggregation. The output is a mapped-factor **counterfactual**, not the actual game response, and no cross-track result is a verified winner.
4. Optional policy cash overlay — attaches to R144's hypothetical project + cashflow + loan bridge **only if** the supplied nonproject cashflow explicitly excludes the policy cash effects. Null/unknown effects disable numeric cash conclusions.
5. Multiple-track comparison, annual project plans, annual budget reservation, year-5 mapped-component comparison, and separately labeled evidence gaps. Results written as JSON and readable Markdown.
6. One consolidated `qualify_once.sh` — **59 legacy R144 tests + 26 R145 checks = 85/85 PASS**. The test uses deliberately fake/synthetic policy responses to show integration correctness; these are not learned or discovered EcoSim coefficients.

## Already-generated outputs (you do not need to run anything)

- `results/R145_JOINT_SYNTHETIC_100K.md`: side-by-side, 5-year illustrative tracks.
- `results/R145_JOINT_SYNTHETIC_100K.json`: all generated plans, assumptions, unknowns and synthetic counterfactual factors.
- `results/R145_INTEGRATED_QUALIFICATION.json`: consolidated 85-check result.
- All previous R143/R144 outputs, code, historical R94 finance snapshot, and evidence remain in the **same** tree.

## Future local use (optional)

```bash
./run_joint_offline.sh \
  --policy-tracks inputs/policy_tracks.synthetic.example.json \
  --budget-per-year 100000 \
  --out results/my_joint_scenarios.json
```

This is **NOT** a € or ECU budget recommendation. 100,000 ECU/year in the example is hypothetical. The example policy +2% training-related response and -5,000 ECU/year expense are wholly fabricated **test fixtures**. No actual EcoSim tax/service fee/staffing factor coefficients are inferred.

On real historical or official data, replace **both** the state template and tracks with provenance-preserving user-authorized values; never assume a `DOCUMENTED_OBSERVATION_ONLY` flag alone means actual server validation. The original R144 `--start-year` rolling replan remains available. All game-changing experiments remain prohibited without user authorization and verified undo behavior.

## Most important missing data

- Authenticated *read-only official* market/setup/team snapshot, explicit current period, original project state, free cash / commitments, credit constraints and interest rates.
- True future effects of taxes, fees, institutions, staff, transport, wages, loans and services; nonlinear interdependence and end-of-year transitions.
- Repeatable/delayed project rules and unrecognized card-factor aliases.
- Competing cities, population/company migration and unobserved market changes.
- Measurement of the project's and operating decisions' **actual** EcoSim plan-to-fact errors, with explicit owner-approved reversible candidate preview if needed.

**Decision gate remains STOP** for gameplay; nothing generated here is a validated winning strategy.
