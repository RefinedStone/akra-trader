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
- the stitched report views layer now composes dedicated saved-view and approval-policy
  collaborators instead of keeping saved-view lifecycle, stitched approval queue, and policy
  catalogs inline in one module
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
