# EcoSim R161 — Offline Release Candidate & Adversarial Audit

**Release class:** `PASS_OFFLINE_ONLY` · **Game decision:** `STOP` · **Live market/team verified:** **NO** · **True five-year forecast accuracy:** **UNKNOWN**.

This is the **same R160 five-year optimizer**, with targeted input-integrity, provenance and release-integrity fixes. It is not a separate planner and does not require Codex, the owner's terminal or a logged-in EcoSim browser. It performs no game writes.

## Actual changes (bounded, independently falsified)

1. **Strict JSON input semantics:** `strategy_5y.read_json` now refuses duplicate keys, JSON `NaN`/`Infinity` constants, missing files and inputs greater than 10 MB. Previously the default JSON parser silently accepted duplicate object members and nonstandard numeric constants. This affects the decision-desk input pipeline directly.
2. **Evidence-path boundary:** `decision_desk_r149._resolve` now only permits existing inputs within the release tree or within the run-config's own directory. Path traversal, absolute host files outside these locations and symlink escapes fail closed. The legacy root-relative `inputs/...` configuration still works. An external user-specific run file may read adjacent input files from its own directory; that does not confer any trust in their content.
3. **Epistemic source distinction:** `strategy_5y.derive_config` no longer labels a self-declared time and source ID as independently `verified=True`. Even a fully populated `CURRENT_READONLY` packet remains `OPERATOR_DECLARED_...` and `NOT_SERVER_VERIFIED` unless real authenticated-server provenance is available. R161 has no such attestation and never claims it.
4. **Offline immutable release gate:** `tools/release_guard_r161.py` checks every distributed file, `SHA256SUMS`, release metadata, the `STOP` status and optionally the ZIP content. It rejects symlinks, credential-looking filenames, unexpected ZIP members, traversal, modified bytes and missing files. `tools/build_release_r161.py` produces a reproducible ZIP, refusing to overwrite an existing one. This is package integrity, **not** an attested build or third-party signature.

## Verification performed now

`results/R161_QUALIFICATION.json` contains **62/62 newly executed PASS checks**, with one full historical end-to-end run of the original R160 decision pipeline. **20** historical candidate IDs were identical to those in the prior R160 report. There is no real gameplay execution. The previous R160 **63/63** result is retained as historic evidence; it was not re-run or added to the 62.

Among the R161 checks: nested duplicate JSON keys, nonstandard numbers, input path escape, source metadata forgery, file tampering, extra archive members, ZIP path traversal, fabricated `GO`, preservation of the independent project-cost audit and consistency of the historical candidate set. The full E2E produces an *illustrative* result only.

The distribution additionally passes `verify_release_r161.sh` and verification of every canonical ZIP member. SHA-256 hashes are stored in `SHA256SUMS` and sealed by `R161_RELEASE_MANIFEST.json`. The published ZIP SHA-256 identifies the whole artifact.

## Commands for later — not required now

From the extracted `ECOSIM_R161_RELEASE_CANDIDATE` directory:

```bash
./verify_release_r161.sh       # read-only, checks all distributed files
./qualify_r161_once.sh        # runs the 62 adversarial checks and one historical sample run
./run_r160_offline.sh         # legacy, generates the historical R160 result
```

The existing historical UI remains at `results/R160_HISTORICAL_CONSISTENCY_DEMO/DECISION_DESK.html`. The R156 local read-only capture UI remains present. Neither connects to an EcoSim session on its own.

## What this does not establish

- No access to the current authorized EcoSim session, no authenticated current `market/team` snapshot, no true spendable cash or verified credit/grants.
- No full causal demographic, institutional, migration or competitor-response simulator.
- No server-confirmed project legality; same-year dependencies, project1 bonus and future cap remain conditional.
- No matched live prediction–fact outcome, measured predictive error, global optimum, winning probability or competition compliance approval.
- **No independent fresh-context human code review**, although adversarial software checks were carried out. The known-source assumptions and test fixtures have not received a separate external audit.

**STOP remains mandatory for in-game actions.** Any future `GO` would require a separate, explicit user-approved decision and fresh real-game evidence, not a successful offline release receipt.
