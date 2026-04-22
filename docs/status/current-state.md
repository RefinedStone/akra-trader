# Current State

Canonical status snapshot for the repository as of April 22, 2026.

Use this document as the source of truth for what is actually implemented. Forward-looking planning
lives under [Roadmap](../roadmap/README.md) and [Blueprint](../blueprint/README.md).

## Product Position

`akra-trader` is currently best described as a single-operator research and runtime control
workstation for crypto-first strategy development.

It is no longer only a backtest demo:

- durable research runs, comparison, presets, and reruns are already present
- sandbox worker sessions exist with heartbeat and restart recovery semantics
- guarded-live control surfaces exist with kill switch, reconciliation, recovery, and venue-backed
  launch gates
- operator visibility includes incidents, delivery history, and audit-oriented surfaces

It is not yet a finished live trading product:

- custom strategy registration is still process-local
- experiment storage remains payload-centric in key paths
- control-room UX now has route-aware shell boundaries, but feature logic is still too monolithic
- guarded-live venue lifecycle handling is real but not complete
- LLM research infrastructure remains an interface skeleton

## Stage Read

- Stage 0: complete
- Stage 1 Research Foundation: largely complete
- Stage 2 Experiment OS: materially underway
- Stage 3 Runtime Ops: partially complete with real worker semantics
- Stage 4 Guarded Live: early but real control-plane coverage
- Stage 5 Intelligence Research: contract only

## Implemented Now

### Research core

- FastAPI backend with explicit domain, application, adapter, and runtime boundaries
- split port contracts under `port_contracts/*` with `ports.py` kept as a compatibility shim
- shared application fallback adapters and comparison policy moved into `application_support/*`
- run-surface enforcement and run serialization helpers moved into `application_support/run_surfaces.py`
- standalone surface/runtime query types plus filter/sort helpers moved into
  `application_support/runtime_queries.py`
- standalone surface binding catalogs moved into
  `application_support/standalone_surface_catalog.py`
- standalone surface execution, query-discovery serialization, and run-subresource binding helpers
  moved into `application_support/standalone_surfaces.py`
- durable run storage through `SqlAlchemyRunRepository`
- repo-local SQLite defaults with configurable Postgres support
- native backtest execution with persisted config, metrics, orders, fills, positions, notes, equity,
  and provenance
- native market-data lineage with dataset identity fingerprints, sync-checkpoint links, canonical
  dataset-boundary contracts, and rerun boundaries
- normalized market-data lineage history and ingestion-job query surfaces for symbol/timeframe
  inspection
- reference-runtime delegation for NostalgiaForInfinity backtests with stored benchmark provenance

### Experiment OS baseline

- run history listing and filtering by mode, strategy, version, and rerun-boundary identity
- native vs reference comparison API and control-room comparison workflow
- experiment presets with lifecycle actions, revisions, and restore flows
- typed query/filter contracts for strategies, presets, runs, and comparison surfaces
- shared query-discovery and run-surface capability contracts for typed query builders and run
  subresource actions
- strategy semantic metadata and parameter-contract hints propagated from catalog records into run
  snapshot and provenance views
- replay-link alias governance, audit browsing, and export-job utilities for query-builder surfaces
- native, sandbox, and paper reruns from stored rerun boundaries with claim-aware validation
  categories for exact-match, checkpoint, window-only, delegated, and mode-translation results

### Runtime ops baseline

- sandbox worker sessions that continue processing newly arrived candles after a priming window
- persisted sandbox heartbeat cadence, processed-candle progress, and recovery history
- separate paper-session mode instead of collapsing paper into sandbox history
- market-data sync for ccxt-backed Binance, Coinbase, and Kraken with gap detection, lag reporting,
  sync checkpoints, backfill status, and failure history
- operator visibility for stale sandbox workers, worker failures, and recent runtime audit events

### Guarded-live baseline

- guarded-live kill switch, reconciliation, recovery, and resume control surfaces
- gated live launch behind configuration, reconciliation, and recovery checks
- venue-backed live order submission plus persisted live run history
- tracked live order lifecycle sync back into local orders, fills, positions, and audit notes
- operator cancel and replace actions for active live orders
- persisted live-session ownership and durable open-order snapshots
- venue-session handoff and continuation baseline for Binance, with supported continuation paths for
  Coinbase Advanced Trade and Kraken public market transport
- guarded-live incidents, delivery attempts, acknowledgment, escalation, remediation state, and
  provider workflow sync
- incident-delivery alias normalization and provider dispatch now flow through an explicit registry
  layer instead of only large condition chains
- the highest-traffic provider family methods for PagerDuty, Opsgenie, incident.io, FireHydrant,
  and Rootly now live in `adapters/operator_delivery_core_providers.py`

### Control room baseline

- route-aware React control-room shell with dedicated workspace routing metadata and shell layout
  modules under `apps/web/src/app/*`
- workspace-level panel grouping now lives under `apps/web/src/routes/*`
- shared control-room type/constant definitions now live in `apps/web/src/controlRoomDefinitions.ts`
- shared control-room transport helpers now live in `apps/web/src/controlRoomApi.ts`
- run-surface capability and comparison-boundary helpers now live in
  `apps/web/src/runSurfaceCapabilities.tsx`
- query-builder feature logic now lives under `apps/web/src/features/query-builder/*`
- query-builder now separates a tiny entry module, a feature model module, a main component
  module, and a replay-governance section module so parser/storage and replay governance are no
  longer mixed into the feature entrypoint
- dense feature content is still mostly in one large control-room file, but shell/routing concerns,
  route-level panel selection, run-surface capability helpers, and query-builder rendering are no
  longer defined inline with the remaining control-room body
- separate histories for backtest, sandbox, paper, and live modes
- guarded-live panels for candidacy blockers, venue snapshots, recovery state, and audit history
- operator surfaces for replay-link alias governance and audit export administration
- runtime control-room workflows now consume focused market-data lineage and ingestion-job history
  for selected instruments during incident triage
- multi-symbol runtime alerts now resolve to a deterministic primary triage focus using instrument
  risk, live-session relevance, payload symbol order, and stable lexical fallback, with the reason
  shown inline to operators
- backend operator alert and incident payloads now embed explicit `primary_focus` metadata for
  multi-symbol contexts so the control room does not have to infer the lead symbol only from
  heuristic parsing
- external operator webhook payloads and provider remediation payloads now carry the same
  normalized `symbol`/`symbols`/`timeframe` plus `primary_focus` context for downstream routing
- provider workflow pull snapshots and remediation sync now restore returned `primary_focus`
  market context back into normalized incident and provider-recovery fields
- provider workflow action payloads now project `market_context` into vendor-specific structured
  fields such as `custom_details`, `details`, or `metadata`, and notes/messages print that block
  separately from generic action context for operator/provider audit
- provider workflow pull normalization now reads that same vendor-native `market_context` back from
  `custom_details`, `details`, or `metadata` so normalized provenance survives round-trips through
  third-party incident systems
- restored provider market context now also preserves provider-specific source provenance for the
  normalized `symbol`, `symbols`, `timeframe`, and `primary_focus` fields carried in provider
  recovery state, and the control-room incident drill-down plus triage export now surface that
  provenance directly to operators
- provider provenance export in the control room now has operator-facing provider/vendor-field
  filters, sort modes, persisted local export history, a team-shared server registry with
  download audit trail, analytics/cross-focus dashboard rollups, and daily time-series views for
  provider drift plus export burn-up instead of a one-off clipboard action
- provider provenance analytics now also supports server-side saved presets, shared dashboard
  views, scheduled provenance reports with background due-run execution plus manual controls, and
  report audit history so the analytics workbench is no longer browser-local only
- operator visibility now also exposes provider-provenance scheduler health with lag/failure
  alerts and audit events, so background report automation is observable alongside runtime faults
- provider provenance analytics now also persists scheduler health-cycle history and exposes
  paginated cycle history, JSON/CSV export, and daily-to-hourly health/lag drill-down surfaces in
  the control room, so provenance automation can be reviewed as an operational timeline instead of
  only a point-in-time alert snapshot
- scheduler-health exports can now also be shared into the same server-side registry with delivery
  and download audit trail plus direct escalation workflow, so automation snapshots can move from
  review into operator handoff without leaving the control room
- those shared scheduler exports now also persist per-export routing and approval policy, so
  chatops-only review, paging routes, and manual approval gates are all visible and enforceable
  before escalation is sent
- scheduler lag and failure alerts now also auto-open that scheduler-export workflow in backend
  automation, creating one shared snapshot per active alert condition and auto-escalating it when
  the saved routing and approval policy already allow delivery; the alert surface can still jump
  into that same workflow for review or follow-up approval
- resolved scheduler alert history rows can now reconstruct historical scheduler-health exports
  from the matching persisted health records instead of always snapshotting the current scheduler
  state, so post-incident handoff can follow the actual alert window that already closed
- scheduler alert history now preserves every lag/failure occurrence per category with occurrence
  ids and timeline position metadata, and the control-room history rows surface that timeline for
  resolved entries instead of collapsing to only the latest scheduler occurrence
- provider provenance analytics now also exposes a paginated scheduler-only alert timeline surface
  with category/status filters, so occurrence review no longer depends on the global operator
  alert-history table
- resolved scheduler occurrences can now export mixed-status post-resolution narratives, so the
  shared scheduler artifact can capture recovery, healthy stabilization, and other intervening
  statuses instead of only the original lag/failure rows
- the same scheduler occurrence slice can now also export, copy, download, and share stitched
  multi-occurrence narrative reports, so repeated lag/failure windows can move into one handoff
  artifact instead of forcing row-by-row reconstruction
- stitched scheduler reports now also have a dedicated saved-view surface, so operators can
  persist a named occurrence slice with export limits and later re-apply, edit, delete, inspect
  immutable revisions, restore old snapshots, copy, download, or share that exact stitched-report
  lens without rebuilding it from the timeline toolbar
- those saved stitched report views now also support bulk governance and a shared team audit
  trail, so multiple saved scheduler handoff lenses can be patched, retired, restored, and
  reviewed across shifts without treating them as browser-local personal state
- those same saved stitched report views now also stage governance plans through the approval
  queue and can reuse named policy templates, so bulk edits move through diff preview, approval,
  apply, and rollback instead of bypassing the shared governance lane
- those saved stitched report views now also expose their own approval-queue slice and stitched
  report policy-catalog surface, so operators can review saved-view governance plans and apply
  stitched-specific queue defaults without jumping back to the generic scheduler governance panel
- that stitched-report governance workspace now also has a stitched-report-only registry and
  revision lifecycle layer, so teams can save, re-apply, delete, and restore dedicated queue
  slices plus default policy bundles without treating stitched-report governance as a filtered
  view of the shared policy catalog alone
- those stitched-report governance registries now also support bulk lifecycle edits and a shared
  team audit surface, so queue-slice bundles can be patched, retired, restored, and reviewed
  across shifts without dropping back to one-registry-at-a-time maintenance
- those same stitched-report governance registries now also stage through the shared governance
  approval queue with reusable policy templates and catalogs, so queue-slice/default-policy bundle
  changes can be previewed, approved, applied, and rolled back instead of mutating directly
- that same stitched-report governance registry workspace now also exposes its own registry-only
  approval-queue slice and stitched-governance-registry policy-catalog surface, so teams can
  review registry plans and apply registry-scoped queue defaults without pivoting back to the
  broader shared scheduler governance panels
- that scheduler occurrence workspace now also exposes a narrative facet plus dedicated named
  templates and narrative-registry boards, so teams can preserve post-resolution recovery or
  recurring-occurrence review layouts as reusable scheduler lenses instead of rebuilding those
  filters by hand
- those scheduler templates and registry boards now also carry edit, delete, and revision-restore
  workflow, so operators can evolve or retire saved narrative lenses without losing prior
  snapshots
- those same scheduler templates and registry boards now also support bulk governance, so control
  room operators can select, delete, or restore multiple saved review lenses in one workflow
  instead of repeating single-entry maintenance
- that bulk governance layer now also supports advanced batch edits, so operators can patch saved
  scheduler narrative names, descriptions, query filters, and shared-board links/layout flags
  across multiple entries in one pass
- scheduler narrative bulk governance now also runs through staged governance plans with per-item
  diff preview, explicit approval, drift checks at apply time, and rollback plans pinned to the
  captured pre-change revisions instead of applying irreversible batch edits immediately
- scheduler narrative governance now also has reusable approval-policy templates plus a control-room
  approval queue view, so staged plans can carry named lane/priority defaults and be reviewed as a
  queue instead of a flat unprioritized plan list
- those governance policy templates now also support edit/delete/version workflow plus a shared
  audit trail, so lane/priority defaults are no longer opaque create-once records
- that approval queue now also supports multi-plan batch approve/apply, and governance policy
  catalogs can bundle linked policy templates into reusable queue/default-policy presets for shift
  handoff workflows
- those governance policy catalogs now also support edit/delete/revision restore, shared audit, and
  bulk governance updates in the control room, so catalog lifecycle is durable instead of being a
  create/list-only preset layer
- those same policy catalogs can now also capture reusable template+registry governance hierarchies
  and stage them straight into the approval queue, with catalog-linked plan metadata so operators
  can review a whole staged hierarchy by its source catalog instead of treating each preview as
  orphaned queue work
- policy-catalog hierarchy steps now also have their own edit, revision-restore, and bulk
  governance workflow in the control room, so reusable staged hierarchies can be corrected or
  selectively restored without recapturing or restoring the whole catalog
- those hierarchy steps can now also be promoted into named reusable step templates and pushed back
  across multiple policy catalogs, so cross-catalog governance no longer depends on recapturing the
  same hierarchy step in every catalog by hand
- those hierarchy-step templates now also support edit/delete/revision restore, bulk governance,
  and a shared team audit surface, so the cross-catalog step library can be corrected, retired,
  reinstated, and traced without recreating each reusable step from an active policy catalog
- those same hierarchy-step templates now also carry saved governance policy defaults and can stage
  approval-queue plans directly, so reusable cross-catalog steps preserve their lane/priority
  policy layer when operators reopen them as queue work
- that approval queue now also filters by source hierarchy-step template and reusable step library
  selections can be batch-staged into queue plans, so operators can reopen one reviewed source or a
  whole selected handoff set without staging each template row one at a time
- the same approval queue now also runs its source-template slice as a server-side query with
  search, sort, and shared dashboard-view persistence, so hierarchy-step approval review can be
  reopened as a named queue workspace instead of a one-off local table filter

### Operator discipline baseline

- baseline runbook set now exists under `docs/operations/*` for daily operations, data incidents,
  sandbox incidents, guarded-live reconciliation, kill-switch handling, and release-time docs
  discipline
- operations documentation now links operator checks and escalation rules back to product-visible
  runtime and guarded-live surfaces

## Partial Or Fragile Areas

- custom strategy registration exists, but registration metadata is still process-local rather than a
  durable strategy registry
- dataset-boundary contracts, rerun validation categories, operator-visible lineage summaries, and
  normalized lineage or ingestion history surfaces now exist, and the control room now consumes
  focused history for incident triage with alert-linked focus routing, merged lineage incident
  history, normalized alert symbol/timeframe payloads, and deterministic multi-symbol primary-focus
  routing plus backend `primary_focus` metadata, but deeper operator action guidance and richer
  history query controls on top of those surfaces are still thin
- provider provenance analytics is now durable, team-shared, and background-scheduled, but there
  are still no saved cross-team dashboard collections above preset/view/report records yet
- run storage is durable, but experiment querying and artifact retrieval still lean too heavily on
  payload-centric persistence
- the control room now has route and shell boundaries, but workspace feature modules still need to
  be extracted out of `App.tsx`
- the top-level control-room file no longer owns its full type/constant, API helper, run-surface
  helper, or query-builder context, but it still owns too much feature-local state and dense
  rendering logic
- the query-builder feature now has a smaller reading surface than before, but its main component
  and model modules are still much larger than one flow should be
- standalone surface binding catalogs are isolated from the executor now, but the catalog module is
  still broad and should split further by bounded flow
- sandbox workers exist, but recent decisions, lag interpretation, and active-session-first operator
  workflows are still weaker than the underlying backend capabilities
- `application.py` and `operator_delivery.py` are smaller and more structured than before, but both
  still need further decomposition into dedicated use-case and provider modules
- `operator_delivery.py` no longer owns the full hot-path provider family end to end, but the
  remaining long-tail provider bodies still need the same treatment
- guarded-live recovery restores meaningful control-plane and order-lifecycle state, but it does not
  yet resume a full venue-native session lifecycle in all cases
- incident delivery and provider sync are broad, but provider-owned policy management and external
  incident ownership remain incomplete
- deployment guidance, backups, and secret governance are not yet product-grade, and the runbook
  baseline still needs drill validation against fuller venue and recovery coverage
- the LLM lane still stops at `DecisionEnginePort`, template strategy shapes, and trace-capable
  envelopes

## Not Implemented Yet

- durable custom strategy registration lifecycle and promotion workflow
- normalized experiment storage for common query, artifact, and export paths
- full venue-native amend flows and broader live order lifecycle management
- complete restart recovery for venue-native live session lifecycles
- operator-grade deployment/runbook package
- prompt versioning, raw trace persistence, replay harness, and fallback/review controls for LLM
  decision research
- multi-user workflows, RBAC, and organization features

## Immediate Next Priorities

1. Harden deterministic research claims around dataset identity, rerun validation, and lineage gaps.
2. Finish the Experiment OS around durable strategy lifecycle, normalized experiment queries, and
   artifact/export posture.
3. Productize the control room around active-session operations, clearer operator workflows, and
   decomposed UI surfaces.
4. Complete guarded-live safety around fuller venue lifecycle handling, runbooks, and deployment
   discipline.
5. Keep the LLM lane isolated until trace, replay, and fallback infrastructure are real features.

## Supporting Docs

- [Product Position](product-position.md)
- [Roadmap Overview](../roadmap/README.md)
- [Next Wave Plan](../roadmap/next-wave-plan.md)
- [Architecture](../architecture.md)
- [LLM Sensitivity](../architecture-llm-sensitivity.md)
- [Blueprint](../blueprint/README.md)
