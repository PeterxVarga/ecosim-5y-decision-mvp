# EcoSim R223 – a single time-coherent, current R156 → R192 read-only source gate

## Exact user-visible outcome

The original R217 previously accepted five actual EcoSim browser views at 15:33, while the four R222 card category views were captured between 15:29 and 17:13. The original R192 requires the current card capture timestamp **within 60 minutes of the current R156 state**. This source boundary is real: do NOT rewrite earlier timestamps or falsely stamp the old file as new.

R223 integrates the already existing original R217/R156/R152 capture, R217 35-status parser, R220 category source verifier, R222 on-page project-condition parser and **original R192 `validate_catalog`**. It checks SHA-256 and actual file timestamps, the period/team/market identity, 35 sequential cards, all 4 observed amounts and each complete visible effect list, 2 explicit dependencies, and current 35 running statuses.

When only three of four current category views are missing, R223 produces a private **HOLD_MISSING_CURRENT_CATEGORY_VIEWS** receipt with the missing categories. If all four exist but the view files are from different hours, it writes **HOLD_NOT_SAME_HOUR_OR_FUTURE_SOURCE** and NEVER produces a current catalog. Only with all current files and a maximum 1-hour span across the 4 category snapshots + current R156 state does it attempt the **original R192** validation. A PASS is **operator-observed 35-card definition parity only**; not server authentication and not game approval.

## Actual progress, 2026-11-02

Newly read from connected browser (no gameplay): P1 current Summary, Economy card view, Finance, Income, Loans. Source text is held privately in `~/Downloads/ecosim-r223-fresh-readonly-pages-20261102/`. These 5 source text files are SHA-pinned to a fresh original R217-produced current R156/immutable bundle `~/Downloads/ecosim-r223-fresh-r156-20261102/`. R191 correctly rejects **maxProjectPerTurn:null** (cap source UNKNOWN). The original Market I numeric cap and real spendable funds were NOT observed on the visible pages or found in the official publicly displayed competition guidance.

The private R223 receipt `~/Downloads/ecosim-r223-intake-qualification-20261102/R223_RECEIPT.json` reports 14 current cards observed, the **3 still missing** current views (Sport és Kultúra, Közlekedés, Környezet), no R192 admission, no gameplay. Old category pages must NOT be copied or retimestamped as live evidence.

## One-command runner for a COMPLETE newly captured set

Collect all five current core views and 4 actual category views in private files of the same source format. After completing those **fresh** observations and verifying they were captured within one hour, run:

```bash
bash team-handoff/r223-coherent-current-intake/run_private.sh \
  --pages-dir "$HOME/Downloads/private_current_9_view_sources" \
  --out-dir "$HOME/Downloads/a_new_private_R223_report"
```

The script calls original `prepare_visible_r217.py` to create a **NEW** immutable 5-page R156 capture and then R223 original-R192 verification. No existing output directory is overwritten; no game changes. A real captured source includes separate source URL, source kind, team/market/period and view identity header. File last-modified times are only *local capture metadata*, not signed server observations.

A CHECK `PASS_R192_OPERATOR_CURRENT_CATALOG_TIME_PARITY_ONLY` will create `current_r192/R223_R192_CURRENT_CATALOG_PRIVATE.json`, a complete current operator-readable R192 source, plus the receipt; otherwise no full catalog is emitted. It does NOT fill in `maxProjectPerTurn` or claim spendable money, so original R191/R214 still HOLD until a real independent cap and finance record.

## Qualification without pretending old data is fresh

```bash
bash team-handoff/r223-coherent-current-intake/qualify_private.sh
```

The test suite covers the actual 5-page partial capture and intentionally stale 3 old page snapshots, source hash tampering, changed current condition, wrong category and destination overwrite. The complete passing R192 path is tested ONLY with **synthetically changed file mtimes on temp copies**, explicitly labeled MOCK, so **no claim of current live R192 success**.

**GAME_ACTION_GATE=STOP, game_writes=0, no merge, no deploy.** Any future gameplay authorization requires separate owner approval. The winning actual city score remains UNKNOWN.
