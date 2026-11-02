# R232 — 2026 organizer-announced four-per-virtual-year cap, conservative limit

Source: public user-provided X-Challenge 2026 kickoff YouTube video,
https://www.youtube.com/watch?v=3GNCkvECOdk&t=1268s (21:08–21:25).
The EcoSim speaker states **four project starts per year**, twenty for the
five-year competition. The recording's original Hungarian captions were
checked, including the speaker's immediate correction of a verbal "24" to
**20**. This is an **official organizer announcement**, substantially
stronger evidence than prior R143 historical/test fallback. However this
is **not** a server-attested market.maxProjectPerTurn value; the live R156
bundle remains unchanged with null, and R191/R192/R214 remain HOLD.

Research falsifier: original R162 client's special "previous project 1
running" allowance may add a *fifth* start. The existing default R143/R162
search already uses a spoken four-per-year base, but one live-source search
with a four-base override returned **22 starts**, including five in years
four and five. This contradicts the organizer's plain four-per-year statement
unless the special server exception is proven. Do not treat a possible UI
exception as an approved competition advantage.

Implementation: add an *optional* announced_absolute_cap=4 to the original
R162 search. It caps the existing client-bonus-adjusted annual number,
retaining the legacy client-exploration behavior for callers who do not
choose the announced strict mode. R232 reuses original R162 optimization,
R160 independent audits, R145/R148 policy UNKNOWN propagation and
previously source-linked current R224/R228/R231 data. No second optimizer.

Native current-source private output in
~/Downloads/ecosim-r232-organizer-cap4-20261102/R232_HU.md and R232_RECEIPT.json.
Eight conditional scenarios at four *illustrative*
annual ECU limits (0/168621/337243/674486), nominal and scenario-min
objective, 40 hypothetical year rows. Zero or at most 4 starts every
single year, maximum 20 in 5 years. These scenario budgets are **not
actual available money**, and the fifth-year project-only conditional mapped
index is **not** a total city/official server-score forecast.

Run on owner Fedora:

    bash team-handoff/r232-organizer-four-cap/run_private.sh --out-dir "$HOME/Downloads/new_unique_r232_result"
    bash team-handoff/r232-organizer-four-cap/qualify_private.sh

The video additionally says around 18:41–19:28 that the plan column is a
projection that may differ from the realized outcome due to other teams'
effects, and around 39:49–40:04 that the **fifth-year final ranking** matters.
Preserve market competitor feedback and all 23 unknown policy/cash impacts.

No private UI captures, Excel, trace, video captions or game session are
committed to this PUBLIC repository. NO_GAME_WRITES, NO_MERGE, NO_DEPLOY.
