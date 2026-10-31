# R166 — Balance sheet observation, not a spending authorization

## Source
- [EcoSim Finance](https://edu.ecosim.hu/simulation/finance), in-page **Vagyoni kimutatás** tab, signed-in browser DOM text, **read only**.
- X-Challenge **2026 Tesztforduló**, market **Z**, team **Jutalom a nap végén**, period **1/1**; observed `2026-10-31T19:14:06.616Z`.
- p0 = FACT; p1 = PLAN. The visible model is NOT proof of the November 2–12 live competition configuration.
- Source data: [`R166_BALANCE_SHEET_READONLY.json`](./R166_BALANCE_SHEET_READONLY.json) (all 25 line items).

## Cross-account checks

| Visible value | p0 FACT ECU | p1 PLAN ECU |
|---|---:|---:|
| Pénzállomány | 184,600 | 865,588 |
| Hitelállomány | 0 | 0 |
| Forgalomképes összesen | 5,364,226 | 5,982,551 |
| Korlátozottan forgalomképes összesen | 8,369,303 | 8,330,217 |
| Forgalomképtelen összesen | 660,000 | 660,000 |
| Összvagyon | 14,373,529 | 14,952,768 |

**Observed equalities:** p1 cash = p1 reserve transfer = p1 period net result = 865,588 ECU. p0 cash = p0 finance “Előző év végi pénzállomány” = 184,600 ECU. However, that finance line shows **0 ECU in p1**; do not add p0 cash to p1 planned cash without game rules.

**Source inconsistencies — NOT patched or explained by assumption:**
- Three displayed asset category subtotals sum to **14,393,529 ECU (p0)** and **14,972,768 ECU (p1)**, **20,000 ECU above** the displayed overall total in both columns.
- The tradeable component rows sum to **5,694,226 ECU (p0)** / **6,312,550 ECU (p1)**, while displayed tradeable subtotals are **5,364,226 / 5,982,551**, i.e. **330,000 / 329,999 ECU** lower. One row “Hulladékgazdálkodási vállalat” is 330,000 ECU, which *may* account for the difference, but its accounting treatment is NOT verified. The one-ECU difference might be rounded UI amounts.
- Restricted and inalienable asset component sums do match their displayed subtotals.

## Decision semantics
- `p1.Pénzállomány=865588` is **observed planned period-end balance**, **NOT** confirmed immediately spendable project capital.
- `p1.Tartalékképzésre=865588` is observed plan value; legal/policy accessibility and liquidity timing remain UNKNOWN.
- **All asset values are NOT interchangeable with cash**, and their sums do not exactly reconcile.
- No automatically derived project/loan cap. No permission to spend, start, save, or finalize game actions.
- **Readiness:** `EVIDENCE_CAPTURED / FINANCING_NOT_PROVEN / GAME_ACTION_STOP`.

## Next meaningful verification
Obtain the actual rule or in-game read-only display for the money available **at the moment of project start**, plus project financing limits, reserve-transfer behavior, partner-grant timing, and loan restrictions. Otherwise evaluate candidate plans only with explicitly hypothetical budgets. Do not use p0→p1 as two observed years for forecast calibration.
