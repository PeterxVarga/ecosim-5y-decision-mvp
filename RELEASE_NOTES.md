# EcoSim R162 — Integrity Review RC (2026-10-31)

- Baseline: existing R161 integrated 5-year offline decision-support MVP.
- Fix 1: overflow JSON float values (for example `1e999`) and invalid JSON inputs are rejected consistently.
- Fix 2: contradictory negative project dependency combinations are rejected at candidate generation time.
- Fix 3: relative-directory verification issue fixed.
- Qualification: **44/44 new checks PASS**, one complete historical E2E run, previous 20 historical candidates preserved. Older checks were not rerun here.
- Release integrity: source ZIP SHA-256 `731c5b823099421e099b748102fac8ae93a2b41f72dd196cafaca2cafb2d5908`.

**This is an offline research release candidate, not a validated winning-strategy engine.** Live action gate remains `STOP`.
