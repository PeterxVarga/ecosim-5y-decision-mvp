# EcoSim R222 – actual displayed project conditions and 24 five-year plan revalidation

## User capability achieved

The original real-round R220 had verified **35/35 visible card names, money and effects**, but incorrectly marked all **project conditions unobserved** because its existing parser did not read the text block titled `Projekt feltételek`. Re-examination of the unchanged, privately collected real UI page source shows exactly two displayed conditions:

- Project 30 – Bubi bővítés: `Bicikliútfejlesztés — Fut` (prerequisite project 29).
- Project 31 – P+R parkolók: `Vasútfejlesztés — Fut` (prerequisite project 27).

The other **33 complete visible cards have no displayed condition block**. That is a source observation, not cryptographic proof that there are no hidden server rules. R222 parses these conditions **from the actual four original UI category texts** (not from the historical R162 catalog) and independently compares every one of the 35 fields through the existing R192 `_card` implementation. Exactly 35/35 visible names, 4 money fields, effect metric/% lists and visible condition lists match the original pinned R162 project data.

## Why full R192 remains HOLD

The four actual browser snapshots are dated **2026-11-02 15:29–17:13 CET**, span 103.55 minutes, and the original immutable R156 state is captured at **15:33 CET**. The original R192 requires a current 35-card capture within **one hour of the state capture**, among other strict checks. R222 gives the R192 validator the **actual last source-page filesystem observation time**, never a falsified one. It correctly returns:

`HOLD_CATALOG_NOT_SAME_PERIOD_CAPTURE_WINDOW`.

The R222 privately generated R192 JSON is **not an admitted current catalog**, even though all 35 observed card fields equal original values. The UI has not provided a number for the current Market I project-start cap. The official 22-page Hungarian handbook says there is a per-period limit, but no market-specific number. Actual spendable cash/committed expenses are still UNKNOWN, and p1 projected net/tartalékképzés is not spendable approval.

## New integrated E2E outcome

The independent `join_current_conditions.py` reads the actual R222 condition evidence and the *previously built* R221 source-linked 24-case five-year scenario result. It checks SHA-linked source identity between R217 and R220, all **24 five-year sequences = 120 virtual year rows**, original R160-qualified plans, no game writes and strict previous-year prerequisite timing.

The dependent project starts are exercised in 2 scenario plans apiece. The reviewer rejects synthetic tampering that removes previously running project 29 or 27, or tries to promote hypothetical budgets into live funding. This is a **source-reality falsification of the original plans**, not a new optimizer. No new 24-run search or duplicate worker was built.

## Read-only private commands on authorized Fedora

Create a fresh private R222 report (not the original version):

```bash
bash team-handoff/r222-visible-conditions/run_private.sh --out-dir "$HOME/Downloads/new_r222_condition_capture"
```

Join to the previous already-qualified R221 24-case report (separate new directory):

```bash
bash team-handoff/r222-visible-conditions/join_private.sh --out-dir "$HOME/Downloads/new_r222_plan_join"
```

Source-driven focused qualifications (existing private original R217/R220/R221 evidence; no game interaction):

```bash
bash team-handoff/r222-visible-conditions/qualify_private.sh
```

Existing source-qualified reports, never Git-committed:
- `~/Downloads/ecosim-r222-current-conditions-20261102/R222_RECEIPT.json`
- `~/Downloads/ecosim-r222-current-conditions-20261102/R222_R192_CURRENT_CATALOG_TIME_HOLD.json`
- `~/Downloads/ecosim-r222-current-dependency-join-20261102/R222_DEPENDENCY_JOIN.json`

Original source pages, current R156 source receipts and rulebook PDF stay in private Fedora directories. The GitHub commit contains **generic source and focused tests only**.

## Capability and safety

- Exact current displayed project prerequisite conditions observed: **2/2**.
- All 35 complete visible cards match historical reference; browser observations are not server attestation.
- Original R192 source time-admission remains HOLD; original R191 cap unknown; R214 finance unknown.
- An approved game decision, a client-scored winning plan and a full city simulation are **NOT** established.
- No EcoSim UI write, Start/Save, debt action, owner-approved gameplay, merge or deployment.
- `GAME_ACTION_GATE=STOP`; game writes 0.

**Next true critical path:** obtain a coherent, same-hour current snapshot of all four category views and current R156 state, the numerical Market I cap, and separately supported same-period spendable funds minus committed costs. Do not silently replace unknown with 0 or with historical 4.
