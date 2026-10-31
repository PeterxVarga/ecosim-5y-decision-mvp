# R161 delivery — offline RC

**Outcome:** a self-contained, reproducibly zip-packaged **R161 candidate**, built by minimally hardening R160. 62/62 new adversarial checks PASS; one full historical sample E2E PASS; historical candidate set 20/20 unchanged; no gameplay writes.

**Three source-code changes:** strict JSON parsing in `tools/strategy_5y.py`, bounded path resolution in `tools/decision_desk_r149.py`, and elimination of false server-origin verification from `tools/strategy_5y.py` provenance labels. Two release tools and tests were added without a new optimizer.

**Boundary:** `PASS_OFFLINE_ONLY`; authoritative actual game state, full city dynamics and forecast validation remain `UNKNOWN`; game actions `STOP`. SHA integrity and file completeness are checked, not third-party signatures. Separate human review not done.

See `README_R161.md`, `results/R161_QUALIFICATION.json`, `R161_RISK_LEDGER.json`, `R161_RELEASE_MANIFEST.json`, and `SHA256SUMS`.
