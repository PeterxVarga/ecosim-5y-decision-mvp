# EcoSim X-Challenge 2026 — P1/P2 evidence and offline decision models (2026-11-04/05)

**Team:** Jutalom a nap végén · **Market:** I · **P2/5** at evidence capture.

**Scope:** P1 historical validation, P2 browser read-only observations, financial-project bridge, indirect business effects, empirical R3 calibration. No new project started or game state changed as part of this publication.

**Current observed P2 PLAN (not FACT):** SmartCity index 60.52, displayed reserve 868,143 ECU; 10 running and 25 non-running projects. Save state UNKNOWN. The P1 FACT index was 58.87.

## Structure

- `reports/`: source-bounded P1/P2 technical and decision reports, including browser subview observations.
- `workbooks/`: P1 competitor comparison and P2 linked, R2 sensitivity and R3 empirical workbooks.
- `src/`: offline Python models, reuse of historical proxy, and 31 regression/unit tests (17 joint/indirect + 14 empirical R3). The files are an audit/research workspace, not an approved live-game agent.
- `data/`: reproducible JSON inputs, hypothetical portfolios, source observations, and uncertainty outputs.
- `archived-runs/`: P1 trial receipts, R232 offline evidence and previously issued reproducible bundles. Archives are historical; read their internal metadata before interpreting as live evidence.

**Evidence distinctions:**
- `VERIFIED` indicates a value displayed in the read-only game UI or an independent source; it does **not** imply a saved P2 decision or live end-to-end execution.
- `DERIVED` marks calculations from displayed values, with whole-number cash rounding of approximately 1 ECU.
- `HYPOTHETICAL / PROXY` labels project effects and modelled portfolio rankings. The TEST-Z project effects are historical and their conversion into exact P2 SmartCity improvements has not been validated server-side.
- Project cards' numeric costs/statuses are checked on P2 (35/35); some effect mapping remains an approximation. Partner grants may have delayed/conditional cash recognition.

## Known high-priority P2 decision risks (not action orders)

Nine P1 nonzero action fields recur in P2 PLAN: five openings (secondary school, sports, culture, outpatient clinic, social home), -8 diesel buses, +50 drivers, +10 mechanics, -50 office staff. P2 PLAN displays bus utilisation 106.46% and office-staff utilisation 108.75%. Do **not** zero the fields without measuring the side effects. No actual P2 decision changes were performed in this delivery.

## Source and verification

The existing repository `ECOSIM_R162_INTEGRITY_REVIEW_RC/` and historical `team-evidence/` retain the prior source and model base, including the original team Excel. This publication adds the 2026-11-04/05 P1/P2 analytical work without replacing those prior trees.

Source files, SHA-256 digests and sizes: `MANIFEST_SHA256.json`.

To validate the bundled offline tests after extracting the archive:

```sh
cd src
python3 -m unittest -q test_joint_model test_indirect_business_sensitivity
cd ..
python3 -m unittest -q src.test_EcoSim_P2_vallalkozasszam_R3
```

For the last command, the R3 test source expects its companion JSON files at the same level. Run it by copying the two `data/EcoSim_P2_vallalkozasszam_*20261105.json` files to the test folder, or use the standalone `archived-runs/EcoSim_P2_vallalkozasszam_empirikus_R3_20261105.zip`, whose tree is self-contained. See `src/README_P2_OFFLINE.md` for the joint model test commands.

**Not published:** browser session cookies, access tokens, raw CDP logs, the 9-MB `.git` repository clone, duplicate earlier originals already on `main`, and the failed/blocked MCP probe artifact. This is a *public repository*; don't commit new private credentials.

**Deferred follow-up:** a controlled P2 one-variable preview/revert trial. That is not yet approved as a live mutation and must be separately checked for autosave behavior.
