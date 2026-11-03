# EcoSim R209 — exact 12 × 3 historical project/policy/finance reuse

This is **not a new simulator**. The source-pinned original R162 project search and R160 audit are joined to the existing R153 tax response, R154 four-tax, R155 six-fee/institution operating, and R159 per-channel cash-timing models. All three policy paths are explicitly `SYNTHETIC_TEST_ONLY`, and the source is the historical **p1 PLAN**, not a later observed FACT.

## Results (local offline source execution)

- 3 distinct hypothetical annual card ceilings, 75k/120k/150k ECU (assumed base cap of 4, never declared as live funding).
- 4 bounded original R162 plans per envelope = **12 schedules** with zero hard R160 violations.
- Each schedule is evaluated across the original 3 source-identical synthetic tax/fee/institution paths: **36 matched five-year project/policy/timing cases**.
- Every combination preserves the precise five-year project IDs and total card cost. Delayed receipts are tracked by tax and fee income **channel**, not silently netted against institutional payroll.
- Negative tests require mismatched source classes and corrupted total project costs to **fail closed**.
- All eight reused core source files (R153, R154, R155, R156, R158, R160, original project catalog/cost and strategy) were compared to the current GitHub Git-blob IDs before the local run.
- Sampled Pareto and partial fiscal outputs are hypothetical. In particular, a positive five-year *partial net* is **not available city cash**, and a zero-opening shortfall is **not a real borrowing requirement**.

## Reproduce

From the repository root:

```bash
python3 -I -B team-handoff/r207-first-round/test_first_round.py
python3 -I -B team-handoff/r207-first-round/test_original_r162_integration.py
python3 -I -B team-handoff/r207-first-round/test_r209_policy_finance_reuse.py
```

Only **existing published, synthetic/historical test fixtures** are read. The R209 script emits a structured JSON result to stdout; do not commit the private run results.

## Known blockers

This does not authenticate the live R191/R192 gate; it does not identify actual spendable funds, government/partner grants, loan ceilings, full future population and business dynamics, all institutional costs, future closed FACT years or official score. The actual R206 private R200/R204/R205 source-gated E2E is still HOLD while Fedora is offline.

**GAME_ACTION_GATE=STOP. Draft only; no merge/release or gameplay actions.**
