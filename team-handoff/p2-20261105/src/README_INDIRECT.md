# EcoSim P2 indirect-company effects stress test

This package is offline/read-only: no game login, browser automation, network call, save, project start or source repository modification.

## Run

Requires Python 3.11+ standard library only. From the extracted folder:

```sh
python3 -m unittest -q test_joint_model.py test_indirect_business_sensitivity.py
python3 indirect_business_sensitivity.py
```

The latter command regenerates the detailed JSON in the current directory.

Data sources: `P2_joined_input.json` (live observed P2 statuses, costs, finance, index factors as of 2026-11-05 + historical TEST Z effects); `P2_joint_scenarios.json` (previous direct-only shortlist); `ecosim_projects_20261030.json` (historical 272 project-card effects). The results are **sensitivity stress tests, not causal estimates, official game forecasts or P2–P5 plans**. Reference P1->P2 observed company-count changes do not identify the company-count-to-index causal formula.

## Deliverables

- `EcoSim_P2_30_kozvetett_hatas_erzekenyseg_20261105.md` explanation and caveats.
- `EcoSim_P2_integralt_modell_kozvetett_R2_20261105.xlsx` extended Excel: prior 6 tabs + interactive sensitivity sheet + 30 effects + 160 scenario grid.
- `P2_indirect_business_sensitivity.json` detailed 30 records and conditional shortlist rankings.
- `indirect_business_sensitivity.py` offline reproducible stress search.
- `test_indirect_business_sensitivity.py` nine targeted tests; previous 8 tests included.

Run is intentionally isolated from other projects and leaves existing original artifacts intact.
