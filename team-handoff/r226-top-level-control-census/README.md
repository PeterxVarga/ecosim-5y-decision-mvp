# EcoSim R226 — all ten top-level menus source-observed, editable control census

## Why this is the highest safe return with existing connected browser rights

The previous R225 real authenticated browser intake observed 18 periodic editable
input cells across institution/transport/income default subviews, reusing the
original R145 policy engine's unknown-factor/cash effect contract. Its "3/12
subviews" denominator represented only a subset and overlooked nested menus.
The account-connected browser currently **only exposes read-only open-tab
contents, without safe page-element click support**. We must not bypass it with
game APIs, mutate forms, simulate clicks via screen coordinates or repeatedly
ask the user to revisit project cards already verified.

R226 uses the already authenticated Brave session to open/read all **ten
top-level simulator routes** with **no game writes**:
`summary, projects, institutions, transport, income, population, corporations,
loans, finance, analysis`.

The actual operator-visible sources show **19 total editable text inputs in
the currently selected visible subviews**, **18 exact R225 inputs reused**
and one newly observed long-term-loan receipt/repayment field (P0=0,
P1 input blank). Seven other top-level visible views are read-only *at
the currently selected subview*, not proof that all their alternate subviews
are read-only.

Exactly **27 distinct visible selector button labels** occur on those pages,
including transport's nested vehicle-type choices. Do NOT claim "27
independent subviews" or "19 of all EcoSim decisions". Source has not yet
exposed the full tax / state-law / other institutions / other transport /
short-term-loan decisions. The project Start buttons are classified as
**potential GAME WRITE ACTIONS**, not periodic editable text inputs.

## Source provenance and safety

The seven newly acquired menu snapshots live under
`~/Downloads/ecosim-r226-full-menu-visible-20261102/`.
The three existing R225 source snapshots are reused from
`~/Downloads/ecosim-r225-periodic-current-20261102/` and SHA-linked to
`~/Downloads/ecosim-r225-periodic-qualification-v2-20261102/R225_RECEIPT.json`.

All 10 pages come from logged-in team `Jutalom a nap végén`, 2026
Selejtező I, period 1/5; their local file observations span **17.364 minutes**
and fall within **60 minutes** of the pinned R223 current R156 state. Source
file timestamps are *operator local metadata*, **NOT game-server-signed
snapshots** and are not permission to start projects.

The only actually added decision input is
`Hitelek/Hosszú távú hitelek/Felvétel / Visszafizetés (+/-)`. Its current
P1 selected value, numeric allowed bounds, financial response, borrowing
eligibility, actual available cap and spendable cash are **UNKNOWN**.
This remains true even though the original read-only page displays 7.5% long
loan interest; that is NOT a bank authorization.

## Original existing engine integration

R226 calls the original R225 `parse_source` for 18/18 existing observed
controls and original R145 `load_tracks`, `policy_factor_replay`,
`policy_money_replay` on **19 explicit UNKNOWN-effect TEST ONLY
placeholder entries**, proving **19/19 factor and 19/19 cash effects stay
UNKNOWN**, not zeros. No alternative policy simulator was built, no selected
gameplay policy created, no false five-year city score forecast.

- 10 source-verified top-level routes
- 27 selector labels, including nested (not a complete leaf-view count)
- 19 currently visible text inputs across 4 active pages
- P1 approved decisions: 0/19 verified
- P1 valid numeric min/max bounds: 0/19 verified
- P1 calibrated causal factor and cash responses: 0/19 verified
- Current actual project start cap: UNKNOWN; approved spendable cash: UNKNOWN

### Reproduction on authorized Fedora

```bash
bash team-handoff/r226-top-level-control-census/run_private.sh \
  --primary-pages "$HOME/Downloads/ecosim-r226-full-menu-visible-20261102" \
  --r225-pages "$HOME/Downloads/ecosim-r225-periodic-current-20261102" \
  --r225-receipt "$HOME/Downloads/ecosim-r225-periodic-qualification-v2-20261102" \
  --r156-dir "$HOME/Downloads/ecosim-r223-fresh-r156-20261102" \
  --out-dir "$HOME/Downloads/a_new_private_R226_result"

bash team-handoff/r226-top-level-control-census/qualify_private.sh
```

The recipient directory must not exist. R226 tests are source-driven and
fail-closed for a missing main nav route, changed selector topology,
an unexpected new editable field, wrong live team/market/round,
disguised/ambiguous loan edit, stale source time relative to original
R156, changed original R225 source SHA and output overwrites.

Private, user-readable output:
`~/Downloads/ecosim-r226-final-census-20261102/R226_HU.md`
and `R226_TEN_MENU_COVERAGE.csv`, full `R226_RECEIPT.json`.
No raw page captures, receipts, auth material or private local reports
committed to Git.

## What is still missing to claim a five-year winning strategy

The financial and competitive objective requires source-verified taxes,
institution operations, tariffs, loans, policy constraints, *causal*
PLAN→FACT transitions and an actual validated city score. Existing R153/R154
tax-response and R155/R159 operating cash models are available but mostly
historical/synthetic, and cannot calibrate real P1 actions by themselves.
A passive current PLAN with only one baseline contains no causal
counterfactual. The next highest-value external observation is the
**Bevételek → Adók** active subview; if page-element navigation becomes
available or user chooses it, integrate actual tax decision fields without
repeating the original 19.

**GAME_ACTION_GATE=STOP. No EcoSim changes, no merge or deployment.**
