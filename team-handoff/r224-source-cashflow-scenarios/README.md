# R224 – Actual Selejtező I P1 cash-flow reconciliation and source-bounded financial sensitivity

## Outcome / source reliability

A newly source-hashed current-period R223 read-only Finance page, originally acquired from the user's authorized logged-in EcoSim browser, reports P1 planned receipts **5,562,335 ECU** including **184,600 ECU** opening cash and **192,025 ECU** of two separate displayed development-grant lines. Planned expenses **excluding reserve/loan reclassification** are **4,511,224 ECU**. Hence:

- P1 planned baseline cash-flow surplus / reserve transfer: **1,051,111 ECU** (5,562,335 − 4,511,224).
- Minus opening cash once: **866,511 ECU**.
- Minus the displayed 130,000 + 62,025 ECU development-grant lines once: **674,486 ECU**.

This is an arithmetic **sensitivity basis**, not proof the 674,486 is available, legally unearmarked or owner-approved for project costs. R224 also verifies that P1 total expense = normal expense + reserve transfer, planned income balances P1 gross expense, P1 loan draw = 0 and the displayed line "Projekt - egyedi alapon összesen" is 0. It deliberately does NOT treat that initial project expense row as future project authorization. The original official 22-page Hungarian handbook warns about automatic debt when expenses exceed revenues and reserves are insufficient.

## Original upstream code reuse

R224 calls existing R217 `rows`/finance parsing, original R152 compiled immutable current R156 state, the **unchanged** original R162 `strategy_5y.search` and its R160 independent audit. No parallel city prediction or duplicate optimizer. The previous R220 35 visible-card source receipt and R222 two actual current card dependencies remain source-bound but **R192 is not time-admitted**. Neither historic card defaults nor the old 4-project assumed cap are treated as true.

R224 derives an *illustrative annual budget axis* as 0%, 25%, 50%, 100% of the conservative **674,486 ECU** P1 arithmetic basis:

`[0,168621,337243,674486] ECU`

Then combines **three explicitly hypothetical** annual project start limits `[1,2,3]` and original model objectives `[nominal,scenario_min]` → **24 five-year original-engine searches**. The original optimizer uses those budgets repeated across **all five years** as a transparent scenario assumption, not as a forecast of P2–P5 revenues/costs. R160 audits each conditional search. The new matrix is *not an actual funding or gameplay recommendation*.

### Illustrative nominal first-year examples (not eligible without original R191/R192 gates)

| Hypothetical cap | Hypothetical annual budget | First-year source-conditioned project IDs | Conservative card cash |
|---:|---:|---|---:|
| 1 | 168,621 | 13 – Informatikai fejlesztés | 55,000 |
| 2 | 168,621 | 13 + 27 – Vasútfejlesztés | 70,000 |
| 2 | 337,243 | 13 + 33 – Népliget megújítása | 256,000 |
| 3 | 337,243 | 4 + 13 + 33 | 299,000 |

The future city score and interaction on fee/tax revenues are unverified. The observed projected cash-flow is **not equivalent** to capital allocation.

## Reproduction (private Fedora artifacts only)

```bash
bash team-handoff/r224-source-cashflow-scenarios/run_private.sh \
  --out-dir "$HOME/Downloads/new_private_R224_output"

bash team-handoff/r224-source-cashflow-scenarios/qualify_private.sh
```

The first command reuses read-only SHA-linked current source pages, immutably observed current R156 from R223, old 35-visible-card and currently displayed condition receipts, and pinned original public handbook PDF. It makes a **new** private directory and writes `R224_RECEIPT.json` and `R224_HU.md`. Does not overwrite earlier private evidence.

Native validation tests (8 targeted source-ledger and negative tests) fail on tampered P1 reserve, malformed source provenance, contradictory duplicate income, source SHA drift, a fictional source cap and accidental promotion of conditional budgets to spending approval.

### Safety, limitations and the next critical fact

`maxProjectPerTurn=UNKNOWN`; `cap_source=UNKNOWN`. `operator_observed_spendable_ecu=UNKNOWN` and `operator_observed_committed_ecu=UNKNOWN`. Actual project cash and grants authorization remain unverified. R191/R192/R214 **HOLD**, owner has not approved any gameplay action. `GAME_ACTION_GATE=STOP`, game writes 0, merge 0, deploy 0.

**Most valuable next action:** identify the actual Market I project-start limit and source-supported current committed/project cash with a *single* live operator observation, before attempting R214 real 3-option advisory. Do not reacquire all 35 cards as a substitute. This artifact is an offline planning aid only.
