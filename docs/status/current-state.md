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
- scheduler lag and failure alerts can now trigger that scheduler-export workflow directly, creating
  a fresh shared snapshot from the alert surface and optionally sending it immediately when the
  saved routing policy allows delivery without additional approval

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
