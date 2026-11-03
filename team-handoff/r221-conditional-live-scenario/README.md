# EcoSim R221 — current observed Selejtező I, condition-only scenario frontier

## Why this is the next critical-path capability

R217 current UI 29 factors / six ongoing projects and R220 current four-category 35/35 **visible** card cost/effect parity are real read-only, source-hashed observations. But the R191 original **actual market cap**, **source-approved spendable project cash**, and R192 **current complete project conditions** remain UNKNOWN. The 22-page official Hungarian EcoSim manual linked from the logged-in /simulation landing page explicitly confirms limited project starts per period, **without stating the numerical market-specific cap**. The manual specifies annual repeated maintenance, once-on-start relative factor effects, and automatic debt in a cash shortfall. Do not promote a displayed projected p1 reserve or net earnings into spendable funds.

Instead of inventing the missing inputs and incorrectly allowing R214 live advice, R221 uses **the original R162 five-year search and original independent R160 audit**, changing **only explicit scenario overrides in memory**. The current R156 state on disk retains `maxProjectPerTurn:null` and five null-year spendable/committed fields; all earlier R191/R192/R214 gates stay HOLD.

## Exactly what is tested

- Current read-only R217 receipt and R220 35-visible-card receipt must be source SHA-linked and match Selejtező / I market / Jutalom a nap végén / period 1.
- Require actual six ongoing project IDs `[14,22,23,24,34,35]`, zero p1 selected projects, and current R156 29 factors plus six index weights.
- Original handbook PDF's SHA-256 `4d6b5c545bb205e5a9f8b92959b6659c4786d10cf6e1e6b2f654fa79c0168087` is pinned (private local download of the linked official public manual).
- 3 **hypothetical** cap scenarios `1,2,3` × 4 **hypothetical annual** card envelopes `0,25k,50k,150k ECU` × 2 original search objectives `nominal,scenario_min` = **24 separate five-year source-conditioned searches**.
- Original R162 uses `cap_override` and `budget_override`; no mutation to source. Original R160 independently audits five-year slots, dependencies and conservative cash, plus explicit `allow_same_year=False` test hypothesis.
- Historical source has 2 named prerequisites (#30 Bubi needs #29 bicycle path running; #31 P+R needs #27 rail running); these are **not established as current official server conditions**, so R221 never admits full R192.
- Output includes the 24 distinct scenario rows and alternative first-year actions, not a recommendation or permission to Start/Save/borrow.

## Repeatable use on the already authorized Fedora host

```bash
bash team-handoff/r221-conditional-live-scenario/run_private.sh \
  --out-dir "$HOME/Downloads/a-new-private-r221-result"
```

R217/R220 receipts, original immutable R156 manifest and original official manual are read from existing pinned private directories; the wrapper does not run on historical-only data. Output directory must not exist beforehand.

Native qualification of the existing full 24-case output, no repeating a 24-run batch just for test count:

```bash
bash team-handoff/r221-conditional-live-scenario/qualify_private.sh
```

**Private** R221.json and Hungarian R221_HU.md at
`~/Downloads/ecosim-r221-current-source-scenarios-20261102/`.

## Evidence and limits

The observed UI 35/35 card displayed costs and effects are matched; hidden condition arrays are not. Historical previous-period project prerequisites are **hypotheses in conditional search**, not server admission. The actual game cap is **UNKNOWN**, actual project spendable budget **UNKNOWN**, future full-city transition **UNKNOWN**, actual score **UNKNOWN**. Official handbook says a deficit can trigger automatic debt; this strategy does NOT automatically borrow, authorize debt or convert reserve into cash. No game session/API access, writes, builds, deployment or merge.

`GAME_ACTION_GATE=STOP`. The only completed user capability is **risk-aware conditional planning before actual cap and money are verified**. Next largest ROI is acquiring those two numbers with current same-period source and verified project conditions, then running original R214 live advisory gate. Do NOT call these scenarios live readiness or recommendations.
