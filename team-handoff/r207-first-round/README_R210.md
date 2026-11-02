# R210 — Original intake-to-advisory current-mode **mock** E2E qualification

## Outcome (Fedora-native, 2026-11-02)

**`PASS_FULL_ORIGINAL_R156_R191_R192_R162_R160_R207_MOCK_E2E`** on two repeated, byte-identical, private temporary mock results. This is a synthetic contract rehearsal, **not a current EcoSim capture**, live score forecast, financing authorization or game-action permission.

The regression `test_r210_current_synthetic_e2e.py` executes the actual original production-path modules rather than merely faking their admission receipts:

1. R156's `create_bundle` builds a local immutable capture from historical *p1 PLAN factor values*, explicitly relabelled with `R210_MOCK_*` identities; no current or server provenance is asserted.
2. R152's original `compile_bundle` constructs the state, preserving all source constraints.
3. R191's real `validate_state(current)`, `validate_r156_bundle`, `year1_finance` accept the mock **structure** and return unapproved / operator-declared results.
4. R192's real `validate_catalog` checks a 35-card mock catalog identical to the pinned solver catalog; a real catalog change must fail closed.
5. R207's actual CLI runs three conditional source-identical R162 bounded searches (50%/80%/100% illustrative ceilings), each with original R157 sensitivities and R160 independent audits, and renders three distinct first-year options. The *same* fixture is executed twice and its JSON/Markdown outputs byte-compared.
6. Negative controls reject **underfunded first-year scenarios**, **changed card definition**, and **historical/test-round provenance passed as current**.

**Native targeted tests:** R191 **112/112 PASS**, R206 **11/11 PASS**, R207 **22/22 PASS**; the independent R209 isolated `python3 -I -B` execution now PASS (12 five-year schedules × 3 synthetic policy paths = 36 partial cases). R206's historical private R200/R204/R205 full join had separately PASSed (9 candidates, 3 new).

## R210 local reproduction

From an authorized Fedora checkout that includes the original R162 modules:

```bash
python3 -I -B team-handoff/r207-first-round/test_r210_current_synthetic_e2e.py
```

No network, no access to EcoSim UI, no gameplay writes. The temporary fixture files are removed after exit. This is *not* an authorization to run the current-round CLI with fake data; only real same-period operator observations may be used outside a test.

## Non-negotiable outstanding evidence gates

- An **actual** current-round complete R156 snapshot: 29 factors, displayed index, observed project statuses, market cap and six weights.
- Real same-period year-one finance / committed obligations and all 35 current card definitions for R191/R192.
- Current ten-tab evidence and independent review; constraints / grants / loan timings / city transition and official scoring still unvalidated.
- Operator review and explicit owner approval before *any* gameplay action.

**`GAME_ACTION_GATE=STOP`; `game_writes=0`; `live_ready=false`. PR stays DRAFT.** All private raw data, captured credentials and temporary reports remain out of the public GitHub repo. The Fedora disk was 98–99% full, so the test used system Python and small temporary files only.
