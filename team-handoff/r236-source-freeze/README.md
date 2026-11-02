# R236 — collect all sources before calculating

This is a **data-collection-only gate**, created in response to the user's
priority: gather every relevant currently available period-1 observation,
reconcile freshness and provenance, THEN optimize. It neither calls the
existing R162 planner nor produces new game decisions.

Reusable evidence joined READ ONLY:
R217 (observed P0/P1 + partial market state), R222 (35 project cards and
conditions), R224 (P1 cashflow and hypothetical funding), R226 (10 top-level
default/selected screens, 27 selector labels), R228 (374 Excel rows,
23 control crosswalk), R232 (organizer 4/year, not server config),
R233 (29 P0 facts / 29 P1 plan factors), R234 (23 still-unknown full
policy ranges and effects), R235 (4 client-side partial lower bounds and
2 unresolved symbolic education ranges), and a fresh connected-browser
readonly Income/Taxes text snapshot from the current user session.

**Do not misinterpret source count as coverage.** Ten initial main views
are not all subviews. Twenty-seven selector labels are not twenty-seven
independently captured full pages. The 35 project card captures span
103.553 minutes, so the original R192 same-period one-hour requirement
remains HOLD. The R226 10-main-view set was collected within 17.364
minutes and lies within one hour of the contemporaneous R156 observation.
The new Income/Taxes browser text is a *static markup representation*;
React-rendered field defaults in the user screenshot may differ from
its HTML value attribute. Neither proves saved P1 policy decisions.

Actual verified P1 value bounds are 0/23; all policy cash/factor effects
are UNKNOWN, not zero. Current financing budget and server project cap
are not authenticated. P2–P5 actual FACT observations are structurally
unavailable until those periods exist. The organizer's official spoken
four starts per year is useful for a conservative plan constraint, but
is not a server-value receipt.

## Native result and reproduction

Private data and ledger on owner Fedora only:

    ~/Downloads/ecosim-r236-source-freeze-20261102/20261102_income_taxes_readonly_browser.txt
    ~/Downloads/ecosim-r236-source-freeze-20261102/result/R236_PRIVATE_LEDGER.json
    ~/Downloads/ecosim-r236-source-freeze-20261102/result/R236_DATA_COVERAGE_HU.md

Replay:

    bash team-handoff/r236-source-freeze/run_private.sh \
      --out-dir "$HOME/Downloads/NEW_UNIQUE_R236_OUTPUT"
    bash team-handoff/r236-source-freeze/qualify_private.sh

The private ledger lists the exact visible subview labels for the next
read-only capture session. The next high-value observation is completing
missing alternate subviews and the period-specific market/finance
constraints, ideally as a fresh coherent snapshot (without a click path
that resets project state). After P1 closes, collect actual new-period
FACT data and observe PLAN-to-FACT transitions without inventing their
causal mapping.

No user/session details, private receipts, browser context, project
values or Excel are published in Git. NO_GAME_WRITES, NO_MERGE, NO_DEPLOY.

## Codex native browser intake, permissions preserved

On Fedora, Codex CLI 0.166.0 with active ChatGPT login and native browser
tool successfully LISTED eight open tabs, including one existing EcoSim
/simulation/income tab. No browser restart or DevTools port was needed.

A separate strict read-only attempt to read the existing tab DOM reported
BROWSER_ORIGIN_PERMISSION_DECLINED. Thus no page content was imported.
This explicit browser permission must be granted by the owner via the
browser UI. Do not bypass it using direct CDP, network calls or other
access routes. Do not infer that a connection means content is authorized.

The new codex_browser_intake.py validates and SHA-links the existing R236
data gate and the Codex last-message JSON, counts declined origins as BLOCKED,
and prevents unknown data from becoming approved. In particular there are
ZERO new observed EcoSim page contents, saved P1 values or policy bounds.

The private source and outcome are stored ONLY on owner Fedora:
- ~/Downloads/ecosim-r236-source-freeze-20261102/codex-current-tabs-readonly-v1.txt
- ~/Downloads/ecosim-r236-source-freeze-20261102/codex-browser-gated-v1/R236_CODEX_BROWSER_INTAKE_PRIVATE.json

Reproduce from already captured blocked evidence only:
    python3 -I -B team-handoff/r236-source-freeze/codex_browser_intake.py --r236 "$HOME/Downloads/ecosim-r236-source-freeze-20261102/result/R236_PRIVATE_LEDGER.json" --codex-result "$HOME/Downloads/ecosim-r236-source-freeze-20261102/codex-current-tabs-readonly-v1.txt" --out-dir "$HOME/Downloads/NEW_CODEX_PRIVATE_IMPORT"
    bash team-handoff/r236-source-freeze/qualify_codex_browser_private.sh

After explicit owner origin consent, re-run Codex ephemeral and read-only,
using the NATIVE browser connector with existing open tabs only. Disable
any navigation, click, hover, typing, page reload, network, save or submit.
Feed the last-message JSON to this importer. Do not enable full tab
navigation until side-effect safety is separately proven.
NO_GAME_WRITES; NO_MERGE; NO_DEPLOY; R191/R192/R214 HOLD.
