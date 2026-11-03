# EcoSim 5-year decision support – R162–R238 source and shared evidence

**PUBLIC repository.** This `main` branch contains the historical offline R162/R189–R195 decision support, the R196–R238 source/test extensions, R165–R175 earlier test-round evidence, and additional I-market source material explicitly authorized for public sharing. **The repo is accessible to people outside the team**, not only teammates.

## Team entrypoints

- **[Magyar adaptív P1–P5 csapatos útmutató](team-handoff/ADAPTIVE_5Y_TEAM_HU.md)** – decision protocol and independent approval gates.
- **[R194/R195 existing offline runner and trade-off](team-handoff/r191-live-admission/README_R195.md)** – reproducible historical and conditional current-year workflows.
- **[Shared EcoSim evidence index](team-evidence/library-20261103/README.md)** – source-labelled I-market and separate historical Z-market observations imported from the owner's ChatGPT Library.
- **[R238 unified current-source intake documentation](team-handoff/r238-unified-private-data/README.md)** – source coverage and remaining live gates; the original ZIP is now at [`team-evidence/original-binaries-20261103/`](team-evidence/original-binaries-20261103/).
- **[Original R162 integrity notes](ECOSIM_R162_INTEGRITY_REVIEW_RC/README_R162.md)** – pinned original release and offline historical validation.

From the repository root, using Git and Python 3:

```bash
bash team-handoff/r191-live-admission/run_team.sh historical
bash team-handoff/r191-live-admission/run_tradeoff.sh historical
```

These are offline historical/model checks, **not** direct live EcoSim actions. The R196–R238 source modules include additional conditional analysis and private-input adapters, but their full cross-module live readiness and P2–P5 prediction accuracy are not validated merely by being present on `main`. Follow the module's own admission and evidence gates. The original R238 ZIP, source XLSX/ZIP archives and Fedora R257 (13 files) / R258 (31 files) evidence were subsequently uploaded to `main` in [commit `8001ab9`](https://github.com/PeterxVarga/ecosim-5y-decision-mvp/commit/8001ab91a830ce034a0da1c5ddd29aab38f52a65). See [`team-evidence/original-binaries-20261103/`](team-evidence/original-binaries-20261103/) and [`team-evidence/fedora-local-20261103/`](team-evidence/fedora-local-20261103/). The R258 receipt describes **unsaved historical A/B UI trials with complete rollback**, not the current server game state. Do not run trial control scripts as routine read-only checks.

## Data sensitivity, provenance and gameplay boundaries

Some published artifacts contain the team's game observations. Because this repository is **public**, competing teams may also inspect them and the Git history. Do not commit credentials, personal secrets, authentication cookies or tokens. The Library text imports are not byte-verified replacements for original binary artifacts.

Missing source is **UNKNOWN**, not zero. Distinguish test-round Z, current selection market I, historical model outputs, P1 PLAN and later confirmed FACT observations. There is **no validated live five-year winning strategy** and no confirmed current-game save receipt here. **`GAME_ACTION_GATE=STOP`**; nothing in this repository authorizes game Project Start/Cancel, Save, or Next Period.

## Pinned original R162 release

- Original archive under GitHub Releases: `r162-20261031`
- Original release ZIP SHA-256:

```text
731c5b823099421e099b748102fac8ae93a2b41f72dd196cafaca2cafb2d5908  ECOSIM_R162_INTEGRITY_REVIEW_RC_20261031.zip
```

To verify the original R162 source:

```bash
cd ECOSIM_R162_INTEGRITY_REVIEW_RC
./verify_release_r162.sh
```
