# EcoSim 5-year Decision Support — R162/R195 team baseline

**PUBLIC offline decision-support repository.** Do not commit authenticated game exports, team-specific live strategy, credentials, session cookies or private R257/R258 evidence. The original R162 historical release was produced offline; the `main` branch also includes the later R189–R195 team decision support.

## For teammates

**[Magyar csapatos adaptív P1–P5 használati útmutató](team-handoff/ADAPTIVE_5Y_TEAM_HU.md)**

From the repository root, with Git and Python 3:

```bash
bash team-handoff/r191-live-admission/run_team.sh historical
bash team-handoff/r191-live-admission/run_tradeoff.sh historical
```

These run historical pinned-source evaluations and produce local reports. For actual current-year analysis, follow the documented `current` admission contract and provide separate, fresh, operator-observed evidence. Missing or stale source => HOLD. Later periods P2–P5 still require a separately qualified period adapter. **No validated live five-year forecast, browser control, automated gameplay or game write permission. `GAME_ACTION_GATE=STOP`.**

## Pinned original release

- Original R162 source: [`ECOSIM_R162_INTEGRITY_REVIEW_RC/`](ECOSIM_R162_INTEGRITY_REVIEW_RC/)
- R162 integrity guide: [`README_R162.md`](ECOSIM_R162_INTEGRITY_REVIEW_RC/README_R162.md)
- Original release tag: `r162-20261031` (ZIP attached under GitHub Releases).
- Original R162 ZIP SHA-256:

```text
731c5b823099421e099b748102fac8ae93a2b41f72dd196cafaca2cafb2d5908  ECOSIM_R162_INTEGRITY_REVIEW_RC_20261031.zip
```

Verify the original source:

```bash
cd ECOSIM_R162_INTEGRITY_REVIEW_RC
./verify_release_r162.sh
```

The R196+ experimental, source-bounded extensions remain in an independent draft pull request, not in `main`; they must not be treated as qualified live outcomes.
