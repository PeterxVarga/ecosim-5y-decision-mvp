# EcoSim R168 — Codex CLI browser/DOM coverage audit (NO GAME WRITES)

## Mission and boundary
Audit **only** the already authorized, logged-in \`https://edu.ecosim.hu/simulation\` web UI. Read-only reconnaissance of all pages and genuinely view-only subtabs to find missing official variables, dynamic constraints, and source-level calculation hints. **Do not change any simulation values, even temporarily.** No scenario testing by altering inputs, no trial saves, no irreversible actions, no automated game execution.

This is **test round Z / 1/1** until the actual page explicitly proves otherwise. Never label PLAN as subsequent-year FACT or test round as live competition.

The current base is R162 on private repo \`PeterxVarga/ecosim-5y-decision-mvp\`; existing Draft PR #1 contains R165–R167 read-only evidence:
- R165 14 visible economics project cards + two finance tables + six service fee lines and effects, reconciled with frozen R94.
- R166 full 25-row balance sheet: p1 planned cash 865588 ECU, but not confirmed spendable; category sum 20000 ECU above displayed total; component-to-tradeable discrepancy 330000/329999 ECU.
- R167 short loan 12%, automatically triggered by negative city financial position; earlier long loan 7.5%.
- Current optimizer and game action readiness: **STOP**.

## Preflight (first, no destructive operations)
1. Establish the actual page's heading, round, market, team, period and observation timestamp. Use browser attachment to currently logged-in user session with explicit consent. If not connected or not logged in, stop and record BLOCKED_AUTH, do not ask for passwords/cookies.
2. Confirm there is no game state mutation on navigation or view-only tab switching. If unsure about a control, DO NOT click it.
3. Create local outputs **outside repo-tracked paths by default** under \`~/Downloads/ecosim-r168-readonly-evidence/\`; do not auto-push or create a PR. No captured credential material.
4. Record the browser/MCP tooling and whether DOM text, screenshots, network metadata or source maps are supported. Do not assume DevTools, HAR, raw response bodies or backend verification.

## Allowlist: page routes to inspect
- /simulation/summary
- /simulation/projects
- /simulation/institutions
- /simulation/transport
- /simulation/income
- /simulation/population
- /simulation/corporations
- /simulation/loans
- /simulation/finance
- /simulation/analysis

View-only subtabs currently known:
- projects: **Gazdaságfejlesztés**, **Sport és Kultúra**, **Közlekedés**, **Környezet**
- income: **Szolgáltatások díjai**, **Adók**, **Állami törvények**
- loans: **Hosszú távú hitelek**, **Rövidlejáratú hitelek**
- finance: **Cash flow**, **Vagyoni kimutatás**
- other routes: enumerate all visible named tabs and inspect **only if** confidently view-only. Enumerate but do not activate ambiguous controls.
- For projects, collect all **35** catalog cards from 4 categories: ID, name, running or available status, initial/startup/investment/maintenance (preserve signed values), partner support, effects, constraints, dependencies, and visible tooltips.
- Summarize accessible help/manual rules; do not infer hidden game rules from labels alone.

**Never click these or semantically similar controls:** Mentés, Véglegesítés, Start/Stop, Projekt indítása, Hitel felvétel/visszafizetés, Számítás mentése, Beküldés, Megerősítés, törlés, vétel, értékesítés, adóváltoztatás.
**Never type, fill, press increment/decrement arrows, change selectors associated with inputs, toggle switches or alter user values.** Avoid opening untrusted external links.
If a tab uses a bare icon button without known read-only role, leave it alone and mark the view BLOCKED_AMBIGUOUS_CONTROL. Opening view-only menus may be allowed only after confirming their navigation intent.

## Capture strategy
For each visited route/view, record:
- observed timestamp and URL path without credentials/query; round/market/team/period; whether p0 FACT or p1 PLAN;
- all **visible** headings, tables, row labels and displayed values, footnotes, help text, limits and read-only selection states;
- input labels, current displayed value vs blank/undefined (do **not** fill);
- full list of view-only tabs, page coverage and missing items;
- project and factor IDs, canonical UI names, units (especially ECU vs thousands), and financial time semantics when explicitly sourced.
- If permitted by game rules, use *sanitized* DOM/accessible-tree snapshots or textual screenshots for audit; prefer minimal structured extracts.

Do not save/export raw \`localStorage\`, \`sessionStorage\`, cookies, authorization headers, token-bearing URLs, HAR, entire API responses, private contact details, personal identifying records, or browser profiles. If investigating network, capture only sanitized method/path/status metadata and explicitly presented UI values; no undocumented write endpoints or probing. Client JS code is only evidence of client implementation, not proof of server acceptance. Respect the competition rules; if uncertain, stop.

## Critical evidence / falsification questions
1. Precise \`market.maxProjectPerTurn\`, per-period already-used starts; rule for project #1 prior-year bonus and same-year dependencies.
2. Cash available **at moment of project start**, permitted sources, reserve and year-end timing, whether p1 projected 865588 is available now (do not assume), existing commitments.
3. Treatment of project partner support (when received, caps, no double-counting); signed \`maintenance_cost=-12000\` project #12, \`-8800\` project #13.
4. Automatic short credit threshold and formula, 12% accrual period, long 7.5% constraints, variable credit rate/caps and loan-vs-reserve interaction.
5. Why asset category totals exceed total assets by 20000 ECU; why tradeable row sum exceeds tradeable subtotal by 330000/329999 ECU; why six fee lines exceed aggregate by 2 ECU.
6. Tax and fee legal bounds, precise marginal response formulas; law toggles, aid/grants and payroll impacts.
7. Institution capacity / payroll / materials / transportation fleet; source and units of all city factors.
8. GDP, migration, corporation count, population, league ranking and competitive interactions.
9. Difference between present test round and actual 5-year competition; when subsequent FACT observations become available.
10. Are there genuine, **already-rendered** read-only preview outputs for candidate decisions? Do not create previews by changing values.

## Result files and acceptance gates
Produce in local directory:
- \`COVERAGE_MATRIX.csv\`: every route + subtab, inspected/blocked/not-visible, timestamp, number of rows, and source URL.
- \`SANITIZED_OBSERVATIONS.json\`: structured captures with provenance and null for unknown/blank values; preserve p0/p1 separately.
- \`UNKNOWN_REGISTER.json\`: one row per missing field with required source/evidence, priority and blockers.
- \`RECONCILIATION.json\`: compare observed values with R162/R165–R167 and R94; list all corrections and mismatches.
- \`UI_RULES.md\`: only source-backed rules with verbatim short original label, route/view and interpretation confidence.
- \`SAFETY_RECEIPT.json\`: mutation_count=0, write_forms_count=0, sensitive_data_export_count=0, game_actions_attempted=0, explicit STOP.
- \`README.md\`: conclusions, exact scope, controls skipped, provenance and replay instructions.

**Success = complete navigable read-only UI coverage with UNKNOWNs enumerated.** Never fabricate values. Never claim real five-year forecast calibration from p0 FACT vs p1 PLAN. Never derive spendable money solely from financial line items. Treat ambiguous or incomplete pages as BLOCKED, not as observed empty. No commit, push, save or gameplay write; owner will decide whether to import sanitized evidence into the existing GitHub draft PR.

## Execution efficiency
Research existing R162/R165–R167 first, then one breadth-first navigation pass, then independent cross-page reconciliation; do not repeatedly rerun the optimizer. Small targeted inspections only when they resolve a critical missing source. Report a single evidence bundle and actionable remaining UNKNOWNs.
