# R142A project limit — static evidence

**Actual market cap: UNKNOWN.** No numeric default or current value was found in the 18 bundles or supplied data. This is a static client finding, not a server rule. The 35-card export does not contain market setup. Original anchor windows in `evidence/R142A_STATIC_ANCHORS.json` were verified byte-for-byte; their 217–230-byte hashes are separate from the 180-byte hashes below.

Let selected period be t, current period c, final period f, current project-state map S(t), prior S(t−1), and market value M. The SmartCity parent passes A = M + 1 if numeric S(t−1).project1 equals 1, else M. This is a blanket increment, not a test that the current card is project1. The card sums over keys in S(t): for nonrepeatable j count 1 exactly if numeric S(t)[j] = 1 and numeric S(t−1)[j] != 1; for repeatable j count 1 exactly if numeric S(t)[j] = t. Remaining U = max(A − count, 0). These are JS coercion rules; the code does not itself require t > 0 for the repeatable card count. The shared calculation of active repeatable projects separately requires positive state and period equality. Verify period-zero behavior rather than extrapolating.

For an existing card, no button is rendered if t > f. If t < c, the status button is disabled. Otherwise a nonrepeatable with both current and prior state 1 shows disabled Running; a counted current selection shows Cancel. Only otherwise, Start is enabled when U is truthy and conditions pass; the handler rechecks both, dispatching 1 for nonrepeatable or t for repeatable. Missing project metadata returns no card. No direct cash/loan test appears in this button branch; decision setup or backend may impose additional constraints. This is not proof of server acceptance. A continuation of a nonrepeatable project is not counted as a new selection. The prior-project1 increment gives an extra allowance even when the new project is unrelated: thus a universal claim that every possible start reduces the *base* allowance by one is false. It does not show that a normal new selection avoids the count.

Conditions split literal `and`, trim each token, and recognize leading `not `. A positive condition requires the numerically coerced selected-period state to be truthy; `not` requires it falsy. This is a raw state test, not the active-project predicate or a test that a prior period has completed. Same-period co-selection can satisfy it in client state, subject to other gates; the optimizer deliberately excludes such cases. A selected new project with a failed condition triggers a reset dispatch to 0 during card rendering. The defaulted delay is displayed if >=1; it is not part of this card's start or slot predicate. Its actual effect timing is not established by this branch.

Least invasive confirmation: an authorized official setup/export containing the actual field and selected/prior project states, or a normal UI label explicitly showing the market cap and adjustment. A disabled button alone cannot identify M because conditions, current selections and period also matter. UI navigation to project cards may itself trigger the reset above; see manual gate. Do not infer a numeric cap from unrelated game chunks.

## Verifiable context windows

| Purpose | Byte range [start,end) | SHA-256 of 180 bytes |
|---|---:|---|
| Market cap and prior project1 | 88836–89016 | `133955481977dd078486bd846ba743805fea7546ea37412c59f8e2e55590e048` |
| Pass adjusted cap to cards | 89196–89376 | `f72dad48ae04c11f2dbd6f3a1200ad9c2665c79fda86e63a4f331fc6866cea93` |

| Purpose | Byte range [start,end) | SHA-256 of 180 bytes |
|---|---:|---|
| Condition test | 13161–13341 | `3e4a35ae9b799791c89cc4fc38c26ccd87136edf1363a8459e31f02f466f876b` |
| New state test | 13502–13682 | `a911fc3d85c86e005cc45071c7607933fb4da2608d00e17233a62f7d7da490b7` |
| Count and remaining | 15964–16144 | `de622dbf56de8b79819090e12dd2cda724613d3f4142686f0b06a62d048f5ed7` |
| Button and dispatch | 16724–16904 | `15336f606145c5929440b5ad362efce16fdb4caa113c78f50e73b4b9448b1bd2` |
| Delay display | 17252–17432 | `8cae1374bb5ebe375579b77e833a5d56d050be822c24d4f436765c91382debb6` |
