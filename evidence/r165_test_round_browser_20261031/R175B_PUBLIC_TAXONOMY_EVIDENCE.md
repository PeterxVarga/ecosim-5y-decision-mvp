# R175B — Public 26 vs historical EcoSim UI 29 taxonomy: documented reconciliation

**Status:** SOURCE_LABELS_VERIFIED_MAPPING_HYPOTHESIS. 2026-10-31. Supplements but does not overwrite user-local R175 outputs or retroactively change their `PARTIAL_OFFLINE_PREP` qualification.

## Source evidence
- X-Challenge 2026 official event site: **https://www.xchallenge.hu/**, expanded section **`A modell értékelése / 6 kategória. 26 szempont.`**; official source shows **26 exact named public assessment criteria** in six groups, respectively **4,4,4,7,3,4**. Accessed 2026-10-31.
- R162 historical test-UI list: private repo `main:ECOSIM_R162_INTEGRITY_REVIEW_RC/tools/r142_proxy_reference.py`, `WEIGHTS`, `COEFF`; 29 factors in six groups respectively **4,5,4,8,4,4**.
- Supporting original 29-key historical baseline: `main:ECOSIM_R162_INTEGRITY_REVIEW_RC/data/ECOSIM_R141_PROJECT_PROXY.json`.
- Independent EcoSim SmartCity public overview: https://edu.ecosim.hu/smartcity; describes six aspects and many sub-aspects, **not** an authoritative exact formula or per-market score definition.
- Machine-readable comparison: `R175B_OFFICIAL26_TO_R162_UI29_CROSSWALK.csv` alongside this file, preserving all 29 R162 source labels, all 26 distinct 2026 public labels, and each match classification.

## Structural explanation of 29 vs 26
Category | Official public | R162 historical test-UI | Difference
---|---:|---:|---:
Gazdaság | 4 | 4 | 0
Környezet | 4 | 5 | 1
Kormányzás | 4 | 4 | 0
Életkörülmények | 7 | 8 | 1
Mobilitás | 3 | 4 | 1
Emberek | 4 | 4 | 0
**Total | 26 | 29 | +3**

The exact count difference has a plausible source-grounded decomposition:
1. **Vízgazdálkodás** is a separate test-UI environment factor, not individually listed among public environment labels.
2. **Közlekedési minőség** is a separate test-UI mobility factor, not individually listed among public mobility labels.
3. **Sport** and **Művelődés** are separate test-UI factors but together appear under one public criterion, **Sport és művelődés**.

Thus these 2 additional separately-listed UI metrics plus one UI split explain the numerical gap **3**; this is a taxonomy hypothesis, **not** a proven server scoring difference or formula equality. These factors must remain in R162 until actual live evidence supports a change.

## Important non-exact wording
- Public **Internethasználat** is NOT exact to historical UI **Digitalizáció**. Internet usage may be an input/component of digitalization, but no source proves they are identical or can be substituted.
- Public **Lakossági képzettség** vs UI **Lakosság képzettsége**: semantic name candidate only.
- Public **Rossz szociális helyzetben lévők aránya** vs abbreviated UI **Rossz szoc. helyzetben lévők aránya**: label abbreviation, not an explicit formula statement.
- Public **Tömegközlekedők aránya** vs UI **Tömegközlekedők aránya, %**: unit display difference; likely corresponds, but exact metric schema has not been server-authenticated.
- Public **Lakossági viszonyok / elégedettség** vs UI **Lakossági viszonyok/elégedettség**: typography candidate only.
- **20** UI labels match public labels exactly; **7** UI rows are candidate matches (including the two rows for the same combined sport/culture public criterion); **2** UI rows are not independently listed on the public site.
- All **26** public labels are covered by some exact or candidate mapping, but coverage is not authoritative equivalence.

## Falsification and conclusions
- PUBLIC marketing text may aggregate or abbreviate detailed game factors. The historical R162 UI list may reflect an earlier/test configuration. Neither source alone proves the current live scoring formula.
- The public example controls are described as **`Lényegi illusztráció`** and must not be reverse engineered into game weights.
- Do NOT change R162's historical weights, 29-factor coefficients, optimizer or qualified R173/R174 parser on the basis of these labels.
- Not a game scoring rule, not an R156-ready input, no inference that the 26-public vs 29-test discrepancy is a software defect.
- Qualifying R175 after adding this independently sourced evidence requires a **new append-only local R175B addendum qualification** that checks real local R175 hashes, all CSV rows/counts, site provenance, and no original artifact changes. The old `PARTIAL_OFFLINE_PREP` receipt stays historical. Do not retroactively call it 11/11.
- Remaining game gates: live team/market/period, 35 authenticated project identities and 70 state flags, project cap/bonus, spendable cash and obligations, loan/grant rules; `GAME_ACTION_GATE=STOP`.

**Public source sections to verify:** https://www.xchallenge.hu/ (hidden by default in UI; expanded footer panel). Primary URL source content presently includes all group titles and labels in page DOM even while accordion is closed.
