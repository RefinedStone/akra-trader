# Technical Roadmap

Rebased to the repository state as of April 22, 2026.

## Goal

Advance the architecture without breaking the core boundary rule:

- domain and application code stay independent from frameworks, exchanges, storage engines, and
  LLM providers

## Current Technical Baseline

Already implemented:

- explicit ports for market data, strategy catalog, run storage, guarded-live state, venue state,
  references, and decision engines
- durable run persistence through SQLAlchemy
- native runtime decomposition into data, execution, risk, cache, supervision, and mode services
- market-data sync with checkpoints, backfill status, gap visibility, and failure history
- experiment presets, rerun boundaries, richer query/filter contracts, and comparison surfaces
- sandbox worker heartbeat and restart recovery
- guarded-live kill switch, reconciliation, recovery, incidents, and venue-backed launch gates

The roadmap now focuses on technical completion and productization rather than greenfield feature
creation.

## Track A: Data Trust And Determinism

### Current baseline

- candle-backed runs already store dataset identity fingerprints
- runs can link directly to sync checkpoints and rerun boundaries
- canonical dataset-boundary contracts and claim-aware rerun validation categories now exist in run
  provenance
- market-data status already exposes checkpoints, gap windows, backfill, lag, and failure history
- normalized lineage-history and ingestion-job query surfaces now exist for symbol/timeframe
  inspection

### Remaining work

- clearer lineage mismatch reporting when rerun guarantees cannot be made
- stronger operator-facing workflows around data-boundary health, ingestion history, and mismatch
  interpretation
- retention, drill, and escalation policy for lineage-history and ingestion-job review paths

## Track B: Experiment OS And Persistence

### Current baseline

- durable run repository with rich provenance payloads
- presets with revisions and lifecycle actions
- richer run, preset, strategy, and comparison query contracts
- native and reference runs already share a comparison and provenance posture

### Remaining work

- durable custom strategy registry and promotion lifecycle
- normalized experiment summary tables for common query paths
- artifact/export registry beyond loosely structured provenance payloads
- clearer benchmark-pack and promotion review model

## Track C: Control Room Productization

### Current baseline

- one control room already covers research launch, histories, comparison, alerts, incidents, and
  guarded-live panels
- operator actions already reach sandbox stop, live stop, cancel/replace, reconciliation, recovery,
  and incident workflows
- runtime operator workflows now include focused lineage-history and ingestion-job triage for the
  currently selected market-data instrument, plus alert-linked focus routing and inline lineage
  incident history
- runtime and guarded-live alert payloads now include normalized symbol/timeframe context where the
  runtime can resolve it directly
- multi-symbol operator alerts now collapse onto one deterministic primary market-data focus using
  instrument risk, live-session relevance, payload order, and stable fallback
- backend operator payloads now expose explicit `primary_focus` metadata so consumers can use the
  selected symbol/timeframe directly instead of rebuilding that choice from raw symbol lists
- external webhook delivery and provider remediation payload builders now pass through that same
  normalized market context for downstream incident tooling
- provider workflow pull normalization now restores returned `primary_focus` market context into
  incident and provider-recovery state rather than keeping only raw target lists
- provider workflow action payloads now project `market_context` into vendor-native structured
  fields like `custom_details`, `details`, or `metadata`, while note/message text keeps the same
  block human-readable in downstream timelines
- provider workflow pull normalization now reads that vendor-native `market_context` back into the
  normalized pull snapshot instead of relying only on top-level provider recovery fields
- normalized provider recovery state now preserves provider-specific source provenance for restored
  market-context fields so downstream audit and export surfaces can distinguish vendor paths, and
  the control room now shows and exports that provenance during incident triage
- provider provenance export in the control room now includes filter/sort controls, persisted
  local export history, a shared server-side registry with audit trail, analytics plus
  cross-focus query rollups, and time-series drift / burn-up dashboards, moving it closer to a
  real operator handoff surface
- provider provenance analytics now also persists saved presets, shared dashboard views, and
  scheduled provenance reports with background due-run execution, manual controls, and audit
  history, so analytics state is durable across operators rather than pinned to one browser tab
- runtime operator visibility now also surfaces provider-provenance scheduler health plus lag and
  failure alerts, so automation regressions can share the same operational channel as worker faults
- provider provenance automation now also keeps durable scheduler health history and exposes
  paginated history, export, and daily-to-hourly health / lag drill-down surfaces in the control
  room, closing the gap between transient scheduler alerts and reviewable operations history
- scheduler-health export now also plugs into the shared export registry with audit trail and
  delivery-backed escalation workflow, so provenance automation review can promote directly into an
  operator handoff artifact
- per-export routing and approval policy now sits on top of that scheduler export workflow, so
  escalation targets and approval gates can be chosen and audited at the export artifact level
- runtime alert review now sits on top of backend auto-created scheduler-export workflows for
  lag/failure conditions, so automation faults open one shared handoff artifact automatically and
  can escalate it immediately when policy allows, tightening the loop between automation detection
  and operator
  handoff

### Remaining work

- decompose the current monolithic UI into clearer product surfaces
- improve active-session views for positions, fills, lag, and recent decisions
- align UI state and operator workflows with runbooks and promotion rules
- add team-level dashboard collections above the current preset/view/report records

## Track D: Runtime Ops And Guarded-Live Stabilization

### Current baseline

- sandbox workers already persist heartbeat, runtime-session progress, and recovery history
- guarded-live control state already persists kill switch, reconciliation, recovery, incidents,
  delivery history, and session ownership
- venue-backed live launch, order cancel, and order replace already exist
- Binance handoff, plus supported Coinbase and Kraken continuation paths, already exist at the
  control-plane level

### Remaining work

- simplify and clarify runtime-session models for operators
- broaden venue-native lifecycle recovery and amend/order-management coverage
- make deployment, credentials, and drill workflows first-class operational concerns

## Track E: Intelligence Research Lane

### Current baseline

- `DecisionEnginePort`
- template strategy shape
- shared decision-envelope contract

### Remaining work

- prompt registry
- raw trace storage
- replay harness
- fallback or review enforcement
- provider-backed decision-engine adapters

## Technical Exit Criteria For The Next Major Milestone

The next milestone should meet these checks:

- repeated runs can defend their dataset identity and mismatch posture
- custom strategy lifecycle is durable across restart and queryable without payload-heavy scans
- the control room reflects active runtime work as clearly as historical inspection
- guarded-live safety is backed by productized operational discipline, not only backend capability
- the LLM lane remains isolated until trace and replay controls exist
