# EcoSim R145 — Combined policy and five-year project engine

**2026-10-31 · Offline release · No user execution required**

## Delivery

This extends `ECOSIM_R144_5Y_CITY_FINANCE_INTEGRATED_20261031.zip` directly. Its existing five-year search, known-factor aggregation, historical R94 accounting and hypothetical loan bridge were retained. An explicit operating-policy track can now be passed into the **same bounded project search**, so changes to annual operating cash costs constrain the project's hypothetical annual envelope and known mapped-factor effects can be replayed in a **combined** annual factor scenario.

### Demonstration only

Under a purely illustrative 100,000 ECU/year project envelope and beam width 6, synthetic training-service spending of 5,000 ECU/year lowers the project's illustrative annual envelope to 95,000 ECU. A fabricated +2% response of the `Lakosság képzettsége` factor is applied in the scenario. A distinct unknown-tax track carries **null** policy score and cash response and does not produce a falsely certified cash forecast. These are code tests, **not** strategy recommendations; rankings reflect incomplete proxies and can even reverse when a budget changes.

### Qualification

`results/R145_INTEGRATED_QUALIFICATION.json` records **85/85** successful checks (59 previous, 26 new), including conservation of negative-cost reservations, exclusion of unknown cash effects, combined factor replay, double-count protection, identical baseline when prior-year policy changes are embedded in a later year's observed baseline, and one consolidated legacy regression. The ZIP is release-integrity checked separately; this does not validate actual EcoSim future scores.

### Scope still missing

This is a **project-plus-supplied-policy-track scenario engine**, not an automatic optimum over all tax rates or institution settings. Real operating decision coefficients cannot be responsibly inferred from the available static UI data, and unknown factors or server-side dynamics remain unmodeled. Market configuration, reliable future cash, candidate preview, competitors and migrations are unresolved. **Final strategy: STOP until validated.**
