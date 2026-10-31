# R147 paired PLAN observations — only *previously authorized*, already gathered evidence

This tool does not visit EcoSim or change a decision. Never initiate an unapproved A/B preview. It can accept a pair of already available snapshots *in the same period, same market, same team*, with 28 Hungarian factor keys matching `inputs/historical_passive_summary_20261030.json`, each observation tagged `kind: PLAN`, `period`, `displayed_index`, `source_evidence_id`, `captured_at`, `team`, and `market`.

Each pair has `id`, `before`, `after`, `new_project_ids` (unique), plus a `controls` object with optional boolean declarations `no_other_decisions_changed`, `same_active_projects_except_new_ids`, and `read_only_evidence_collected_after_owner_authorized_preview`. These are OPERATOR declarations, not validated by code. All outputs are labelled non-causal and non-forecast. Inter-year p0 FACT versus p1 PLAN is rejected, not assumed a controlled pair.

No real paired observations are shipped; zero observations yields an explicit UNKNOWN result, not a zero error or a PASS of model accuracy.
