# R225 — actual Selejtező I periodic decision inventory → original R145 unknown-impact contract

## Critical-path improvement: not another project optimizer

The previous source-linked R224 five-year plan could choose projects but **not** calibrate
tax, tariffs, institution operating, transport, or other periodic decisions. Reuse
existing original `R145 policy_tracks.py`, R148 combined-factor replay, original
R153/R154 taxes and R155/R159 operational finance, rather than building a competing
municipal simulation engine. The key missing prerequisite is the actual current
operator-controllable **decision-space contract**, not a new beam search.

### Actual observed current UI

Using the authorized connected Browser read-only views in the already logged-in
X-Challenge 2026 **Selejtező / I market / Jutalom a nap végén / P1**, we captured
three active *subviews*:
1. `/simulation/institutions` → Oktatás: three wage/training/development
   input cells and four school/open-close input cells (**7**).
2. `/simulation/transport` → Járművek / Belsőégésű motoros buszok:
   procurement, purchase age, vehicle maintenance; plus infrastructure
   maintenance and communications (**5**).
3. `/simulation/income` → Szolgáltatások díjai: six price/tariff input
   cells (**6**).

**18/18 currently displayed editable numeric input fields** parsed. On these three
parent menus, **12 named known subviews** are accessible through the UI: 6
institution classes, 3 vehicle/personnel subviews, 3 income subviews. **Only 3/12**
are observed. That denominator is for these three parent-menu subdivisions,
NOT all game decision surfaces and NOT total project readiness.
The remaining nine views (e.g. tax, state law, other institutions, electric
buses and transport personnel) remain UNKNOWN, even when the historical workbook
contains rows with similar names.

The source displays P0 baseline numbers but empty P1 text input values. An empty
form does not prove a valid saved P1 value. Visible `!` warning icons suggest
additional variable restrictions but do **not** expose a numeric minimum/maximum.
No button value, limit, financial or score response was inferred from a blank
input or guessed from older test data. The classification of UI input keys is
an *observation*, not a ranking of admissible actions.

### Reuse of existing upstream-like internal engine

`R225_R145_UNKNOWN_EFFECT_CONTRACT_TEST_ONLY.json` is **explicitly a schema-only
test fixture**, never a selected gameplay policy! The original `load_tracks()`,
`policy_factor_replay()`, `policy_money_replay()` verify:
- exactly 18 syntactically valid documented *placeholder* entries;
- **18 unknown factor effects** (not zero), **18 unknown cash impacts** (not zero);
- no calibrated actual response, no cash completion, no project spending permission;
- no automatic joint five-year optimization with these uncontrolled unknowns.

The real reusable artifact is the typed **periodic UI control inventory** with
source URL, local source SHA-256, P0 displayed value, original label, unique key,
P1 `null`, allowed bounds `null`, factor/cash response `null`, and explicit
unobserved subview names.

### Private qualified artifacts (not GitHub)

- `~/Downloads/ecosim-r225-periodic-current-20261102/` — 3 private read-only
  visible page snapshots from authorized browser connection.
- `~/Downloads/ecosim-r225-periodic-qualification-v2-20261102/R225_RECEIPT.json`
  — typed 18-input source inventory, exact provenance, 9 missing subviews,
  3 source hashes, local capture timestamps.
- `R225_PERIODIC_UI_CONTROL_INVENTORY.csv` — human-reviewed P0 per-field ledger.
- `R225_R145_UNKNOWN_EFFECT_CONTRACT_TEST_ONLY.json` — temporary schema
  test only; **do not import as selected real policy changes**.
- `R225_HU.md` — high-level Hungarian summary.

All actual source captures and reports are private, outside repository.

### Private native commands

```bash
bash team-handoff/r225-periodic-control-intake/run_private.sh \
  --pages-dir "$HOME/Downloads/ecosim-r225-periodic-current-20261102" \
  --r156-dir "$HOME/Downloads/ecosim-r223-fresh-r156-20261102" \
  --out-dir "$HOME/Downloads/a_new_private_R225_result"

bash team-handoff/r225-periodic-control-intake/qualify_private.sh
```

A result folder must not previously exist and the three source snapshots
must be within 60 minutes of the source-linked P1 R156 captured state. The
timestamps are **local file metadata, NOT cryptographic game-server attestation**.
As the round progresses, capture new source views and the corresponding current
R156 together; never alter old timestamps to obtain a pass.

The focused native test suite checks actual input identity and P0, original R145
UNKNOWN propagation, malformed HTML tables, unexpected writable rows, active
subview mismatch, field count/name drift, non-operator-approved P1 form values,
stale source times, source SHA linkage and refusal to overwrite private output.

### Gates, limits and next ROI

**R225 is functional source intake, NOT five-year policy optimization.** Actual
Market I project cap UNKNOWN, actual spendable and committed project finance UNKNOWN;
P1 input bounds and actual p1 decisions unknown; future P2–P5 periodic effects
uncalibrated. Original R191, R192, R214 remain HOLD; actual winning five-year plan
and official score forecast UNKNOWN.

Next largest ROI: acquire additional *independent periodic subview observations*
(especially tax and other institution/transport controls), then compare
historical PLAN→FACT responses before adding bounded, explicit policy effect
tracks to the unchanged R145/R148 + R162 search. Do not use 18 blank fields as
evidence of complete city optimization.

`GAME_ACTION_GATE=STOP`; no save, no Start, no submission, no loan, no merge
or deployment authorized.
