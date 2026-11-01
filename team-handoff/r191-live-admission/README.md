# R191 — Live Admission Hardening (EcoSim, read-only)

**Qualification: `PASS_LOCAL_CONTRACT_REGRESSIONS_NATIVE_E2E_HOLD`**  
**GAME_ACTION_GATE=STOP** · **No EcoSim writes, no automated gameplay, no GitHub main changes**

## Why this chunk

The original R162 full historical release candidate passed its own historical E2E previously, but the newer R189/R190 bounded rescheduler has not passed native integration with the exact pinned R162 checkout. The previous `run_r162_shadow.py` used plain `json.loads()` and did not require a CURRENT_READONLY capture packet or year-one finance evidence before treating data as a source. This release adds **strict input admission** while retaining the unchanged `bounded_shadow_r189.py`.

## Implemented

- `tools/admission_r191.py`: explicit `historical` / `current` modes; no historical test input accepted as live; complete 29 direct factor baselines; 35 project-status rows with exact R156 hash-linked receipt; actual market cap, six aggregation weights, provenance, capture freshness (48 hours) and same-period state consistency. Checks reference the original R156 packet's immutable hashes; these hashes **do not** establish an authenticated EcoSim origin.
- Current-year financing gate is separate from the speculative remaining four years: the operator must explicitly record observed year-one spendable/committed figures, matching period, source and near-time capture. If the candidate's first-year **illustrative** budget exceeds declared residual funds, stop. This is **not a server-approved budget**.
- `tools/run_r191_shadow.py`: imports the **original R162 `json_integrity_r162.read_json`** after checking clean pinned Git HEAD. Uses original R162 strategy and original R160 audit, selects a seed only if **zero hard violations and zero conditional items**, applies unchanged R189 local year-only improvement, and re-audits every accepted candidate. Requires explicit mode and source; original R162 fallback on missing active/factor/bonus/cap never authorizes current analysis.
- Only creates a **new output** outside the pinned repo and its working tree; no game requests. The generated report retains complete evidence/HOLD/proxy labels and never marks gameplay approved.

## Verified in this container (2026-11-01)

| Test chain | Executed | Result |
|---|---:|---|
| R189 existing structural regression | 19 | PASS |
| R190 existing source receipt regression | 6 | PASS |
| R191 new admission and mocked runner contract tests | 30 | PASS |
| **Total** | **55** | **55 PASS** |

`tests/test_r191_runner.py` mocks the **native R162/R160 imports** for contract verification. It is **not** proof of native R162/R160 execution. Old R189/R190 tests are rerun from their retained original ZIPs, not repackaged as newly developed tests. Full native integration with the clean exact Git pin remains HOLD.

## Team commands

Run the new tests from the project branch:

```bash
python3 -B -m unittest discover -s team-handoff/r191-live-admission/tests -v
```

For a **test-round-only** scenario, create a *separate, clean, detached* worktree at the original R162 source pin and run:

```bash
git worktree add --detach ../ecosim-r162-pinned 9d2d17d822bb97a210151e269454a0432a1952ae
python3 -B team-handoff/r191-live-admission/tools/run_r191_shadow.py \
  --mode historical-test \
  --repo-root ../ecosim-r162-pinned/ECOSIM_R162_INTEGRITY_REVIEW_RC \
  --state team-handoff/r191-live-admission/examples/historical_test_state.json \
  --annual-budget 100000 --cap 4 \
  --out /tmp/ecosim-r191-historical-$(date +%s).json
```

For an actual **current read-only** snapshot, first use R156's supported capture/export pipeline and its generated `manifest.json`, `factors.csv`, `projects.csv`, `parameters.json`, `R156_ACQUISITION_RECEIPT.json`. The `--state` must be an R152/R149-compatible normalized JSON for the **same** current period/team/market, matching the hash-linked receipt. A separately observed year-one finance file is also required. No example in this package claims to be live data.

Example **shape only** of the finance file (replace *all* values from source views):

```json
{
  "mode": "CURRENT_YEAR1_OPERATOR_READONLY",
  "source_evidence_id": "ECO-SIM-FINANCE-PERIOD-SOURCE",
  "captured_at_local": "2026-11-02T13:15:00+01:00",
  "period": 1,
  "operator_observed_spendable_ecu": 0,
  "operator_observed_committed_ecu": 0
}
```

The values `0` above are **placeholders**, not a zero balance claim. The source timestamp must match the factor/project state within one hour. Don't use the example verbatim.

```bash
python3 -B team-handoff/r191-live-admission/tools/run_r191_shadow.py \
  --mode current-readonly \
  --repo-root ../ecosim-r162-pinned/ECOSIM_R162_INTEGRITY_REVIEW_RC \
  --state /path/to/CURRENT_NORMALIZED_STATE.json \
  --r156-bundle /path/to/immutable_R156_bundle \
  --year1-finance /path/to/observed_year1_finance.json \
  --annual-budget 100000 --cap 4 \
  --out /tmp/ecosim-r191-current-$(date +%s).json
```

`--annual-budget` is always **hypothetical** for future years, and for the first year must not exceed the independently recorded operator-observed available residual. `--cap` must be explicitly supported by the currently captured market. This does not make the resulting plan authorized or predictive.

## Next gates before live-ready status

1. Execute the actual pinned R162 Python stack plus R189/R191 from a real clean Git worktree and save R160 independent audit receipts. The current sandbox cannot clone the private repo and the user's Fedora remote agent is offline, so this remains **HOLD**.
2. At first live session, collect **current** R156 factor/project/cap/weight snapshot and finance evidence. Compare current 35 project-card costs and effects with historical catalog; if cards changed, **HOLD** until a catalog upgrade is reviewed. R156 currently checks statuses but does not prove unchanged project financial/effect definitions.
3. Have a teammate independently review the exact first-year candidate, signed costs/grants/loan timing, nonproject actions, source dates and any unknown prerequisites. Save an operator approval record only for actual gameplay actions separately; this package never performs them.
4. After the first period resolves, capture FACT and compare with frozen PLAN prediction for calibration and replanning. Never call the R157 synthetic retention profiles true outcome bounds.

**PASS means tested code contracts, not automatic live decisions.**
