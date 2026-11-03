# EcoSim R205 – recover and reconcile previously uploaded evidence

This release follows R204 and **reuses the original R200–R204 code**. It does not create a second city simulator. This is a historical, read-only source-intake and crosswalk improvement, not a current-round or live gameplay admission.

## Research and re-use finding

The user had *already uploaded* CSV exports of the Income, Loans and Rules views, observation provenance and source index. Earlier R200/R204 treated Income as indirect and Loans as unknown because those documents were not part of the source-pinned local R200 profile. **Do not ask for these already uploaded views again.**

The private Fedora evidence directory contains five CSVs reconstructed from the file library's parsed-sheet text and a local manifest containing file-library IDs and SHA-256 of the **normalized** copies. These are **not byte-identical original uploads**, nor should they inherit old raw-export hashes. The public repository contains neither these exports nor their private manifests.

## Actual admission and reconciliation

- Five CSVs, 49 + 7 + 5 + 24 + 15 = 100 normalized rows; reject missing/changed file hashes, nonunique IDs, malformed rows and cross-source team/market/round inconsistency.
- All 24 observations reference valid IDs and URLs in the 15-row source register.
- Four tax receipts plus six service receipts (p0 FACT and p1 PLAN) exactly match the already-qualified R202 observed raw values, **10/10**. The sole explicit fee alias is the transport income label `Tömegközlekedés` (R202) versus `Személyszállítás` (Income).
- Long/short-term loan rates are read from the private historical loan table and independently cross-checked against timestamped UI observations, never embedded as public constants. Validate the written long-loan borrow-or-repay and automatic-short-loan conditions; **loan ceilings and settlement timing remain unknown**.
- Both recorded development-grant amounts are preserved as historical observations **without treating them as available project funding**.
- R204 current readiness remains HOLD. No new server scoring, cash approval, full-city simulation or current-round truth is inferred.
- The R202 report SHA-256 and its cross-model R204 finance/institution identity must match before executing the crosswalk.

## Fedora reproduction

`bash team-handoff/r205-historical-library-reconciliation/run_private.sh`

One command performs two independent historical replays and byte-compares their JSON/Markdown, then executes the entire R196–R205 targeted test chain. It creates a fresh private result directory under Downloads. Outputs are `R205.json` and `R205_HU.md`; prior R204 detailed five-year rankings remain unchanged.

## Gates

**GAME_ACTION_GATE=STOP**. Not a live budget, not a real loan approval, not a server score prediction or a citywide optimum. Remaining unknowns: market loan ceilings, grant availability/timing, complete transport/population/business/other institutions, consecutive closed FACT years and actual state transitions. Draft-only, review required; never merge/release on the basis of this evidence alone.
