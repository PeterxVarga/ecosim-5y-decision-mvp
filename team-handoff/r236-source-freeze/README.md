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
