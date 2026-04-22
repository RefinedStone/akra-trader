# Data Incident Response

Purpose: define the response path for stale sync, repeated ingestion failures, gap expansion, or
unclear dataset lineage.

## Trigger Conditions

- market-data freshness is stale relative to the active timeframe
- sync failures repeat without recovery
- gap windows expand or remain unresolved
- rerun or comparison work cannot defend its dataset boundary

## Product Surfaces

- market-data health and sync status surfaces
- normalized market-data lineage history and ingestion-job history query surfaces
- control-room triage workflow that binds the currently selected instrument to lineage and
  ingestion history review, auto-links runtime alerts into that focus, and keeps a merged lineage
  incident history in view
- multi-symbol alerts resolve to one explicit primary triage focus using instrument risk,
  live-session relevance, payload symbol order, and stable fallback, and the control room shows why
- backend operator alert and incident payloads now carry explicit `primary_focus` metadata for that
  selected symbol/timeframe and candidate set
- operator and guarded-live alert payloads now carry normalized symbol/timeframe context when the
  runtime knows it
- external webhook and provider remediation payloads now carry the same normalized market context
  so downstream incident systems do not need to reconstruct the lead symbol from free-form text
- when a provider returns that market context during workflow pull or remediation sync, Akra now
  restores it into normalized incident fields instead of dropping the selected focus on re-entry
- provider workflow actions now also project that `market_context` into provider-native structured
  fields such as `custom_details`, `details`, or `metadata`, and render it as an explicit
  note/message section so provider timelines preserve the selected symbol/timeframe
- provider pull normalization now reads those same vendor-native structured fields back so
  recovered incidents keep the same selected symbol/timeframe and `primary_focus` after external
  round-trips
- the normalized provider recovery state now keeps provider-specific source provenance for restored
  market-context fields so operators can see which vendor payload path last supplied that focus,
  and the control-room incident drill-down plus triage export now carry that provenance forward
- provider provenance export in the triage panel now supports provider/vendor-field filtering,
  sort controls, persisted local export history, a team-shared registry and audit trail, plus
  provider/vendor/focus/requester rollups, cross-focus query results, and daily provider-drift /
  export burn-up dashboards so repeated incident handoff does not start from an empty clipboard
  or an untraceable copy action
- provider provenance analytics now also has server-side saved presets, shared dashboard views,
  scheduled provenance reports, report audit trails, background due-run execution, and manual
  controls so teams can reuse the same triage and analytics framing across shifts instead of
  rebuilding filters locally
- operator visibility now also emits provider-provenance scheduler lag and failure alerts plus a
  scheduler-health snapshot, so automation drift shows up in the same operator review loop as
  runtime incidents
- the provenance analytics workspace now also shows paginated scheduler-cycle history, scheduler
  health export, and daily-to-hourly health / lag drill-down tables, so operators can distinguish
  one-off lag from sustained automation regression before escalating
- scheduler health export can now be shared into the team registry, leaves delivery/download /
  escalation audit records, and can be escalated directly to configured operator delivery targets
  when automation drift needs a cross-shift handoff
- each shared scheduler export now also carries its own routing and approval policy, so operators
  can hold a snapshot in chatops review, switch it to paging delivery, and require explicit
  approval before sending higher-noise escalation routes
- active scheduler lag/failure alerts now also auto-start one shared export workflow per active
  alert condition in backend automation, and that workflow auto-escalates when its saved routing
  and approval policy already permit delivery; the alert surface still exposes direct controls to
  inspect, approve, or re-escalate that same handoff artifact without leaving alert review
- when that scheduler alert has already resolved, the alert-history row can now reconstruct a
  historical scheduler export from the persisted health-cycle records for the same detected /
  resolved window instead of exporting the current scheduler snapshot
- repeated lag/failure cycles now stay visible as separate scheduler alert occurrences with
  per-category timeline position in alert history, so resolved review can pick the exact closed
  window instead of losing older occurrences behind the latest row
- the scheduler automation workspace now has its own paginated alert-occurrence table with
  category/status filters, so teams can review or reconstruct scheduler incidents without paging
  through unrelated operator alerts
- resolved scheduler exports now also support a mixed-status post-resolution narrative mode, so
  operator handoff can include the recovery path and stabilization history after the alert closed
- the same scheduler occurrence slice can now also export a stitched multi-occurrence narrative
  report and share that artifact into the scheduler export registry, so repeated lag/failure
  windows can be handed off as one reviewed report instead of separate row reconstructions
- stitched scheduler reports now also have a dedicated saved-view surface, so an operator can
  save the current scheduler occurrence slice as a named report lens and later re-apply, edit,
  delete, inspect immutable revisions, restore prior snapshots, copy, download, or share that
  same stitched artifact shape during a later handoff
- those saved stitched report views now also expose bulk governance and a shared team audit
  surface, so repeated scheduler handoff lenses can be reviewed, patched, or retired as shared
  operational assets instead of one-off personal shortcuts
- those same saved stitched report views now also use staged governance plans with reusable
  policy templates, so bulk stitched-report edits enter the shared approval queue with previewed
  diffs and rollback targets before they touch the active handoff lens
- those same saved stitched report views now also have a dedicated approval-queue slice and
  stitched-report policy catalog surface, so shift leads can review and stage saved-view
  governance directly from the stitched report workspace instead of pivoting through the generic
  scheduler governance controls first
- that stitched-report governance workspace now also has its own saved registry and revision
  lifecycle layer, so shift leads can persist a stitched-only queue slice plus default policy
  bundle and later re-apply or restore it during handoff without reopening the generic shared
  catalog workflow first
- those stitched-report governance registries now also have bulk governance controls and a
  dedicated team audit trail, so shift leads can patch or retire multiple queue/default bundles
  together and still review who changed which stitched handoff lane later
- those same stitched-report governance registries now also use staged governance plans with
  reusable policy templates and catalogs, so queue-slice/default-policy bundle changes can enter
  preview, approval, apply, and rollback workflow before they touch the active stitched handoff
  configuration
- that same stitched-report governance registry workspace now also exposes a registry-only
  approval queue and stitched-governance-registry policy-catalog surface, so registry bundle
  review and queue-defaulting can stay in the stitched handoff surface instead of detouring
  through the generic scheduler governance queue
- those same stitched-governance-registry policy templates, policy catalogs, and staged plans
  now also live in their own stitched-registry governance record layer and API surface, so
  stitched handoff approvals no longer depend on the generic scheduler governance backing store
- the same scheduler occurrence table now also carries a narrative facet and can stage dedicated
  scheduler narrative templates plus named registry boards, so cross-shift review can reopen the
  same post-resolution or recurring-occurrence lens instead of rebuilding filters manually
- that same scheduler occurrence timeline now also supports deeper server-side search over
  occurrence IDs, alert text, market context, and narrative status sequences, so shift leads can
  isolate the right lag/failure handoff slice before exporting or sharing a stitched report
- that same scheduler occurrence search now also exposes weighted ranking metadata and highlights,
  so incident review can explain why a given lag/failure narrative matched the current query
  before a stitched export is handed to the next operator
- that search path now also accepts advanced operators and semantic retrieval hints, so an
  operator can narrow narrative review with queries such as
  `status:resolved recovered -category:failure` before handing off a stitched report
- that scheduler narrative search now also executes against a dedicated full-text index with
  boolean query support, so incident review can combine `AND` / `OR` / `NOT` clauses and market
  context operators before exporting a stitched handoff narrative
- that full-text path now also reuses a dedicated external scheduler search service plus tuned
  relevance scoring, so repeated incident review searches do not depend on rebuilding every
  lexical hint from health-record payloads or the run repository
- that same scheduler retrieval now also keeps query analytics and operator relevance feedback,
  then folds those signals into learned ranking adjustments, so the next handoff search can bias
  toward the narrative patterns operators already judged useful
- that same scheduler retrieval now also has a query analytics dashboard and feedback moderation
  queue, so operators can review which searches are being used and approve relevance signals
  before they influence learned ranking
- that same scheduler search quality workflow now also exposes long-horizon trend buckets,
  moderator and actor rollups, stale/high-score moderation backlog signals, and batch moderation
  actions, so governance can clear or review search feedback as an operational queue instead of
  one row at a time
- that same scheduler governance path now also provides moderation policy catalogs and staged
  approval plans, so operators can stage selected search feedback, enforce score or note
  requirements, and apply approved moderation batches back into learned scheduler ranking
- those same moderation policy catalogs now also expose revision history, audit trails, and bulk
  governance, so teams can review lifecycle changes and roll out governance-default updates
  across multiple moderation catalogs in one pass
- that same moderation-catalog layer now also has reusable governance policies and a staged
  approval queue for catalog lifecycle changes, so teams can preview, approve, and apply search
  moderation catalog updates behind saved governance defaults before those defaults start driving
  future moderation plans
- that same retrieval path now also emits cross-occurrence semantic/vector clusters, so a handoff
  can start from grouped recovery or failure narratives instead of only a flat ranked result set
  from scratch before ranking results
- those saved scheduler narrative templates and boards now also support edit, delete, and
  revision-restore workflow, so teams can correct or retire shared review lenses without losing
  the previous incident-handoff snapshot
- the same scheduler narrative workspace now also has bulk governance controls, so shift leads
  can review, delete, or restore multiple saved templates and boards during cleanup without
  repeating one-by-one actions
- that bulk governance flow now also supports advanced batch edits for metadata, query filters,
  registry template links, and board layout flags, so the saved scheduler review layer can be
  re-aligned during incident handoff without reopening each entry individually
- those same bulk edits now stage a governance plan first, showing per-entry diffs, requiring an
  explicit approval step before apply, and keeping rollback targets tied to the captured
  pre-approval revisions if the shared scheduler review lens needs to be reverted
- the scheduler governance layer now also supports reusable policy templates and an approval queue,
  so shift leads can stage named lane/priority defaults for repeated handoff flows and review
  pending vs ready-to-apply narrative plans without scanning a flat plan registry
- those policy templates now also have revision history and a shared team audit trail, so review
  defaults can be edited, deleted, restored, and traced without leaving the control room
- the same approval queue now also supports batch approve/apply, and named governance policy
  catalogs can reapply linked template bundles plus queue defaults when a handoff or follow-the-sun
  review cycle needs to rehydrate the same discipline quickly
- those policy catalogs now also expose revision history, team audit, and bulk lifecycle controls,
  so handoff presets can be edited, deleted, restored, and batch-retired without leaving the
  operator workspace
- those same policy catalogs can now capture reusable template/registry governance hierarchies and
  stage them directly into the approval queue, so a shift handoff can repopulate a catalog-linked
  review stack in one action instead of re-previewing each plan manually
- those captured hierarchies now also expose step-level edit, revision-restore, and bulk
  governance workflow, so operators can correct or selectively recover one reusable hierarchy step
  without replacing the rest of the catalog
- those same hierarchy steps can now be saved as named step templates and reapplied across several
  policy catalogs, so cross-catalog handoffs can sync one reviewed governance step into multiple
  queue catalogs without rebuilding it one catalog at a time
- those hierarchy-step templates now also have their own edit/delete/revision-restore, bulk
  governance, and shared team audit workflow, so the reusable cross-catalog step library can be
  cleaned up, recovered, and attributed without re-exporting the same hierarchy step from a live
  catalog
- those same reusable hierarchy-step templates now also store queue policy defaults and can stage
  approval-queue plans directly, so a reviewed cross-catalog step can reopen with the intended
  lane, priority, and policy provenance instead of relying on manual queue reconfiguration
- the same queue now also filters by source hierarchy-step template and supports batch staging from
  selected reusable step templates, so shift operators can reopen one source lineage or a reviewed
  bundle of reusable steps as approval work in a single action
- that same source-template approval queue now also supports server-side search, sort, and saved
  dashboard views, so operators can reopen the exact hierarchy-step approval slice and ordering
  they used during a previous shift review
- run provenance and rerun-boundary views
- lineage posture summaries that collapse rerun taxonomy into exact-match, drift-aware, or unresolved
  operator guidance
- comparison and lineage-oriented research surfaces
- incident and operator-event history

## Triage

1. Identify the affected venue, symbol set, and timeframe.
   If one alert covers multiple symbols, use the control-room primary-focus note as the initial
   review anchor rather than guessing the lead symbol.
2. Determine whether the issue is freshness, gap coverage, repeated failure, or lineage ambiguity.
3. Determine whether any active sandbox, paper, or guarded-live sessions depend on the affected data.
4. Separate one-off lag from a true incident. Repeated failure or unclear lineage is an incident.

## Immediate Actions

1. Pause or stop active work that depends on data you cannot defend.
2. Record the affected symbols, timeframe, and visible failure mode.
3. If the issue affects promotion or benchmark claims, block those decisions until lineage is clear.
4. If the issue affects guarded-live readiness, treat it as a safety blocker rather than a data nuisance.

## Resolution Path

1. Wait for sync recovery only if the gap is clearly bounded and no live-affecting action depends on it.
2. Rerun or compare only after the dataset boundary is explicit again.
3. If freshness recovers but lineage is still ambiguous, keep the incident open.
4. Record whether the final posture is exact-match, drift-aware, or unresolved.

## Escalate If

- the same venue or timeframe continues failing across multiple sync cycles
- gap windows grow while active execution remains exposed
- rerun validation cannot explain whether a result is matched or drifted
- the operator cannot explain which dataset identity or checkpoint a decision relied on

## Closeout Record

Record at minimum:

- affected venue, symbol set, and timeframe
- failure class
- active sessions impacted
- whether stop or hold actions were taken
- the final lineage posture used to reopen work

## Related Runbooks

- [Daily Operations Checklist](daily-operations-checklist.md)
- [Sandbox Runtime Incident](sandbox-runtime-incident.md)
- [Release And Docs Checklist](release-and-docs-checklist.md)
