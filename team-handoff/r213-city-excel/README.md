# EcoSim R213 — full historical Excel city-source reconciliation

## The critical integration

The 384-row SmartCity X-Challenge 2026 test-round Excel was already on the
authorized Fedora computer and in the user's ChatGPT conversation. Earlier
development was unnecessarily treating the population/institution/transport/
company/cash-flow data as *unavailable*. They are **observed historically**,
though the corresponding next-period causal effect model is still UNKNOWN.

R213 reuses the two original (personal, **never committed**) workbooks. The
uploaded copy has SHA-256 `c6cd0681a28872beb556652b584674f442c5105c379f365027ee9dbd3efe69bc`;
the older copy has SHA-256 `4db0e1b415d5670af1427985eaccb8f9fe0b096c6402a67e1fb41fca21e76667`.
They differ in file bytes but the **374 labelled rows × five team data columns match
exactly**; do not misidentify them as two yearly observations.

The generic importer is pure stdlib and read-only. It handles simple OOXML
cells A:F with no cached-formula assumptions; it rejects formula cells,
unexpected sheet count, malformed sections, unexpected identifiers or missing
source SHA. It outputs only private source-linked R213 JSON / Hungarian markdown.

## Integrated evidence and limitations

1. Validate exact workbook bytes and 10 visible top-level sections.
2. Preserve all five team columns. The selected team's detailed 113-row
   Finance section is populated; the other four teams' blank finance cells
   are **missing**, not zero. The Excel's `Hitelek` heading has no detail.
3. Independently match all **29 SmartCity metric labels** and 51.96 baseline
   against the original R156 52.48 same-period **PLAN**; it is **not** a
   closed FACT year or a trained dynamics model. The original R156 file remains
   unchanged.
4. Join the existing 35-card R162 test catalog / six running projects,
   and seven R205 historically captured loan rows (7.5%, 12% interest only).
5. Reconcile workbook historical finance exactly up to 0.01 ECU rounding;
   preserve unresolved **20,000 ECU** historical asset-subtotal disagreement.
   Historic 130,000/62,025 grants and p1 reserve projections cannot be
   independently added to available project cash. Credit limit UNKNOWN.
6. Attach a **source-hashed, descriptive-only** R211 finance-stress context:
   12 schedules × 3 synthetic policies × 3 hypothetical annual obligations.
   Explicitly NOT additive to R213's observed p0 cash or historical revenue.
   The original R211 and R162 optimizer code is untouched.

### Native reproduction

```bash
bash team-handoff/r213-city-excel/run_private.sh
```

Uses the already available two local workbooks and original private R205/R211
reports; neither raw workbook nor private reports are committed to GitHub.
Runs 12 source-driven negative/semantic tests, two entire reconciliations and
byte-compares both JSON + Hungarian report.

### What this does *not* prove

The recorded history is not the current live city; R156 p1 is a **plan**,
not a second closed period. Past numerical snapshots alone do not determine
institution staffing, transport/migration, business activity, credit, grant
settlement, or the official score transition. The R211 cash-pressure numbers
are *incremental synthetic sensitivities*, not the true project budget.
`GAME_ACTION_GATE=STOP`; no game writes; no release or merge.

Optional source-diff input: add `--candidate-workbook /private/new_export.xlsx --candidate-source-claim CURRENT_UNVERIFIED_OPERATOR_EXPORT` to `city_excel_r213.py` alongside the full historical source arguments. The candidate comparison requires matching row identities and same selected team, records all changed source row IDs plus missing cells, and does NOT establish current game provenance or server authenticity. This does NOT replace R156/R191/R192 current admission. The 12th test specifically verifies false live attestation is rejected.

For the next real round, prioritize only a read-only current R156 snapshot,
current 35-card catalog and finance evidence, and direct source-diff versus
this historical baseline. Never silently substitute historical values for
missing present-round observations.
