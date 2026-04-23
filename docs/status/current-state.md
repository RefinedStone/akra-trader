# Current State

Canonical status snapshot for the repository as of April 23, 2026.

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
- comparison serialization helpers moved into
  `application_support/comparison_serialization.py`
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
- shared control-room type families now live under `apps/web/src/controlRoomDefinitions/*`
  behind `apps/web/src/controlRoomDefinitions.ts`
- shared control-room transport helpers now live under `apps/web/src/controlRoomApi/*` behind
  `apps/web/src/controlRoomApi.ts`
- run-surface capability and comparison-boundary helpers now live in
  `apps/web/src/runSurfaceCapabilities.tsx`
- query-builder feature logic now lives under `apps/web/src/features/query-builder/*`
- route smoke tests now cover `WorkspaceRouteContent` plus the dedicated workspace route shells
- query-builder now separates a tiny entry module, a feature model module, a main component
  module, replay-governance/replay-apply/replay-collision/simulation-diff/replay-step section
  modules, replay-intent/replay-review/replay-promotion flow hooks, an expression-authoring flow
  hook, a coordination-simulation flow hook, and a shared runtime-candidate trace review component
  so URL hydrate, alias-resolution, share/export administration, governance sync, expression
  authoring, replay apply conflict review, replay promotion approval, replay provenance review,
  runtime-candidate drill-through, and the solver-heavy coordination path no longer sit inline with
  the main component body
- provider-provenance workspace cards plus dedicated workspace section collaborators now own the
  saved report, cross-focus query, scheduler workspace, analytics review, and shared registry audit
  flows, so runtime incident triage no longer carries that provider-provenance workspace body
  inline
- the provider-provenance workspace cards layer now routes the governance policy templates surface
  through a dedicated card plus template-registry, policy-catalog, catalog-hierarchy,
  hierarchy-step-template, and policy-catalog-audit collaborators instead of one giant governance
  card body inside `RuntimeProviderProvenanceWorkspaceCards`
- the provider-provenance workspace cards layer now routes the scheduler narrative templates
  surface through a dedicated card wrapper instead of keeping template drafting, bulk governance,
  registry listing, and revision history inline inside `RuntimeProviderProvenanceWorkspaceCards`
- the scheduler narrative templates card now composes dedicated bulk-governance, registry-table,
  and revision-history collaborators instead of mixing bulk governance, template registry rows,
  and template revision history inline in one card body
- the provider-provenance workspace cards layer now routes the scheduler narrative registry
  surface through a dedicated card wrapper instead of keeping registry drafting, bulk governance,
  registry listing, and revision history inline inside `RuntimeProviderProvenanceWorkspaceCards`
- the scheduler narrative registry card now composes dedicated bulk-governance, registry-table,
  and revision-history collaborators instead of mixing bulk governance, registry rows, and
  registry revision history inline in one card body
- the scheduler narrative registry bulk-governance collaborator now composes dedicated
  governance-bar and bulk-edit-stage collaborators instead of mixing selection-policy preview
  actions and advanced bulk edit staging inline in one governance module
- the scheduler narrative registry table collaborator now composes dedicated table-view and
  row-detail collaborators instead of mixing table shell, row review, and row actions inline in
  one registry module
- the scheduler narrative template bulk-governance collaborator now composes dedicated
  governance-bar and bulk-edit-stage collaborators instead of mixing selection-policy preview
  actions and advanced bulk edit staging inline in one governance module
- the scheduler narrative template registry-table collaborator now composes dedicated table-view
  and row-detail collaborators instead of mixing table shell, row review, and row actions inline
  in one registry module
- the scheduler narrative template revision-history collaborator now composes dedicated
  history-table and revision-action collaborators instead of mixing revision table shell and
  revision mutations inline in one history module
- the hierarchy-step-template collaborator now composes dedicated draft, registry, versions, and
  audit collaborators instead of keeping template drafting, bulk cross-catalog governance,
  revision history, and audit review inline in one section module
- the hierarchy-step-template registry collaborator now composes dedicated bulk-selection-stage,
  bulk-step-stage, and registry-table collaborators instead of mixing bulk template staging,
  hierarchy step patch staging, and the registry table body inside one section module
- the hierarchy-step-template registry-table collaborator now composes dedicated row-detail and
  row-action collaborators instead of mixing template/origin review cells and row mutations inline
  in one table owner
- the hierarchy-step-template versions collaborator now routes revision history through a dedicated
  versions-table collaborator, and the versions-table layer now composes dedicated version-row-
  detail and version-row-action collaborators instead of keeping revision review and restore
  actions inline in one section module
- the hierarchy-step-template audit collaborator now composes dedicated audit-filter and audit-
  table collaborators, and the audit-table layer now routes rows through dedicated audit-summary,
  audit-template, and audit-actor cell collaborators instead of keeping filter controls and audit
  row bodies inline in one section module
- the governance-policy-template registry collaborator now composes dedicated draft, catalog-
  workflow, registry-table, versions, and audit collaborators instead of mixing template editing,
  catalog bundling, registry listing, revision history, and audit review inline in one section
  module
- the governance-policy-template registry-table collaborator now composes dedicated row-detail and
  row-action collaborators instead of mixing template/scope review cells and row actions inline in
  one table owner
- the governance-policy-template versions collaborator now routes revision history through a
  dedicated versions-table collaborator, and the versions-table layer now composes dedicated
  version-row-detail and version-row-action collaborators instead of keeping revision review and
  restore actions inline in one section module
- the governance-policy-template audit collaborator now composes dedicated audit-filter and audit-
  table collaborators, and the audit-table layer now routes rows through dedicated audit-summary,
  audit-template, and audit-actor cell collaborators instead of keeping filter controls and audit
  row bodies inline in one section module
- the governance-policy-catalog collaborator now composes dedicated bulk-edit, registry-table, and
  versions collaborators instead of mixing bulk selection edits, catalog registry listing, and
  revision history inline in one section module
- the governance-policy-catalog bulk-edit collaborator now composes dedicated bulk-selection,
  bulk-metadata-stage, and bulk-action collaborators instead of mixing selection summary/toggle
  controls, staged metadata/default-template edits, and bulk delete/restore/update actions inline
  in one filter-bar owner
- the governance-policy-catalog bulk-selection collaborator now composes dedicated bulk-selection-
  state and bulk-selection-summary collaborators instead of mixing the select-all toggle state and
  selected-count summary inline in one selection owner
- the governance-policy-catalog bulk-action collaborator now composes dedicated bulk-delete-
  action, bulk-restore-action, and bulk-update-action collaborators instead of mixing delete,
  restore, and update action triggers inline in one action owner
- the governance-policy-catalog bulk-metadata-stage collaborator now composes dedicated bulk-name-
  stage, bulk-description-stage, and bulk-default-template-stage collaborators instead of mixing
  name prefix/suffix edits, description staging, and default-template staging inline in one
  metadata owner
- the governance-catalog-hierarchy collaborator now composes dedicated bulk-selection-stage, bulk-
  patch-stage, table, editor, and versions collaborators instead of mixing bulk governance
  staging, captured-step review, direct step editing, and step revision history inline in one
  governance section module
- the governance-catalog-hierarchy bulk-selection-stage collaborator now composes dedicated bulk-
  selection-state and bulk-selection-action collaborators instead of mixing staged selection
  fields and bulk action triggers inline in one bulk staging owner
- the governance-catalog-hierarchy bulk-patch-stage collaborator now composes dedicated bulk-
  query-patch-stage and bulk-layout-patch-stage collaborators instead of mixing query and layout
  patch ownership inline in one bulk patch owner
- the governance-catalog-hierarchy table collaborator now composes dedicated row-detail and row-
  action collaborators instead of mixing captured-step review cells and row-level edit/version
  actions inline in one table owner
- the governance-catalog-hierarchy editor collaborator now composes dedicated editor-metadata-form
  and editor-patch-textarea collaborators instead of mixing metadata form controls and patch
  textarea ownership inline in one editor module
- the governance-catalog-hierarchy versions collaborator now routes revision history through a
  dedicated versions-table collaborator, and the versions-table layer now composes dedicated
  version-row-detail and version-row-action collaborators instead of keeping revision review and
  restore actions inline in one section module
- the governance-policy-catalog registry-table collaborator now composes dedicated row-detail and
  row-action collaborators instead of mixing catalog/default review cells and row actions inline
  in one table owner
- the governance-policy-catalog versions collaborator now routes revision history through a
  dedicated versions-table collaborator, and the versions-table layer now composes dedicated
  version-row-detail and version-row-action collaborators instead of keeping revision review and
  restore actions inline in one section module
- focused provider readback, persisted export history, and shared export registry flows now route
  through dedicated provider-provenance collaborators, so `RuntimeDataIncidentTriagePanel` no
  longer carries that focused provider export body inline
- focused lineage history now routes through a dedicated provider-provenance collaborator, so
  `RuntimeDataIncidentTriagePanel` no longer carries that lineage history body inline
- focused ingestion jobs now route through a dedicated provider-provenance collaborator, so
  `RuntimeDataIncidentTriagePanel` no longer carries that ingestion jobs body inline
- focused lineage incident history now routes through a dedicated provider-provenance
  collaborator, so `RuntimeDataIncidentTriagePanel` no longer carries that incident history body
  inline
- the provider-provenance scheduler workspace now routes through dedicated automation, moderation,
  stitched-governance, and shared-export sections instead of one giant scheduler body
- the scheduler moderation workspace now composes separate alert-review, moderation-governance,
  and alert-timeline sections, and the moderation-governance layer further splits policy-catalog
  ownership from approval-queue ownership instead of recombining those flows in one module
- the moderation policy-catalog layer now composes dedicated catalog-lifecycle,
  governance-policy, and meta-policy collaborators instead of keeping those three lifecycle
  surfaces inline in one section module
- the moderation approval-queue layer now composes dedicated moderation-governance,
  catalog-governance, and scheduler-moderation approval collaborators instead of keeping the three
  queue flows inline in one section module
- the stitched-governance layer now composes a stitched-report-views collaborator and a registry-
  lifecycle collaborator instead of keeping saved views, stitched approval slices, and registry
  lifecycle surfaces inline in one module
- the stitched registry editor-history layer now composes dedicated editing and audit-history
  collaborators instead of keeping registry drafting, bulk edits, table actions, team audit, and
  revision history inline in one section module
- the stitched registry editing layer now composes dedicated draft, bulk-edit, and table
  collaborators instead of keeping registry drafting, selection governance, bulk edit staging, and
  registry listing inline in one section module
- the stitched registry draft layer now composes dedicated identity-stage, default-policy-stage,
  action, and search collaborators instead of keeping registry drafting inputs, default policy
  staging, save/cancel actions, and registry search inline in one section module
- the stitched registry bulk-edit layer now composes dedicated selection-summary,
  selection-actions, metadata-stage, queue-stage, and policy-stage collaborators instead of
  keeping selection governance and bulk edit staging controls inline in one section module; the
  policy-stage now owns governance-policy staging without duplicating that selector in the
  selection-action controls, selection-actions now split between toggle-action and preview-actions
  collaborators, metadata-stage now splits name affix staged-state from description staged-state
  collaborators, queue-stage now splits queue core state from query/sort staged-state
  collaborators, and policy-stage splits default-policy staged-state from governance-policy
  staged-state while routing preview bulk-edit dispatch through a dedicated policy preview-action
  collaborator
- the stitched registry audit-history layer now routes the revision history table body through
  dedicated revision-recorded, revision-snapshot, and revision-action cell collaborators instead
  of keeping the revision row body inline in one section module, and now routes the audit-event
  table body through dedicated audit-when, audit-action, audit-actor, and audit-detail cell
  collaborators instead of keeping the audit row inline; the revision-history and audit-event
  table shells now route through dedicated table collaborators instead of staying inline in audit-
  history, and the audit filter bar is now split between dedicated select and text-input
  collaborators instead of keeping all audit filters in one block
- the stitched registry review layer now composes dedicated queue-surface and policy-catalog-
  surface collaborators instead of keeping both review shells inline in one module; the queue
  surface owns the queue summary/filter/loading shell above the queue table, and the policy-
  catalog surface owns the catalog summary/search shell above the policy catalog table; the queue
  and policy-catalog surfaces now route stable summary and empty-state leaves through dedicated
  collaborators instead of keeping those summary and empty-state blocks inline; queue rows now
  route through dedicated plan-detail, preview-detail, and action collaborators, and policy rows
  now route through dedicated catalog-detail, defaults-detail, and action collaborators
- the stitched registry review layer now routes the approval-queue table through dedicated queue-
  table and queue-row collaborators, and routes the registry policy-catalog table through
  dedicated policy-catalog-table and policy-catalog-row collaborators instead of keeping both
  table shells and row bodies inline in one review module; the review filter bars are now split
  between queue-filter-state, queue-filter-policy, queue-filter-query, and policy-catalog-search
  collaborators instead of keeping all review filters inline in one review module
- the stitched registry table layer now composes dedicated listing and revision-selection
  collaborators, now routes the table header through dedicated table-header and header-selection
  collaborators, and now also routes each registry row body through dedicated row-selection,
  row-detail, and row-action-cell collaborators instead of keeping registry listing state, header
  shell, row selection, row details, and revision toggle selection inline in one section module
- the stitched report views layer now composes dedicated saved-view and approval-policy
  collaborators instead of keeping saved-view lifecycle, stitched approval queue, and policy
  catalogs inline in one module
- the stitched report approval-policy layer now composes dedicated approval-queue and policy-
  catalog collaborators instead of keeping stitched governance queue review and policy catalog
  defaults inline in one module
- the stitched report policy-catalog layer now composes dedicated review and selection
  collaborators instead of keeping catalog review details and catalog action selection inline in one
  module
- the stitched report policy-catalog selection layer now composes dedicated action-cell and
  selection-state collaborators instead of keeping the action cell wrapper and button state inline
  in one module
- the stitched report policy-catalog selection-state layer now composes dedicated derived-state and
  selection-action collaborators instead of keeping button enablement checks and catalog-selection
  dispatch inline in one module
- the stitched report policy-catalog selection-action layer now composes dedicated action-dispatch
  and trigger-wiring collaborators instead of keeping catalog action dispatch and button wiring
  inline in one module
- the stitched report policy-catalog action-dispatch layer now composes dedicated per-action
  handlers and shared dispatch plumbing collaborators instead of keeping common catalog dispatch
  plumbing and action-specific handlers inline in one module
- the stitched report policy-catalog trigger-wiring layer now composes dedicated button-layout and
  callback-wiring collaborators instead of keeping button layout and callback binding inline in one
  module
- the stitched report policy-catalog review layer now composes dedicated default-body and
  catalog-state collaborators instead of keeping catalog state and default policy detail cells
  inline in one module
- the stitched report policy-catalog review layer now also composes dedicated table-shell and
  row-detail collaborators instead of keeping table structure and row composition inline in one
  module
- the stitched report approval-queue layer now keeps outer table shell, empty-state branching, and
  per-plan row-shell ownership while composing dedicated queue-state and action collaborators
  instead of routing plan-list row structure through one nested body wrapper
- the stitched report approval-queue action layer now composes dedicated review-state and mutation
  collaborators for a single plan row instead of also carrying plan-list row mapping and `<tr>`
  shell ownership inline with row-level review state and queue mutation controls
- the stitched report approval-queue review-state layer now composes dedicated plan-cell and
  preview-cell collaborators instead of keeping both row cells inline in one review-state owner
- the stitched report approval-queue plan-cell layer now composes dedicated identity-summary,
  origin-summary, and approval-summary leaf collaborators instead of keeping plan metadata copy
  inline in one cell owner
- the stitched report approval-queue preview-cell layer now composes dedicated preview-headline,
  rollback-summary, and preview-count leaf collaborators instead of keeping preview-state copy
  inline in one cell owner
- the stitched report approval-queue mutation layer now keeps the action-cell shell while directly
  composing queue-action and commit-control collaborators instead of routing those row actions
  through extra mutation leaf wrappers
- the stitched report approval-queue queue-action leaf now composes dedicated dispatch and
  status-view collaborators instead of keeping shared-queue dispatch and selected-state copy inline
  in one leaf owner
- the stitched report approval-queue commit-control layer now directly composes per-mutation
  plan-gate collaborators, and the plan-gate layer now mounts commit-action directly once
  eligibility-state and label-policy are resolved, instead of routing through extra passthrough
  leaf wrappers
- the stitched report approval-queue commit-action layer now composes dedicated dispatch-flow and
  mutation-trigger collaborators instead of keeping mutation dispatch branching and button rendering
  inline in one module
- the stitched report approval-queue plan-gate layer now composes dedicated eligibility-state and
  label-policy collaborators instead of keeping mutation eligibility checks and button-label policy
  inline in one module
- the stitched report approval queue-state layer now composes dedicated summary and filter-state
  plus async-state collaborators instead of pushing queue async readout down into the filter
  ownership layer
- the stitched report approval queue filter-state layer now composes dedicated query-input and
  toggle-reset collaborators directly instead of routing queue filters through a separate filter-bar
  wrapper while mixing in async queue state
- the stitched report approval queue toggle-reset layer now composes dedicated filter-select,
  reset-selection, and reset-action collaborators directly instead of routing template/catalog/sort
  controls through a separate reset-apply wrapper
- the stitched report approval queue filter-select layer now composes dedicated queue-state, lane,
  and priority selector collaborators, and the reset-selection layer now composes dedicated policy-
  template and policy-catalog selector collaborators instead of keeping multiple selector bodies
  inline in each leaf owner
- the stitched report approval queue query-input layer now composes dedicated search-input binding
  and search-input field collaborators instead of keeping search filter update wiring and input
  layout inline in one leaf owner
- the stitched report saved-view layer now composes dedicated bulk-edit, revision-review, and
  audit collaborators instead of keeping selection governance, revision restore, and team audit
  flows inline in one module
- the stitched report bulk-edit layer now composes dedicated selection-governance, filter-stage,
  and limit-policy-stage collaborators instead of keeping bulk selection, staged filter editing,
  and staged approval controls inline in one module
- the stitched report bulk limit/policy stage now composes dedicated approval and policy
  collaborators instead of keeping numeric approval staging and policy template selection inline in
  one module
- the stitched report bulk approval stage now composes dedicated limit-controls and preview
  collaborators instead of keeping numeric limit inputs and staged bulk preview controls inline in
  one module
- the stitched report bulk preview stage now composes dedicated preview-state and approval-trigger
  collaborators instead of keeping button label state and approval trigger control inline in one
  module
- the stitched report bulk limit-controls stage now composes dedicated slice-limit and
  history-limit collaborators instead of keeping slice sizing and history sizing inputs inline in
  one module
- the stitched report bulk history-limit stage now composes dedicated history and drill-down
  collaborators instead of keeping the two history sizing inputs inline in one module
- the stitched report bulk slice-limit stage now composes dedicated window, result, and
  occurrence collaborators instead of keeping the three slice sizing inputs inline in one module
- the stitched registry-lifecycle layer now composes dedicated review and editor-history
  collaborators instead of keeping registry queue/catalog review, registry editing, audits, and
  revision history in one module
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
- provider provenance tooling now covers shared exports, audit trail, scheduled reports, analytics
  dashboards, scheduler health history, and lag/failure review instead of a one-off local export
  path
- scheduler alert review now supports stitched multi-occurrence narratives, saved views, shared
  registries, revision restore, bulk governance, and staged approval queues for handoff workflows
- scheduler governance now includes reusable policy templates, policy catalogs, captured plan
  hierarchies, and dedicated approval-queue surfaces instead of one-off record mutation
- scheduler search moderation governance now also supports reusable meta-policies and a dedicated
  staged approval queue for updating moderation governance policies before those defaults change
- scheduler narrative retrieval now runs through dedicated server-side lexical/semantic search,
  ranking, clustering, external index storage, query analytics, relevance feedback, and moderation
  governance surfaces

### Operator discipline baseline

- baseline runbook set now exists under `docs/operations/*` for daily operations, data incidents,
  sandbox incidents, guarded-live reconciliation, kill-switch handling, and release-time docs
  discipline
- release and docs checklist now codifies the required sync between status, roadmap, operations,
  and planning docs whenever operator-visible capability changes
- operations documentation now links operator checks and escalation rules back to product-visible
  runtime and guarded-live surfaces

## Partial Or Fragile Areas

- data-boundary contracts, rerun validation categories, lineage mismatch summaries, and
  normalized lineage or ingestion history surfaces are in place, but richer operator action
  guidance, retention, escalation, and drill coverage on top of those surfaces are still thin
- custom strategy registration exists, but registration metadata is still process-local rather than a
  durable strategy registry
- run storage is durable, but experiment querying and artifact retrieval still lean too heavily on
  payload-centric persistence
- provider provenance analytics is now durable, team-shared, and background-scheduled, but there
  are still no saved cross-team dashboard collections above preset/view/report records yet
- the control room now has route and shell boundaries, but `App.tsx` and the remaining workspace
  feature modules still own too much dense state and rendering logic
- the query-builder feature is materially smaller across replay intent/governance, authoring/
  simulation-core, replay-review/promotion-approval, and replay provenance/runtime-candidate
  review work, but standalone surface catalogs, `application.py`, the remaining large workspace
  modules, and the long-tail provider modules still need further decomposition by bounded flow
- `domain/models.py` now re-exports extracted provider-provenance records, but the remaining
  operator and guarded-live model families still need the same treatment
- sandbox workers exist, but active-session-first views for recent decisions, lag interpretation,
  positions, and fills are still weaker than the backend capabilities
- guarded-live recovery restores meaningful control-plane and order-lifecycle state, but it does not
  yet resume a full venue-native session lifecycle in all cases
- incident delivery and provider sync are broad, but provider-owned policy management and external
  incident ownership remain incomplete
- deployment guidance, backups, secret governance, and runbook drill validation are not yet
  product-grade
- the LLM lane still stops at `DecisionEnginePort`, template strategy shapes, and trace-capable
  envelopes

## Not Implemented Yet

- durable custom strategy registration lifecycle and promotion workflow
- normalized experiment storage for common query, artifact, and export paths
- full venue-native amend flows and broader live order lifecycle management
- complete restart recovery for venue-native live session lifecycles
- operator-grade deployment, backup, and credential governance package
- prompt versioning, raw trace persistence, replay harness, and fallback/review controls for LLM
  decision research
- multi-user workflows, RBAC, and organization features

## Immediate Next Priorities

1. Finish Batch 1 by delivering durable strategy lifecycle, normalized experiment summaries, and
   artifact/export registry paths.
2. Tighten operator-facing lineage health with clearer action guidance, retention, and escalation
   rules on top of the deterministic data baseline.
3. Productize the control room around active-session operations, clearer operator workflows, and
   decomposed UI surfaces.
4. Complete guarded-live safety around fuller venue lifecycle handling, validated drills, and
   deployment discipline.
5. Keep the LLM lane isolated until prompt registry, trace, replay, and fallback infrastructure are
   real features.

## Supporting Docs

- [Product Position](product-position.md)
- [Roadmap Overview](../roadmap/README.md)
- [Next Wave Plan](../roadmap/next-wave-plan.md)
- [Architecture](../architecture.md)
- [LLM Sensitivity](../architecture-llm-sensitivity.md)
- [Blueprint](../blueprint/README.md)
