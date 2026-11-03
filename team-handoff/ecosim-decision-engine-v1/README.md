# EcoSim R204 – unified historical decision engine

An offline, source-hash-checked **historical test-only** workflow over existing R201/R202/R203 reports. No new independent simulator. The two modules produce a unified packet and a candidate comparison without logging into EcoSim or writing gameplay state.

## What this proves

- Identical 17 candidate IDs, first-year project sets and five-year card costs across R201 and R203.
- Identical 18-channel calibration source identities, 51 conditional policy evaluations and 85 annual ledgers.
- 255 direct-effect sensitivity computations reused; five-year partial model ranking rechecked.
- Every plan's worst partial net and four hypothetical annual cap filters are reconciled.
- A Hungarian 17-plan comparison table and machine-readable CSV/JSON are produced privately.
- Fail-closed when server accuracy, spendable cash, current-round readiness or game action is asserted.

## What this does NOT prove

No full city dynamics, current-round observation, monetary unit calibration, financing authorization, verified loans/grants, server score model or global city optimum. The R203 input is a **p1 PLAN**, not a second completed FACT year. Unknown indirect effects are not zero. Illustrative 50k/90k/100k/150k project caps are not real budgets. Cross-scenario partial net is not available cash.

## Native verification

Use `run_private.sh` on the authorized Fedora machine with the previously generated local historical R201, R202 and R203 reports. It creates a new private output directory containing `DECISION_PACKET.json`, `DECISION_PACKET_HU.md`, `DECISION_COMPARISON.json`, `DECISION_COMPARISON_HU.md` and `DECISION_COMPARISON.csv`.

Run synthetic, independent public regressions with:
`python3 -I -B team-handoff/ecosim-decision-engine-v1/test_decision_brief.py`

All historical authenticated source exports stay under gitignored local paths. Code, synthetic tests and README only may be committed. **GAME_ACTION_GATE=STOP. Draft PR; no merge or release.**
