# R142A decision gate — STOP

**STOP final selection.** Actual base cap, selected and previous-period state, spendable cash/financing and a candidate preview are unproven. The smallest missing inputs are an authorized market cap plus previous project1 and current selected-state counts; an authoritative spendable amount or financing rules with commitments and support timing; and an approved, verified candidate preview. Unknown aliases and nonlinear factors can decide the ranking; do not fabricate a winner.

One offline optimizer run screened 27/29 non-running projects, excluding #30 and #31 for prerequisites; same-period conditions can in fact be satisfied by raw state, so this is a conservative screen, not an exact eligibility rule. It enumerated 36,480 combinations under its 200,000 ECU ceiling. The fixed weights and baseline come from prior UI observations, not confirmed current market data. Exact-count K below means **available new selections assumed**, not necessarily the numeric market cap: prior project1 may add one and existing selections consume slots. All budgets are hypothetical and first-year thresholds equal startup + investment + max(maintenance,0), with no grants or negative maintenance netted. Actual financing needs could be greater.

| Assumed K and budget | Candidate IDs | Conservative first-year cost | Proxy Δ | Missing alias |
|---|---|---:|---:|---|
| K=1, 30,000 ECU | #27 Vasútfejlesztés | 15,000 | +0.152320 | small-business count 0.01% |
| K=2, 100,000 ECU | #13 Informatikai fejlesztés + #27 | 70,000 | +0.369114 | #27 small-business count 0.01% |
| K=3, 100,000 ECU | #8 Okos Gazdaság Alkalmazások + #13 + #27 | 99,000 | +0.479708 | #8 0.03% and #27 0.01% small-business count |

#13 has signed annual maintenance −8,800; it is not used as funding. #8 has +3,000 annual maintenance and 3,500 support label; the latter is not prepaid funds. The three-year conservative cost of the third combination is 105,000 ECU under unchanged annual rates, not a total verified lifecycle cost.

For candidate effects, code calls factor functions using `administration` (Ke), `internetUsage` (ot), `populationConditions` (Nt), `workingConditions` (Dt), `populationQualification` (Wt), `companyFriendliness` (Re), `sustainability` (We), `airQuality` (Be), `publicSafety` (mt), `settlementDevelopment` (St), `transportQuality` (le), and `publicTransportRatio` (Et). These are code-key/function associations; matching Hungarian exported labels to keys is an interpretation unless corroborated by the language mapping. Exact small-business alias and indirect business-count propagation remain unproven. Effects are aggregated multiplicatively in the default shared branch, but some factor functions cap or clamp the result (e.g. le, St, Et), and nonlinear dependencies can propagate. Applying card percentages directly to displayed factors is therefore only a proxy. Source windows for factor calls are in status.

Falsifiers: a different cap or existing selection, failed condition or repeatability, insufficient confirmed cash, support or costs settling differently, changed baseline/weights, a decisive missing alias or indirect effect, or an approved preview ranking another feasible combination higher. GO only after these facts are resolved and the owner separately authorizes any necessary draft preview; this report does not authorize a start or save.
