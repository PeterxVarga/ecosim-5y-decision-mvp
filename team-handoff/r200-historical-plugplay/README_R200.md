# EcoSim R200 — Historical test corpus accounting and interchangeable input profile

## Purpose and source-driven finding

R195/R199 precisely replays two five-year project schedules under three historical/synthetic fiscal and operating policy tracks. Those runs previously omitted the other tabs' observed financial and institutional inputs. R200 validates and audits those sources explicitly, rather than silently treating them as spendable money or claiming an entire city optimization.

## Evidence covered

- 35 historic project cards, six running; 29 R156 city factors and six archived index weights, plus one displayed index. R94 p0 FACT was 51.96, p1 PLAN 52.48, NOT two closed actual years.
- 113 R94 finance rows (88 cash flow, 25 wealth); 46 fact/plan differences and missing monetary-unit labels throughout. The p1 plan revenues of 5,376,812 minus expenses excluding reserve of 4,511,224 equal a planned reserve movement of 865,588. This does NOT prove that this amount is authorized to spend or that financial and project card units are identical.
- An independent private institution snapshot covers ONLY the Education page: 5 tables, 37 rows, 64 numeric observations, 7 editable fields. Its original source SHA matches its analysis document.
- R175B crosswalk 29 historical factor mappings; no proof of full official public 26 labels versus 29 client factors formula equivalence.
- Historical R154 four-tax and R155 six-fee source formula components evaluated using synthetic exogenous future city bases. R94 observed first-year raw four-tax sum: 499,925; observed six-fee sum: 1,802,870. Synthetic first-year modeled baselines: 454,368.608 ECU and 369,571.95112968 ECU. Their monetary scales and assumptions have not been matched; this discrepancy is a falsification prompt, not a quantified model-error claim.
- The six displayed fee component values exceed the cash-flow fee subtotal by 2 units in both observed columns; the tool retains the discrepancy.
- The two exact R195 schedules × three synthetic fiscal/operating paths are reused from the R199 report with checked annual IDs and costs.
- **Expanded historical candidate comparison:** hash-locked R149 original full decision desk contains 15 further five-year project schedules × three tax/operating paths (45 calculations); R199 adds two nonidentical full schedules × three paths (6). The result is 17 distinct candidates and 51 conditional project-policy pairs. For each path a three-objective (partial index, partial net, hypothetical zero-opening cash stress) sample Pareto set is recomputed from the existing calculators. Not a global optimizer, and not a calibrated live projection.

## Tools and semantics

The corpus loader uses one versioned JSON profile with 16 source roles, explicit source class, content SHA256, team/market/round/year identity. It emits R200.json and R200_HU.md including a ten-tab coverage matrix, factual R94 financial rows, R94 versus synthetic-basis discrepancy, and the partial R199 paired analysis.

It rejects JSON duplicate keys/nonfinite numbers, altered source hashes, path traversal, missing source roles, historical/current mode mixing, and accidental reuse of exact archived historical bytes as current evidence. It NEVER calls the EcoSim website or uses credential data.

## Privacy

THIS GITHUB REPOSITORY IS PUBLIC. Raw authenticated snapshots, the full historical/private input profile, and proof reports are intentionally excluded by the local .gitignore. Only generic source code, tests, and this README may be published through the draft PR. Do not commit private fixtures, new game states, HAR, cookies, tokens, or logs.

## Reproduce on the current Fedora machine

    bash team-handoff/r200-historical-plugplay/run_historical_private.sh

The script checks Git exclusion before copying anything, reuses the local private observations without overwriting them, reconstructs the SHA-pinned historical profile and emits a private report and tests. On other machines the private source files must be supplied separately. A clean public clone cannot run the private historical dataset without those files.

For independent tests, with fixtures present:

    python3 -I -B -m unittest discover -s team-handoff/r200-historical-plugplay/tests -v

## Future plug-and-play scope

An entirely NEW current-readonly profile can reference fresh operator-observed files inside its own directory and include source hashes and provenance. The R200 importer will refuse test/synthetic source fallback. Until actual current R195 and R153–R159 evaluators and finance admission can be validated, the system returns HOLD_CURRENT_SOURCE_INTAKE_ONLY: input-contract readiness is NOT live-model readiness.

Remaining unknowns: actual project spendable cash, loan/grant and settlement timing, public-vs-client index model identity, other institution pages, firms, population, transport capacity, market reactions, fully calibrated multi-year city transition.

GAME_ACTION_GATE=STOP. Draft PR pending review; no merge, no EcoSim writes.
